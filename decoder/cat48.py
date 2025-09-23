import numpy as np

import pandas as pd
import bitstring


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


mapper = [
    ("DSI", decode_dsi),
    ("Time of Day", decode_time_of_day),
    ("Target Description", decode_target_desc),
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
    for item in data_items_to_decode[:3]:
        result, step = mapper[item][1](data[start:])
        decoded[mapper[item][0]] = result
        start += step
    print(f"Decoded CAT48 Data Items: {decoded}")
    return data_items_to_decode
