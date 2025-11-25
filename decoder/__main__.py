import argparse
from time import time
from rich import print
import numpy as np
from .decoder import Decoder
from .geoutils import CoordinatesWGS84


def parse_args():
    """Create CLI parser mirroring the Rust benchmark flags."""
    parser = argparse.ArgumentParser(description="ASTERIX decoder")
    parser.add_argument("--test-radar", action="store_true", help="Use test radar data")
    parser.add_argument("--test-adsb", action="store_true", help="Use test ADS-B data")
    parser.add_argument("--test-all", action="store_true", help="Use all test data")
    parser.add_argument("--parallel", action="store_true", help="Use parallel decoding")
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Maximum number of messages to decode",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Test Radar: {args.test_radar}")
    print(f"Test ADS-B: {args.test_adsb}")
    print(f"Test All: {args.test_all}")
    start = time()
    radar_lat = (41 + 18 / 60.0 + 2.5184 / 3600.0) * np.pi / 180
    radar_lon = (2 + 6 / 60.0 + 7.4095 / 3600.0) * np.pi / 180
    radar_alt = 27.25
    coords_radar = CoordinatesWGS84(radar_lat, radar_lon, radar_alt)

    if args.test_radar:
        decoder = Decoder()
        decoded = decoder.load(
            "Test_Data/datos_asterix_radar.ast",
            args.parallel,
            max_messages=args.max_messages,
            radar_coords=coords_radar,
        )
    if args.test_adsb:
        decoder = Decoder()
        decoded = decoder.load(
            "Test_Data/datos_asterix_adsb.ast",
            args.parallel,
            max_messages=args.max_messages,
            radar_coords=coords_radar,
        )
    if args.test_all:
        decoder = Decoder()
        decoded = decoder.load(
            "Test_Data/datos_asterix_combinado.ast",
            args.parallel,
            max_messages=args.max_messages,
            radar_coords=coords_radar,
        )
    print(f"Decoded {len(decoded)} messages")
    # print(decoded)
    print(f"Elapsed Time: {time()-start} s")
    print(decoded)
    decoder.export_to_csv(decoded)
