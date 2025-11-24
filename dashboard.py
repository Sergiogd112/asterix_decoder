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

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
from tqdm import tqdm

from decoder.decoder import Decoder
from decoder.geoutils import CoordinatesWGS84
from mapdata import *

DEFAULT_DATA = "Test_Data/datos_asterix_combinado.ast"

ALL_EXPECTED_COLUMNS = [
    "Category",
    "SAC",
    "SIC",
    "ATP Description",
    "ARC Description",
    "RC Description",
    "RAB Description",
    "GBS",
    "Latitude (deg)",
    "Longitude (deg)",
    "ICAO Address (hex)",
    "Time (s since midnight)",
    "UTC Time (HH:MM:SS)",
    "Mode-3/A Code",
    "Flight Level (FL)",
    "Altitude (ft)",
    "Altitude (m)",
    "Target Identification",
    "IAS (kt)",
    "Mach",
    "Magnetic Heading (deg)",
    "Target Status VFI",
    "Target Status RAB",
    "Target Status GBS",
    "Target Status NRM",
    "Ground Speed (kts)",
    "Track Angle (deg)",
    "STAT (CAT48)",
]


def generate_per_frame_df(df: pd.DataFrame):
    before_missing_count = df["Altitude (m)"].isna().sum()
    before_missing_mask = df["Altitude (m)"].isna()

    def _time_weight_interp(g):
        g = g.sort_values("Time (s since midnight)").copy()
        t = g["Time (s since midnight)"].astype(float).to_numpy()
        h = g["Altitude (m)"].to_numpy(dtype=float)
        mask_known = ~np.isnan(h)
        non_na = int(mask_known.sum())
        if non_na == 0:
            # nothing to do for this aircraft
            return g
        if non_na == 1:
            # Only a single known value: fill entire group with that value
            single_val = float(h[mask_known][0])
            g["Altitude (m)"] = single_val
            return g
        # Use numpy.interp which performs linear interpolation in x (time).
        t_known = t[mask_known]
        h_known = h[mask_known]
        # np.interp will fill values outside known xp with edge values (desired behavior)
        h_interp = np.interp(t, t_known, h_known)
        g["Altitude (m)"] = h_interp
        return g

    # Apply per-aircraft interpolation using time as the independent variable
    df = df.groupby(["Target Identification", "Category"], group_keys=False).apply(
        _time_weight_interp
    )

    after_missing_count = df["Altitude (m)"].isna().sum()
    print("Missing Altitude (m) after :", after_missing_count)

    # Show a few example rows that were NaN before but are now filled:
    rows = []
    for (aid, cat), g in tqdm(df.groupby(["Target Identification", "Category"])):
        g = g.sort_values("frame")
        minf = int(g["frame"].min())
        maxf = int(g["frame"].max())
        frames_all = np.arange(minf, maxf + 1, dtype=int)

        # Aggregate existing known values per frame (mean if multiple records per frame)
        agg = g.groupby("frame").agg(
            {
                "Latitude (deg)": "mean",
                "Longitude (deg)": "mean",
                "Altitude (m)": "mean",
                "IAS (kt)": "first",
                "Magnetic Heading (deg)": "first",
                "Ground Speed (kts)": "first",
                "Target Status GBS": "first",
                "STAT (CAT48)": "first",
            }
        )
        # Reindex to include all frames in the span
        agg = agg.reindex(frames_all)
        agg["Target Status GBS"] = agg["Target Status GBS"].ffill()
        agg["STAT (CAT48)"] = agg["STAT (CAT48)"].ffill()
        agg = agg.reset_index()
        # Ensure the frame column exists and is integer
        if "frame" not in agg.columns and "index" in agg.columns:
            agg = agg.rename(columns={"index": "frame"})
        agg["frame"] = agg["frame"].astype(int)

        # Interpolate each coordinate using the frame integer as x-axis
        for col in ["Latitude (deg)", "Longitude (deg)", "Altitude (m)"]:
            vals = agg[col].to_numpy(dtype=float)
            # known points mask
            known = ~np.isnan(vals)
            if known.sum() == 0:
                # leave as NaN
                interp_vals = np.full_like(vals, np.nan, dtype=float)
            elif known.sum() == 1:
                # single known value -> propagate to all frames
                single_val = float(vals[known][0])
                interp_vals = np.full_like(vals, single_val, dtype=float)
            else:
                xp = agg["frame"].to_numpy(dtype=float)[known]
                fp = vals[known]
                # np.interp fills values outside xp with the edge values (desired behavior)
                interp_vals = np.interp(agg["frame"].to_numpy(dtype=float), xp, fp)
            agg[col] = interp_vals

        # Add identification and time columns. Use frame as Time (s since midnight) per your requirement.
        agg["Target Identification"] = aid
        agg["Time (s since midnight)"] = agg["frame"].astype(float)
        agg["Category"] = cat

        rows.append(
            agg[
                [
                    "Category",
                    "frame",
                    "Target Identification",
                    "Time (s since midnight)",
                    "Latitude (deg)",
                    "Longitude (deg)",
                    "Altitude (m)",
                    "IAS (kt)",
                    "Magnetic Heading (deg)",
                    "Ground Speed (kts)",
                    "Target Status GBS",
                    "STAT (CAT48)",
                ]
            ]
        )

    # Concatenate all aircraft frames into a single DataFrame
    per_frame_df = (
        pd.concat(rows, ignore_index=True)
        if rows
        else pd.DataFrame(
            columns=[
                "Category",
                "frame",
                "Target Identification",
                "Time (s since midnight)",
                "Latitude (deg)",
                "Longitude (deg)",
                "Altitude (m)",
                "IAS (kt)",
                "Magnetic Heading (deg)",
                "Ground Speed (kts)",
                "Target Status GBS",
                "STAT (CAT48)",
            ]
        )
    )

    per_frame_df["Ground Status"] = per_frame_df.apply(
        Dashboard.determine_ground_status, axis=1
    )

    # Sort for convenience
    per_frame_df = per_frame_df.sort_values(
        ["frame", "Target Identification", "Category"]
    ).reset_index(drop=True)
    return per_frame_df


