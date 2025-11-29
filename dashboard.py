"""DearPyGui dashboard for visualizing ASTERIX messages on a map.

Run with:

    python dashboard.py

This file creates a DearPyGui window to display aircraft positions on an
interactive map, with play/pause and speed controls.

The dashboard loads ASTERIX data using `decoder.Decoder().load()` (see
`decoder/__main__.py` for example usage).
"""

import time
import threading
import traceback
import colorsys

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
from tqdm import tqdm

import decoderrs
from decoder.decoder import Decoder
from decoder.geoutils import CoordinatesWGS84
from mapdata import *

DEFAULT_DATA = "Test_Data/datos_asterix_combinado.ast"

ALL_EXPECTED_COLUMNS = [
    "Category",
    "SAC",
    "SIC",
    "Time (s since midnight)",
    "Time String",
    "Latitude (deg)",
    "Longitude (deg)",
    "Height (m)",
    "Height (ft)",
    "Altitude (m)",
    "Altitude (ft)",
    "Range (m)",
    "Range (NM)",
    "Theta (deg)",
    "Mode-3/A Code",
    "Flight Level (FL)",
    "Aircraft Address",
    "Target Identification",
    "Barometric Pressure Setting",
    "Roll Angle",
    "Track Angle",
    "Ground Speed (kts) BDS",
    "Track Angle Rate",
    "TAS",
    "Magnetic Heading (deg) BDS",
    "IAS (kt)",
    "Mach",
    "Barometric Altitude Rate",
    "Inertial Vertical Velocity",
    "Track Number",
    "Ground Speed (kts)",
    "Magnetic Heading (deg)",
    "STAT",
    "GBS",
    "Is_Pure",
    "Is_Static",
]


def generate_per_frame_df(df: pd.DataFrame):
    """Interpolate sparse aircraft telemetry into per-frame samples using a vectorized approach.

    Args:
        df: Raw decoded ASTERIX records containing positional fields.

    Returns:
        DataFrame where each aircraft/category pair has a contiguous
        frame timeline with interpolated latitude, longitude, altitude,
        and motion attributes. The frame column is used later for
        playback and filtering.
    """

    # Part 1: Initial time-based interpolation for Altitude (m)
    # This remains as it was, as it operates on the original time, not frames.
    def _time_weight_interp(g):
        g = g.sort_values("Time (s since midnight)").copy()
        t = g["Time (s since midnight)"].astype(float).to_numpy()
        h = g["Altitude (m)"].to_numpy(dtype=float)
        mask_known = ~np.isnan(h)
        non_na = int(mask_known.sum())
        if non_na == 0:
            return g
        if non_na == 1:
            single_val = float(h[mask_known][0])
            g["Altitude (m)"] = single_val
            return g
        t_known = t[mask_known]
        h_known = h[mask_known]
        h_interp = np.interp(t, t_known, h_known)
        g["Altitude (m)"] = h_interp
        return g

    df = df.sort_values("Time (s since midnight)").reset_index(drop=True)
    df = pd.DataFrame(
        df.groupby(["Target Identification", "Category"], group_keys=False).apply(
            _time_weight_interp
        )
    )

    # Part 2: Vectorized frame-based processing

    # Define aggregation spec for columns
    agg_spec = {
        "Latitude (deg)": "mean",
        "Longitude (deg)": "mean",
        "Altitude (m)": "mean",
        "Height (m)": "first",
        "Height (ft)": "first",
        "IAS (kt)": "first",
        "Magnetic Heading (deg)": "first",
        "Ground Speed (kts)": "first",
        "Roll Angle": "first",
        "GBS": "first",
        "STAT": "first",
        "Time String": "first",
        "Barometric Pressure Setting": "first",
        "Track Angle": "first",
        "Ground Speed (kts) BDS": "first",
        "Track Angle Rate": "first",
        "TAS": "first",
        "Magnetic Heading (deg) BDS": "first",
        "Barometric Altitude Rate": "first",
        "Inertial Vertical Velocity": "first",
        "Track Number": "first",
        "Aircraft Address": "first",
        "Flight Level (FL)": "first",
        "Mode-3/A Code": "first",
        "Is_Pure": "first",
        "Is_Static": "first",
        "Mach": "first",
        "Theta (deg)": "first",
        "Range (m)": "first",
        "Range (NM)": "first",
    }

    # Use only columns that exist in the dataframe
    agg_spec_filtered = {k: v for k, v in agg_spec.items() if k in df.columns}

    # Aggregate to one record per aircraft/frame
    agg_df = df.groupby(["Target Identification", "Category", "frame"]).agg(
        agg_spec_filtered
    )

    # Get frame ranges for each aircraft
    frame_ranges = df.groupby(["Target Identification", "Category"])["frame"].agg(
        ["min", "max"]
    )

    if frame_ranges.empty:
        # Return an empty DataFrame with the expected columns if no data
        return pd.DataFrame(columns=df.columns.tolist() + ["Ground Status"])

    # Create a complete multi-index for all frames of all aircraft
    new_index_tuples = []
    for idx, row in frame_ranges.iterrows():
        aid, cat = idx
        for frame in range(int(row["min"]), int(row["max"]) + 1):
            new_index_tuples.append((aid, cat, frame))

    multi_index = pd.MultiIndex.from_tuples(
        new_index_tuples, names=["Target Identification", "Category", "frame"]
    )

    # Reindex to create rows for all frames, making the data dense
    per_frame_df = agg_df.reindex(multi_index)

    # Group for vectorized operations
    grouped = per_frame_df.groupby(level=["Target Identification", "Category"])

    # Interpolate coordinate columns
    interp_cols = ["Latitude (deg)", "Longitude (deg)", "Altitude (m)", "Roll Angle"]
    interp_cols_present = [c for c in interp_cols if c in per_frame_df.columns]

    if interp_cols_present:
        per_frame_df[interp_cols_present] = grouped[interp_cols_present].transform(
            lambda x: x.interpolate(method="linear", limit_direction="both")
        )

    # Forward-fill and then back-fill other columns
    ffill_cols = [c for c in per_frame_df.columns if c not in interp_cols_present]
    if ffill_cols:
        per_frame_df[ffill_cols] = grouped[ffill_cols].ffill()
        per_frame_df[ffill_cols] = grouped[ffill_cols].bfill()

    per_frame_df = per_frame_df.reset_index()

    # Add Time column
    per_frame_df["Time (s since midnight)"] = per_frame_df["frame"].astype(float)

    # Calculate Ground Status
    per_frame_df["Ground Status"] = per_frame_df.apply(
        Dashboard.determine_ground_status, axis=1
    )

    # Final sort
    per_frame_df = per_frame_df.sort_values(
        ["frame", "Target Identification", "Category"]
    ).reset_index(drop=True)

    return per_frame_df


