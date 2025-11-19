"""DearPyGui dashboard for visualizing ASTERIX messages on a map.

Run with:

    python dashboard.py

This file creates a DearPyGui window to display aircraft positions on an
interactive map, with play/pause and speed controls.

The dashboard loads ASTERIX data using `decoder.Decoder().load()` (see
`decoder/__main__.py` for example usage).
"""

import time

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
    "Height (m)",
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
    before_missing_count = df["Height (m)"].isna().sum()
    before_missing_mask = df["Height (m)"].isna()

    def _time_weight_interp(g):
        g = g.sort_values("Time (s since midnight)").copy()
        t = g["Time (s since midnight)"].astype(float).to_numpy()
        h = g["Height (m)"].to_numpy(dtype=float)
        mask_known = ~np.isnan(h)
        non_na = int(mask_known.sum())
        if non_na == 0:
            # nothing to do for this aircraft
            return g
        if non_na == 1:
            # Only a single known value: fill entire group with that value
            single_val = float(h[mask_known][0])
            g["Height (m)"] = single_val
            return g
        # Use numpy.interp which performs linear interpolation in x (time).
        t_known = t[mask_known]
        h_known = h[mask_known]
        # np.interp will fill values outside known xp with edge values (desired behavior)
        h_interp = np.interp(t, t_known, h_known)
        g["Height (m)"] = h_interp
        return g

    # Apply per-aircraft interpolation using time as the independent variable
    df = df.groupby(["Target Identification", "Category"], group_keys=False).apply(
        _time_weight_interp
    )

    after_missing_count = df["Height (m)"].isna().sum()
    print("Missing Height (m) after :", after_missing_count)

    # Show a few example rows that were NaN before but are now filled:
    filled_rows = df[~df["Height (m)"].isna() & before_missing_mask]
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
                "Height (m)": "mean",
                "IAS (kt)": "first",
                "Magnetic Heading (deg)": "first",
                "Ground Speed (kts)": "first",
                "Target Status GBS": "first",
                "STAT (CAT48)": "first",
            }
        )
        # Reindex to include all frames in the span
        agg = agg.reindex(frames_all)
        agg = agg.reset_index()
        # Ensure the frame column exists and is integer
        if "frame" not in agg.columns and "index" in agg.columns:
            agg = agg.rename(columns={"index": "frame"})
        agg["frame"] = agg["frame"].astype(int)

        # Interpolate each coordinate using the frame integer as x-axis
        for col in ["Latitude (deg)", "Longitude (deg)", "Height (m)"]:
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
                    "Height (m)",
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
                "Height (m)",
                "IAS (kt)",
                "Magnetic Heading (deg)",
                "Ground Speed (kts)",
                "Target Status GBS",
                "STAT (CAT48)",
            ]
        )
    )
    # Sort for convenience
    per_frame_df = per_frame_df.sort_values(
        ["frame", "Target Identification", "Category"]
    ).reset_index(drop=True)
    return per_frame_df


def load_messages(data_file: str, parallel: bool = True, max_messages=None):
    """Load ASTERIX messages using the project's Decoder and return a
    normalized pandas.DataFrame containing lat/lon and relevant fields.

    We attempt to use a numeric timestamp if present (CAT21 provides
    "Time (s since midnight)"). When not present we fall back to the
    message index to produce animation frames.
    """
    decoder = Decoder()
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25
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

    def _file_dialog_callback(self, sender, app_data):
        self.data_file = app_data['file_path_name']
        dpg.set_value("data_file_text", self.data_file)

    def _load_callback(self):
        max_messages = None if self.load_all else self.max_messages
        
        dpg.configure_item("load_button", show=False)
        dpg.configure_item("loading_text", show=True)

        df = load_messages(self.data_file, max_messages=max_messages)
        
        dashboard = Dashboard(df)
        self.main_controller.set_dashboard(dashboard)
        dashboard.create_ui()
        
        dpg.delete_item("Loading Window")
        dpg.set_primary_window("Primary Window", True)

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

        with dpg.window(label="Loading", tag="Loading Window", width=400, height=200):
            dpg.add_text("Select ASTERIX data file:")
            with dpg.group(horizontal=True):
                dpg.add_text(self.data_file, tag="data_file_text")
                dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog_id"))

            dpg.add_spacer()

            dpg.add_input_int(
                label="Max Messages",
                default_value=self.max_messages,
                callback=lambda s, a: setattr(self, 'max_messages', a),
                tag="max_messages_input"
            )
            dpg.add_checkbox(
                label="Load All",
                callback=self._toggle_load_all,
                tag="load_all_checkbox"
            )

            dpg.add_spacer()
            
            dpg.add_button(label="Load and Run", callback=self._load_callback, tag="load_button")
            dpg.add_text("Loading...", show=False, tag="loading_text")


