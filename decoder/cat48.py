import numpy as np

import pandas as pd
import bitstring
from rich import print


def decode_dsi(data, pos):
    """Optimized inline version for DSI (fixed length)."""
    sac = data[pos : pos + 8].uint
    sic = data[pos + 8 : pos + 16].uint
    return {"SAC": sac, "SIC": sic}, 16


def decode_time_of_day(data, pos):
    """Optimized inline version for Time of Day (fixed length)."""
    time_of_day = data[pos : pos + 24].uint / 128.0
    return time_of_day, 24


def decode_target_desc(data, pos):
    """Optimized version using octet extraction and bit operations."""
    remaining = len(data) - pos
    if remaining < 8:
        raise ValueError("Data length must be at least 8 bits for Target Description")

    octet1 = data[pos : pos + 8].uint
    target_type_idx = (octet1 >> 5) & 0x7
    simulated = (octet1 >> 4) & 0x1
    rdp = (octet1 >> 3) & 0x1
    spi = (octet1 >> 2) & 0x1
    rab = (octet1 >> 1) & 0x1
    ext1 = octet1 & 0x1
    new_pos = pos + 8

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
        "Target_Type": target_types[target_type_idx],
        "Simulated": bool(simulated),
        "RDP": bool(rdp),
        "SPI": bool(spi),
        "RAB": bool(rab),
    }

    if not ext1:
        return target_desc, 8

    if remaining < 16:
        raise ValueError(
            "Data length must be at least 16 bits for extended Target Description"
        )

    octet2 = data[new_pos : new_pos + 8].uint
    test = (octet2 >> 7) & 0x1
    ext_range = (octet2 >> 6) & 0x1
    xpulse = (octet2 >> 5) & 0x1
    mil_em = (octet2 >> 4) & 0x1
    mil_id = (octet2 >> 3) & 0x1
    foe_fri_idx = (octet2 >> 1) & 0x3
    ext2 = octet2 & 0x1
    new_pos += 8

    foe_fri_table = [
        "No Mode 4 Interrogation",
        "Friendly Target",
        "Unknown Target",
        "No reply",
    ]
    target_desc.update(
        {
            "Test": bool(test),
            "Extended_Range": bool(ext_range),
            "XPulse": bool(xpulse),
            "Military_Emergency": bool(mil_em),
            "Military_Identification": bool(mil_id),
            "FOE/FRI": foe_fri_table[foe_fri_idx],
        }
    )

    if not ext2:
        return target_desc, 16

    if remaining < 24:
        raise ValueError(
            "Data length must be at least 24 bits for second extended Target Description"
        )

    octet3 = data[new_pos : new_pos + 8].uint
    ads_pop = (octet3 >> 7) & 0x1
    ads_val = (octet3 >> 6) & 0x1
    scn_pop = (octet3 >> 5) & 0x1
    scn_val = (octet3 >> 4) & 0x1
    pai_pop = (octet3 >> 3) & 0x1
    pai_val = (octet3 >> 2) & 0x1
    # Note: bits 1-0 not used in original; ext3 = (octet3 >> 0) & 0x1 but original uses data[23] which is LSB of octet3
    ext3 = octet3 & 0x1
    new_pos += 8

    target_desc.update(
        {
            "ADS-B Element_Populated": bool(ads_pop),
            "ADS-B Value": bool(ads_val),
            "SCN Element_Populated": bool(scn_pop),
            "SCN Value": bool(scn_val),
            "PAI Element_Populated": bool(pai_pop),
            "PAI Value": bool(pai_val),
        }
    )

    # No further extension in CAT48, consume 24 bits even if ext3
    return target_desc, 24


def decode_measure_position_slant_polar(data, pos):
    """Optimized inline version (fixed length)."""
    range_nm = data[pos : pos + 16].uint / 256.0
    theta = data[pos + 16 : pos + 32].uint * (360.0 / 65536.0)
    return {"Range NM": range_nm, "Theta": theta}, 32


