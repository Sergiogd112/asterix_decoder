#!/usr/bin/env python3

import bitstring

# Read some test data to find messages with BP=1013.6
with open("Test_Data/datos_asterix_adsb.ast", "rb") as f:
    data = f.read()

# Simple ASTERIX parser to find CAT21 messages with BP
pos = 0
count = 0
found_1013 = False

while pos < len(data) and count < 20:
    if pos + 3 > len(data):
        break

    # Read ASTERIX header
    cat = data[pos]
    length = (data[pos + 1] << 8) | data[pos + 2]

    if cat != 21:
        pos += 3 + length
        continue

    # Read data payload
    if pos + 3 + length > len(data):
        break

    block_data = data[pos + 3 : pos + 3 + length]
    bits = bitstring.BitArray(block_data)

    # Decode FSPEC
    fspec_data = []
    more_fspec = True
    bit_pos = 0

    while more_fspec and bit_pos < len(bits):
        fspec_bits = bits[bit_pos : bit_pos + 8]
        for i in range(7):
            fspec_data.append(bool(fspec_bits[i]))
        more_fspec = bool(fspec_bits[7])
        bit_pos += 8

    # Check if FRN 42 (Receiver ID) is present
    if len(fspec_data) >= 42 and fspec_data[41]:  # FRN 42 is at index 41
        print(f"\nMessage {count + 1}: CAT{cat}, length {length}")
        print(f"FRN 42 (Receiver ID) is present")

        # Find position of FRN 42 data by skipping fields 1-41
        field_pos = bit_pos

        # Let's manually count through fields to find FRN 42 position
        # This is complex due to variable length fields, so let's use a simpler approach
        # Look for the pattern that should give us BP=1013.6

        # Try to find BP data by looking for the pattern
        # We need to find where the pressure data should be
        remaining_bits = bits[field_pos:]

        # Look for REP (1 byte) + presence (1 byte) + pressure (2 bytes)
        for i in range(0, min(64, len(remaining_bits) - 32), 8):
            test_bits = remaining_bits[i : i + 32]
            if len(test_bits) >= 32:
                rep = test_bits[0:8].uint
                presence = test_bits[8:16].uint

                if (presence & 0x80) != 0:  # BP present
                    pressure_raw = test_bits[16:32].uint
                    pressure_12bit = (pressure_raw >> 4) & 0xFFF
                    bp_value = pressure_12bit * 0.1 + 800.0

                    if abs(bp_value - 1013.6) < 0.1:
                        print(f"Found BP=1013.6 at offset {field_pos + i}")
                        print(f"  REP: {rep}")
                        print(f"  Presence: {presence:08b}")
                        print(f"  Pressure raw: {pressure_raw:016b}")
                        print(f"  Pressure 12-bit: {pressure_12bit:012b}")
                        print(f"  Calculated BP: {bp_value}")
                        found_1013 = True
                        break

                if found_1013:
                    break

        if found_1013:
            break

    count += 1
    pos += 3 + length

    if count >= 20:
        break