def load_messages(
    data_file: str, parallel: bool = True, max_messages=None, decoder_choice="Python"
):
    """Load ASTERIX messages using the project's Decoder and return a
    normalized pandas.DataFrame containing lat/lon and relevant fields.

    We attempt to use a numeric timestamp if present (CAT21 provides
    "Time (s since midnight)"). When not present we fall back to the
    message index to produce animation frames.
    """
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25

    if decoder_choice == "Rust":
        try:
            import decoderrs

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
                time_value = item.get(
                    "Time of Day", item.get("Time (s since midnight)", None)
                )
                if time_value is None:
                    continue

                mapped_item = {}

                # Map fields with different names
                mapped_item["Category"] = item.get("category", "")
                mapped_item["SAC"] = item.get("SAC", 0)
                mapped_item["SIC"] = item.get("SIC", 0)
                mapped_item["ATP Description"] = ""
                mapped_item["ARC Description"] = ""
                mapped_item["RC Description"] = ""
                mapped_item["RAB Description"] = (
                    "RAB set" if item.get("RAB", False) else "RAB not set"
                )
                mapped_item["GBS"] = ""
                mapped_item["Latitude (deg)"] = item.get("Latitude (deg)", 0)
                mapped_item["Longitude (deg)"] = item.get("Longitude (deg)", 0)
                mapped_item["ICAO Address (hex)"] = item.get("Aircraft Address", "")
                mapped_item["Time (s since midnight)"] = time_value
                mapped_item["UTC Time (HH:MM:SS)"] = item.get("Time String", "")
                mapped_item["Mode-3/A Code"] = item.get("Mode-3/A Code", "")
                mapped_item["Flight Level (FL)"] = item.get("Flight Level (FL)", 0)
                mapped_item["Altitude (ft)"] = item.get("Altitude (ft)", 0)
                mapped_item["Altitude (m)"] = item.get("Altitude (m)", 0)
                mapped_item["Target Identification"] = item.get(
                    "Aircraft Identification", ""
                )
                mapped_item["IAS (kt)"] = item.get("IAS (kt)", 0)
                mapped_item["Mach"] = item.get("Mach", 0)
                mapped_item["Magnetic Heading (deg)"] = item.get(
                    "Magnetic Heading (deg)", 0
                )
                mapped_item["Target Status VFI"] = ""
                mapped_item["Target Status RAB"] = (
                    "RAB set" if item.get("RAB", False) else "RAB not set"
                )
                mapped_item["Target Status GBS"] = ""
                mapped_item["Target Status NRM"] = ""
                mapped_item["Ground Speed (kts)"] = item.get("Ground Speed (kts)", 0)
                mapped_item["Track Angle (deg)"] = item.get("Theta (deg)", 0)
                mapped_item["STAT (CAT48)"] = item.get("STAT", "")

                decoded.append(mapped_item)
        except ImportError as e:
            print(
                f"Warning: Rust decoder not available ({e}), falling back to Python decoder"
            )
            decoder = Decoder()
            coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)
            decoded = decoder.load(
                data_file,
                parallel,
                max_messages=max_messages,
                radar_coords=coords_radar,
            )
        except Exception as e:
            print(f"Error using Rust decoder ({e}), falling back to Python decoder")
            decoder = Decoder()
            coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)
            decoded = decoder.load(
                data_file,
                parallel,
                max_messages=max_messages,
                radar_coords=coords_radar,
            )
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
        .sort_values("Time (s since midnight)")
        .query("40.9 < `Latitude (deg)` < 41.7 and 1.5 < `Longitude (deg)` < 2.6")
        .reset_index(drop=True)
    )

    return df