def decode_mode3a_octal(data, pos):
    """Optimized inline version (fixed length, bug fixed for D field)."""
    octet1 = data[pos : pos + 8].uint
    octet2 = (
        data[pos + 8 : pos + 16].uint if len(data) >= pos + 16 else 0
    )  # Assume full
    validated = (octet1 >> 7) & 0x1
    garbled = (octet1 >> 6) & 0x1
    derived = (octet1 >> 5) & 0x1
    # Assuming spare bit at >>4, then A at bits 3-0 of octet1? Original slicing suggests A at pos+4:7 (bits4-6)
    # To match original slicing exactly without assuming byte split
    a = data[pos + 4 : pos + 7].uint
    b = data[pos + 7 : pos + 10].uint
    c = data[pos + 10 : pos + 13].uint
    d = data[pos + 13 : pos + 16].uint  # Fixed from original bug
    return {
        "Validated": bool(validated),
        "Garbled": bool(garbled),
        "Derived from reply": bool(derived),
        "A": a,
        "B": b,
        "C": c,
        "D": d,
    }, 16


def decode_fl_binary(data, pos):
    """Optimized inline version (fixed length)."""
    validated = data[pos]
    garbled = data[pos + 1]
    fl = data[pos + 2 : pos + 16].uint / 4.0
    return {
        "Validated": bool(validated),
        "Garbled": bool(garbled),
        "FL": fl,
    }, 16


def decode_radar_plot_characteristics(data, pos):
    """Optimized version using octet and bit operations."""
    remaining = len(data) - pos
    if remaining < 8:
        raise ValueError(
            "Data length must be at least 8 bits for Radar Plot Characteristics"
        )

    first_oct = data[pos : pos + 8].uint
    new_pos = pos + 8
    radar_plot_characteristics = {}

    # Match original bit positions (data[0] = MSB = >>7 &1, etc.)
    if (first_oct >> 7) & 0x1:
        if remaining < 16:
            raise ValueError("Insufficient bits for SSR plot runlength")
        ssr_run = data[new_pos : new_pos + 8].uint * 360.0 / 8192.0
        radar_plot_characteristics["SSR plot runlength"] = ssr_run
        new_pos += 8
    if (first_oct >> 6) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Number of received replies SSR")
        radar_plot_characteristics["Number of received replies SSR"] = data[
            new_pos : new_pos + 8
        ].uint
        new_pos += 8
    if (first_oct >> 5) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Amplitude of (M)SSR reply")
        radar_plot_characteristics["Amplitude of (M)SSR reply"] = data[
            new_pos : new_pos + 8
        ].uint
        new_pos += 8
    if (first_oct >> 4) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Primary Plot Runlength")
        radar_plot_characteristics["Primary Plot Runlength (deg)"] = (
            data[new_pos : new_pos + 8].uint * 360.0 / 8192.0
        )
        new_pos += 8
    if (first_oct >> 3) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Amplitude of Primary Plot")
        radar_plot_characteristics["Amplitude of Primary Plot (dBm)"] = data[
            new_pos : new_pos + 8
        ].uint
        new_pos += 8
    if (first_oct >> 2) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Range (PSR-SSR)")
        radar_plot_characteristics["Range (PSR-SSR)"] = (
            data[new_pos : new_pos + 8].uint / 256.0
        )
        new_pos += 8
    if (first_oct >> 1) & 0x1:
        if remaining < new_pos - pos + 8:
            raise ValueError("Insufficient bits for Azimuth (PSR-SSR)")
        radar_plot_characteristics["Azimuth (PSR-SSR)"] = (
            data[new_pos : new_pos + 8].uint * 360.0 / 16384.0
        )
        new_pos += 8

    return radar_plot_characteristics, new_pos - pos


def decode_aircraft_address(data, pos):
    """Optimized inline version (fixed length)."""
    address_int = data[pos : pos + 24].uint
    address = f"{address_int:06X}"
    return address, 24


