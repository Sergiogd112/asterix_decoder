import numpy as np

import pandas as pd
import bitstring
from rich import print

def decode_dsi(data):
    """Decode Data Source Identifier (DSI) from a binary data string.

    Decodes the SAC (System Area Code) and SIC (System Identification Code) fields
    that comprise the Data Source Identifier in ASTERIX Category 48.

    Args:
        data (str): Binary string containing the DSI data. Must be at least 8 bits long.

    Returns:
        tuple: A tuple containing:
            - dsi (tuple): A tuple with (SAC, SIC) values
            - int: Number of bits processed (16)

    Raises:
        ValueError: If input data length is less than 8 bits
    """
    if len(data) < 8:
        raise ValueError("Data length must be at least 8 bits for DSI")
    sac = data[0:8]
    sac = data[8:16]
    dsi = (sac, sac)
    return dsi, 16


def decode_time_of_day(data):
    """Decodes the Time of Day from the given data.

    Time of Day in Cat 48 represents the absolute time, expressed as UTC,
    that has elapsed since last midnight, measured in 128ths (2^-7) of a second.

    Parameters:
        data (BitArray): Binary data containing Time of Day field. Must be at least 24 bits long.

    Returns:
        tuple: A tuple containing:
            - float: Time of day in seconds since last midnight
            - int: Number of bits processed (24)

    Raises:
        ValueError: If the input data length is less than 24 bits.
    """
    if len(data) < 24:
        raise ValueError("Data length must be at least 24 bits for Time of Day")
    time_of_day = data[0:24].uint / 2.0**7
    return time_of_day, 24


def decode_target_desc(data):
    """Decode Target Description data for CAT048.

    This function decodes target description data according to EUROCONTROL ASTERIX CAT048
    specification. It processes up to three levels of field extensions providing detailed
    target information.

    Args:
        data (BitArray): Bit array containing the target description data. Must be at least
            8 bits long, and longer if field extensions are present.

    Returns:
        tuple: A tuple containing:
            - dict: Decoded target description with following possible keys:
                * Target_Type (str): Type of target detection
                * Simulated (bool): Simulated target report
                * RDP (bool): RDP chain indicator
                * SPI (bool): Special Position Identification
                * RAB (bool): Report from aircraft or field monitor
                * Test (bool): Test target indicator (if extended)
                * Extended_Range (bool): Extended range indicator (if extended)
                * XPulse (bool): X-pulse from Mode 2 (if extended)
                * Military_Emergency (bool): Military emergency indicator (if extended)
                * Military_Identification (bool): Military identification (if extended)
                * FOE/FRI (str): Mode 4 Friend/Foe status (if extended)
                * ADS-B Element_Populated (bool): ADS-B data availability (if second extension)
                * ADS-B Value (bool): ADS-B status (if second extension)
                * SCN Element_Populated (bool): SCN data availability (if second extension)
                * SCN Value (bool): SCN status (if second extension)
                * PAI Element_Populated (bool): PAI data availability (if second extension)
                * PAI Value (bool): PAI status (if second extension)
            - int: Number of bits processed

    Raises:
        ValueError: If the input data length is insufficient for the required fields and
            their extensions.
    """
    if len(data) < 8:
        raise ValueError("Data length must be at least 8 bits for Target Description")
    target_types = [
        "No detection",
        "Single PSR detection",
        "Single SSR detection",
        "SSR + PSR detection",
        "Single Mode S All-Call detection",
        "Single Mode S Roll-Call detection",
        "Mode S All-Call + PSR",
        "Mode S Roll-Call + PSR",
    ]
    target_desc = {
        "Target_Type": target_types[data[0:3].uint],
        "Simulated": data[3],
        "RDP": data[4],
        "SPI": data[5],
        "RAB": data[6],
    }

    field_extension = data[7]
    step = 8
    if not field_extension:
        return target_desc, step
    if len(data) < 16:
        raise ValueError(
            "Data length must be at least 16 bits for extended Target Description"
        )
    foe_fri_table = [
        "No Mode 4 Interrogation",
        "Friendly Target",
        "Unknown Target",
        "No reply",
    ]
    target_desc.update(
        {
            "Test": data[8],
            "Extended_Range": data[9],
            "XPulse": data[10],
            "Military_Emergency": data[11],
            "Military_Identification": data[12],
            "FOE/FRI": foe_fri_table[data[13:15].uint],
        }
    )
    field_extension_2 = data[15]
    step += 8
    if not field_extension_2:
        return target_desc, step
    if len(data) < 24:
        raise ValueError(
            "Data length must be at least 24 bits for second extended Target Description"
        )
    target_desc.update(
        {
            "ADS-B Element_Populated": data[16],
            "ADS-B Value": data[17],
            "SCN Element_Populated": data[18],
            "SCN Value": data[19],
            "PAI Element_Populated": data[20],
            "PAI Value": data[21],
        }
    )
    field_extension_3 = data[23]

    step += 8
    if not field_extension_3:
        return target_desc, step
    print("No further extension defined in CAT48 for Target Description")
    return target_desc, step