class LoadingScreen:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.data_file = DEFAULT_DATA
        self.max_messages = 100000
        self.load_all = False
        self.decoder_choice = "Python"

        # Check if Rust decoder is available
        try:
            import decoderrs

            self.decoder_options = ["Python", "Rust"]
        except ImportError:
            self.decoder_options = ["Python"]
            print("Warning: Rust decoder not available, only Python option shown")

    def _file_dialog_callback(self, sender, app_data):
        self.data_file = app_data["file_path_name"]
        dpg.set_value("data_file_text", self.data_file)

    def _load_callback(self):
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
                dpg.configure_item("loading_text", label=f"Error: {str(e)}")
                # Show the load button again so user can retry
                dpg.configure_item("load_button", show=True)
                dpg.configure_item("loading_text", show=False)

        # Start the loading thread
        loading_thread = threading.Thread(target=load_in_thread, daemon=True)
        loading_thread.start()

    def _toggle_load_all(self, sender, app_data):
        self.load_all = app_data
        dpg.configure_item("max_messages_input", enabled=not self.load_all)

    def create_ui(self):
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self._file_dialog_callback,
            tag="file_dialog_id",
            width=700,
            height=400,
        ):
            dpg.add_file_extension(".*")
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
    @staticmethod
    def determine_ground_status(row):
        if pd.notna(row["STAT (CAT48)"]):
            stat = row["STAT (CAT48)"]
            is_ground = "on ground" in stat
            is_airborne = "airborne" in stat
            if is_ground and not is_airborne:
                return "On Ground"
            if is_airborne and not is_ground:
                return "Airborne"
        if pd.notna(row["Target Status GBS"]):
            if row["Target Status GBS"] == "Ground bit set":
                return "On Ground"
            if row["Target Status GBS"] == "No ground bit":
                return "Airborne"
        return "Unknown"

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df["Ground Status"] = self.df.apply(self.determine_ground_status, axis=1)
        self.per_frame_df = generate_per_frame_df(df)
        self.per_frame_df = self.per_frame_df.dropna(
            subset=["Latitude (deg)", "Longitude (deg)"]
        )

        self.all_aircraft_keys = [
            tuple(x)
            for x in self.per_frame_df[["Target Identification", "Category"]]
            .drop_duplicates()
            .to_numpy()
        ]
        self.aircraft_series = {}

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

        self.filtered_per_frame_df = self.per_frame_df.copy()
        self.filtered_df = self.df.copy()

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

        self.filtered_per_frame_df = filtered_df

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
        self.filtered_df = filtered_df

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

        self._apply_filters()
        self._update_plot()

    def _play_callback(self):
        self.is_playing = True

    def _pause_callback(self):
        self.is_playing = False

    def _speed_callback(self, sender, app_data):
        self.playback_speed = app_data

    def _frame_slider_callback(self, sender, app_data):
        self.current_frame = app_data
        self._update_plot()

    def _export_callback(self):
        dpg.show_item("export_dialog_id")

    def _save_csv_callback(self, sender, app_data):
        # Check if a file was selected
        if "file_path_name" in app_data:
            file_path = app_data["file_path_name"]

            desired_first_columns = [
                "Category",
                "SAC",
                "SIC",
                "Latitude (deg)",
                "Longitude (deg)",
                "Altitude (m)",
                "Target Identification",
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
        if not hasattr(self, "filtered_per_frame_df"):
            return
        frame_data = self.filtered_per_frame_df[
            self.filtered_per_frame_df["frame"] == self.current_frame
        ]

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

        for key in self.aircraft_series:
            if key not in aircraft_in_frame:
                dpg.set_value(self.aircraft_series[key], ([], []))

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

                # Create scatter series for each aircraft
                for aid, cat in self.all_aircraft_keys:
                    key = (aid, cat)
                    self.aircraft_series[key] = dpg.add_scatter_series(
                        x=[], y=[], label=f"{aid}-{cat}", parent="y_axis"
                    )
            with dpg.tooltip(parent="y_axis", tag="plot_tooltip"):
                dpg.add_text("", tag="tooltip_text")
            dpg.configure_item("plot_tooltip", show=False)

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
                default_value=self.altitude_min_filter,
                callback=self._filter_callback,
            )
            dpg.add_input_float(
                label="Max Altitude",
                tag="altitude_max_filter",
                default_value=self.altitude_max_filter,
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
            dpg.add_spacer()
            dpg.add_button(label="Export to CSV", callback=self._export_callback)

        with dpg.window(
            label="Clicked Aircraft Info", width=250, height=150, pos=[950, 360]
        ):
            dpg.add_text("ID: N/A", tag="clicked_id")
            dpg.add_text("Category: N/A", tag="clicked_category")
            dpg.add_text("Altitude: N/A", tag="clicked_altitude")
            dpg.add_text("Time: N/A", tag="clicked_time")

        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self._mouse_wheel_callback)

        self._apply_filters()
        self._update_plot()
        self.last_update_time = time.time()

    def update(self):
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

            if closest_aircraft is not None and min_dist_sq < threshold_sq:
                info = (
                    f"ID: {closest_aircraft['Target Identification']}\n"
                    f"Category: {closest_aircraft['Category']}\n"
                    f"Altitude: {closest_aircraft['Altitude (m)']:.2f} m\n"
                    f"Time: {closest_aircraft['Time (s since midnight)']} s"
                )
                if pd.notna(closest_aircraft.get("IAS (kt)")):
                    info += f"\nIAS: {closest_aircraft['IAS (kt)']:.2f} kt"
                if pd.notna(closest_aircraft.get("Magnetic Heading (deg)")):
                    info += f"\nHeading: {closest_aircraft['Magnetic Heading (deg)']:.2f} deg"
                if pd.notna(closest_aircraft.get("Ground Speed (kts)")):
                    info += f"\nGS: {closest_aircraft['Ground Speed (kts)']:.2f} kts"
                if pd.notna(closest_aircraft.get("Target Status GBS")):
                    info += f"\nSTAT: {closest_aircraft['Target Status GBS']}"
                if pd.notna(closest_aircraft.get("STAT (CAT48)")):
                    info += f"\nSTAT (CAT48): {closest_aircraft['STAT (CAT48)']}"

                dpg.set_value("tooltip_text", info)
                dpg.configure_item("plot_tooltip", show=True)
            else:
                dpg.configure_item("plot_tooltip", show=False)
                closest_aircraft = None  # Reset if not close enough
        else:
            dpg.configure_item("plot_tooltip", show=False)

        if dpg.is_item_clicked("map_plot") and closest_aircraft is not None:
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
            if not clicked_aircraft_data.empty:
                dpg.set_value(
                    "clicked_id",
                    f"ID: {clicked_aircraft_data.iloc[0]['Target Identification']}",
                )
                dpg.set_value(
                    "clicked_category",
                    f"Category: {clicked_aircraft_data.iloc[0]['Category']}",
                )
                dpg.set_value(
                    "clicked_altitude",
                    f"Altitude: {clicked_aircraft_data.iloc[0]['Altitude (m)']:.2f} m",
                )
                dpg.set_value(
                    "clicked_time",
                    f"Time: {clicked_aircraft_data.iloc[0]['Time (s since midnight)']} s",
                )
            else:
                dpg.set_value("clicked_id", f"ID: {aid} (out of frame)")
                dpg.set_value("clicked_category", f"Category: {cat} (out of frame)")
                dpg.set_value("clicked_altitude", "Altitude: N/A")
                dpg.set_value("clicked_time", "Time: N/A")


class MainController:
    def __init__(self):
        self.dashboard = None

    def set_dashboard(self, dashboard):
        self.dashboard = dashboard

    def run(self):
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
