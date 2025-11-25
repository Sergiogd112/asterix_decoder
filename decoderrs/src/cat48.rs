use crate::geoutils::*;
use bitvec::prelude::*;
use serde::Serialize;

/// Serializable representation of CAT48 fields required by the dashboard.
#[derive(Debug, Serialize, Default)]
pub struct Cat48 {
    #[serde(rename = "Category")]
    pub category: u8,
    #[serde(rename = "SAC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sac: Option<u8>,
    #[serde(rename = "SIC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sic: Option<u8>,
    #[serde(rename = "Time (s since midnight)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_of_day: Option<f64>,
    #[serde(rename = "Time String")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_string: Option<String>,
    #[serde(rename = "Target Type")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_type: Option<String>,
    #[serde(rename = "Simulated")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub simulated: Option<bool>,
    #[serde(rename = "RDP")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rdp: Option<bool>,
    #[serde(rename = "SPI")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub spi: Option<bool>,
    #[serde(rename = "RAB")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rab: Option<bool>,
    #[serde(rename = "Test")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub test: Option<bool>,
    #[serde(rename = "Extended Range")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extended_range: Option<bool>,
    #[serde(rename = "XPulse")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub xpulse: Option<bool>,
    #[serde(rename = "Military Emergency")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub military_emergency: Option<bool>,
    #[serde(rename = "Military Identification")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub military_identification: Option<bool>,
    #[serde(rename = "FOE/FRI")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub foe_fri: Option<String>,
    #[serde(rename = "ADS-B Element Populated")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ads_b_element_populated: Option<bool>,
    #[serde(rename = "ADS-B Value")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ads_b_value: Option<bool>,
    #[serde(rename = "SCN Element Populated")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scn_element_populated: Option<bool>,
    #[serde(rename = "SCN Value")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scn_value: Option<bool>,
    #[serde(rename = "PAI Element Populated")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pai_element_populated: Option<bool>,
    #[serde(rename = "PAI Value")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pai_value: Option<bool>,
    #[serde(rename = "Range (NM)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub range_nm: Option<f64>,
    #[serde(rename = "Range (m)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub range_m: Option<f64>,
    #[serde(rename = "Theta (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub theta: Option<f64>,
    #[serde(rename = "Mode-3/A Code")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mode3a_code: Option<String>,
    #[serde(rename = "Flight Level (FL)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub flight_level: Option<f64>,
    #[serde(rename = "Altitude (ft)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub altitude_ft: Option<f64>,
    #[serde(rename = "Altitude (m)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub altitude_m: Option<f64>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub radar_plot_characteristics: Option<RadarPlotCharacteristics>,
    #[serde(rename = "Aircraft Address")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub aircraft_address: Option<String>,
    #[serde(rename = "Target Identification")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_identification: Option<String>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mode_s_mb_data: Option<ModeSMBData>,
    #[serde(rename = "Track Number")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub track_number: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub calculated_pos_in_cart: Option<(f64, f64)>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub calc_track_vel_polar: Option<CalcTrackVelPolar>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub track_status: Option<TrackStatus>,
    #[serde(rename = "Communications Capability")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_communications_capability: Option<String>,
    #[serde(rename = "STAT")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stat_cat48: Option<String>,
    #[serde(rename = "SI/II")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_si_ii: Option<String>,
    #[serde(rename = "Mode S Specific Service Capability")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_mode_s_specific_service_capability: Option<bool>,
    #[serde(rename = "Altitude Reporting Capability")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_altitude_reporting_capability: Option<bool>,
    #[serde(rename = "Aircraft Identification Capability")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_aircraft_identification_capability: Option<bool>,
    #[serde(rename = "ACAS Status")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_acas_status: Option<String>,
    #[serde(rename = "Hybrid Surveillance")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_hybrid_surveillance: Option<bool>,
    #[serde(rename = "TA/RA")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_ta_ra: Option<String>,
    #[serde(rename = "Applicable MOPS Doc")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub com_acas_cap_fl_st_applicable_mops_doc: Option<String>,
    #[serde(rename = "Latitude (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub latitude: Option<f64>,
    #[serde(rename = "Longitude (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub longitude: Option<f64>,
}

