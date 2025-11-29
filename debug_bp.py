#!/usr/bin/env python3

import bitstring

# Read some test data to examine the raw bytes for RE field
with open("Test_Data/datos_asterix_adsb.ast", "rb") as f:
    data = f.read()

# Parse ASTERIX format
pos = 0
count = 0
while pos < len(data) and count < 10:
    if pos + 3 > len(data):
        break

    # Read CAT and LEN
    cat = data[pos]
    length = (data[pos + 1] << 8) | data[pos + 2]

    if cat != 21:
        pos += 3 + length
        continue

    # Read data block
    if pos + 3 + length > len(data):
        break

    block_data = data[pos + 3 : pos + 3 + length]
    bits = bitstring.BitArray(block_data)

    print(f"\nMessage {count + 1}:")
    print(f"Length: {length}")

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
        print("FRN 42 (Receiver ID) found!")

        # Also check if this message has Target ID matching ground truth
        has_target_id = len(fspec_data) >= 29 and fspec_data[28]  # FRN 29

        # Find the position of FRN 42 data
        # Skip over fields 1-41
        current_pos = bit_pos

        # Let's manually count through the fields to find FRN 42 position
        field_sizes = {
            1: 16,  # Data Source ID
            2: 8,  # Target Report Descriptor (variable)
            3: 16,  # Track Number
            4: 8,  # Service Identification
            5: 24,  # Time of Applicability for Position
            6: 48,  # Position in WGS-84 Co-ordinates
            7: 64,  # Position in WGS-84 Co-ordinates High Resolution
            8: 24,  # Time of Applicability for Velocity
            9: 16,  # Air Speed
            10: 16,  # True Air Speed
            11: 24,  # Target Address
            12: 24,  # Time of Message Reception of Position
            13: 32,  # Time of Message Reception of Position-High Precision
            14: 24,  # Time of Message Reception for Velocity
            15: 32,  # Time of Message Reception of Velocity-High Precision
            16: 16,  # Geometric Height
            17: None,  # Quality Indicators (variable)
            18: 8,  # MOPS Version
            19: 16,  # Mode 3/A Code
            20: 16,  # Roll Angle
            21: 16,  # Flight Level
            22: 16,  # Magnetic Heading
            23: 8,  # Target Status
            24: 16,  # Barometric Vertical Rate
            25: 16,  # Geometric Vertical Rate
            26: 32,  # Airborne Ground Vector
            27: 16,  # Track Angle Rate
            28: 24,  # Time of Report Transmission
            29: 48,  # Target Identification
            30: 8,  # Emitter Category
            31: None,  # Met Information (variable)
            32: 16,  # Selected Altitude
            33: 16,  # Final State Selected Altitude
            34: None,  # Trajectory Intent (variable)
            35: 8,  # Service Management
            36: 8,  # Aircraft Operational Status
            37: None,  # Surface Capabilities and Characteristics (variable)
            38: 8,  # Message Amplitude
            39: None,  # Mode S MB Data (variable)
            40: 56,  # ACAS Resolution Advisory Report
            41: 8,  # Receiver ID
        }

        # Calculate position up to FRN 42
        for frn in range(1, 42):
            if frn < len(fspec_data) and fspec_data[frn - 1]:
                if frn in field_sizes:
                    if field_sizes[frn] is not None:
                        current_pos += field_sizes[frn]
                    else:
                        print(
                            f"Variable field {frn} encountered, cannot calculate position accurately"
                        )
                        break
                else:
                    print(f"Unknown field {frn}")
                    break

        # Now at FRN 42 position
        print(f"FRN 42 starts at bit position: {current_pos}")

        if current_pos + 16 <= len(bits):
            # Read REP byte
            rep = bits[current_pos : current_pos + 8].uint
            print(f"REP: {rep}")

            # Read presence bits
            presence = bits[current_pos + 8 : current_pos + 16].uint
            print(f"Presence bits: {presence:08b}")

            if (presence & 0x80) != 0:  # Bit 0 set
                # Read pressure data
                pressure_raw = bits[current_pos + 16 : current_pos + 32].uint
                print(f"Raw pressure (16 bits): {pressure_raw:016b} ({pressure_raw})")

                # Try different extraction methods
                method1 = (pressure_raw >> 4) & 0xFFF  # My previous attempt
                method2 = pressure_raw & 0xFFF  # Current attempt
                method3 = (pressure_raw >> 2) & 0x3FF  # Alternative

                print(f"Method 1 (>>4): {method1} -> BP: {method1 * 0.1 + 800:.1f}")
                print(f"Method 2 (&FFF): {method2} -> BP: {method2 * 0.1 + 800:.1f}")
                print(f"Method 3 (>>2): {method3} -> BP: {method3 * 0.1 + 800:.1f}")

                # Try different formulas
                print(f"Method 1 alt: {method1} -> BP: {method1 * 0.1 + 900:.1f}")
                print(f"Method 2 alt: {method2} -> BP: {method2 * 0.1 + 900:.1f}")
                print(f"Method 1 alt2: {method1} -> BP: {method1 * 0.1 + 1000:.1f}")
                print(f"Method 2 alt2: {method2} -> BP: {method2 * 0.1 + 1000:.1f}")

                # Let's also try to simulate the C# approach exactly
                # C# convert function creates MSB-first array
                pressure_bits = []
                for i in range(16):
                    pressure_bits.append((pressure_raw >> (15 - i)) & 1)

                # Extract bits 4-15 (12 bits)
                extracted_bits = pressure_bits[4:16]
                extracted_value = 0
                for bit in extracted_bits:
                    extracted_value = (extracted_value << 1) | bit

                bp_value = extracted_value * 0.1 + 800.0
                print(f"C# simulation: {extracted_value} -> BP: {bp_value:.1f}")

                # Check if this matches expected ground truth
                if abs(bp_value - 1013.6) < 0.1:
                    print("*** MATCHES GROUND TRUTH! ***")
                else:
                    print(
                        f"Expected: 1013.6, Got: {bp_value:.1f}, Diff: {bp_value - 1013.6:.1f}"
                    )

    count += 1
    pos += 3 + length

    if count >= 5:
        break