def decode_aircraft_id(data, pos):
    """Optimized version with unrolled loop for character decoding (unrolling small loop for speed)."""
    if len(data) - pos < 48:
        raise ValueError("Data length must be at least 48 bits for Aircraft ID")
    chars = []
    for i in range(8):
        start_bit = pos + i * 6
        char_code = data[start_bit : start_bit + 6].uint
        if char_code == 0:
            chars.append(" ")
        elif 1 <= char_code <= 26:
            chars.append(chr(char_code + 64))  # A-Z
        elif 48 <= char_code <= 57:
            chars.append(chr(char_code))  # 0-9
        else:
            chars.append(" ")  # Invalid
    aircraft_id = "".join(chars).rstrip()
    return aircraft_id, 48


def decode_BDS_4_0(data, pos):
    if len(data) - pos < 56:
        raise ValueError("Data length must be at least 56 bits for BDS 4,0")
    status_mcp = data[pos]
    mcp_alt = data[pos + 1 : pos + 13].uint / 16.0
    status_fms = data[pos + 13]
    fms_alt = data[pos + 14 : pos + 26].uint / 16.0
    status_bar = data[pos + 26]
    bar_press = data[pos + 27 : pos + 39].uint * 0.1 + 800.0
    # Bits 39-46 unused?
    status_mcp_mode = data[pos + 47]
    vnav = data[pos + 48]
    alt_hold = data[pos + 49]
    approach = data[pos + 50]
    # Bits 51-52 unused?
    status_target = data[pos + 53]
    target_alt_idx = data[pos + 54 : pos + 56].uint
    target_alt_source = ["Unknown", "Aircraft Altitude", "MCP/FCU", "FMS"][
        target_alt_idx
    ]
    bds_4_0 = {
        "Status MCP/FCU": bool(status_mcp),
        "MCP/FCU Selected Altitude": mcp_alt,
        "Status FMS": bool(status_fms),
        "FMS Selected Altitude": fms_alt,
        "Status Barometric Reference": bool(status_bar),
        "Barometric Pressure Setting": bar_press,
        "Status MCP/FCU Mode": bool(status_mcp_mode),
        "VNAV Mode": bool(vnav),
        "ALT Hold Mode": bool(alt_hold),
        "Approach Mode": bool(approach),
        "Status Target Source": bool(status_target),
        "Target Alt Source": target_alt_source,
    }
    return bds_4_0, 56


def decode_BDS_5_0(data, pos):
    if len(data) - pos < 56:
        raise ValueError("Data length must be at least 56 bits for BDS 5,0")
    status_roll = data[pos]
    roll_angle = data[pos + 1 : pos + 11].int * (45 / 256)
    status_track = data[pos + 11]
    track_angle = data[pos + 12 : pos + 23].int * (90 / 512)
    status_gs = data[pos + 23]
    gs = data[pos + 24 : pos + 34].uint * 2.0
    status_ta_rate = data[pos + 34]
    ta_rate = data[pos + 35 : pos + 45].int * (8 / 256)
    status_tas = data[pos + 45]
    tas = data[pos + 46 : pos + 56].uint * 2.0
    bds_5_0 = {
        "Status Roll Angle": bool(status_roll),
        "Roll Angle": roll_angle,
        "Status Track Angle": bool(status_track),
        "Track Angle": track_angle,
        "Status Ground Speed": bool(status_gs),
        "Ground Speed": gs,
        "Status Track Angle Rate": bool(status_ta_rate),
        "Track Angle Rate": ta_rate,
        "Status TAS": bool(status_tas),
        "TAS": tas,
    }
    return bds_5_0, 56