#[derive(Debug, Serialize, Default)]
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

#[derive(Debug, Serialize, Default, Clone)]
pub struct RadarPlotCharacteristics {
    #[serde(rename = "SSR Plot Runlength")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ssr_plot_runlength: Option<f64>,
    #[serde(rename = "Number of Received Replies SSR")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub number_of_received_replies_ssr: Option<u8>,
    #[serde(rename = "Amplitude of (M)SSR Reply")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub amplitude_of_mssr_reply: Option<u8>,
    #[serde(rename = "Primary Plot Runlength (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub primary_plot_runlength: Option<f64>,
    #[serde(rename = "Amplitude of Primary Plot (dBm)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub amplitude_of_primary_plot: Option<u8>,
    #[serde(rename = "Range (PSR-SSR)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub range_psr_ssr: Option<f64>,
    #[serde(rename = "Azimuth (PSR-SSR)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub azimuth_psr_ssr: Option<f64>,
}

#[derive(Debug, Serialize, Default)]
pub struct ModeSMBData {
    #[serde(rename = "Repetition")]
    pub repetition: u8,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bds_4_0: Option<BDS40>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bds_5_0: Option<BDS50>,
    #[serde(flatten)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bds_6_0: Option<BDS60>,
}

#[derive(Debug, Serialize, Default)]
pub struct BDS40 {
    #[serde(rename = "Status MCP/FCU")]
    pub status_mcp: bool,
    #[serde(rename = "MCP/FCU Selected Altitude")]
    pub mcp_alt: f64,
    #[serde(rename = "Status FMS")]
    pub status_fms: bool,
    #[serde(rename = "FMS Selected Altitude")]
    pub fms_alt: f64,
    #[serde(rename = "Status Barometric Reference")]
    pub status_bar: bool,
    #[serde(rename = "Barometric Pressure Setting")]
    pub bar_press: f64,
    #[serde(rename = "Status MCP/FCU Mode")]
    pub status_mcp_mode: bool,
    #[serde(rename = "VNAV Mode")]
    pub vnav: bool,
    #[serde(rename = "ALT Hold Mode")]
    pub alt_hold: bool,
    #[serde(rename = "Approach Mode")]
    pub approach: bool,
    #[serde(rename = "Status Target Source")]
    pub status_target: bool,
    #[serde(rename = "Target Alt Source")]
    pub target_alt_source: String,
}

#[derive(Debug, Serialize, Default)]
pub struct BDS50 {
    #[serde(rename = "Status Roll Angle")]
    pub status_roll: bool,
    #[serde(rename = "Roll Angle")]
    pub roll_angle: f64,
    #[serde(rename = "Status Track Angle")]
    pub status_track: bool,
    #[serde(rename = "Track Angle")]
    pub track_angle: f64,
    #[serde(rename = "Status Ground Speed")]
    pub status_gs: bool,
    #[serde(rename = "Ground Speed (kts)")]
    pub gs: f64,
    #[serde(rename = "Status Track Angle Rate")]
    pub status_ta_rate: bool,
    #[serde(rename = "Track Angle Rate")]
    pub ta_rate: f64,
    #[serde(rename = "Status TAS")]
    pub status_tas: bool,
    #[serde(rename = "TAS")]
    pub tas: f64,
}

#[derive(Debug, Serialize, Default)]
pub struct BDS60 {
    #[serde(rename = "Status Magnetic Heading")]
    pub status_mag_h: bool,
    #[serde(rename = "Magnetic Heading (deg) BDS")]
    pub mag_h: f64,
    #[serde(rename = "Status IAS")]
    pub status_ias: bool,
    #[serde(rename = "IAS (kt)")]
    pub ias: f64,
    #[serde(rename = "Status Mach")]
    pub status_mach: bool,
    #[serde(rename = "Mach")]
    pub mach: f64,
    #[serde(rename = "Status Barometric Altitude Rate")]
    pub status_bar_rate: bool,
    #[serde(rename = "Barometric Altitude Rate")]
    pub bar_rate: f64,
    #[serde(rename = "Status Inertial Vertical Velocity")]
    pub status_inert_vv: bool,
    #[serde(rename = "Inertial Vertical Velocity")]
    pub inert_vv: f64,
}

