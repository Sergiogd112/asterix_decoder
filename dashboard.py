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
import numpy as np

from asgiref.wsgi import WsgiToAsgi

from decoder.decoder import Decoder
from decoder.geoutils import CoordinatesWGS84


DEFAULT_DATA = "Test_Data/datos_asterix_combinado.ast"


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
    dash_app = Dash(__name__, suppress_callback_exceptions=True)

    max_frame = int(df["frame"].max()) if not df.empty else 0
    min_frame = int(df["frame"].min()) if not df.empty else 0
    print(f"Max frame: {max_frame}")
    dash_app.layout = html.Div(
        [
            html.H3("ASTERIX Aircraft Playback"),
            dcc.Graph(id="map", style={"height": "80vh"}),
            html.Div(
                [
                    html.Button("Play", id="btn-play", n_clicks=0),
                    html.Button("Pause", id="btn-pause", n_clicks=0),
                    html.Button("Faster", id="btn-faster", n_clicks=0),
                    html.Button("Slower", id="btn-slower", n_clicks=0),
                    html.Span(id="speed-display", style={"marginLeft": "1rem"}),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "10px"},
            ),
            html.Div([
                html.Label("Frame: ", style={"marginRight": "10px"}),
                dcc.Input(
                    id="frame-input",
                    type="number",
                    min=min_frame,
                    max=max_frame,
                    value=min_frame,
                    style={"width": "100px"}
                ),
                html.Span(f" / {max_frame}", style={"marginLeft": "10px"}),
            ], style={"display": "flex", "alignItems": "center", "margin": "10px 0"}),
            dcc.Interval(id="interval", interval=1000, disabled=True),
            # Store current interval (ms) and playing state
            dcc.Store(
                id="store-interval", data={"interval_ms": 1000, "playing": False}
            ),
            dcc.Store(id="store-df", data=df.to_dict(orient="records")),
        ],
        style={"margin": "12px", "fontFamily": "Arial, sans-serif"},
    )

    @dash_app.callback(
        Output("store-interval", "data"),
        Output("interval", "interval"),
        Output("interval", "disabled"),
        Output("btn-play", "style"),
        Output("btn-pause", "style"),
        Input("btn-play", "n_clicks"),
        Input("btn-pause", "n_clicks"),
        Input("btn-faster", "n_clicks"),
        Input("btn-slower", "n_clicks"),
        State("store-interval", "data"),
    )
    def control_playback(n_play, n_pause, n_faster, n_slower, store):
        # store: {interval_ms, playing}
        interval_ms = store.get("interval_ms", 1000)
        playing = store.get("playing", False)

        ctx = callback_context
        if not ctx.triggered:
            button_styles = (
                {"display": "none"} if playing else {},
                {} if playing else {"display": "none"},
            )
            return store, interval_ms, not playing, *button_styles

        prop = ctx.triggered[0]["prop_id"].split(".")[0]

        if prop == "btn-play":
            playing = True
        elif prop == "btn-pause":
            playing = False
        elif prop == "btn-faster":
            interval_ms = max(50, int(interval_ms * 0.5))
        elif prop == "btn-slower":
            interval_ms = int(interval_ms * 2)

        store = {"interval_ms": interval_ms, "playing": playing}
        button_styles = (
            {"display": "none"} if playing else {},
            {} if playing else {"display": "none"},
        )
        return store, interval_ms, not playing, *button_styles

    @dash_app.callback(
        Output("frame-input", "value"),
        Input("interval", "n_intervals"),
        Input("frame-input", "value"),
        State("frame-input", "max"),
        State("store-interval", "data"),
    )
    def advance_frame(n_intervals, current_frame, max_val, store):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "frame-input":
            # Manual input
            try:
                frame = int(current_frame)
                if frame < 0:
                    return 0
                if frame > max_val:
                    return max_val
                return frame
            except (ValueError, TypeError):
                return 0
        
        # Automatic advance
        if n_intervals is None or not store.get("playing", False):
            return no_update
        
        next_frame = int(current_frame + 1)
        if next_frame > max_val:
            next_frame = 0
        return next_frame

    @dash_app.callback(
        Output("map", "figure"),
        Input("frame-input", "value"),
        # State("store-df", "data"),
        State("map", "relayoutData"),
    )
    def update_map(frame, relayoutData):
        df_local = df#pd.DataFrame(records)
        if df_local.empty:
            fig = px.scatter_map(lat=[], lon=[], zoom=9)
            fig.update_layout(mapbox_style="open-street-map")
            return fig

        frame = int(frame)
        df_frame = df_local[df_local["frame"] == frame]
        if df_frame.empty:
            # empty frame -> return blank map centered on data
            center = {
                "lat": df_local["Latitude (deg)"].mean(),
                "lon": df_local["Longitude (deg)"].mean(),
            }
            fig = px.scatter_map(lat=[], lon=[], center=center, zoom=9)
            fig.update_layout(mapbox_style="open-street-map")
            return fig

        # Preserve the current map view if available
        if relayoutData and "mapbox.center" in relayoutData:
            center = relayoutData["mapbox.center"]
            zoom = relayoutData.get("mapbox.zoom", 9)
        else:
            center = {
                "lat": df_frame["Latitude (deg)"].mean(),
                "lon": df_frame["Longitude (deg)"].mean(),
            }
            zoom = 9

        fig = px.scatter_map(
            df_frame,
            lat="Latitude (deg)",
            lon="Longitude (deg)", 
            hover_name="Target Identification",
            hover_data={
            "Flight Level (FL)": True,
            "Time (s since midnight)": True,
            },
            color="Flight Level (FL)",
            range_color=[0, 1000], # Add range for Flight Level coloring
            size_max=12,
            center=center,
            zoom=zoom,
            height=700,
        )
        fig.update_layout(mapbox_style="open-street-map")
        # fig.update_traces(marker=dict(size=10, color="red"))
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig

    @dash_app.callback(
        Output("speed-display", "children"),
        Input("store-interval", "data"),
    )
    def show_speed(store):
        interval_ms = store.get("interval_ms", 1000)
        fps = 1000 / interval_ms
        return f"Speed: {fps:.1f} frames/second"

    return dash_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to astix file")
    parser.add_argument(
        "--no-parallel", action="store_true", help="Disable parallel decoding"
    )
    parser.add_argument("--max-messages", type=int, default=None)
    args = parser.parse_args()

    data_file = Path(args.data)
    if not data_file.exists():
        raise SystemExit(f"Data file not found: {data_file}")

    df = load_messages(
        str(data_file), parallel=not args.no_parallel, max_messages=args.max_messages
    )
    dash_app = build_app(df)

    # Wrap WSGI server as ASGI so uv/uvicorn can serve it using `uv run dash:app`
    asgi_app = WsgiToAsgi(dash_app.server)

    # Expose the ASGI app as `app` variable for the runner to import
    global app
    app = asgi_app


if __name__ == "__main__":
    # If executed directly, start dash using Flask development server for convenience
    df = load_messages(DEFAULT_DATA, max_messages=100000)
    dash_app = build_app(df)
    dash_app.run(debug=True, port=8050)