def decode_BDS_6_0(data, pos):
    if len(data) - pos < 56:
        raise ValueError("Data length must be at least 56 bits for BDS 6,0")
    status_mag_h = data[pos]
    mag_h = data[pos + 1 : pos + 12].int * (90 / 512)
    status_ias = data[pos + 12]
    ias = data[pos + 13 : pos + 23].uint * 1.0
    status_mach = data[pos + 23]
    mach = data[pos + 24 : pos + 34].uint * (2.048 / 512)
    status_bar_rate = data[pos + 34]
    bar_rate = data[pos + 35 : pos + 45].int * 32.0
    status_inert_vv = data[pos + 45]
    inert_vv = data[pos + 46 : pos + 56].int * 32.0
    bds_6_0 = {
        "Status Magnetic Heading": bool(status_mag_h),
        "Magnetic Heading": mag_h,
        "Status IAS": bool(status_ias),
        "IAS": ias,
        "Status Mach": bool(status_mach),
        "Mach": mach,
        "Status Barometric Altitude Rate": bool(status_bar_rate),
        "Barometric Altitude Rate": bar_rate,
        "Status Inertial Vertical Velocity": bool(status_inert_vv),
        "Inertial Vertical Velocity": inert_vv,
    }
    return bds_6_0, 56


mapper_bds = [
    None,
    None,
    None,
    None,
    [("4,0", decode_BDS_4_0)],
    [("5,0", decode_BDS_5_0)],
    [("6,0", decode_BDS_6_0)],
]


def decode_mode_s_mb_data(data, pos):
    if len(data) - pos < 72:
        raise ValueError("Data length must be at least 72 bits for Mode S MB Data")
    repetition = data[pos : pos + 8].uint
    required_bits = 8 + repetition * 64  # 56 data + 8 BDS code
    if len(data) - pos < required_bits:
        raise ValueError(
            f"Data length must be at least {required_bits} bits for {repetition} Mode S MB Data blocks"
        )
    bds = {"Repetition": repetition}
    start = pos + 8
    for i in range(repetition):
        block_start = start
        bda1 = data[block_start + 56 : block_start + 60].uint  # BDS1,2 bits 56-59
        bda2 = data[
            block_start + 60 : block_start + 64
        ].uint  # BDS1,2 bits 60-63, but original +56:56+4 and +4:+8
        if bda1 < 4:
            start += 64
            continue
        if bda1 >= len(mapper_bds) or mapper_bds[bda1] is None:
            print(f"No decoder implemented for BDS {bda1},{bda2}")
            start += 64
            continue
        bds_entry = mapper_bds[bda1]
        if bda2 >= len(bds_entry) or bds_entry[bda2] is None:
            print(f"No decoder implemented for BDS {bda1},{bda2}")
            start += 64
            continue
        bds_name, bds_decoder = bds_entry[bda2]
        decoded_bds, _ = bds_decoder(
            data, block_start + 8
        )  # Data starts after 8-bit header per block? Original: data[start + 8 : start + 8 + 56]
        bds[bds_name] = decoded_bds
        start += 64  # 56 + 8

    return bds, required_bits - (
        start - pos - required_bits
    )  # Actually, total = 8 + rep*64
    # Wait, return total consumed: 8 + rep*64
    return bds, 8 + repetition * 64


def decode_track_number(data, pos):
    if len(data) - pos < 16:
        raise ValueError("Data length must be at least 16 bits for Track Number")
    track_num = data[pos + 4 : pos + 16].uint  # Bits 0-3 unused?
    return track_num, 16


def decode_calculated_pos_in_cart(data, pos):
    if len(data) - pos < 32:
        raise ValueError(
            "Data length must be at least 32 bits for Calculated Position in Cartesian Coordinates"
        )
    # Placeholder: original returns None
    return None, 32


def decode_calc_track_vel_polar(data, pos):
    if len(data) - pos < 32:
        raise ValueError(
            "Data length must be at least 32 bits for Calculated Track Velocity in Polar Representation"
        )
    groundspeed = data[pos : pos + 16].uint / (2**14)
    heading = data[pos + 16 : pos + 32].uint * (360.0 / (2**16))
    return {
        "Groundspeed (NM/s)": groundspeed,
        "Heading (deg)": heading,
    }, 32


