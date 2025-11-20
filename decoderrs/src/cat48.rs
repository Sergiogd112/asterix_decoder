use bitvec::prelude::*;
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct Cat48 {
    pub category: u8,
    pub data_source_identifier: Option<DataSourceIdentifier>,
    pub time_of_day: Option<f64>,
    pub target_desc: Option<TargetDesc>,
    pub slant_polar: Option<SlantPolar>,
    pub mode3a_code: Option<String>,
    pub flight_level: Option<f64>,
}

#[derive(Debug, Serialize)]
pub struct DataSourceIdentifier {
    pub sac: u8,
    pub sic: u8,
}

#[derive(Debug, Serialize)]
pub struct TargetDesc {
    pub target_type: String,
    pub simulated: bool,
    pub rdp: bool,
    pub spi: bool,
    pub rab: bool,
    pub test: Option<bool>,
    pub extended_range: Option<bool>,
    pub xpulse: Option<bool>,
    pub military_emergency: Option<bool>,
    pub military_identification: Option<bool>,
    pub foe_fri: Option<String>,
    pub ads_b_element_populated: Option<bool>,
    pub ads_b_value: Option<bool>,
    pub scn_element_populated: Option<bool>,
    pub scn_value: Option<bool>,
    pub pai_element_populated: Option<bool>,
    pub pai_value: Option<bool>,
}

#[derive(Debug, Serialize)]
pub struct SlantPolar {
    pub range_nm: f64,
    pub range_m: f64,
    pub theta: f64,
}

fn decode_target_desc(data: &BitSlice<u8, Msb0>) -> (TargetDesc, usize) {
    let mut pos = 0;
    let octet1 = data[pos..pos + 8].load::<u8>();
    let target_type_idx = (octet1 >> 5) & 0x7;
    let simulated = (octet1 >> 4) & 0x1 != 0;
    let rdp = (octet1 >> 3) & 0x1 != 0;
    let spi = (octet1 >> 2) & 0x1 != 0;
    let rab = (octet1 >> 1) & 0x1 != 0;
    let ext1 = (octet1 & 0x1) != 0;
    pos += 8;

    let target_types = [
        "No detection",
        "Single PSR detection",
        "Single SSR detection",
        "SSR + PSR detection",
        "Single Mode S All-Call detection",
        "Single Mode S Roll-Call detection",
        "Mode S All-Call + PSR",
        "Mode S Roll-Call + PSR",
    ];
    let mut target_desc = TargetDesc {
        target_type: target_types[target_type_idx as usize].to_string(),
        simulated,
        rdp,
        spi,
        rab,
        test: None,
        extended_range: None,
        xpulse: None,
        military_emergency: None,
        military_identification: None,
        foe_fri: None,
        ads_b_element_populated: None,
        ads_b_value: None,
        scn_element_populated: None,
        scn_value: None,
        pai_element_populated: None,
        pai_value: None,
    };

    if !ext1 {
        return (target_desc, 8);
    }

    let octet2 = data[pos..pos + 8].load::<u8>();
    target_desc.test = Some((octet2 >> 7) & 0x1 != 0);
    target_desc.extended_range = Some((octet2 >> 6) & 0x1 != 0);
    target_desc.xpulse = Some((octet2 >> 5) & 0x1 != 0);
    target_desc.military_emergency = Some((octet2 >> 4) & 0x1 != 0);
    target_desc.military_identification = Some((octet2 >> 3) & 0x1 != 0);
    let foe_fri_idx = (octet2 >> 1) & 0x3;
    let ext2 = (octet2 & 0x1) != 0;
    pos += 8;

    let foe_fri_table = [
        "No Mode 4 Interrogation",
        "Friendly Target",
        "Unknown Target",
        "No reply",
    ];
    target_desc.foe_fri = Some(foe_fri_table[foe_fri_idx as usize].to_string());

    if !ext2 {
        return (target_desc, 16);
    }

    let octet3 = data[pos..pos + 8].load::<u8>();
    target_desc.ads_b_element_populated = Some((octet3 >> 7) & 0x1 != 0);
    target_desc.ads_b_value = Some((octet3 >> 6) & 0x1 != 0);
    target_desc.scn_element_populated = Some((octet3 >> 5) & 0x1 != 0);
    target_desc.scn_value = Some((octet3 >> 4) & 0x1 != 0);
    target_desc.pai_element_populated = Some((octet3 >> 3) & 0x1 != 0);
    target_desc.pai_value = Some((octet3 >> 2) & 0x1 != 0);
    pos += 8;

    (target_desc, 24)
}

