#!/usr/bin/env python3

import numpy as np
import pandas as pd


# Test the interpolation fix
def test_interpolation():
    # Simulate the case: aircraft appears at frame 5 only
    frames = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    latitudes = [
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        41.5,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]

    # Create test dataframe
    df = pd.DataFrame({"frame": frames, "Latitude (deg)": latitudes})

    print("Original data:")
    print(df)

    # Apply the fixed interpolation logic
    vals = df["Latitude (deg)"].to_numpy(dtype=float)
    known = ~np.isnan(vals)

    if known.sum() == 0:
        interp_vals = np.full_like(vals, np.nan, dtype=float)
    elif known.sum() == 1:
        interp_vals = np.full_like(vals, np.nan, dtype=float)
        known_indices = np.where(known)[0]
        if len(known_indices) > 0:
            known_frame_idx = known_indices[0]
            interp_vals[known_frame_idx] = float(vals[known][0])
    else:
        xp = df["frame"].to_numpy(dtype=float)[known]
        fp = vals[known]
        interp_vals = np.interp(df["frame"].to_numpy(dtype=float), xp, fp)

    df["Latitude (deg)"] = interp_vals

    print("\nAfter interpolation:")
    print(df)

    # Check if aircraft only appears at frame 5
    print(f"\nAircraft should only appear at frame 5:")
    print(f"Frame 5: {df.loc[5, 'Latitude (deg)']}")
    print(
        f"Other frames should be NaN: {df.loc[df['frame'] != 5, 'Latitude (deg)'].tolist()}"
    )


if __name__ == "__main__":
    test_interpolation()