#[derive(Debug, Serialize, Default)]
pub struct CalcTrackVelPolar {
    #[serde(rename = "Ground Speed (kts)")]
    pub groundspeed: f64,
    #[serde(rename = "Magnetic Heading (deg)")]
    pub heading: f64,
}

#[derive(Debug, Serialize, Default, Clone)]
pub struct TrackStatus {
    #[serde(rename = "ConfVTent")]
    pub conf_vtent: bool,
    #[serde(rename = "Type of Sensor")]
    pub type_of_sensor: String,
    #[serde(rename = "DOU")]
    pub dou: bool,
    #[serde(rename = "Manoeuver detection Horizontal")]
    pub man_h: bool,
    #[serde(rename = "Climbing/Descending")]
    pub climb_desc: String,
    #[serde(rename = "End of Track")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_of_track: Option<bool>,
    #[serde(rename = "Ghost")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ghost: Option<bool>,
    #[serde(rename = "SUP")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sup: Option<bool>,
    #[serde(rename = "TCC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tcc: Option<bool>,
}

fn decode_dsi(data: &BitSlice<u8, Msb0>) -> (u8, u8, usize) {
    let sac = data[0..8].load::<u8>();
    let sic = data[8..16].load::<u8>();
    (sac, sic, 16)
}

fn decode_time_of_day(data: &BitSlice<u8, Msb0>) -> (f64, String, usize) {
    let time_val = data[0..24].load_be::<u32>();
    let time_sec = (time_val as f64) / 128.0;
    let sec = time_sec % 60.0;
    let min = ((time_sec / 60.0).floor()) % 60.0;
    let hr = (time_sec / 3600.0).floor() % 24.0;
    let time_string = format!("{:02}:{:02}:{:06.3}", hr as u8, min as u8, sec);
    (time_sec, time_string, 24)
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
        ..Default::default()
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
    // pos += 8; // Not needed as we return 24 bits total

    (target_desc, 24)
}

fn decode_slant_polar(data: &BitSlice<u8, Msb0>) -> (f64, f64, f64, usize) {
    let range_nm = data[0..16].load_be::<u16>() as f64 / 256.0;
    let theta = data[16..32].load_be::<u16>() as f64 * (360.0 / 65536.0);
    (range_nm, range_nm * 1852.0, theta, 32)
}

fn decode_mode3a_octal(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let a = data[4..7].load::<u8>();
    let b = data[7..10].load::<u8>();
    let c = data[10..13].load::<u8>();
    let d = data[13..16].load::<u8>();
    (format!("{}{}{}{}", a, b, c, d), 16)
}

fn decode_fl_binary(data: &BitSlice<u8, Msb0>) -> (f64, usize) {
    let fl = data[2..16].load_be::<u16>() as f64 / 4.0; // Changed to u16 to match Python's uint behavior for now
    (fl, 16)
}

fn decode_aircraft_address(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let address_int = data[0..24].load_be::<u32>();
    let address = format!("{:06X}", address_int);
    (address, 24)
}

fn decode_aircraft_id(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let mut chars = String::new();
    for i in 0..8 {
        let start_bit = i * 6;
        let end_bit = start_bit + 6;
        let char_code = data[start_bit..end_bit].load_be::<u8>();
        let c = match char_code {
            1..=26 => (char_code + 64) as char,
            48..=57 => char_code as char,
            _ => ' ',
        };
        chars.push(c);
    }
    (chars.trim_end().to_string(), 48)
}

fn decode_track_number(data: &BitSlice<u8, Msb0>) -> (u16, usize) {
    (data[4..16].load_be::<u16>(), 16)
}

fn decode_calc_track_vel_polar(data: &BitSlice<u8, Msb0>) -> (CalcTrackVelPolar, usize) {
    let groundspeed = data[0..16].load_be::<u16>() as f64 * 0.22;
    let heading = data[16..32].load_be::<u16>() as f64 * (360.0 / 65536.0);
    (
        CalcTrackVelPolar {
            groundspeed,
            heading,
        },
        32,
    )
}