def decode_track_status(data, pos):
    if len(data) - pos < 8:
        raise ValueError("Data length must be at least 8 bits for Track Status")
    conf_vt = data[pos]
    type_sensor_idx = data[pos + 1 : pos + 3].uint
    dou = data[pos + 3]
    man_h = data[pos + 4]
    climb_desc_idx = data[pos + 5 : pos + 7].uint
    ext = data[pos + 7]
    track_status = {
        "ConfVTent": bool(conf_vt),
        "Type of Sensor": [
            "Combined Track",
            "PSR Track",
            "SSR/Mode S Track",
            "Invalid",
        ][type_sensor_idx],
        "DOU": bool(dou),
        "Manoeuver detection Horizontal": bool(man_h),
        "Climbing/Descending": ["Maintaining", "Climbing", "Descending", "Unknown"][
            climb_desc_idx
        ],
    }
    bits = 8
    if ext:
        if len(data) - pos < 16:
            raise ValueError("Insufficient bits for extended Track Status")
        track_status.update(
            {
                "End of Track": bool(data[pos + 8]),
                "Ghost": bool(data[pos + 9]),
                "SUP": bool(data[pos + 10]),
                "TCC": bool(data[pos + 11]),
            }
        )
        bits = 16

    return track_status, bits


def decode_track_quality(data, pos):
    if len(data) - pos < 32:
        raise ValueError("Data length must be at least 32 bits for Track Quality")
    # Placeholder: original returns None
    return None, 32


def decode_warning_error(data, pos):
    if len(data) - pos < 8:
        raise ValueError("Data length must be at least 8 bits for Warning/Error")
    codes = []
    current_pos = pos
    while data[current_pos + 7]:  # FX bit
        code = data[current_pos : current_pos + 7].uint
        codes.append(code)
        current_pos += 8
    bits_consumed = current_pos - pos
    return codes, bits_consumed


def decode_mode_3a_code_conf(data, pos):
    if len(data) - pos < 16:
        raise ValueError(
            "Data length must be at least 16 bits for Mode 3/A Code Confidence Indicator"
        )
    # Placeholder: original returns None
    return None, 16


def decode_mode_c_code_conf(data, pos):
    if len(data) - pos < 32:
        raise ValueError(
            "Data length must be at least 32 bits for Mode C Code and Confidence Indicator"
        )
    # Placeholder: original returns None
    return None, 32


def decode_height_3d_radar(data, pos):
    if len(data) - pos < 16:
        raise ValueError(
            "Data length must be at least 16 bits for Height Measured by 3D Radar"
        )
    # Placeholder: original returns None
    return None, 16


def decode_radial_doppler_speed(data, pos):
    # Original is broken: return None, 8 * data[0] + 56 * data[1] + 8 — invalid
    # Assuming fixed length or placeholder; for now, consume 16 bits or as is.
    if len(data) - pos < 16:
        raise ValueError(
            "Data length must be at least 16 bits for Radial Doppler Speed"
        )
    # Placeholder
    return None, 16


