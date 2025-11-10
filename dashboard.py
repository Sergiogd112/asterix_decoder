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
    df = df.groupby("Target Identification", group_keys=False).apply(_time_weight_interp)

    after_missing_count = df["Height (m)"].isna().sum()
    print("Missing Height (m) after :", after_missing_count)

    # Show a few example rows that were NaN before but are now filled:
    filled_rows = df[~df["Height (m)"].isna() & before_missing_mask]
    rows = []
    for aid, g in tqdm(df.groupby("Target Identification")):
        g = g.sort_values("frame")
        minf = int(g["frame"].min())
        maxf = int(g["frame"].max())
        frames_all = np.arange(minf, maxf + 1, dtype=int)

        # Aggregate existing known values per frame (mean if multiple records per frame)
        agg = g.groupby("frame").agg(
            {"Latitude (deg)": "mean", "Longitude (deg)": "mean", "Height (m)": "mean"}
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
        # Optionally carry Category if available (take first non-null)
        try:
            cat = g["Category"].dropna().iloc[0]
        except Exception:
            cat = np.nan
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
            ]
        )
    )
    # Sort for convenience
    per_frame_df = per_frame_df.sort_values(
        ["frame", "Target Identification"]
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
    df = pd.DataFrame(decoded)
    df = df.dropna(subset=["Time (s since midnight)"])
    df = (
        df.assign(frame=df["Time (s since midnight)"].astype(int))
        .sort_values("Time (s since midnight)")
        .query("40.9 < `Latitude (deg)` < 41.7 and 1.5 < `Longitude (deg)` < 2.6")
        .reset_index(drop=True)
    )

    return df


class Dashboard:
    def __init__(self, df: pd.DataFrame):
        self.per_frame_df = generate_per_frame_df(df)
        self.per_frame_df = self.per_frame_df.dropna(
            subset=["Latitude (deg)", "Longitude (deg)"]
        )

        self.all_aircraft_ids = self.per_frame_df["Target Identification"].unique()
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
        frame_data = self.per_frame_df[self.per_frame_df["frame"] == self.current_frame]

        aircraft_in_frame = set()
        for _, row in frame_data.iterrows():
            aid = row["Target Identification"]
            lon = [row["Longitude (deg)"]]
            lat = [row["Latitude (deg)"]]
            if aid in self.aircraft_series:
                dpg.set_value(self.aircraft_series[aid], (lon, lat))
                aircraft_in_frame.add(aid)

        for aid in self.all_aircraft_ids:
            if aid not in aircraft_in_frame and aid in self.aircraft_series:
                dpg.set_value(self.aircraft_series[aid], ([], []))

    def run(self):
        dpg.create_context()

        lat_max = 41.7
        lat_min = 40.9
        lon_max = 2.6
        lon_min = 1.5
        lat_lon_ratio = (lat_max - lat_min) / (lon_max - lon_min)
        plot_width = 1000
        plot_height = int(plot_width * lat_lon_ratio)

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
                height=plot_height,
                width=plot_width,
                tag="map_plot",
            ):
                dpg.add_plot_legend()

                # Setup axes first
                dpg.add_plot_axis(dpg.mvXAxis, label="Longitude (deg)", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Latitude (deg)", tag="y_axis")
                dpg.set_axis_limits("x_axis", lon_min, lon_max)
                dpg.set_axis_limits("y_axis", lat_min, lat_max)

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
                for aid in self.all_aircraft_ids:
                    self.aircraft_series[aid] = dpg.add_scatter_series(
                        x=[], y=[], label=aid, parent="y_axis"
                    )

        dpg.create_viewport(
            title="ASTERIX Aircraft Playback",
            width=plot_width + 40,
            height=plot_height + 120,
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()

        self._update_plot()
        self.last_update_time = time.time()

        while dpg.is_dearpygui_running():
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

            dpg.render_dearpygui_frame()

        dpg.destroy_context()


if __name__ == "__main__":
    df = load_messages(DEFAULT_DATA, max_messages=100000)
    dashboard = Dashboard(df)
    dashboard.run()