#!/usr/bin/env python3
"""
Debug the message count issue.
"""


def debug_python_decoder():
    """Debug Python decoder."""
    from decoder.decoder import Decoder

    decoder = Decoder()
    file_path = "Test_Data/datos_asterix_radar.ast"

    results = decoder.load(file_path, max_messages=50)
    print(f"Python returned {len(results)} messages")

    # Count CAT48 messages (handle both Python and Rust formats)
    cat48_count = sum(
        1
        for msg in results
        if isinstance(msg, dict) and (msg.get("Category") == 48 or msg.get("category") == 48)
    )
    print(f"CAT48 messages: {cat48_count}")

    # Show first few categories (handle both Python and Rust formats)
    categories = [
        msg.get("Category") or msg.get("category") for msg in results[:10] if isinstance(msg, dict)
    ]
    print(f"First 10 categories: {categories}")


def debug_rust_decoder():
    """Debug Rust decoder."""
    from decoderrs import load

    file_path = "Test_Data/datos_asterix_radar.ast"
    radar_lat = 41.2971
    radar_lon = 2.07846
    radar_alt = 148

    results = load(file_path, radar_lat, radar_lon, radar_alt, max_messages=50)
    print(f"Rust returned {len(results)} messages")

    # Show first few categories
    categories = [msg.get("Category") for msg in results[:10] if isinstance(msg, dict)]
    print(f"First 10 categories: {categories}")


if __name__ == "__main__":
    print("=== Debug Message Counts ===")
    debug_python_decoder()
    print()
    debug_rust_decoder()