def decode_com_acas_cap_fl_st(data, pos):
    if len(data) - pos < 16:
        raise ValueError(
            "Data length must be at least 16 bits for Communications / ACAS Capability and Flight Status"
        )
    comm_cap_idx = data[pos : pos + 3].uint
    flight_stat_idx = data[pos + 3 : pos + 6].uint
    si_ii = data[pos + 6]
    # Bit 7 unused?
    mode_s_ssc = data[pos + 8]
    alt_rep = data[pos + 9]
    ac_id_cap = data[pos + 10]
    acas_stat = data[pos + 11]
    hybrid = data[pos + 12]
    ta_ra = data[pos + 13]
    mops_idx = data[pos + 14 : pos + 16].uint
    result = {
        "Communications Capability": [
            "No com",
            "Comm A and B",
            "Comm A,B and Uplink ELM",
            "Comm A,B and Uplink ELM and Downlink",
            "Level 5 Transponder Capability",
            "Not assigned",
            "Not assigned",
            "Not assigned",
        ][comm_cap_idx],
        "Flight Status": [
            "No alert, no SPI, airborne",
            "No alert, no SPI, on ground",
            "Alert, no SPI, airborne",
            "Alert, no SPI, on ground",
            "Alert, SPI, airborne or ground",
            "No alert, SPI, airborne or ground",
            "Not assigned",
            "Unknown",
        ][flight_stat_idx],
        "SI/II": "II" if si_ii else "SI",
        "Mode S Specific Service Capability": bool(mode_s_ssc),
        "Altitude Reporting Capability": bool(alt_rep),
        "Aircraft Identification Capability": bool(ac_id_cap),
        "ACAS Status": "Operational" if acas_stat else "Failed or Standby",
        "Hybrid Surveillance": bool(hybrid),
        "TA/RA": "TA and RA" if ta_ra else "TA",
        "Applicable MOPS Doc": [
            "RTCA DO-185",
            "RTCA DO-185A",
            "RTCA DO-185B",
            "Reserved For Future Versions",
        ][mops_idx],
    }
    return result, 16


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
    ("Track Number", decode_track_number),
    ("Calculated Position in Cartesian Coords", decode_calculated_pos_in_cart),
    ("Calculated Track Velocity in Polar Representation", decode_calc_track_vel_polar),
    ("Track Status", decode_track_status),
    ("Track Quality", decode_track_quality),
    ("Warning/Error", decode_warning_error),
    ("Mode-3/A Code Confidence Indicator", decode_mode_3a_code_conf),
    ("Mode-C Code and Confidence Indicator", decode_mode_c_code_conf),
    ("Height Measured by 3D Radar", decode_height_3d_radar),
    ("Radial Doppler Speed", decode_radial_doppler_speed),
    ("Communications / ACAS Capability and Flight Status", decode_com_acas_cap_fl_st),
]


def decode_cat48(cat, len_bytes, data: bitstring.BitArray):
    """Optimized version using position tracking to avoid repeated slicing."""
    if cat != 48:
        raise ValueError("Category must be 48 for DecodeCat48")
    # Assume data starts from FSPEC (after CAT and LEN octets). Original start=8, but logic is on pos=0.
    # Adjust pos to 0 for simplicity, matching original data[:7] etc.
    pos = 0
    # FSPEC Block 1: bits 0-6 items, bit7 FX1
    fspec_block_1 = [data[pos + i] for i in range(7)]
    fx1 = data[pos + 7]
    pos += 8  # Advance past first octet

    data_items_to_decode = [i for i, present in enumerate(fspec_block_1) if present]

    if fx1:
        # FSPEC Block 2: bits 8-14 items (offset +7), bit15 FX2
        fspec_block_2 = [data[pos + i] for i in range(7)]
        fx2 = data[pos + 7]
        pos += 8
        data_items_to_decode += [
            i + 7 for i, present in enumerate(fspec_block_2) if present
        ]

        if fx2:
            # FSPEC Block 3: bits 16-22 items (+14), bit23 FX3
            fspec_block_3 = [data[pos + i] for i in range(7)]
            fx3 = data[pos + 7]
            pos += 8
            data_items_to_decode += [
                i + 14 for i, present in enumerate(fspec_block_3) if present
            ]

            if fx3:
                # FSPEC Block 4: bits 24-30 items (+21), no FX4 in CAT48
                fspec_block_4 = [data[pos + i] for i in range(7)]
                pos += 8  # Consume the octet, even if no FX
                data_items_to_decode += [
                    i + 21 for i, present in enumerate(fspec_block_4) if present
                ]

    decoded = {}
    for item in data_items_to_decode:
        if item >= len(mapper):
            continue  # Skip undefined
        item_name, decoder = mapper[item]
        result, step = decoder(data, pos)
        decoded[item_name] = result
        pos += step

    return decoded