fn decode_radar_plot_characteristics(
    data: &BitSlice<u8, Msb0>,
) -> (RadarPlotCharacteristics, usize) {
    let mut pos = 0;
    let first_octet = data[pos..pos + 8].load::<u8>();
    pos += 8;

    let mut rpc = RadarPlotCharacteristics::default();
    let mut bits_used = 8;

    // Check each bit in first octet
    if (first_octet >> 7) & 0x1 != 0 {
        // SSR plot runlength
        let runlength = data[pos..pos + 8].load::<u8>() as f64 * 360.0 / 8192.0;
        rpc.ssr_plot_runlength = Some(runlength);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 6) & 0x1 != 0 {
        // Number of received replies SSR
        let replies = data[pos..pos + 8].load::<u8>();
        rpc.number_of_received_replies_ssr = Some(replies);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 5) & 0x1 != 0 {
        // Amplitude of (M)SSR reply
        let amplitude = data[pos..pos + 8].load::<u8>();
        rpc.amplitude_of_mssr_reply = Some(amplitude);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 4) & 0x1 != 0 {
        // Primary Plot Runlength
        let runlength = data[pos..pos + 8].load::<u8>() as f64 * 360.0 / 8192.0;
        rpc.primary_plot_runlength = Some(runlength);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 3) & 0x1 != 0 {
        // Amplitude of Primary Plot
        let amplitude = data[pos..pos + 8].load::<u8>();
        rpc.amplitude_of_primary_plot = Some(amplitude);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 2) & 0x1 != 0 {
        // Range (PSR-SSR)
        let range = data[pos..pos + 8].load::<u8>() as f64 / 256.0;
        rpc.range_psr_ssr = Some(range);
        pos += 8;
        bits_used += 8;
    }

    if (first_octet >> 1) & 0x1 != 0 {
        // Azimuth (PSR-SSR)
        let azimuth = data[pos..pos + 8].load::<u8>() as f64 * 360.0 / 16384.0;
        rpc.azimuth_psr_ssr = Some(azimuth);
        // pos += 8;
        bits_used += 8;
    }

    (rpc, bits_used)
}

fn decode_bds_4_0(data: &BitSlice<u8, Msb0>) -> (BDS40, usize) {
    let status_mcp = data[0];
    let mcp_alt = data[1..13].load_be::<u16>() as f64 / 16.0;
    let status_fms = data[13];
    let fms_alt = data[14..26].load_be::<u16>() as f64 / 16.0;
    let status_bar = data[26];
    let bar_press = data[27..39].load_be::<u16>() as f64 * 0.1 + 800.0;
    let status_mcp_mode = data[47];
    let vnav = data[48];
    let alt_hold = data[49];
    let approach = data[50];
    let status_target = data[53];
    let target_alt_idx = data[54..56].load_be::<u16>() as usize;

    let target_alt_source = match target_alt_idx {
        0 => "Unknown",
        1 => "Aircraft Altitude",
        2 => "MCP/FCU",
        3 => "FMS",
        _ => "Unknown",
    };

    let bds_4_0 = BDS40 {
        status_mcp,
        mcp_alt,
        status_fms,
        fms_alt,
        status_bar,
        bar_press,
        status_mcp_mode,
        vnav,
        alt_hold,
        approach,
        status_target,
        target_alt_source: target_alt_source.to_string(),
    };

    (bds_4_0, 56)
}

fn decode_bds_5_0(data: &BitSlice<u8, Msb0>) -> (BDS50, usize) {
    let status_roll = data[0];
    let roll_angle_raw = data[1..11].load_be::<u16>();
    let roll_angle = if roll_angle_raw >= 1024 {
        (roll_angle_raw as i32 - 2048) as f64
    } else {
        roll_angle_raw as f64
    } * (45.0 / 256.0);
    let status_track = data[11];
    let track_angle_raw = data[12..23].load_be::<u16>();
    let track_angle = if track_angle_raw >= 1024 {
        (track_angle_raw as i32 - 2048) as f64
    } else {
        track_angle_raw as f64
    } * (90.0 / 512.0);
    let status_gs = data[23];
    let gs = data[24..34].load_be::<u16>() as f64 * 2.0;
    let status_ta_rate = data[34];
    let ta_rate_raw = data[35..45].load_be::<u16>();
    let ta_rate = if ta_rate_raw >= 1024 {
        (ta_rate_raw as i32 - 2048) as f64
    } else {
        ta_rate_raw as f64
    } * (8.0 / 256.0);
    let status_tas = data[45];
    let tas = data[46..56].load_be::<u16>() as f64 * 2.0;

    let bds_5_0 = BDS50 {
        status_roll,
        roll_angle,
        status_track,
        track_angle,
        status_gs,
        gs,
        status_ta_rate,
        ta_rate,
        status_tas,
        tas,
    };

    (bds_5_0, 56)
}

