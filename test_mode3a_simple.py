#!/usr/bin/env python3

import bitstring


def test_mode3a_implementation():
    """Test Mode-3/A implementation with known values."""

    # Test with some known 16-bit values
    test_values = [
        0x1234,  # Example from earlier
        0x5678,  # Another example
        0x9ABC,  # Another example
        0xDEF0,  # Another example
    ]

    for val in test_values:
        print(f"\n=== Testing value: 0x{val:04X} ({val}) ===")
        print(f"Raw bits: {val:016b}")

        # C# implementation simulation
        print("\nC# implementation:")
        csharp_array = []
        for i in range(15, -1, -1):
            csharp_array.append((val >> i) & 1)

        digits = []
        for i in range(0, 12, 3):
            bit0 = csharp_array[i + 4]
            bit1 = csharp_array[i + 5]
            bit2 = csharp_array[i + 6]
            digit = (bit0 << 2) | (bit1 << 1) | bit2
            digits.append(digit)
            print(
                f"Digit {i // 3}: array[{i + 4},{i + 5},{i + 6}] = {bit0}{bit1}{bit2} -> {digit}"
            )

        csharp_code = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
        print(f"C# final code: {csharp_code:04d}")

        # My Python implementation
        print("\nMy Python implementation:")
        my_digits = []
        for i in range(0, 12, 3):
            bit0 = (val >> (15 - (i + 4))) & 1
            bit1 = (val >> (15 - (i + 5))) & 1
            bit2 = (val >> (15 - (i + 6))) & 1
            digit = (bit0 << 2) | (bit1 << 1) | bit2
            my_digits.append(digit)
            print(
                f"Digit {i // 3}: bits {15 - (i + 4)},{15 - (i + 5)},{15 - (i + 6)} = {bit0}{bit1}{bit2} -> {digit}"
            )

        my_code = (
            my_digits[0] * 1000 + my_digits[1] * 100 + my_digits[2] * 10 + my_digits[3]
        )
        print(f"My final code: {my_code:04d}")

        # Check if they match
        if csharp_code == my_code:
            print("✓ MATCH!")
        else:
            print("✗ MISMATCH!")


if __name__ == "__main__":
    test_mode3a_implementation()