def load_messages(
    data_file: str, parallel: bool = True, max_messages=None, decoder_choice="Python"
):
    """Decode ASTERIX data and normalize it for dashboard consumption.

    Args:
        data_file: Path to the .ast capture file.
        parallel: Whether to fan out CAT decoding across processes.
        max_messages: Optional hard cap to accelerate debugging.
        decoder_choice: "Python" for local decoder, "Rust" for FFI path.

    Returns:
        DataFrame containing the superset of columns expected by the UI
        filtered to a geographic bounding box and enriched with a frame
        index derived from the numeric timestamp.
    """
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25

    if decoder_choice == "Rust":
        raw_decoded = decoderrs.load(
            file_path=data_file,
            radar_lat=radar_lat,
            radar_lon=radar_lon,
            radar_alt=radar_alt,
            max_messages=max_messages,
        )

        # Map Rust decoder output to expected format
        decoded = []
        for item in raw_decoded:
            # Skip messages with no time information
            time_value = item.get("Time (s since midnight)", None)

            if time_value is None:
                # print("No time information found for item:", item)
                continue

            mapped_item = {}

            # Map fields with different names
            mapped_item["Category"] = item.get("Category", "")
            mapped_item["SAC"] = item.get("SAC", 0)
            mapped_item["SIC"] = item.get("SIC", 0)
            mapped_item["Time (s since midnight)"] = time_value
            mapped_item["Time String"] = item.get("Time String", "")
            mapped_item["Latitude (deg)"] = item.get("Latitude (deg)", 0)
            mapped_item["Longitude (deg)"] = item.get("Longitude (deg)", 0)
            mapped_item["Height (m)"] = item.get("Height (m)", 0)
            mapped_item["Height (ft)"] = item.get("Height (ft)", 0)
            mapped_item["Altitude (m)"] = item.get("Altitude (m)", 0)
            mapped_item["Altitude (ft)"] = item.get("Altitude (ft)", 0)
            mapped_item["Range (m)"] = item.get("Range (m)", 0)
            mapped_item["Range (NM)"] = item.get("Range (NM)", 0)
            mapped_item["Theta (deg)"] = item.get("Theta (deg)", 0)
            mapped_item["Mode-3/A Code"] = item.get("Mode-3/A Code", "")
            mapped_item["Flight Level (FL)"] = item.get("Flight Level (FL)", 0)
            mapped_item["Aircraft Address"] = item.get("Aircraft Address", "")
            mapped_item["Target Identification"] = item.get("Target Identification", "")
            mapped_item["Barometric Pressure Setting"] = item.get(
                "Barometric Pressure Setting", 0
            )
            mapped_item["Roll Angle"] = item.get("Roll Angle", 0)
            mapped_item["Track Angle"] = item.get("Track Angle", 0)
            mapped_item["Ground Speed (kts) BDS"] = item.get(
                "Ground Speed (kts) BDS", 0
            )
            mapped_item["Track Angle Rate"] = item.get("Track Angle Rate", 0)
            mapped_item["TAS"] = item.get("TAS", 0)
            mapped_item["Magnetic Heading (deg) BDS"] = item.get(
                "Magnetic Heading (deg) BDS", 0
            )
            mapped_item["IAS (kt)"] = item.get("IAS (kt)", 0)
            mapped_item["Mach"] = item.get("Mach", 0)
            mapped_item["Barometric Altitude Rate"] = item.get(
                "Barometric Altitude Rate", 0
            )
            mapped_item["Inertial Vertical Velocity"] = item.get(
                "Inertial Vertical Velocity", 0
            )
            mapped_item["Track Number"] = item.get("Track Number", 0)
            mapped_item["Ground Speed (kts)"] = item.get("Ground Speed (kts)", 0)
            mapped_item["Magnetic Heading (deg)"] = item.get(
                "Magnetic Heading (deg)", 0
            )
            mapped_item["STAT"] = item.get("STAT", "")
            mapped_item["GBS"] = item.get("GBS", False)
            mapped_item["Is_Pure"] = item.get("Is_Pure", False)
            mapped_item["Is_Static"] = item.get("Is_Static", False)

            decoded.append(mapped_item)
    else:  # Python
        decoder = Decoder()
        coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)

        decoded = decoder.load(
            data_file, parallel, max_messages=max_messages, radar_coords=coords_radar
        )
    df = pd.DataFrame(decoded).reindex(columns=ALL_EXPECTED_COLUMNS)
    df = df.dropna(subset=["Time (s since midnight)"])
    df = (
        df.assign(frame=df["Time (s since midnight)"].astype(int))
        .query("40.9 < `Latitude (deg)` < 41.7 and 1.5 < `Longitude (deg)` < 2.6")
        .reset_index(drop=True)
    )

    return df


