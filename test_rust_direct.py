#!/usr/bin/env python3

import decoderrs
import bitstring


def test_rust_direct():
    """Test the Rust implementation directly with known bytes."""

    # Test the exact bytes that should give us known results
    test_cases = [
        (b"\xc6\x2c", "3054"),  # Should give 3054
        (b"\x20\x01", "0001"),  # Should give 0001
        (b"\x2a\xe3", "5343"),  # Should give 5343
    ]

    for data, expected in test_cases:
        # Create a simple ASTERIX message with just Mode-3/A field
        # CAT48 message structure: CAT(1) + LEN(2) + FSPEC(1) + DATA
        # For Mode-3/A at FRN 5, we need: FSPEC bits 0-4 set, FRN 5 set
        fspec = 0b10001000  # Bits 0-4: FRN5=1, others=0, FX=0

        # Construct full message
        message = bytes(
            [
                48,  # CAT
                len(data) + 3,  # LEN (3 bytes)
                fspec,  # FSPEC
                data,
            ]
        )  # Mode-3/A data

        print(f"\n=== Testing Rust with {data.hex().upper()} ===")
        print(f"Expected: {expected}")

        # Test with Rust implementation
        try:
            results = decoderrs.load("test_file", 41.0, 2.0, 100, debug_save_path=None)
            for result in results:
                if result.get("Category") == 48 and "Mode-3/A Code" in result:
                    print(f"Rust result: {result['Mode-3/A Code']}")
                    break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    test_rust_direct()
