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
        "Test_Data/datos_asterix_adsb.ast",
        radar_lat=radar_lat,
        radar_lon=radar_lon,
        radar_alt=radar_alt,
        max_messages=1000,
    )
    print(
        f"Decoded {len(decoded_rust)} messages with Rust decoder in {time()-start:.2f} seconds"
    )
    count_no_time = 0
    for item in decoded_rust:
        # Skip messages with no time information
        time_value =item.get("Time (s since midnight)", None)
        
        if time_value is None:
            # print("No time information found for item:", item)
            count_no_time += 1
    print(f"Number of messages with no time information: {count_no_time}")
    decoded_rust = [item for item in decoded_rust if item.get("Time (s since midnight)", None) is not None]
    df_rust = pd.json_normalize(decoded_rust)
    df_rust.to_csv("adsb_rust.csv", index=False)
    print(f"Decoding time with Rust: {time()-start:.2f} seconds")
    print("Saved adsb_rust.csv")
    gc.collect()
    # Decode with Python
    start = time()
    decoder = Decoder()
    decoded_python = decoder.load(
        "Test_Data/datos_asterix_adsb.ast",
        parallel=True,
        max_messages=1000,
        radar_coords=coords_radar,
    )
    df_python = pd.DataFrame(decoded_python)
    # The rust implementation returns a dict, so we need to flatten the python one
    print(
        f"Decoded {len(decoded_python)} messages with Python decoder in {time()-start:.2f} seconds"
    )
    df_python = pd.json_normalize(df_python.to_dict("records"))
    df_python.to_csv("adsb_python.csv", index=False)
    print(f"Decoding time with Python: {time()-start:.2f} seconds")
    print("Saved adsb_python.csv")
