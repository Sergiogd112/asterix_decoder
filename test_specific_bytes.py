#!/usr/bin/env python3

import bitstring


def test_specific_bytes():
    """Test the specific bytes we found in the Python implementation."""

    # Test the exact bytes from Python results
    test_cases = [
        ("C62C", "3054"),  # Expected from Python
        ("2001", "0001"),  # Expected from Python
        ("2AE3", "5343"),  # Expected from Python
    ]

    for hex_bytes, expected in test_cases:
        # Convert hex string to bytes
        if len(hex_bytes) == 4:
            data = bytes.fromhex(hex_bytes)
        else:
            # Odd length, add leading zero
            data = bytes.fromhex("0" + hex_bytes)

        bits = bitstring.BitArray(data)
        val = bits[0:16].uintbe  # Get 16-bit value

        print(f"\n=== Testing {hex_bytes} ===")
        print(f"Raw bytes: {data.hex().upper()}")
        print(f"16-bit value: 0x{val:04X} ({val})")
        print(f"Expected: {expected}")

        # Apply the C# algorithm
        digits = []
        for i in range(4):
            # C# extracts array[i+4], array[i+5], array[i+6]
            # This corresponds to bits: 15-(i+4), 15-(i+5), 15-(i+6)
            bit0 = (val >> (15 - (i + 4))) & 1
            bit1 = (val >> (15 - (i + 5))) & 1
            bit2 = (val >> (15 - (i + 6))) & 1
            digit = (bit0 << 2) | (bit1 << 1) | bit2
            digits.append(digit)
            print(
                f"Digit {i}: bits {15 - (i + 4)},{15 - (i + 5)},{15 - (i + 6)} = {bit0}{bit1}{bit2} -> {digit}"
            )

        # Combine into 4-digit octal code
        mode3a_code = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
        print(f"Combined: {digits[0]}{digits[1]}{digits[2]}{digits[3]} = {mode3a_code}")

        # Format with leading zeros
        if mode3a_code < 10:
            result = f"000{mode3a_code}"
        elif mode3a_code < 100:
            result = f"00{mode3a_code}"
        elif mode3a_code < 1000:
            result = f"0{mode3a_code}"
        else:
            result = f"{mode3a_code}"

        print(f"Final result: {result}")
        print(f"Match expected: {'✓' if result == expected else '✗'}")


if __name__ == "__main__":
    test_specific_bytes()
