#!/usr/bin/env python3
"""
Test single message decoding.
"""


def test_single_message():
    """Test with single message."""
    from decoderrs import load

    file_path = "Test_Data/datos_asterix_radar.ast"
    radar_lat = 41.2971
    radar_lon = 2.07846
    radar_alt = 148

    # Test with just 1 message
    results = load(file_path, radar_lat, radar_lon, radar_alt, max_messages=1)
    print(f"Rust returned {len(results)} messages")

    if results:
        print("First message:")
        print(results[0])
    else:
        print("No messages decoded")


if __name__ == "__main__":
    test_single_message()
