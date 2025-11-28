#!/usr/bin/env python3

import bitstring


def extract_mode3a_from_asterix():
    """Extract actual Mode-3/A bytes from ASTERIX data and test decoding."""

    # Read test file
    with open("Test_Data/datos_asterix_radar.ast", "rb") as f:
        data = f.read()

    # Simple ASTERIX parsing to find CAT48 messages with Mode 3/A
    pos = 0
    count = 0
    while pos < len(data) and count < 3:
        if pos + 3 > len(data):
            break

        # Read CAT and length
        cat = data[pos]
        length = (data[pos + 1] << 8) | data[pos + 2]

        if cat == 48 and length > 0 and pos + 3 + length <= len(data):
            # Extract payload
            payload = data[pos + 3 : pos + 3 + length]
            bits = bitstring.BitArray(payload)

            # Decode FSPEC first
            fspec_data = []
            more_fspec = True
            bit_pos = 0

            while more_fspec and bit_pos < len(bits):
                if bit_pos + 8 > len(bits):
                    break

                fspec_bits = bits[bit_pos : bit_pos + 8]
                for i in range(7):
                    fspec_data.append(bool(fspec_bits[i]))
                more_fspec = bool(fspec_bits[7])
                bit_pos += 8

            # Check if Mode 3/A (FRN 5) is present for CAT48
            if len(fspec_data) >= 5 and fspec_data[4]:  # FRN 5 is index 4
                print(f"\n=== CAT48 Message {count + 1} ===")
                print(f"FSPEC length: {len(fspec_data)} fields")
                print(f"Mode 3/A present: {fspec_data[4]}")

                # Skip to Mode 3/A field (need to skip FRN 1-4)
                # FRN 1: Data Source ID (2 bytes)
                # FRN 2: Target Report Descriptor (1+ bytes)
                # FRN 3: Track Number (2 bytes)
                # FRN 4: Service Identification (1 byte)
                mode3a_start = bit_pos

                # Skip Data Source ID (2 bytes = 16 bits)
                if fspec_data[0]:
                    mode3a_start += 16

                # Skip Target Report Descriptor (variable)
                if fspec_data[1]:
                    # Skip 1 byte + any FX extensions
                    trd_bits = bits[mode3a_start : mode3a_start + 8]
                    mode3a_start += 8
                    if trd_bits[7]:  # FX bit set
                        # Skip extension
                        mode3a_start += 8
                        # Check for more extensions
                        while mode3a_start + 8 <= len(bits) and bits[mode3a_start + 7]:
                            mode3a_start += 8

                # Skip Track Number (2 bytes)
                if fspec_data[2]:
                    mode3a_start += 16

                # Skip Service Identification (1 byte)
                if fspec_data[3]:
                    mode3a_start += 8

                # Now extract Mode 3/A (2 bytes)
                if mode3a_start + 16 <= len(bits):
                    mode3a_bits = bits[mode3a_start : mode3a_start + 16]
                    val = mode3a_bits.uint

                    print(f"Mode 3/A raw bytes: {val:04X}")
                    print(f"Mode 3/A raw bits: {val:016b}")

                    # Test both implementations
                    # Old implementation
                    old_code = val & 0x0FFF
                    old_a = (old_code >> 9) & 0b111
                    old_b = (old_code >> 6) & 0b111
                    old_c = (old_code >> 3) & 0b111
                    old_d = old_code & 0b111
                    old_result = old_a * 1000 + old_b * 100 + old_c * 10 + old_d

                    # New C# implementation
                    digits = []
                    for i in range(0, 12, 3):
                        bit0 = (val >> (15 - (i + 4))) & 1
                        bit1 = (val >> (15 - (i + 5))) & 1
                        bit2 = (val >> (15 - (i + 6))) & 1
                        digit = (bit0 << 2) | (bit1 << 1) | bit2
                        digits.append(digit)

                    new_result = (
                        digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
                    )

                    print(
                        f"Old implementation: {old_a}{old_b}{old_c}{old_d} -> {old_result:04d}"
                    )
                    print(
                        f"New C# implementation: {digits[0]}{digits[1]}{digits[2]}{digits[3]} -> {new_result:04d}"
                    )

                    count += 1

        pos += 3 + length


if __name__ == "__main__":
    extract_mode3a_from_asterix()