class LoadingScreen:
    """Collects user input and asynchronously bootstraps the dashboard."""

    def __init__(self, main_controller):
        """Initialize default UI values and keep a MainController handle."""
        self.main_controller = main_controller
        self.data_file = DEFAULT_DATA
        self.max_messages = 100000
        self.load_all = False
        self.decoder_choice = "Rust"

        self.decoder_options = ["Python", "Rust"]

    def _file_dialog_callback(self, sender, app_data):
        """Update the selected file path when the picker resolves."""
        self.data_file = app_data["file_path_name"]
        dpg.set_value("data_file_text", self.data_file)

    def _load_callback(self):
        """Kick off dataset decoding on a background thread."""
        max_messages = None if self.load_all else self.max_messages

        dpg.configure_item("load_button", show=False)
        dpg.configure_item("loading_text", show=True)

        # Start loading in a separate thread to prevent GUI hanging
        def load_in_thread():
            try:
                df = load_messages(
                    self.data_file,
                    max_messages=max_messages,
                    decoder_choice=self.decoder_choice,
                )

                # Schedule UI updates to run on the main thread
                dpg.configure_item("loading_text", label="Creating dashboard...")

                dashboard = Dashboard(df)
                self.main_controller.set_dashboard(dashboard)
                dashboard.create_ui()

                dpg.delete_item("Loading Window")
                dpg.set_primary_window("Primary Window", True)
            except Exception as e:
                print(f"Error: {str(e)}")
                print(traceback.format_exc())
                dpg.configure_item("loading_text", label=f"Error: {str(e)}")
                # Show the load button again so user can retry
                dpg.configure_item("load_button", show=True)
                dpg.configure_item("loading_text", show=False)

        # Start the loading thread
        loading_thread = threading.Thread(target=load_in_thread, daemon=True)
        loading_thread.start()

    def _toggle_load_all(self, sender, app_data):
        """Enable/disable the max-messages input when toggling full loads."""
        self.load_all = app_data
        dpg.configure_item("max_messages_input", enabled=not self.load_all)

    def create_ui(self):
        """Render the loading screen widgets, dialogs, and callbacks."""
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self._file_dialog_callback,
            tag="file_dialog_id",
            width=700,
            height=400,
        ):
            # dpg.add_file_extension(".*")
            dpg.add_file_extension(".ast")

        with dpg.window(label="Loading", tag="Loading Window", width=400, height=250):
            dpg.add_text("Select ASTERIX data file:")
            with dpg.group(horizontal=True):
                dpg.add_text(self.data_file, tag="data_file_text")
                dpg.add_button(
                    label="Select File",
                    callback=lambda: dpg.show_item("file_dialog_id"),
                )

            dpg.add_spacer()

            dpg.add_combo(
                items=self.decoder_options,
                label="Decoder",
                default_value=self.decoder_choice,
                callback=lambda s, a: setattr(self, "decoder_choice", a),
            )

            dpg.add_input_int(
                label="Max Messages",
                default_value=self.max_messages,
                callback=lambda s, a: setattr(self, "max_messages", a),
                tag="max_messages_input",
            )
            dpg.add_checkbox(
                label="Load All",
                callback=self._toggle_load_all,
                tag="load_all_checkbox",
            )

            dpg.add_spacer()

            dpg.add_button(
                label="Load and Run", callback=self._load_callback, tag="load_button"
            )
            dpg.add_text("Loading...", show=False, tag="loading_text")


