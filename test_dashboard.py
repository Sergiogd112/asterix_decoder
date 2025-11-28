#!/usr/bin/env python3

import sys
import os

sys.path.append(".")

# Add current directory to path for imports
os.chdir("/home/sergiogd/Github/asterix_decoder")

from dashboard import load_messages, Dashboard
import pandas as pd


def test_dashboard():
    print("Testing dashboard with small dataset...")

    # Load a small subset of data
    df = load_messages(
        "Test_Data/datos_asterix_combinado.ast",
        max_messages=50,
        decoder_choice="Python",
    )

    if df.empty:
        print("No data loaded")
        return

    print(f"Loaded {len(df)} messages")
    print(f"Frame range: {df['frame'].min()} to {df['frame'].max()}")

    # Check for aircraft with single positions
    for keys, group in df.groupby(["Target Identification", "Category"]):  # type: ignore
        if isinstance(keys, tuple) and len(keys) == 2:
            aid, cat = keys
        else:
            continue
        positions = group.dropna(subset=["Latitude (deg)", "Longitude (deg)"])
        print(f"Aircraft {aid}-{cat}: {len(positions)} positions")
        if len(positions) <= 2:
            print(f"  Frames: {positions['frame'].tolist()}")
            print(
                f"  Positions: {positions[['frame', 'Latitude (deg)', 'Longitude (deg)']].to_dict('records')}"  # type: ignore
            )

    # Create dashboard
    dashboard = Dashboard(df)
    print("Dashboard created successfully")

    # Test a few frame updates
    print("Testing frame updates...")
    for frame in range(
        dashboard.min_frame, min(dashboard.min_frame + 10, dashboard.max_frame)
    ):
        dashboard.current_frame = frame
        dashboard._update_plot()
        frame_data = dashboard.filtered_per_frame_df[
            dashboard.filtered_per_frame_df["frame"] == frame
        ]
        aircraft_in_frame = len(frame_data)
        print(f"Frame {frame}: {aircraft_in_frame} aircraft")


if __name__ == "__main__":
    test_dashboard()
