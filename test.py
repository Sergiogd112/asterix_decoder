import decoderrs
import numpy as np
import pandas as pd
from rich import print
from time import time
import gc
from decoder.decoder import Decoder
from decoder.geoutils import CoordinatesWGS84

if __name__ == "__main__":
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25
    coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)
    start = time()
    # Decode with Rust
    decoded_rust = decoderrs.load(
        "Test_Data/datos_asterix_radar.ast",
        radar_lat=radar_lat,
        radar_lon=radar_lon,
        radar_alt=radar_alt,
        max_messages=100,
    )
    print(
        f"Decoded {len(decoded_rust)} messages with Rust decoder in {time()-start:.2f} seconds"
    )
    # count_no_time = 0
    # for item in decoded_rust:
    #     # Skip messages with no time information
    #     time_value = item.get("Time (s since midnight)", None)

    #     if time_value is None:
    #         # print("No time information found for item:", item)
    #         count_no_time += 1
    # print(f"Number of messages with no time information: {count_no_time}")
    # decoded_rust = [
    #     item
    #     for item in decoded_rust
    #     if item.get("Time (s since midnight)", None) is not None
    # ]
    df_rust = pd.json_normalize(decoded_rust)#.sort_values(by="Time (s since midnight)")
    columns_sorted = sorted(df_rust.columns)
    first_columns = [
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
    ]
    # first_columns = [
    #     "Category",
    #     "SAC",
    #     "SIC",
    #     "Time (s since midnight)",
    #     "Time String",
    #     "Latitude (deg)",
    #     "Longitude (deg)",
    #     "Height (m)",
    #     "Height (ft)",
    #     "Altitude (m)",
    #     "Altitude (ft)",
    #     "Mode-3/A Code",
    #     "Flight Level (FL)",
    #     "Aircraft Address",
    #     "Target Identification",
    #     "Barometric Pressure Setting",
    #     "GBS",
    # ]
    existing_cols = [col for col in first_columns if col in df_rust.columns]
    other_cols = sorted([col for col in df_rust.columns if col not in first_columns])
    ordered_cols = existing_cols + other_cols
    df_rust = df_rust[ordered_cols].query(
        "40.9 <= `Latitude (deg)` <= 41.7 and 1.5 <= `Longitude (deg)` <= 2.6"  # and not(GBS)"
    )
    print(len(df_rust))
    df_rust.to_csv("radar_rust.csv", index=False)
    print(f"Decoding time with Rust: {time()-start:.2f} seconds")
    print("Saved radar_rust.csv")
    gc.collect()
    # Decode with Python
    start = time()
    decoder = Decoder()
    decoded_python = decoder.load(
        "Test_Data/datos_asterix_radar.ast",
        parallel=False,
        max_messages=100,
        radar_coords=coords_radar,
    )
    df_python = pd.DataFrame(decoded_python)
    # The rust implementation returns a dict, so we need to flatten the python one
    print(
        f"Decoded {len(decoded_python)} messages with Python decoder in {time()-start:.2f} seconds"
    )

    existing_cols = [col for col in first_columns if col in df_python.columns]
    other_cols = sorted([col for col in df_python.columns if col not in first_columns])
    ordered_cols = existing_cols + other_cols
    df_python = df_python[ordered_cols].query(
        "40.9 <= `Latitude (deg)` <= 41.7 and 1.5 <= `Longitude (deg)` <= 2.6"  # and not(GBS)"
    )
    df_python.to_csv("radar_python.csv", index=False)
    # compare the dfs cell by cell
    print(len(df_python))
    df_python = df_python[first_columns].round(6)
    df_rust = df_rust[first_columns].round(6)
    comparison = df_python.eq(df_rust)
    print(comparison)
    if not comparison.all().all():
        diffs = np.where(comparison == False)
        for row, col in zip(*diffs):
            if df_python.iat[row, col] != df_rust.iat[row, col] and not(
                 (df_python.iat[row, col] is np.nan
                or pd.isna(df_python.iat[row, col]))
                and  (df_rust.iat[row, col] is np.nan
                or pd.isna(df_rust.iat[row, col]))
            ):
                print(
                    f"Difference found at row {row}, column {df_python.columns[col]}:"
                    + f" Python={df_python.iat[row, col]}, Rust={df_rust.iat[row, col]},"
                    + f" is Python NaN: {pd.isna(df_python.iat[row, col])}, is Rust NaN: {pd.isna(df_rust.iat[row, col])}"
                )

    print(f"Decoding time with Python: {time()-start:.2f} seconds")
    print("Saved radar_python.csv")
