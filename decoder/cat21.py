import numpy as np

import pandas as pd
import bitstring
from rich import print

def decode_cat21(cat, length, data: bitstring.BitArray):
    if cat != 21:
        raise ValueError("Category must be 21 for decode_cat21")
    
    # Make sure we have a BitArray
    if not isinstance(data, bitstring.BitArray):
        data = bitstring.BitArray(bin=data)
    
    start = 8  # Start after category byte
    decoded = {}
    
    # Decode FSPEC (Field Specification)
    fspec_block_1 = data[start:start+7]
    fx1 = data[start+7]
    start += 8
    
    data_items_to_decode = [i for i, bit in enumerate(fspec_block_1) if bit]
    
    # Handle FSPEC extensions
    if fx1:
        fspec_block_2 = data[start:start+7]
        fx2 = data[start+7]
        data_items_to_decode += [i + 7 for i, bit in enumerate(fspec_block_2) if bit]
        start += 8
        
        if fx2:
            fspec_block_3 = data[start:start+7]
            fx3 = data[start+7]
            data_items_to_decode += [i + 14 for i, bit in enumerate(fspec_block_3) if bit]
            start += 8
            
            if fx3:
                fspec_block_4 = data[start:start+7]
                data_items_to_decode += [i + 21 for i, bit in enumerate(fspec_block_4) if bit]
                start += 8
    
    # ESSENTIAL CAT21 Data Item mapper (only green items from your table)
    cat21_mapper = {
        1: ("Data Source Identification", lambda d: (decode_data_source_identification(int(d[:16].uint)), 16)),
        2: ("Target Report Descriptor", lambda d: (decode_target_report_descriptor(d[:d.length].bytes), (d.length + 7) // 8)),
        7: ("Position in WGS-84 Co-ordinates High Resolution", lambda d: (decode_high_resolution_position(d[:64].bytes), 64)),
        11: ("Target Address", lambda d: (decode_target_address(d[:24].bytes), 24)),
        12: ("Time of Message Reception of Position", lambda d: (decode_time_of_message_reception_position(d[:24].bytes), 24)),
        19: ("Mode 3/A Code", lambda d: (decode_mode_3a_code(int(d[:16].uint)), 16)),
        21: ("Flight Level", lambda d: (decode_flight_level(d[:16].bytes), 16)),
        29: ("Target Identification", lambda d: (decode_target_identification(d[:48].bytes), 48)),
    }
    
    # Decode each data item
    for item in data_items_to_decode:
        if item in cat21_mapper:
            item_name, decoder_func = cat21_mapper[item]
            try:
                # Calculate available bits
                available_bits = len(data) - start
                if available_bits <= 0:
                    break
                    
                result, step = decoder_func(data[start:])
                decoded[item_name] = result
                start += step
            except Exception as e:
                decoded[item_name] = f"Error decoding: {str(e)}"
                # Try to continue with next item
                continue
        else:
            # Skip non-essential items but note their presence
            decoded[f"Non-essential Item FRN {item+1}"] = "Skipped (not in essential list)"
    
    print("Decoded CAT21 Essential Data Items:")
    for key, value in decoded.items():
        if "Skipped" not in str(value):
            print(f"  {key}: {value}")
    
    return data_items_to_decode, decoded, start


##############################################################################################################################

def decode_data_source_identification(two_bytes: int) -> dict:

    if not (0 <= two_bytes <= 0xFFFF):
        raise ValueError("Value must be a 16-bit integer between 0 and 65535.")

    sac = (two_bytes >> 8) & 0xFF  # bits 16–9
    sic = two_bytes & 0xFF         # bits 8–1

    return {
        "SAC": sac,
        "SIC": sic
    }

##############################################################################################################################


def decode_target_report_descriptor(data: bytes) -> dict:

    if len(data) < 1:
        raise ValueError("Target Report Descriptor requires at least 1 octet.")

    result = {}
    offset = 0
    fx = 1  # Assume FX = 1 to enter loop

    # ==========================
    # Primary Subfield
    # ==========================
    byte_val = data[offset]
    offset += 1
    fx = byte_val & 0b1

    atp = (byte_val >> 5) & 0b111
    arc = (byte_val >> 3) & 0b11
    rc = (byte_val >> 2) & 0b1
    rab = (byte_val >> 1) & 0b1

    atp_map = {
        0: "24-Bit ICAO address",
        1: "Duplicate address",
        2: "Surface vehicle address",
        3: "Anonymous address",
        4: "Reserved",
        5: "Reserved",
        6: "Reserved",
        7: "Reserved",
    }

    arc_map = {
        0: "25 ft",
        1: "100 ft",
        2: "Unknown",
        3: "Invalid",
    }

    result["Primary"] = {
        "ATP": atp,
        "ATP Description": atp_map.get(atp, "Reserved"),
        "ARC": arc,
        "ARC Description": arc_map.get(arc, "Reserved"),
        "RC": rc,
        "RC Description": "Range Check passed, CPR validation pending" if rc else "Default",
        "RAB": rab,
        "RAB Description": "Report from field monitor (fixed transponder)" if rab else "Report from target transponder",
    }

    # ==========================
    # First Extension
    # ==========================
    if fx and len(data) > offset:
        byte_val = data[offset]
        offset += 1
        fx = byte_val & 0b1

        dcr = (byte_val >> 7) & 0b1
        gbs = (byte_val >> 6) & 0b1
        sim = (byte_val >> 5) & 0b1
        tst = (byte_val >> 4) & 0b1
        saa = (byte_val >> 3) & 0b1
        cl = (byte_val >> 1) & 0b11

        cl_map = {
            0: "Report valid",
            1: "Report suspect",
            2: "No information",
            3: "Reserved for future use",
        }

        result["First Extension"] = {
            "DCR": dcr,
            "DCR Description": "Differential correction (ADS-B)" if dcr else "No differential correction (ADS-B)",
            "GBS": gbs,
            "GBS Description": "Ground Bit set" if gbs else "Ground Bit not set",
            "SIM": sim,
            "SIM Description": "Simulated target report" if sim else "Actual target report",
            "TST": tst,
            "TST Description": "Test Target" if tst else "Default",
            "SAA": saa,
            "SAA Description": "Equipment not capable of providing Selected Altitude" if saa else "Equipment capable of providing Selected Altitude",
            "CL": cl,
            "CL Description": cl_map.get(cl, "Reserved"),
        }

    # ==========================
    # Second Extension (Error Conditions)
    # ==========================
    if fx and len(data) > offset:
        byte_val = data[offset]
        offset += 1
        fx = byte_val & 0b1

        ipc = (byte_val >> 5) & 0b1
        nogo = (byte_val >> 4) & 0b1
        cpr = (byte_val >> 3) & 0b1
        ldpj = (byte_val >> 2) & 0b1
        rcf = (byte_val >> 1) & 0b1

        result["Second Extension"] = {
            "IPC": ipc,
            "IPC Description": "Independent Position Check failed" if ipc else "Default",
            "NOGO": nogo,
            "NOGO Description": "NOGO-bit set" if nogo else "NOGO-bit not set",
            "CPR": cpr,
            "CPR Description": "CPR Validation failed" if cpr else "CPR Validation correct",
            "LDPJ": ldpj,
            "LDPJ Description": "Local Decoding Position Jump detected" if ldpj else "LDPJ not detected",
            "RCF": rcf,
            "RCF Description": "Range Check failed" if rcf else "Default",
        }

    # Return all decoded fields
    return result

##############################################################################################################################

def decode_high_resolution_position(data: bytes) -> dict:

    if len(data) < 8:
        raise ValueError("High-Resolution Position requires 8 bytes.")

    # --- Extract 4 bytes for latitude and longitude ---
    lat_raw = int.from_bytes(data[0:4], byteorder="big", signed=True)
    lon_raw = int.from_bytes(data[4:8], byteorder="big", signed=True)

    # --- Apply scaling (LSB = 180 / 2^30) ---
    scale = 180.0 / (2**30)
    latitude = lat_raw * scale
    longitude = lon_raw * scale

    return {
        "Latitude (deg)": latitude,
        "Longitude (deg)": longitude,
        "Raw Latitude": lat_raw,
        "Raw Longitude": lon_raw,
        "Resolution (deg/LSB)": scale,
        "Note": "Positive latitude = North, Positive longitude = East"
    }

##############################################################################################################################
def decode_target_address(data: bytes) -> dict:
    if len(data) < 3:
        raise ValueError("Target Address requires 3 bytes (24 bits).")

    # Extract the 24-bit address (big-endian)
    icao_addr = int.from_bytes(data[0:3], byteorder="big", signed=False)

    # Format as 6-character hexadecimal string (uppercase, zero-padded)
    icao_hex = f"{icao_addr:06X}"

    return {
        "ICAO Address (hex)": icao_hex,
        "ICAO Address (decimal)": icao_addr,
        "Description": "Unique 24-bit aircraft address (emitter identifier)"
    }

##############################################################################################################################

def decode_time_of_message_reception_position(data: bytes) -> dict:
    
    if len(data) < 3:
        raise ValueError("Time of Message Reception for Position requires 3 bytes (24 bits).")

    # Extract 24-bit unsigned integer
    time_raw = int.from_bytes(data[0:3], byteorder="big", signed=False)

    # Convert to seconds (LSB = 1/128 s)
    time_seconds = time_raw / 128.0

    # Convert to hours, minutes, seconds (for readability)
    hours = int(time_seconds // 3600)
    minutes = int((time_seconds % 3600) // 60)
    seconds = time_seconds % 60

    return {
        "Raw Value": time_raw,
        "Time (s since midnight)": round(time_seconds, 6),
        "UTC Time (HH:MM:SS)": f"{hours:02d}:{minutes:02d}:{seconds:06.3f}",
        "Resolution (s/LSB)": 1 / 128,
        "Note": "Time resets to zero at midnight (UTC)"
    }


##############################################################################################################################

def decode_mode_3a_code(two_bytes: int) -> dict:

    if not (0 <= two_bytes <= 0xFFFF):
        raise ValueError("Value must be a 16-bit integer between 0 and 65535.")

    # Extract bits
    A4 = (two_bytes >> 12) & 0b1
    A2 = (two_bytes >> 11) & 0b1
    A1 = (two_bytes >> 10) & 0b1
    B4 = (two_bytes >> 9) & 0b1
    B2 = (two_bytes >> 8) & 0b1
    B1 = (two_bytes >> 7) & 0b1
    C4 = (two_bytes >> 6) & 0b1
    C2 = (two_bytes >> 5) & 0b1
    C1 = (two_bytes >> 4) & 0b1
    D4 = (two_bytes >> 3) & 0b1
    D2 = (two_bytes >> 2) & 0b1
    D1 = (two_bytes >> 1) & 0b1

    # Convert to octal digits
    A = (A4 << 2) | (A2 << 1) | A1
    B = (B4 << 2) | (B2 << 1) | B1
    C = (C4 << 2) | (C2 << 1) | C1
    D = (D4 << 2) | (D2 << 1) | D1

    mode3a_code = f"{A}{B}{C}{D}"

    return {
        "Raw": two_bytes,
        "A": A,
        "B": B,
        "C": C,
        "D": D,
        "Mode-3/A Code": mode3a_code
    }

##############################################################################################################################

def decode_flight_level(data: bytes) -> dict:
    
    if len(data) < 2:
        raise ValueError("Flight Level requires 2 bytes (16 bits).")

    # Read signed 16-bit value (two’s complement)
    fl_raw = int.from_bytes(data[0:2], byteorder="big", signed=True)

    # Apply LSB scaling: 1/4 Flight Level
    flight_level = fl_raw / 4.0

    # Convert to feet (1 FL = 100 ft)
    altitude_ft = flight_level * 100.0

    return {
        "Raw Value": fl_raw,
        "Flight Level (FL)": flight_level,
        "Altitude (ft)": altitude_ft,
        "Resolution (FL/LSB)": 0.25,
        "Description": "Barometric flight level (not QNH corrected)"
    }

##############################################################################################################################

def decode_target_identification(data: bytes) -> dict:
    
    if len(data) < 6:
        raise ValueError("Target Identification requires 6 bytes (48 bits).")

    # Convert to bit string
    bit_str = ''.join(f'{byte:08b}' for byte in data)
    chars = []

    # ICAO 6-bit character decoding table (Annex 10, Table 3-9)
    ia5_table = {
        0: "",   1: "A",  2: "B",  3: "C",  4: "D",  5: "E",  6: "F",  7: "G",
        8: "H",  9: "I", 10: "J", 11: "K", 12: "L", 13: "M", 14: "N", 15: "O",
        16: "P", 17: "Q", 18: "R", 19: "S", 20: "T", 21: "U", 22: "V", 23: "W",
        24: "X", 25: "Y", 26: "Z", 27: "",  28: "",  29: "",  30: "",  31: "",
        32: " ", 33: "",  34: "",  35: "",  36: "",  37: "",  38: "",  39: "",
        40: "0", 41: "1", 42: "2", 43: "3", 44: "4", 45: "5", 46: "6", 47: "7",
        48: "8", 49: "9", 50: "",  51: "",  52: "",  53: "",  54: "",  55: "",
        56: "",  57: "",  58: "",  59: "",  60: "",  61: "",  62: "",  63: ""
    }

    # Split the 48 bits into 8 groups of 6 bits
    for i in range(0, 48, 6):
        six_bits = int(bit_str[i:i + 6], 2)
        chars.append(ia5_table.get(six_bits, ""))

    target_id = ''.join(chars).strip()

    return {
        "Raw Bits": bit_str,
        "Target Identification": target_id,
        "Description": "Target callsign or registration (IA-5 encoded, 8 chars)"
    }


##############################################################################################################################
