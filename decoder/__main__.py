import argparse
from .decoder import Decoder

def parse_args():
    parser = argparse.ArgumentParser(description='ASTERIX decoder')
    parser.add_argument('--test-radar', action='store_true', help='Use test radar data')
    parser.add_argument('--test-adsb', action='store_true', help='Use test ADS-B data')
    parser.add_argument('--test-all', action='store_true', help='Use all test data')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print(f"Test Radar: {args.test_radar}")
    print(f"Test ADS-B: {args.test_adsb}")
    print(f"Test All: {args.test_all}")
    if args.test_radar:
        decoder = Decoder()
        decoder.load('Test_Data/datos_asterix_radar.ast')
    if args.test_adsb:
        decoder = Decoder()
        decoder.load('Test_Data/datos_asterix_adsb.ast')
    if args.test_all:
        decoder = Decoder()
        decoder.load('Test_Data/datos_asterix_combinado.ast')