fn decode_bds_6_0(data: &BitSlice<u8, Msb0>) -> (BDS60, usize) {
    let status_mag_h = data[0];
    let mag_h_raw = data[1..12].load_be::<u16>();
    let mag_h = (if mag_h_raw >= 1024 {
        (mag_h_raw as i32 - 2048) as f64
    } else {
        mag_h_raw as f64
    }) * (90.0 / 512.0);
    let status_ias = data[12];
    let ias = data[13..23].load_be::<u16>() as f64 * 1.0;
    let status_mach = data[23];
    let mach = data[24..34].load_be::<u16>() as f64 * (2.048 / 512.0);
    let status_bar_rate = data[34];
    let bar_rate_raw = data[35..45].load_be::<u16>();
    let bar_rate = if bar_rate_raw >= 512 {
        (bar_rate_raw as i32 - 1024) as f64
    } else {
        bar_rate_raw as f64
    } * 32.0;
    let status_inert_vv = data[45];
    let inert_vv_raw = data[46..56].load_be::<u16>();
    let inert_vv = if inert_vv_raw >= 512 {
        (inert_vv_raw as i32 - 1024) as f64
    } else {
        inert_vv_raw as f64
    } * 32.0;

    let bds_6_0 = BDS60 {
        status_mag_h,
        mag_h,
        status_ias,
        ias,
        status_mach,
        mach,
        status_bar_rate,
        bar_rate,
        status_inert_vv,
        inert_vv,
    };

    (bds_6_0, 56)
}

fn decode_mode_s_mb_data(data: &BitSlice<u8, Msb0>) -> (ModeSMBData, usize) {
    let repetition = data[0..8].load::<u8>();
    let required_bits: usize = 8 + (repetition as usize) * 64; // 8 header + repetition * 64 data bits

    if data.len() < required_bits {
        return (ModeSMBData::default(), 8); // Return default if insufficient data
    }

    let mut mb_data = ModeSMBData {
        repetition,
        ..Default::default()
    };

    let mut pos = 8;
    for _i in 0..repetition {
        if pos + 64 > data.len() {
            break;
        }

        let block_start = pos;
        let bda1 = data[block_start + 56..block_start + 60].load_be::<u16>();
        let bda2 = data[block_start + 60..block_start + 64].load_be::<u16>();

        match bda1 {
            4 => {
                if bda2 == 0 && pos + 56 <= data.len() {
                    let (bds_4_0, _) = decode_bds_4_0(&data[block_start + 8..block_start + 64]);
                    mb_data.bds_4_0 = Some(bds_4_0);
                }
            }
            5 => {
                if bda2 == 0 && pos + 56 <= data.len() {
                    let (bds_5_0, _) = decode_bds_5_0(&data[block_start + 8..block_start + 64]);
                    mb_data.bds_5_0 = Some(bds_5_0);
                }
            }
            6 => {
                if bda2 == 0 && pos + 56 <= data.len() {
                    let (bds_6_0, _) = decode_bds_6_0(&data[block_start + 8..block_start + 64]);
                    mb_data.bds_6_0 = Some(bds_6_0);
                }
            }
            _ => {
                // Unsupported BDS
            }
        }

        pos += 64;
    }

    (mb_data, required_bits)
}

