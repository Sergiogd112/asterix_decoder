#!/usr/bin/env python3
"""
Test Rust message structure.
"""


def test_rust_message_structure():
    """Test Rust message structure."""
    from decoderrs import load

    file_path = "Test_Data/datos_asterix_radar.ast"
    radar_lat = 41.2971
    radar_lon = 2.07846
    radar_alt = 148

    results = load(file_path, radar_lat, radar_lon, radar_alt, max_messages=1)

    if results:
        msg = results[0]
        print("Message type:", type(msg))
        print(
            "Message keys:",
            list(msg.keys()) if hasattr(msg, "keys") else "No keys method",
        )
        print("Message:", msg)
    else:
        print("No messages")


if __name__ == "__main__":
    test_rust_message_structure()
