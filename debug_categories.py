#!/usr/bin/env python3
"""
Debug message categories in file.
"""


def debug_categories():
    """Debug what categories are in the file."""
    from decoder.decoder import Decoder

    decoder = Decoder()
    file_path = "Test_Data/datos_asterix_radar.ast"

    # Get first 100 messages without filtering
    with open(file_path, "rb") as f:
        data = f.read()

    # Manual parsing to see categories
    import bitstring

    bv = bitstring.BitArray(bytes=data)
    current_pos = 0
    total_bits = len(bv)
    message_count = 0

    print("First 20 message categories:")
    while current_pos + 24 <= total_bits and message_count < 20:
        cat = bv[current_pos : current_pos + 8].uint
        length = bv[current_pos + 8 : current_pos + 24].uint

        print(f"Message {message_count + 1}: CAT={cat}, length={length}")

        if length < 3:
            break

        current_pos += length * 8
        message_count += 1


if __name__ == "__main__":
    debug_categories()