fn decode_track_status(data: &BitSlice<u8, Msb0>) -> (TrackStatus, usize) {
    let mut bits = 8;
    let octet1 = data[0..8].load::<u8>();
    let conf_vtent = (octet1 >> 7) & 0x1 != 0;
    let type_sensor_idx = ((octet1 >> 5) & 0x3) as usize;
    let dou = (octet1 >> 4) & 0x1 != 0;
    let man_h = (octet1 >> 3) & 0x1 != 0;
    let climb_desc_idx = ((octet1 >> 1) & 0x3) as usize;
    let ext = (octet1 & 0x1) != 0;

    let mut track_status = TrackStatus {
        conf_vtent,
        type_of_sensor: ["Combined Track", "PSR Track", "SSR/Mode S Track", "Invalid"]
            [type_sensor_idx]
            .to_string(),
        dou,
        man_h,
        climb_desc: ["Maintaining", "Climbing", "Descending", "Unknown"][climb_desc_idx]
            .to_string(),
        ..Default::default()
    };

    if ext {
        bits = 16;
        let octet2 = data[8..16].load::<u8>();
        track_status.end_of_track = Some((octet2 >> 7) & 0x1 != 0);
        track_status.ghost = Some((octet2 >> 6) & 0x1 != 0);
        track_status.sup = Some((octet2 >> 5) & 0x1 != 0);
        track_status.tcc = Some((octet2 >> 4) & 0x1 != 0);
    }

    (track_status, bits)
}

fn decode_com_acas_cap_fl_st(
    data: &BitSlice<u8, Msb0>,
) -> (
    String,
    String,
    String,
    bool,
    bool,
    bool,
    String,
    bool,
    String,
    String,
    usize,
) {
    let octet1 = data[0..8].load_be::<u8>();
    let octet2 = data[8..16].load_be::<u8>();

    let comm_cap_idx = (octet1 >> 5) as usize;
    let flight_stat_idx = ((octet1 >> 2) & 0x7) as usize;
    let si_ii = (octet1 >> 1) & 0x1 != 0;

    let mode_s_ssc = (octet2 >> 7) & 0x1 != 0;
    let alt_rep = (octet2 >> 6) & 0x1 != 0;
    let ac_id_cap = (octet2 >> 5) & 0x1 != 0;
    let acas_stat = (octet2 >> 4) & 0x1 != 0;
    let hybrid = (octet2 >> 3) & 0x1 != 0;
    let ta_ra = (octet2 >> 2) & 0x1 != 0;
    let mops_idx = (octet2 & 0x3) as usize;

    (
        [
            "No com",
            "Comm A and B",
            "Comm A,B and Uplink ELM",
            "Comm A,B and Uplink ELM and Downlink",
            "Level 5 Transponder Capability",
            "Not assigned",
            "Not assigned",
            "Not assigned",
        ][comm_cap_idx]
            .to_string(),
        [
            "No alert, no SPI, airborne",
            "No alert, no SPI, on ground",
            "Alert, no SPI, airborne",
            "Alert, no SPI, on ground",
            "Alert, SPI, airborne or ground",
            "No alert, SPI, airborne or ground",
            "Not assigned",
            "Unknown",
        ][flight_stat_idx]
            .to_string(),
        if si_ii { "II" } else { "SI" }.to_string(),
        mode_s_ssc,
        alt_rep,
        ac_id_cap,
        if acas_stat {
            "Operational"
        } else {
            "Failed or Standby"
        }
        .to_string(),
        hybrid,
        if ta_ra { "TA and RA" } else { "TA" }.to_string(),
        [
            "RTCA DO-185",
            "RTCA DO-185A",
            "RTCA DO-185B",
            "Reserved For Future Versions",
        ][mops_idx]
            .to_string(),
        16,
    )
}

