import decoderrs
import numpy as np
import pandas as pd
from rich import print
from time import time
from decoder.decoder import Decoder
from decoder.geoutils import CoordinatesWGS84

if __name__ == "__main__":
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25
    coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)
    start=time()
    # Decode with Rust
    decoded_rust = decoderrs.load(
        "Test_Data/datos_asterix_combinado.ast",
        radar_lat=radar_lat,
        radar_lon=radar_lon,
        radar_alt=radar_alt,
    )
    print(f"Decoded {len(decoded_rust)} messages with Rust decoder")
    df_rust = pd.json_normalize(decoded_rust)
    df_rust.to_csv("full_rust.csv", index=False)
    print(f"Decoding time with Rust: {time()-start:.2f} seconds")
    print("Saved cat48_rust.csv")

    # Decode with Python
    start=time()
    decoder = Decoder()
    decoded_python = decoder.load(
        "Test_Data/datos_asterix_combinado.ast",
        parallel=True,
        # max_messages=1000,
        radar_coords=coords_radar,
    )
    df_python = pd.DataFrame(decoded_python)
    # The rust implementation returns a dict, so we need to flatten the python one
    print(f"Decoded {len(decoded_python)} messages with Python decoder")
    df_python = pd.json_normalize(df_python.to_dict('records'))
    df_python.to_csv("full_python.csv", index=False)
    print(f"Decoding time with Python: {time()-start:.2f} seconds")
    print("Saved cat48_python.csv")