class Dashboard:
    """Manage DearPyGui state, filtering logic, and playback updates."""

    @staticmethod
    def determine_ground_status(row):
        """Derive ground/airborne status from CAT48 STAT and CAT21 flags."""
        if pd.notna(row["STAT"]):
            stat = row["STAT"]
            is_ground = "on ground" in stat
            is_airborne = "airborne" in stat
            if is_ground and not is_airborne:
                return "On Ground"
            if is_airborne and not is_ground:
                return "Airborne"
        if pd.notna(row["GBS"]):
            # GBS is now boolean. True means on ground.
            if row["GBS"]:
                return "On Ground"
            else:  # If GBS is False, it implies airborne based on context
                return "Airborne"
        return "Unknown"

    def __init__(self, df: pd.DataFrame):
        """Prepare filtered/per-frame datasets and GUI caches."""
        self.df: pd.DataFrame = df
        self.df["Ground Status"] = self.df.apply(self.determine_ground_status, axis=1)
        self.per_frame_df: pd.DataFrame = generate_per_frame_df(df)
        self.per_frame_df = self.per_frame_df.dropna(
            subset=["Latitude (deg)", "Longitude (deg)"]
        )

        self.all_aircraft_keys = [  # type: ignore
            tuple(x)
            for x in self.per_frame_df[["Target Identification", "Category"]]
            .drop_duplicates()
            .to_numpy()
        ]
        self.aircraft_series = {}
        self.aircraft_trail_segments = {}
        self.series_theme_cache = {}
        self.aircraft_color_cache = {}
        # Number of frames to keep in the visible history trail.
        self.trail_length_frames = 45
        self.trail_segment_count = 1

        self.current_frame = 0
        self.min_frame = 0
        self.max_frame = 0
        if not self.per_frame_df.empty:
            self.min_frame = int(self.per_frame_df["frame"].min())
            self.max_frame = int(self.per_frame_df["frame"].max())
            self.current_frame = self.min_frame

        self.is_playing = True
        self.playback_speed = 10.0
        self.last_update_time = 0
        self.clicked_aircraft_key = None

        self.viewport_width = 0
        self.viewport_height = 0
        self.last_resize_time = 0
        self.resize_debounce_time = 0.2  # 200ms debounce

        # Filter values
        self.lat_min_filter = 40.9
        self.lat_max_filter = 41.7
        self.lon_min_filter = 1.5
        self.lon_max_filter = 2.6
        self.altitude_min_filter = self.per_frame_df["Altitude (m)"].min()
        self.altitude_max_filter = self.per_frame_df["Altitude (m)"].max()
        self.ground_status_filter = "All"
        self.category_filter = "All"
        self.categories = ["All"] + self.per_frame_df["Category"].unique().tolist()
        self.ground_statuses = ["All", "On Ground", "Airborne"]
        self.pure_filter = "All"
        self.static_filter = "All"
        self.pure_statuses = ["All", "Pure", "Not Pure"]
        self.static_statuses = ["All", "Static", "Not Static"]

        self.filtered_per_frame_df: pd.DataFrame = self.per_frame_df.copy()
        self.filtered_df: pd.DataFrame = self.df.copy()

    def _apply_filters(self):
        """Filters the per_frame_df based on the current filter settings."""
        filtered_df = self.per_frame_df.copy()

        # Apply filters
        if not filtered_df.empty:
            filtered_df = filtered_df[
                (filtered_df["Latitude (deg)"] >= self.lat_min_filter)
                & (filtered_df["Latitude (deg)"] <= self.lat_max_filter)
                & (filtered_df["Longitude (deg)"] >= self.lon_min_filter)
                & (filtered_df["Longitude (deg)"] <= self.lon_max_filter)
                & (filtered_df["Altitude (m)"] >= self.altitude_min_filter)
                & (filtered_df["Altitude (m)"] <= self.altitude_max_filter)
            ]

            if self.ground_status_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["Ground Status"] == self.ground_status_filter
                ]

            if self.category_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["Category"].astype(str) == self.category_filter
                ]
            if self.pure_filter != "All":
                is_pure = self.pure_filter == "Pure"
                filtered_df = filtered_df[filtered_df["Is_Pure"] == is_pure]

            if self.static_filter != "All":
                is_static = self.static_filter == "Static"
                filtered_df = filtered_df[filtered_df["Is_Static"] == is_static]

        self.filtered_per_frame_df = pd.DataFrame(filtered_df)

        # Filter df
        filtered_df = self.df.copy()
        if not filtered_df.empty:
            # Drop rows with NaN in coordinate columns to avoid errors
            filtered_df = filtered_df.dropna(
                subset=["Latitude (deg)", "Longitude (deg)", "Altitude (m)"]
            )

            filtered_df = filtered_df[
                (filtered_df["Latitude (deg)"] >= self.lat_min_filter)
                & (filtered_df["Latitude (deg)"] <= self.lat_max_filter)
                & (filtered_df["Longitude (deg)"] >= self.lon_min_filter)
                & (filtered_df["Longitude (deg)"] <= self.lon_max_filter)
                & (filtered_df["Altitude (m)"] >= self.altitude_min_filter)
                & (filtered_df["Altitude (m)"] <= self.altitude_max_filter)
            ]

            if self.ground_status_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["Ground Status"] == self.ground_status_filter
                ]

            if self.category_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["Category"].astype(str) == self.category_filter
                ]
            if self.pure_filter != "All":
                is_pure = self.pure_filter == "Pure"
                filtered_df = filtered_df[filtered_df["Is_Pure"] == is_pure]

            if self.static_filter != "All":
                is_static = self.static_filter == "Static"
                filtered_df = filtered_df[filtered_df["Is_Static"] == is_static]
        self.filtered_df = pd.DataFrame(filtered_df)

    def _get_aircraft_color(self, key, cat):
        """Return a soft, distinct color per aircraft using pastel HSV hashing."""
        if key in self.aircraft_color_cache:
            return self.aircraft_color_cache[key]

        # Derive hue from the aircraft identifier hash for stable uniqueness.
        hue = (abs(hash(key)) % 360) / 360.0
        saturation = 0.35  # lower saturation for softer colors
        value = 0.82  # slightly dimmer for night-friendly palette
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = [int(r * 255), int(g * 255), int(b * 255), 255]
        self.aircraft_color_cache[key] = color
        return color

    def _get_series_theme(self, series_type, color, cat=None):
        """Cache and return a DearPyGui theme with the requested color."""
        key = (series_type, tuple(color), cat)
        if key not in self.series_theme_cache:
            with dpg.theme() as theme:
                with dpg.theme_component(series_type):
                    if series_type == dpg.mvScatterSeries:
                        dpg.add_theme_color(
                            dpg.mvPlotCol_MarkerOutline,
                            color,
                            category=dpg.mvThemeCat_Plots,
                        )
                        filled = color.copy()
                        filled[3] = min(255, color[3] + 40)
                        dpg.add_theme_color(
                            dpg.mvPlotCol_MarkerFill,
                            filled,
                            category=dpg.mvThemeCat_Plots,
                        )
                        if cat == 21:
                            dpg.add_theme_style(
                                dpg.mvPlotStyleVar_Marker,
                                dpg.mvPlotMarker_Square,
                                category=dpg.mvThemeCat_Plots,
                            )
                        elif cat == 48:
                            dpg.add_theme_style(
                                dpg.mvPlotStyleVar_Marker,
                                dpg.mvPlotMarker_Circle,
                                category=dpg.mvThemeCat_Plots,
                            )
                        else:
                            dpg.add_theme_style(
                                dpg.mvPlotStyleVar_Marker,
                                dpg.mvPlotMarker_Circle,
                                category=dpg.mvThemeCat_Plots,
                            )  # Default to circle
                    elif series_type == dpg.mvLineSeries:
                        dpg.add_theme_color(
                            dpg.mvPlotCol_Line,
                            color,
                            category=dpg.mvThemeCat_Plots,
                        )
                        dpg.add_theme_style(
                            dpg.mvPlotStyleVar_LineWeight,
                            3.5,
                            category=dpg.mvThemeCat_Plots,
                        )
            self.series_theme_cache[key] = theme
        return self.series_theme_cache[key]

    def _update_trail_segments(self, key, coords):
        """Update single translucent trail series for the aircraft."""
        segments = self.aircraft_trail_segments.get(key, [])
        if not segments:
            return
        seg = segments[0]
        if not coords or len(coords[0]) < 2:
            dpg.set_value(seg, ([], []))
            return
        dpg.set_value(seg, coords)

    def _filter_callback(self, sender, app_data):
        """Callback for all filter UI elements."""
        filter_tag = dpg.get_item_alias(sender)
        if filter_tag == "lat_min_filter":
            self.lat_min_filter = app_data
        elif filter_tag == "lat_max_filter":
            self.lat_max_filter = app_data
        elif filter_tag == "lon_min_filter":
            self.lon_min_filter = app_data
        elif filter_tag == "lon_max_filter":
            self.lon_max_filter = app_data
        elif filter_tag == "altitude_min_filter":
            self.altitude_min_filter = app_data
        elif filter_tag == "altitude_max_filter":
            self.altitude_max_filter = app_data
        elif filter_tag == "ground_status_filter":
            self.ground_status_filter = app_data
        elif filter_tag == "category_filter":
            self.category_filter = app_data
        elif filter_tag == "pure_filter":
            self.pure_filter = app_data
        elif filter_tag == "static_filter":
            self.static_filter = app_data

        self._apply_filters()
        self._update_plot()

    def _play_callback(self):
        """Resume playback when the play button is pressed."""
        self.is_playing = True

    def _pause_callback(self):
        """Pause playback when the pause button is pressed."""
        self.is_playing = False

    def _speed_callback(self, sender, app_data):
        """Apply the requested frames-per-second value."""
        self.playback_speed = app_data

    def _frame_slider_callback(self, sender, app_data):
        """Jump to an arbitrary frame via the slider widget."""
        self.current_frame = app_data
        self._update_plot()

    def _export_callback(self):
        """Open the export dialog so the user can pick a CSV path."""
        dpg.show_item("export_dialog_id")

    def _save_csv_callback(self, sender, app_data):
        """Persist the currently filtered dataset to disk."""
        # Check if a file was selected
        if "file_path_name" in app_data:
            file_path = app_data["file_path_name"]

            desired_first_columns = [
                "Category",
                "SAC",
                "SIC",
                "Time (s since midnight)",
                "Time String",
                "Latitude (deg)",
                "Longitude (deg)",
                "Height (m)",
                "Height (ft)",
                "Altitude (m)",
                "Altitude (ft)",
                "Range (m)",
                "Range (NM)",
                "Theta (deg)",
                "Mode-3/A Code",
                "Flight Level (FL)",
                "Aircraft Address",
                "Target Identification",
                "Barometric Pressure Setting",
                "Roll Angle",
                "Track Angle",
                "Ground Speed (kts) BDS",
                "Track Angle Rate",
                "TAS",
                "Magnetic Heading (deg) BDS",
                "IAS (kt)",
                "Mach",
                "Barometric Altitude Rate",
                "Inertial Vertical Velocity",
                "Track Number",
                "Ground Speed (kts)",
                "Magnetic Heading (deg)",
                "STAT",
                "GBS",
                "Is_Pure",
                "Is_Static",
            ]

            current_columns = self.filtered_df.columns.tolist()

            # Separate desired columns from the rest
            first_columns = [
                col for col in desired_first_columns if col in current_columns
            ]
            remaining_columns = [
                col for col in current_columns if col not in desired_first_columns
            ]

            # Combine to get the new order
            new_column_order = first_columns + remaining_columns

            # Reindex the DataFrame
            df_to_export = self.filtered_df[new_column_order]

            df_to_export.to_csv(file_path, index=False)
        dpg.configure_item("export_dialog_id", show=False)

    def _update_plot(self):
        """Refresh aircraft scatter/trail series for the active frame."""
        if not hasattr(self, "filtered_per_frame_df"):
            return
        frame_data = self.filtered_per_frame_df[
            self.filtered_per_frame_df["frame"] == self.current_frame
        ]

        # Pre-compute recent history for trails so we only slice once.
        trail_window = self.filtered_per_frame_df[
            (
                self.filtered_per_frame_df["frame"]
                >= self.current_frame - self.trail_length_frames
            )
            & (self.filtered_per_frame_df["frame"] <= self.current_frame)
        ]
        trail_dict = {}
        if not trail_window.empty:
            for key, group in trail_window.groupby(
                ["Target Identification", "Category"]
            ):
                group_df = pd.DataFrame(group).sort_values("frame")
                trail_dict[key] = (
                    group_df["Longitude (deg)"].tolist(),
                    group_df["Latitude (deg)"].tolist(),
                )

        aircraft_in_frame = set()
        for _, row in frame_data.iterrows():
            aid = row["Target Identification"]
            cat = row["Category"]
            key = (aid, cat)
            lon = [row["Longitude (deg)"]]
            lat = [row["Latitude (deg)"]]
            if key in self.aircraft_series:
                dpg.set_value(self.aircraft_series[key], (lon, lat))
                aircraft_in_frame.add(key)
            if key in self.aircraft_trail_segments:
                self._update_trail_segments(key, trail_dict.get(key))

        for key in self.aircraft_series:
            if key not in aircraft_in_frame:
                dpg.set_value(self.aircraft_series[key], ([], []))
            if key in self.aircraft_trail_segments and key not in trail_dict:
                self._update_trail_segments(key, None)

    def _mouse_wheel_callback(self, sender, app_data):
        """Callback for mouse wheel events for zooming."""
        if dpg.is_item_hovered("map_plot"):
            # Get mouse position in plot coordinates
            mouse_pos = dpg.get_plot_mouse_pos()
            mx, my = mouse_pos[0], mouse_pos[1]

            # Get current axis limits
            x_min, x_max = dpg.get_axis_limits("x_axis")
            y_min, y_max = dpg.get_axis_limits("y_axis")

            # Zoom factor
            zoom_factor = 1.1
            if app_data < 0:
                zoom_factor = 1 / 1.1

            # New limits
            new_x_min = mx - (mx - x_min) * zoom_factor
            new_x_max = mx + (x_max - mx) * zoom_factor
            new_y_min = my - (my - y_min) * zoom_factor
            new_y_max = my + (y_max - my) * zoom_factor

            # Set new axis limits
            dpg.set_axis_limits("x_axis", new_x_min, new_x_max)
            dpg.set_axis_limits("y_axis", new_y_min, new_y_max)

    def create_ui(self):
        """Build the primary DearPyGui windows, handlers, and plots."""
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self._save_csv_callback,
            tag="export_dialog_id",
            width=700,
            height=400,
            default_filename="filtered_data.csv",
        ):
            dpg.add_file_extension(".csv")

        with dpg.window(tag="Primary Window"):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Play", callback=self._play_callback)
                dpg.add_button(label="Pause", callback=self._pause_callback)
                dpg.add_slider_float(
                    label="Speed (fps)",
                    min_value=1.0,
                    max_value=60.0,
                    default_value=self.playback_speed,
                    callback=self._speed_callback,
                )

            dpg.add_slider_int(
                label="Frame",
                tag="frame_slider",
                min_value=self.min_frame,
                max_value=self.max_frame,
                callback=self._frame_slider_callback,
            )

            with dpg.plot(
                label="Aircraft Map",
                height=-1,
                width=-1,
                tag="map_plot",
                pan_button=dpg.mvMouseButton_Middle,
            ):
                # Setup axes first
                dpg.add_plot_axis(dpg.mvXAxis, label="Longitude (deg)", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Latitude (deg)", tag="y_axis")
                dpg.set_axis_limits("x_axis", self.lon_min_filter, self.lon_max_filter)
                dpg.set_axis_limits("y_axis", self.lat_min_filter, self.lat_max_filter)

                # Add static map features
                dpg.add_line_series(
                    coast_data[0].tolist(),
                    coast_data[1].tolist(),
                    label="Coastline",
                    parent="y_axis",
                )
                dpg.add_line_series(
                    runway_L_data[0].tolist(),
                    runway_L_data[1].tolist(),
                    label="Runway L",
                    parent="y_axis",
                )
                dpg.add_line_series(
                    runway_R_data[0].tolist(),
                    runway_R_data[1].tolist(),
                    label="Runway R",
                    parent="y_axis",
                )
                dpg.add_line_series(
                    runway_diag_data[0].tolist(),
                    runway_diag_data[1].tolist(),
                    label="Runway Diagonal",
                    parent="y_axis",
                )

                # Create scatter series for each aircraft with category-specific markers and colors
                # print(
                #     f"DEBUG: Creating {len(self.all_aircraft_keys)} aircraft series..."
                # )
                for aid, cat in self.all_aircraft_keys:
                    key = (aid, cat)
                    color = self._get_aircraft_color(key, cat)
                    subtler_color = color.copy()
                    subtler_color[3] = 90  # Softer alpha for the trails

                    series = dpg.add_scatter_series(
                        x=[],
                        y=[],
                        label=f"{aid}-{cat}",
                        parent="y_axis",
                    )
                    dpg.bind_item_theme(
                        series,
                        self._get_series_theme(dpg.mvScatterSeries, color, cat),
                    )

                    self.aircraft_series[key] = series
                    trail_color = subtler_color.copy()
                    trail_color[3] = 80  # high transparency
                    trail_series = dpg.add_line_series(
                        x=[],
                        y=[],
                        label="",
                        parent="y_axis",
                    )
                    dpg.bind_item_theme(
                        trail_series,
                        self._get_series_theme(dpg.mvLineSeries, trail_color),
                    )
                    self.aircraft_trail_segments[key] = [trail_series]
                #     print(f"DEBUG: Created series {key} -> {series}")
                # print(
                #     f"DEBUG: Total aircraft series created: {len(self.aircraft_series)}"
                # )
            with dpg.tooltip(parent="y_axis", tag="plot_tooltip"):
                dpg.add_text("", tag="tooltip_text")

        with dpg.window(label="Legend", width=150, height=80, pos=[950, 620]):
            dpg.add_text("CAT21 (Squares)")
            dpg.add_text("CAT48 (Circles)")

        with dpg.window(label="Filters", width=250, height=300, pos=[950, 50]):
            dpg.add_text("Filters")
            dpg.add_input_float(
                label="Min Latitude",
                tag="lat_min_filter",
                default_value=self.lat_min_filter,
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Max Latitude",
                tag="lat_max_filter",
                default_value=self.lat_max_filter,
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Min Longitude",
                tag="lon_min_filter",
                default_value=self.lon_min_filter,
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Max Longitude",
                tag="lon_max_filter",
                default_value=self.lon_max_filter,
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Min Altitude",
                tag="altitude_min_filter",
                default_value=float(self.altitude_min_filter),
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Max Altitude",
                tag="altitude_max_filter",
                default_value=float(self.altitude_max_filter),
                callback=self._filter_callback,
            )
            dpg.add_combo(
                label="Ground Status",
                tag="ground_status_filter",
                items=self.ground_statuses,
                default_value=self.ground_status_filter,
                callback=self._filter_callback,
            )
            dpg.add_combo(
                label="Category",
                tag="category_filter",
                items=self.categories,
                default_value=self.category_filter,
                callback=self._filter_callback,
            )
            dpg.add_combo(
                label="Pure",
                tag="pure_filter",
                items=self.pure_statuses,
                default_value=self.pure_filter,
                callback=self._filter_callback,
            )
            dpg.add_combo(
                label="Static",
                tag="static_filter",
                items=self.static_statuses,
                default_value=self.static_filter,
                callback=self._filter_callback,
            )
            dpg.add_spacer()
            dpg.add_button(label="Export to CSV", callback=self._export_callback)

        with dpg.window(
            label="Clicked Aircraft Info", width=250, height=250, pos=[950, 360]
        ):
            dpg.add_text("ID: N/A", tag="clicked_id")
            dpg.add_text("Category: N/A", tag="clicked_category")
            dpg.add_text("Altitude: N/A", tag="clicked_altitude")
            dpg.add_text("Time: N/A", tag="clicked_time")
            dpg.add_text("IAS: N/A", tag="clicked_ias")
            dpg.add_text("GS: N/A", tag="clicked_gs")
            dpg.add_text("Heading: N/A", tag="clicked_heading")
            dpg.add_text("Roll: N/A", tag="clicked_roll")

        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self._mouse_wheel_callback)

        self._apply_filters()
        self._update_plot()
        self.last_update_time = time.time()

    def update(self):
        """Advance animation, update hover tooltips, and sync click info."""
        new_width = dpg.get_viewport_width()
        new_height = dpg.get_viewport_height()

        if self.viewport_width == 0:  # Initialize on first frame
            self.viewport_width = new_width
            self.viewport_height = new_height

        if new_width != self.viewport_width or new_height != self.viewport_height:
            self.last_resize_time = time.time()
            self.viewport_width = new_width
            self.viewport_height = new_height

        is_resizing = (time.time() - self.last_resize_time) < self.resize_debounce_time

        if is_resizing:
            # Skip updates during resize to prevent lag
            return

        # Animation logic
        if self.is_playing:
            time_per_frame = 1.0 / self.playback_speed
            now = time.time()
            if now - self.last_update_time >= time_per_frame:
                self.current_frame += 1
                if self.current_frame > self.max_frame:
                    self.current_frame = self.min_frame
                dpg.set_value("frame_slider", self.current_frame)
                self._update_plot()
                self.last_update_time = now

        # Hover and click logic
        frame_data = self.filtered_per_frame_df[
            self.filtered_per_frame_df["frame"] == self.current_frame
        ]

        closest_aircraft = None
        is_hovering_plot = dpg.is_item_hovered("map_plot")

        if is_hovering_plot:
            mouse_pos = dpg.get_plot_mouse_pos()
            mx, my = mouse_pos[0], mouse_pos[1]

            plot_limits_x = dpg.get_axis_limits("x_axis")
            plot_width_units = plot_limits_x[1] - plot_limits_x[0]
            threshold = plot_width_units / 100
            threshold_sq = threshold * threshold

            min_dist_sq = float("inf")

            for _, row in frame_data.iterrows():
                px, py = row["Longitude (deg)"], row["Latitude (deg)"]
                dist_sq = (mx - px) ** 2 + (my - py) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_aircraft = row

            if (
                closest_aircraft is not None
                and not closest_aircraft.empty
                and min_dist_sq < threshold_sq
            ):
                info = (
                    f"ID: {closest_aircraft['Target Identification']}\n"
                    f"Category: {closest_aircraft['Category']}\n"
                    f"Altitude: {closest_aircraft['Altitude (m)']:.2f} m\n"
                    f"Time: {closest_aircraft['Time (s since midnight)']} s"
                )
                ias_value = closest_aircraft.get("IAS (kt)")
                if ias_value is not None and pd.notna(ias_value):
                    info += f"\nIAS: {ias_value:.2f} kt"
                heading_value = closest_aircraft.get("Magnetic Heading (deg)")
                if heading_value is not None and pd.notna(heading_value):
                    info += f"\nHeading: {heading_value:.2f} deg"
                gs_value = closest_aircraft.get("Ground Speed (kts)")
                if gs_value is not None and pd.notna(gs_value):
                    info += f"\nGS: {gs_value:.2f} kts"
                roll_value = closest_aircraft.get("Roll Angle")
                if roll_value is not None and pd.notna(roll_value):
                    info += f"\nRoll: {roll_value:.2f} deg"
                status_value = closest_aircraft.get("GBS")
                if status_value is not None and pd.notna(status_value):
                    info += f"\nGBS: {status_value}"
                stat_value = closest_aircraft.get("STAT")
                if stat_value is not None and pd.notna(stat_value):
                    info += f"\nSTAT: {stat_value}"

                dpg.set_value("tooltip_text", info)
            else:
                closest_aircraft = None  # Reset if not close enough

        if (
            dpg.is_item_clicked("map_plot")
            and closest_aircraft is not None
            and not closest_aircraft.empty
        ):
            self.clicked_aircraft_key = (
                closest_aircraft["Target Identification"],
                closest_aircraft["Category"],
            )

        if self.clicked_aircraft_key:
            aid, cat = self.clicked_aircraft_key
            clicked_aircraft_data = frame_data[
                (frame_data["Target Identification"] == aid)
                & (frame_data["Category"] == cat)
            ]
            clicked_df = pd.DataFrame(clicked_aircraft_data)
            if not clicked_df.empty:
                aircraft = clicked_df.iloc[0]
                dpg.set_value("clicked_id", f"ID: {aircraft['Target Identification']}")
                dpg.set_value("clicked_category", f"Category: {aircraft['Category']}")
                dpg.set_value(
                    "clicked_altitude", f"Altitude: {aircraft['Altitude (m)']:.2f} m"
                )
                dpg.set_value(
                    "clicked_time", f"Time: {aircraft['Time (s since midnight)']} s"
                )

                # Add IAS, GS, Heading, and Roll Angle
                if pd.notna(aircraft.get("IAS (kt)")):
                    dpg.set_value("clicked_ias", f"IAS: {aircraft['IAS (kt)']:.2f} kt")
                else:
                    dpg.set_value("clicked_ias", "IAS: N/A")

                if pd.notna(aircraft.get("Ground Speed (kts)")):
                    dpg.set_value(
                        "clicked_gs", f"GS: {aircraft['Ground Speed (kts)']:.2f} kts"
                    )
                else:
                    dpg.set_value("clicked_gs", "GS: N/A")

                if pd.notna(aircraft.get("Magnetic Heading (deg)")):
                    dpg.set_value(
                        "clicked_heading",
                        f"Heading: {aircraft['Magnetic Heading (deg)']:.2f} deg",
                    )
                else:
                    dpg.set_value("clicked_heading", "Heading: N/A")

                if pd.notna(aircraft.get("Roll Angle")):
                    dpg.set_value(
                        "clicked_roll", f"Roll: {aircraft['Roll Angle']:.2f} deg"
                    )
                else:
                    dpg.set_value("clicked_roll", "Roll: N/A")
            else:
                dpg.set_value("clicked_id", f"ID: {aid} (out of frame)")
                dpg.set_value("clicked_category", f"Category: {cat} (out of frame)")
                dpg.set_value("clicked_altitude", "Altitude: NA")
                dpg.set_value("clicked_time", "Time: N/A")
                dpg.set_value("clicked_ias", "IAS: N/A")
                dpg.set_value("clicked_gs", "GS: N/A")
                dpg.set_value("clicked_heading", "Heading: N/A")
                dpg.set_value("clicked_roll", "Roll: N/A")


class MainController:
    """Entry-point helper driving DearPyGui's lifecycle."""

    def __init__(self):
        self.dashboard = None

    def set_dashboard(self, dashboard):
        """Store the active dashboard instance created by the loader."""
        self.dashboard = dashboard

    def run(self):
        """Start DearPyGui, show the loader, and pump the render loop."""
        dpg.create_context()

        loading_screen = LoadingScreen(self)
        loading_screen.create_ui()

        dpg.create_viewport(
            title="ASTERIX Aircraft Playback",
            width=1200,
            resizable=True,
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            if self.dashboard:
                self.dashboard.update()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()


if __name__ == "__main__":
    main_controller = MainController()
    main_controller.run()