fn decode_slant_polar(data: &BitSlice<u8, Msb0>) -> (SlantPolar, usize) {
    let range_nm = data[0..16].load::<u16>() as f64 / 256.0;
    let theta = data[16..32].load::<u16>() as f64 * (360.0 / 65536.0);
    let slant_polar = SlantPolar {
        range_nm,
        range_m: range_nm * 1852.0,
        theta,
    };
    (slant_polar, 32)
}

fn decode_mode3a_octal(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let a = data[4..7].load::<u8>();
    let b = data[7..10].load::<u8>();
    let c = data[10..13].load::<u8>();
    let d = data[13..16].load::<u8>();
    let code = format!("{}{}{}{}", a, b, c, d);
    (code, 16)
}

fn decode_fl_binary(data: &BitSlice<u8, Msb0>) -> (f64, usize) {
    let fl = data[2..16].load::<u16>() as f64 / 4.0;
    (fl, 16)
}

pub fn decode_cat48(data: &BitSlice<u8, Msb0>) -> Cat48 {
    let mut decoded = Cat48 {
        category: 48,
        data_source_identifier: None,
        time_of_day: None,
        target_desc: None,
        slant_polar: None,
        mode3a_code: None,
        flight_level: None,
    };

    let mut pos = 0;
    let mut fspec_bits = data[pos..pos+8].to_bitvec();
    pos += 8;
    if fspec_bits[7] {
        fspec_bits.extend_from_bitslice(&data[pos..pos+8]);
        pos += 8;
        if fspec_bits[15] {
            fspec_bits.extend_from_bitslice(&data[pos..pos+8]);
            pos += 8;
            if fspec_bits[23] {
                fspec_bits.extend_from_bitslice(&data[pos..pos+8]);
                pos += 8;
            }
        }
    }


    if fspec_bits[0] {
        // I048/010, Data Source Identifier, 2 octets
        let sac = data[pos..pos+8].load::<u8>();
        let sic = data[pos+8..pos+16].load::<u8>();
        decoded.data_source_identifier = Some(DataSourceIdentifier { sac, sic });
        pos += 16;
    }

    if fspec_bits[1] {
        // I048/140, Time-of-Day, 3 octets
        let time_val = data[pos..pos+24].load::<u32>();
        decoded.time_of_day = Some(time_val as f64 / 128.0);
        pos += 24;
    }

    if fspec_bits[2] {
        // I048/020, Target Description
        let (target_desc, bits_consumed) = decode_target_desc(&data[pos..]);
        decoded.target_desc = Some(target_desc);
        pos += bits_consumed;
    }

    if fspec_bits[3] {
        // I048/040, Measured Position in Slant Polar Coordinates
        let (slant_polar, bits_consumed) = decode_slant_polar(&data[pos..]);
        decoded.slant_polar = Some(slant_polar);
        pos += bits_consumed;
    }

    if fspec_bits[4] {
        // I048/070, Mode-3/A Code in Octal Representation
        let (code, bits_consumed) = decode_mode3a_octal(&data[pos..]);
        decoded.mode3a_code = Some(code);
        pos += bits_consumed;
    }

    if fspec_bits[5] {
        // I048/090, Flight Level in Binary Representation
        let (fl, bits_consumed) = decode_fl_binary(&data[pos..]);
        decoded.flight_level = Some(fl);
        pos += bits_consumed;
    }

    decoded
}