def decode_measure_position_slant_polar(data):
    """Decode Measured Position in Slant Polar Coordinates from binary data.
    This function decodes the Measured Position in Slant Polar Coordinates data item
    from ASTERIX Category 48. It extracts the Range and Theta values from the provided
    binary data.
    Args:
        data (BitArray): Binary string containing the Measured Position in Slant Polar Coordinates data.
                          Must be at least 32 bits long.
    Returns:
        tuple: A tuple containing:
            - dict: A dictionary with the following keys:
                * 'Range NM': Range in nautical miles (float)
                * 'Theta': Angle in degrees (float)
            - int: Number of bits processed (32)
    Raises:
        ValueError: If input data length is less than 32 bits
    """
    if len(data) < 32:
        raise ValueError(
            "Data length must be at least 32 bits for Measured Position in Slant Polar Coordinates"
        )
    return {
        "Range NM": data[0:16].uint / 256.0,
        "Theta": data[16:24].uint * (360.0 / 2**16),
    }, 32


def decode_mode3a_octal(data):
    """Decode Mode 3/A Octal from binary data.
    This function decodes the Mode 3/A Octal data item from ASTERIX Category 48.
    It extracts the Validated, Garbled, Derived from reply flags and the A, B, C, D
    octal digits from the provided binary data.
    Args:
        data (BitArray): Binary string containing the Mode 3/A Octal data.
                          Must be at least 16 bits long.
    Returns:
        tuple: A tuple containing:
            - dict: A dictionary with the following keys:
                * 'Validated' (bool): Validated flag
                * 'Garbled' (bool): Garbled flag
                * 'Derived from reply' (bool): Derived from reply flag
                * 'A' (int): First octal digit
                * 'B' (int): Second octal digit
                * 'C' (int): Third octal digit
                * 'D' (int): Fourth octal digit
            - int: Number of bits processed (16)
    Raises:
        ValueError: If input data length is less than 16 bits
    """
    if len(data) < 16:
        raise ValueError("Data length must be at least 16 bits for Mode 3/A Octal")
    return {
        "Validated": data[0],
        "Garbled": data[1],
        "Derived from reply": data[2],
        "A": (data[3:7].uint),
        "B": (data[7:11].uint),
        "C": (data[11:16].uint),
        "D": (data[16:21].uint),
    }, 16


def decode_fl_binary(data):
    """Decode Flight Level (Binary) from binary data.
    This function decodes the Flight Level (Binary) data item from ASTERIX Category 48.
    It extracts the Validated, Garbled flags and the Flight Level value from the provided
    binary data.
    Args:
        data (BitArray): Binary string containing the Flight Level (Binary) data.
                          Must be at least 16 bits long.
    Return:
        tuple: A tuple containing
            - dict: A dictionary with the following keys:
                * 'Validated' (bool): Validated Flag,
                * 'Garbled' (bool): Garbled Flag
                * 'FL' (float): Flight Level in hundreds of feet
            - int: Number of bits processed
    Raises:
        ValueError: If input data length is less than 16 bits
    """

    if len(data) < 16:
        raise ValueError(
            "Data length must be at least 16 bits for Flight Level (Binary)"
        )
    return {
        "Validated": data[0],
        "Garbled": data[1],
        "FL": data[2:16].uint / 4.0,
    }, 16


def decode_radar_plot_characteristics(data):
    """Decode Radar Plot Characteristics from binary data.
    This function decodes the Radar Plot Characteristics data item from ASTERIX Category 48.
    It extracts various radar plot characteristics based on the presence flags in the
    provided binary data.
    Args:
        data (BitArray): Binary string containing the Radar Plot Characteristics data.
                          Must be at least 8 bits long, and longer if presence flags are set.
    Returns:
        tuple: A tuple containing:
            - dict or None: A dictionary with the following possible keys if present:
                * 'SSR plot runlength' (float): SSR plot runlength in degrees
                * 'Number of received replies SSR' (int): Number of received SSR replies
                * 'Amplitude of (M)SSR reply' (int): Amplitude of (M)SSR reply
                * 'Primary Plot Runlength' (float): Primary plot runlength in degrees
                * 'Amplitude of Primary Plot' (int): Amplitude of primary plot
                * 'Range (PSR-SSR)' (float): Range difference between PSR and SSR in nautical miles
                * 'Azimuth (PSR-SSR)' (float): Azimuth difference between PSR and SSR in degrees
            - int: Number of bits processed
    Raises:
        ValueError: If input data length is less than 8 bits
    """
    if len(data) < 8:
        raise ValueError(
            "Data length must be at least 8 bits for Radar Plot Characteristics"
        )
    # if not data[7]:
    #     return None, 8
    radar_plot_characteristics = {}
    current = 8
    if data[0]:
        radar_plot_characteristics["SSR plot runlength"] = (
            data[current : current + 8].uint * 360.0 / 2**13
        )
        current += 8
    if data[1]:
        radar_plot_characteristics["Number of received replies SSR"] = data[
            current : current + 8
        ].uint
        current += 8
    if data[2]:
        radar_plot_characteristics["Amplitude of (M)SSR reply"] = data[
            current : current + 8
        ].uint
        current += 8
    if data[3]:
        radar_plot_characteristics["Primary Plot Runlength"] = (
            data[current : current + 8].uint * 360.0 / 2**13
        )
        current += 8
    if data[4]:
        radar_plot_characteristics["Amplitude of Primary Plot"] = data[
            current : current + 8
        ].uint
        current += 8
    if data[5]:
        radar_plot_characteristics["Range (PSR-SSR)"] = (
            data[current : current + 8].uint / 256.0
        )
        current += 8
    if data[6]:
        radar_plot_characteristics["Azimuth (PSR-SSR)"] = (
            data[current : current + 8].uint * 360.0 / 2**14
        )
        current += 8
    return radar_plot_characteristics, current