class Dashboard:
    def __init__(self, df: pd.DataFrame):
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
        self.height_min_filter = self.per_frame_df["Height (m)"].min()
        self.height_max_filter = self.per_frame_df["Height (m)"].max()
        self.gbs_filter = False
        self.category_filter = "All"
        self.categories = ["All"] + self.per_frame_df["Category"].unique().tolist()

        self.filtered_per_frame_df = self.per_frame_df.copy()
    
    def _apply_filters(self):
        """Filters the per_frame_df based on the current filter settings."""
        filtered_df = self.per_frame_df.copy()

        # Apply filters
        if not filtered_df.empty:
            filtered_df = filtered_df[
                (filtered_df["Latitude (deg)"] >= self.lat_min_filter) &
                (filtered_df["Latitude (deg)"] <= self.lat_max_filter) &
                (filtered_df["Longitude (deg)"] >= self.lon_min_filter) &
                (filtered_df["Longitude (deg)"] <= self.lon_max_filter) &
                (filtered_df["Height (m)"] >= self.height_min_filter) &
                (filtered_df["Height (m)"] <= self.height_max_filter)
            ]

            if self.gbs_filter:
                filtered_df = filtered_df[filtered_df["Target Status GBS"] == "Ground bit set"]

            if self.category_filter != "All":
                filtered_df = filtered_df[filtered_df["Category"] == self.category_filter]

        self.filtered_per_frame_df = filtered_df


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
        elif filter_tag == "height_min_filter":
            self.height_min_filter = app_data
        elif filter_tag == "height_max_filter":
            self.height_max_filter = app_data
        elif filter_tag == "gbs_filter":
            self.gbs_filter = app_data
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

    def _update_plot(self):
        if not hasattr(self, 'filtered_per_frame_df'):
            return
        frame_data = self.filtered_per_frame_df[self.filtered_per_frame_df["frame"] == self.current_frame]

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
                dpg.add_plot_legend()

                # Setup axes first
                dpg.add_plot_axis(dpg.mvXAxis, label="Longitude (deg)", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Latitude (deg)", tag="y_axis")
                dpg.set_axis_limits("x_axis", self.lon_min_filter, self.lon_max_filter)
                dpg.set_axis_limits("y_axis", self.lat_min_filter, self.lat_max_filter)

                # Add static map features
                dpg.add_line_series(
                    coast_data[0].tolist(), coast_data[1].tolist(), label="Coastline", parent="y_axis"
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
        
        with dpg.window(label="Filters", width=250, height=300, pos=[950, 50]):
            dpg.add_text("Filters")
            dpg.add_input_float(label="Min Latitude", tag="lat_min_filter", default_value=self.lat_min_filter, callback=self._filter_callback)
            dpg.add_input_float(label="Max Latitude", tag="lat_max_filter", default_value=self.lat_max_filter, callback=self._filter_callback)
            dpg.add_input_float(label="Min Longitude", tag="lon_min_filter", default_value=self.lon_min_filter, callback=self._filter_callback)
            dpg.add_input_float(label="Max Longitude", tag="lon_max_filter", default_value=self.lon_max_filter, callback=self._filter_callback)
            dpg.add_input_float(label="Min Height", tag="height_min_filter", default_value=self.height_min_filter, callback=self._filter_callback)
            dpg.add_input_float(label="Max Height", tag="height_max_filter", default_value=self.height_max_filter, callback=self._filter_callback)
            dpg.add_checkbox(label="GBS", tag="gbs_filter", default_value=self.gbs_filter, callback=self._filter_callback)
            dpg.add_combo(label="Category", tag="category_filter", items=self.categories, default_value=self.category_filter, callback=self._filter_callback)

        with dpg.window(label="Clicked Aircraft Info", width=250, height=150, pos=[950, 360]):
            dpg.add_text("ID: N/A", tag="clicked_id")
            dpg.add_text("Category: N/A", tag="clicked_category")
            dpg.add_text("Height: N/A", tag="clicked_height")
            dpg.add_text("Time: N/A", tag="clicked_time")

        with dpg.window(tag="custom_tooltip", show=False, no_title_bar=True, no_resize=True, no_move=True, autosize=True):
            dpg.add_text("", tag="tooltip_text")

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
                    f"Height: {closest_aircraft['Height (m)']:.2f} m\n"
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

                # Position and show tooltip
                mouse_pos_global = dpg.get_mouse_pos()
                dpg.set_item_pos(
                    "custom_tooltip", [mouse_pos_global[0] + 15, mouse_pos_global[1] + 15]
                )
                dpg.configure_item("custom_tooltip", show=True)
            else:
                dpg.configure_item("custom_tooltip", show=False)
                closest_aircraft = None  # Reset if not close enough
        else:
            dpg.configure_item("custom_tooltip", show=False)

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
                    "clicked_height",
                    f"Height: {clicked_aircraft_data.iloc[0]['Height (m)']:.2f} m",
                )
                dpg.set_value(
                    "clicked_time",
                    f"Time: {clicked_aircraft_data.iloc[0]['Time (s since midnight)']} s",
                )
            else:
                dpg.set_value("clicked_id", f"ID: {aid} (out of frame)")
                dpg.set_value("clicked_category", f"Category: {cat} (out of frame)")
                dpg.set_value("clicked_height", "Height: N/A")
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
