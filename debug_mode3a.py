#!/usr/bin/env python3

import bitstring


def decode_mode3a_code_debug(data: bitstring.BitArray):
    """Debug version to show bit extraction details."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Mode 3/A Code.")
    val = data[0:16].uint

    print(f"Raw 16-bit value: {val:016b} ({val})")

    # Simulate C# bit array (MSB-first)
    print("\nC# array (MSB to LSB):")
    csharp_array = []
    for i in range(15, -1, -1):
        bit = (val >> i) & 1
        csharp_array.append(bit)
        print(f"array[{i:2d}] = {bit}")

    # Extract exactly like C# code
    print("\nC# style extraction:")
    digits = []
    for i in range(0, 12, 3):
        # C# code: array[i + 4], array[i + 5], array[i + 6]
        bit0 = csharp_array[i + 4]
        bit1 = csharp_array[i + 5]
        bit2 = csharp_array[i + 6]
        digit = (bit0 << 2) | (bit1 << 1) | bit2
        digits.append(digit)
        print(
            f"Digit {i // 3}: array[{i + 4},{i + 5},{i + 6}] = {bit0}{bit1}{bit2} -> {digit}"
        )

    mode3a_code = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
    print(f"C# final code: {mode3a_code:04d}")

    # Test my corrected implementation
    print("\nMy corrected implementation:")
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
    print(f"My corrected code: {my_code:04d}")

    return mode3a_code, my_code


# Test with a simple example
if __name__ == "__main__":
    # Test with a known value
    test_val = 0x1234  # Example value
    test_bits = bitstring.BitArray(uint=test_val, length=16)
    print(f"Testing with value: {test_val:04X}")
    cs_code = decode_mode3a_code_debug(test_bits)
