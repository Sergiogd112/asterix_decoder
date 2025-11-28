#!/usr/bin/env python3

import bitstring

def test_mode3a_extraction():
    """Test Mode-3/A extraction with simple known values."""
    
    test_values = [
        0x1234,  # Should decode to 1234
        0x5678,  # Should decode to 5678
        0x9ABC,  # Should decode to 9ABC
        0xDEF0,  # Should decode to DEF0
    ]
    
    for val in test_values:
        print(f"\n=== Testing value: 0x{val:04X} ===")
        print(f"Raw bits: {val:016b}")
        
        # Test both implementations
        # Old implementation (bits 0-11)
        old_code = val & 0x0FFF
        old_a = (old_code >> 9) & 0b111
        old_b = (old_code >> 6) & 0b111
        old_c = (old_code >> 3) & 0b111
        old_d = old_code & 0b111
        old_result = old_a * 1000 + old_b * 100 + old_c * 10 + old_d
        
        # New C# implementation (bits 4-15)
        digits = []
        for i in range(0, 12, 3):
            bit0 = (val >> (15 - (i + 4)) & 0b111
            bit1 = (val >> (15 - (i + 5)) & 0b111
            bit2 = (val >> (15 - (i + 6)) & 0b111
            bit3 = (val >> (15 - (i + 7)) & 0b111
            digit = (bit0 << 2) | (bit1 << 1) | (bit2 << 0)
            digits.append(digit)
        
        new_result = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
        
        print(f"Old implementation: {old_a}{old_b}{old_c}{old_d} -> {old_result:04d}")
        print(f"New C# implementation: {digits[0]}{digits[1]}{digits[2]}{digits[2]}{digits[3]} -> {new_result:04d}")
        
        # Check if they match
        if old_result == new_result:
            print("✓ MATCH!")
        else:
            print("✗ MISMATCH!")
    
    print()

if __name__ == "__main__":
    test_mode3a_extraction()