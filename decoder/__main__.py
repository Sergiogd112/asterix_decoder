import argparse
from time import time
from .decoder import Decoder


def parse_args():
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
    if args.test_radar:
        decoder = Decoder()
        decoder.load(
            "Test_Data/datos_asterix_radar.ast",
            args.parallel,
            max_messages=args.max_messages,
        )
    if args.test_adsb:
        decoder = Decoder()
        decoder.load(
            "Test_Data/datos_asterix_adsb.ast",
            args.parallel,
            max_messages=args.max_messages,
        )
    if args.test_all:
        decoder = Decoder()
        decoder.load(
            "Test_Data/datos_asterix_combinado.ast",
            args.parallel,
            max_messages=args.max_messages,
        )
    print(f"Elapsed Time: {time()-start} s")