def decode_aircraft_address(data):
    """Decode Aircraft Address from binary data.
    This function decodes the Aircraft Address data item from ASTERIX Category 48.
    It extracts the 24-bit aircraft address from the provided binary data.
    Args:
        data (BitArray): Binary string containing the Aircraft Address data.
                          Must be at least 24 bits long.
    Returns:
        tuple: A tuple containing:
            - str: Aircraft address as a hexadecimal string
            - int: Number of bits processed (24)
    Raises:
        ValueError: If input data length is less than 24 bits
    """
    if len(data) < 24:
        raise ValueError("Data length must be at least 24 bits for Aircraft Address")
    address = f"{data[0:24].uint:06X}"
    return address, 24

def decode_aircraft_id(data):
    """Decode Aircraft ID from binary data.
    This function decodes the Aircraft ID data item from ASTERIX Category 48.
    It extracts the 8-character aircraft identification from the provided binary data.
    Args:
        data (BitArray): Binary string containing the Aircraft ID data.
                          Must be at least 48 bits long.
    Returns:
        tuple: A tuple containing:
            - str: Aircraft ID as an 8-character string
            - int: Number of bits processed (48)
    Raises:
        ValueError: If input data length is less than 48 bits
    """
    if len(data) < 48:
        raise ValueError("Data length must be at least 48 bits for Aircraft ID")
    chars = []
    for i in range(8):
        char_code = data[i * 6 : (i + 1) * 6].uint
        if char_code == 0:
            chars.append(" ")
        elif 1 <= char_code <= 26:
            chars.append(chr(char_code + 64))  # A-Z
        elif 48 <= char_code <= 57:
            chars.append(chr(char_code))  # 0-9
        else:
            chars.append(" ")  # Invalid character code
    aircraft_id = "".join(chars).rstrip()
    return aircraft_id, 48

def decode_mode_s_mb_data(data):
    if len(data) < 72:
        raise ValueError("Data length must be at least 72 bits for Mode S MB Data")
    repetition = data[0:8].uint
    return {"Repetition": repetition}, 72

mapper = [
    ("DSI", decode_dsi),
    ("Time of Day", decode_time_of_day),
    ("Target Description", decode_target_desc),
    (
        "Measured Position in Slant Polar Coordinates",
        decode_measure_position_slant_polar,
    ),
    ("Mode 3/A Octal", decode_mode3a_octal),
    ("Flight Level (Binary)", decode_fl_binary),
    ("Radar Plot Characteristics", decode_radar_plot_characteristics),
    ("Aircraft Address", decode_aircraft_address),
    ("Aircraft ID", decode_aircraft_id),
    ("Mode S MB Data", decode_mode_s_mb_data),
]


def decode_cat48(cat, len, data: bitstring.BitArray):
    if cat != 48:
        raise ValueError("Category must be 48 for DecodeCat48")
    start = 8
    data = bitstring.BitArray(bin=data)
    fspec_block_1 = data[:7]
    fx1 = data[7]
    data_items_to_decode = [i for i, bit in enumerate(fspec_block_1) if bit is True]
    if fx1:
        fspec_block_2 = data[8:15]
        fx2 = data[15]
        data_items_to_decode += [
            i + 7 for i, bit in enumerate(fspec_block_2) if bit is True
        ]
        start += 8
        if fx2:
            fspec_block_3 = data[16:23]
            fx3 = data[23]
            data_items_to_decode += [
                i + 14 for i, bit in enumerate(fspec_block_3) if bit is True
            ]
            start += 8
            if fx3:
                fspec_block_4 = data[24:31]
                data_items_to_decode += [
                    i + 21 for i, bit in enumerate(fspec_block_4) if bit is True
                ]
                start += 8
    else:
        fspec_block_2 = None
        fspec_block_3 = None
        fspec_block_4 = None
    decoded = {}
    for item in data_items_to_decode[:9]:
        result, step = mapper[item][1](data[start:])
        decoded[mapper[item][0]] = result
        start += step
    print("Decoded CAT48 Data Items:")
    print(decoded)
    return data_items_to_decode