/// Decode a CAT48 payload into `Cat48`, optionally enriching with geodesic coords.
pub fn decode_cat48(category: u8, data: &BitSlice<u8, Msb0>, radar_coords: Option<CoordinatesWGS84>) -> Cat48 {
    let mut decoded = Cat48 {
        category,
        ..Default::default()
    };

    let mut pos = 0;
    let fspec_block_1 = data[pos..pos + 8].to_bitvec();
    pos += 8;
    let fx1 = fspec_block_1[7];

    let mut data_items_to_decode = Vec::new();
    for i in 0..7 {
        if fspec_block_1[i] {
            data_items_to_decode.push(i);
        }
    }

    if fx1 {
        let fspec_block_2 = data[pos..pos + 8].to_bitvec();
        pos += 8;
        let fx2 = fspec_block_2[7];

        for i in 0..7 {
            if fspec_block_2[i] {
                data_items_to_decode.push(i + 7);
            }
        }

        if fx2 {
            let fspec_block_3 = data[pos..pos + 8].to_bitvec();
            pos += 8;
            let fx3 = fspec_block_3[7];

            for i in 0..7 {
                if fspec_block_3[i] {
                    data_items_to_decode.push(i + 14);
                }
            }

            if fx3 {
                let fspec_block_4 = data[pos..pos + 8].to_bitvec();
                // pos += 8; // Not used - this is the last field in this structure

                for i in 0..7 {
                    if fspec_block_4[i] {
                        data_items_to_decode.push(i + 21);
                    }
                }
            }
        }
    }

    // Process data items based on FSPEC
    for &item in &data_items_to_decode {
        match item {
            0 => {
                // I048/010, Data Source Identifier, 2 octets
                let (sac, sic, bits) = decode_dsi(&data[pos..]);
                decoded.sac = Some(sac);
                decoded.sic = Some(sic);
                pos += bits;
            }
            1 => {
                // I048/140, Time-of-Day, 3 octets
                let (tod, tstr, bits) = decode_time_of_day(&data[pos..]);
                decoded.time_of_day = Some(tod);
                decoded.time_string = Some(tstr);
                pos += bits;
            }
            2 => {
                // I048/020, Target Description
                let (td, bits) = decode_target_desc(&data[pos..]);
                decoded.target_type = Some(td.target_type.clone());
                decoded.simulated = Some(td.simulated);
                decoded.rdp = Some(td.rdp);
                decoded.spi = Some(td.spi);
                decoded.rab = Some(td.rab);
                decoded.test = td.test;
                decoded.extended_range = td.extended_range;
                decoded.xpulse = td.xpulse;
                decoded.military_emergency = td.military_emergency;
                decoded.military_identification = td.military_identification;
                decoded.foe_fri = td.foe_fri;
                decoded.ads_b_element_populated = td.ads_b_element_populated;
                decoded.ads_b_value = td.ads_b_value;
                decoded.scn_element_populated = td.scn_element_populated;
                decoded.scn_value = td.scn_value;
                decoded.pai_element_populated = td.pai_element_populated;
                decoded.pai_value = td.pai_value;
                pos += bits;
            }
            3 => {
                // I048/040, Measured Position in Slant Polar Coordinates
                let (range_nm, range_m, theta, bits) = decode_slant_polar(&data[pos..]);
                decoded.range_nm = Some(range_nm);
                decoded.range_m = Some(range_m);
                decoded.theta = Some(theta);
                pos += bits;
            }
            4 => {
                // I048/070, Mode-3/A Code in Octal Representation
                let (m3a, bits) = decode_mode3a_octal(&data[pos..]);
                decoded.mode3a_code = Some(m3a.clone());
                pos += bits;
            }
            5 => {
                // I048/090, Flight Level in Binary Representation
                let (fl, bits) = decode_fl_binary(&data[pos..]);
                decoded.flight_level = Some(fl);
                decoded.altitude_ft = Some(fl * 100.0);
                decoded.altitude_m = Some(fl * 30.48); // 1 ft = 0.3048 m
                pos += bits;
            }
            6 => {
                // I048/161 Radar Plot Characteristics
                let (rpc, bits) = decode_radar_plot_characteristics(&data[pos..]);
                decoded.radar_plot_characteristics = Some(rpc.clone());
                pos += bits;
            }
            7 => {
                // I048/030 Aircraft Address
                let (aa, bits) = decode_aircraft_address(&data[pos..]);
                decoded.aircraft_address = Some(aa.clone());
                pos += bits;
            }
            8 => {
                // I048/040 Aircraft Identification
                let (aid, bits) = decode_aircraft_id(&data[pos..]);
                decoded.target_identification = Some(aid.clone());
                pos += bits;
            }
            9 => {
                // I048/050 Mode S MB Data
                let (mb_data, bits) = decode_mode_s_mb_data(&data[pos..]);
                decoded.mode_s_mb_data = Some(mb_data);
                pos += bits;
            }
            10 => {
                // I048/060 Track Number
                let (tn, bits) = decode_track_number(&data[pos..]);
                decoded.track_number = Some(tn);
                pos += bits;
            }
            11 => {
                // I048/080 Calculated Position in Cartesian Coordinates
                // Skipping, not needed for flattened output
                pos += 32; // Fixed size
            }
            12 => {
                // I048/100 Calculated Track Velocity in Polar Representation
                let (ctvp, bits) = decode_calc_track_vel_polar(&data[pos..]);
                decoded.calc_track_vel_polar = Some(ctvp);
                pos += bits;
            }
            13 => {
                // I048/110 Track Status
                let (ts, bits) = decode_track_status(&data[pos..]);
                decoded.track_status = Some(ts.clone());
                pos += bits;
            }
            14 => {
                pos+=32;
            }
            15 => {
                while data[pos+7] {
    // pos += 8; // Not needed as we're at the end of the field
                }
            }
            16 => {
                pos += 16;
            }
            17 => {
                pos += 32;
            }
            18 => {
                pos += 16;
            }
            19 => {
                pos += 16;
            }
            20 => {
                // I048/220 Com/ACAS Capability and Flight Status
                let (
                    communications_capability,
                    stat,
                    si_ii,
                    mode_s_specific_service_capability,
                    altitude_reporting_capability,
                    aircraft_identification_capability,
                    acas_status,
                    hybrid_surveillance,
                    ta_ra,
                    applicable_mops_doc,
                    bits,
                ) = decode_com_acas_cap_fl_st(&data[pos..]);
                decoded.com_acas_cap_fl_st_communications_capability =
                    Some(communications_capability);
                decoded.stat_cat48 = Some(stat);
                decoded.com_acas_cap_fl_st_si_ii = Some(si_ii);
                decoded.com_acas_cap_fl_st_mode_s_specific_service_capability =
                    Some(mode_s_specific_service_capability);
                decoded.com_acas_cap_fl_st_altitude_reporting_capability =
                    Some(altitude_reporting_capability);
                decoded.com_acas_cap_fl_st_aircraft_identification_capability =
                    Some(aircraft_identification_capability);
                decoded.com_acas_cap_fl_st_acas_status = Some(acas_status);
                decoded.com_acas_cap_fl_st_hybrid_surveillance = Some(hybrid_surveillance);
                decoded.com_acas_cap_fl_st_ta_ra = Some(ta_ra);
                decoded.com_acas_cap_fl_st_applicable_mops_doc = Some(applicable_mops_doc);
                pos += bits;
            }
            _ => {
                // Skip unknown or unimplemented data items
            }
        }
    }

    // "on ground" altitude correction logic
    if decoded.altitude_m.is_none() {
        if let Some(stat) = &decoded.stat_cat48 {
            if stat.ends_with("on ground") {
                decoded.flight_level = Some(0.0);
                decoded.altitude_ft = Some(0.0);
                decoded.altitude_m = Some(0.0);
            }
        }
    }

    if let (Some(rc), Some(r_m), Some(th), Some(h_m)) = (
        radar_coords,
        decoded.range_m,
        decoded.theta,
        decoded.altitude_m,
    ) {
        // Only proceed if all necessary values are present and range_m > 0
        if r_m > 0.0 {
            let theta_rad = th.to_radians();
            // Clamp argument of asin to avoid NaN for small floating point errors
            let arg = (h_m - rc.height) / r_m;
            let elevation_rad = arg.clamp(-1.0, 1.0).asin();

            let coords_polar = CoordinatesPolar {
                rho: r_m,
                theta: theta_rad,
                elevation: elevation_rad,
            };
            let coords_cart = change_radar_spherical_2_radar_cartesian(&coords_polar);
            let coords_geocentric = change_radar_cartesian_2_geocentric(&rc, &coords_cart);
            let coords_geodesic = change_geocentric_2_geodesic(&coords_geocentric);

            decoded.latitude = Some(coords_geodesic.lat.to_degrees());
            decoded.longitude = Some(coords_geodesic.lon.to_degrees());
            // decoded.altitude_m is already set or derived earlier.
        } else {
            // If range is zero or negative, or altitude is missing, coordinate conversion is not meaningful.
            // Set latitude/longitude to None
            decoded.latitude = None;
            decoded.longitude = None;
        }
    }

    decoded
}
