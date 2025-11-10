"""Dash dashboard for visualizing ASTERIX messages on a map.

Run with an ASGI runner (the user's environment uses `uv run`):

    uv run dash:app

This file exposes an ASGI `app` object so it can be served by uv/uvicorn.

The dashboard loads ASTERIX data using `decoder.Decoder().load()` (see
`decoder/__main__.py` for example usage). It displays aircraft positions on an
interactive map, with play/pause and speed controls.
"""

from pathlib import Path
import argparse
import json
from collections import defaultdict

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context, no_update
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from tqdm import tqdm

from asgiref.wsgi import WsgiToAsgi

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
        # np.interp will fill values outside known xp with edge values (good for endpoint filling).
        h_interp = np.interp(t, t_known, h_known)
        g["Height (m)"] = h_interp
        return g

    # Apply per-aircraft interpolation using time as the independent variable
    df = df.groupby("Target Identification", group_keys=False).apply(
        _time_weight_interp
    )

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


def build_app(df: pd.DataFrame):
    """Construct the Dash app given a prepared dataframe of points.

    The returned ASGI app is wrapped outside this function.
    """
    print("Building Dash app...")
    dash_app = Dash(__name__)

    per_frame_df = generate_per_frame_df(df)
    per_frame_df = per_frame_df.dropna(subset=["Latitude (deg)", "Longitude (deg)"])
    print("Creating figure...")
    lat_max = 41.7
    lat_min = 40.9
    lon_max = 2.6
    lon_min = 1.5
    lat_lon_ratio = (lat_max - lat_min) / (lon_max - lon_min)
    # Create static traces for map features
    static_traces = [
        go.Scatter(
            x=coast_data[0],
            y=coast_data[1],
            mode="lines",
            line=dict(color="black", width=1),
            name="Coastline",
            showlegend=False,
        ),
        go.Scatter(
            x=runway_L_data[0],
            y=runway_L_data[1],
            mode="lines",
            line=dict(color="red", width=4),
            name="Runway L",
        ),
        go.Scatter(
            x=runway_R_data[0],
            y=runway_R_data[1],
            mode="lines",
            line=dict(color="blue", width=4),
            name="Runway R",
        ),
        go.Scatter(
            x=runway_diag_data[0],
            y=runway_diag_data[1],
            mode="lines",
            line=dict(color="green", width=4),
            name="Runway Diagonal",
        ),
    ]

    if not per_frame_df.empty:
        # Create animated scatter plot for aircraft
        fig = px.scatter(
            per_frame_df,
            x="Longitude (deg)",
            y="Latitude (deg)",
            animation_frame="frame",
            animation_group="Target Identification",
            hover_name="Target Identification",
            hover_data={
                "Height (m)": True,
                "Time (s since midnight)": True,
            },
            color="Target Identification",
            range_x=[lon_min, lon_max],
            range_y=[lat_min, lat_max],
            height=800,
            width=int(800 / lat_lon_ratio),
        )

        # Add static traces to each frame of the animation
        for frame in fig.frames:
            frame.data += tuple(static_traces)

        # Add static traces to the base figure
        fig.add_traces(static_traces)

    else:
        # If there's no data, create a static map
        fig = go.Figure(
            data=static_traces,
            layout=go.Layout(
                xaxis=dict(range=[lon_min, lon_max]),
                yaxis=dict(range=[lat_min, lat_max]),
                height=800,
                width=int(800 / lat_lon_ratio),
            ),
        )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    print("Configuring animation...")
    dash_app.layout = html.Div(
        [
            html.H3("ASTERIX Aircraft Playback"),
            html.Div(
                [
                    html.Label("Playback Speed (frames/sec):"),
                    dcc.Slider(
                        id="speed-slider",
                        min=1,
                        max=60,
                        step=1,
                        value=10,
                        marks={i: str(i) for i in range(0, 60, 5)},
                    ),
                ],
                style={"width": "50%", "margin-bottom": "20px"},
            ),
            dcc.Graph(id="map", figure=fig, style={"height": "80vh"}),
        ],
        style={"margin": "12px", "fontFamily": "Arial, sans-serif"},
    )

    @dash_app.callback(
        Output("map", "figure"),
        Input("speed-slider", "value"),
        State("map", "figure"),
        prevent_initial_call=True,
    )
    def update_animation_speed(speed, fig):
        if not fig or not speed:
            return no_update
        if speed <= 1:
            speed = 1

        duration = 1000 / speed

        fig["layout"]["updatemenus"][0]["buttons"][0]["args"][1] = {
            "frame": {"duration": duration, "redraw": True},
            "transition": {"duration": 0, "easing": "linear"},
        }
        return fig

    return dash_app


# Load data and create app instance
df = load_messages(DEFAULT_DATA, max_messages=100000)
dash_app = build_app(df)

# Expose the ASGI app for servers like uvicorn
app = WsgiToAsgi(dash_app.server)


if __name__ == "__main__":
    # If executed directly, start dash using Flask development server for convenience.
    # use_reloader=False prevents the script from running twice on startup.
    dash_app.run(debug=True, port=8050, use_reloader=False)
