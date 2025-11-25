use bitvec::prelude::*;
use serde::Serialize;

/// Serializable representation of the CAT21 fields consumed by the dashboard.
#[derive(Debug, Serialize, Default)]
pub struct Cat21 {
    #[serde(rename = "Category")]
    pub category: u8,
    #[serde(rename = "SAC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sac: Option<u8>,
    #[serde(rename = "SIC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sic: Option<u8>,
    #[serde(rename = "ATP Description")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub atp_description: Option<String>,
    #[serde(rename = "ARC Description")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub arc_description: Option<String>,
    #[serde(rename = "RC Description")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rc_description: Option<String>,
    #[serde(rename = "RAB Description")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rab_description: Option<String>,
    #[serde(rename = "GBS")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gbs: Option<u8>,
    #[serde(rename = "Latitude (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub latitude: Option<f64>,
    #[serde(rename = "Longitude (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub longitude: Option<f64>,
    #[serde(rename = "ICAO Address (hex)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub icao_address: Option<String>,
    #[serde(rename = "Time (s since midnight)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_of_reception_position: Option<f64>,
    #[serde(rename = "UTC Time (HH:MM:SS)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub utc_time: Option<String>,
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
    #[serde(rename = "IAS (kt)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ias: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mach: Option<f64>,
    #[serde(rename = "Magnetic Heading (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub magnetic_heading: Option<f64>,
    #[serde(rename = "Target Status VFI")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_status_vfi: Option<String>,
    #[serde(rename = "Target Status RAB")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_status_rab: Option<String>,
    #[serde(rename = "Target Status GBS")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_status_gbs: Option<String>,
    #[serde(rename = "Target Status NRM")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_status_nrm: Option<String>,
    #[serde(rename = "Ground Speed (kts)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ground_speed_kts: Option<f64>,
    #[serde(rename = "Track Angle (deg)")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub track_angle: Option<f64>,
    #[serde(rename = "Target Identification")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_identification: Option<String>,
}

fn decode_data_source_id(data: &BitSlice<u8, Msb0>) -> (u8, u8, usize) {
    let sac = data[0..8].load::<u8>();
    let sic = data[8..16].load::<u8>();
    (sac, sic, 16)
}

fn decode_target_report_descriptor(data: &BitSlice<u8, Msb0>) -> (String, String, String, String, Option<u8>, usize) {
    let val = data[0..8].load::<u8>();
    let atp = (val >> 5) & 0b111;
    let arc = (val >> 3) & 0b11;
    let rc = (val >> 2) & 1;
    let rab = (val >> 1) & 1;
    let fx = data[7];

    let atp_map = [
        "24-Bit ICAO address",
        "Duplicate address",
        "Surface vehicle address",
        "Anonymous address",
    ];
    let arc_map = ["25 ft", "100 ft", "Unknown", "invalid"];

    let atp_description = atp_map.get(atp as usize).unwrap_or(&"Reserved").to_string();
    let arc_description = arc_map.get(arc as usize).unwrap_or(&"Reserved").to_string();
    let rc_description = if rc == 0 { "Range Check Passed" } else { "Range Check Failed" }.to_string();
    let rab_description = if rab == 1 { "Report from field monitor" } else { "Report from ADS-B transceiver" }.to_string();

    let mut bits_processed = 8;
    let mut gbs_value = None;

    // Handle FX extensions
    if fx {
        // Handle GBS bit in first extension (Python version: decoded["GBS"] = data[bits_processed+2])
        if data.len() >= bits_processed + 8 {
            // GBS bit is at position bits_processed+2 in the first extension octet
            gbs_value = Some(data[bits_processed + 2] as u8);
        }
        
        let mut current_fx = fx;
        while current_fx {
            if data.len() < bits_processed + 8 {
                break;
            }
            current_fx = data[bits_processed + 7];
            bits_processed += 8;
        }
    }

    (atp_description, arc_description, rc_description, rab_description, gbs_value, bits_processed)
}

fn decode_wgs84_coords_high_res(data: &BitSlice<u8, Msb0>) -> (f64, f64, usize) {
    let lat_raw = data[0..32].load_be::<i32>();
    let lon_raw = data[32..64].load_be::<i32>();
    let lsb = 180.0 / (2_f64.powi(30));
    let lat = lat_raw as f64 * lsb;
    let lon = lon_raw as f64 * lsb;
    (lat, lon, 64)
}

fn decode_target_address(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let addr = data[0..24].load_be::<u32>();
    let address = format!("{:06X}", addr);
    (address, 24)
}

fn decode_time_of_reception_position(data: &BitSlice<u8, Msb0>) -> (f64, String, usize) {
    let time_val = data[0..24].load_be::<u32>() as f64 / 128.0;
    let h = (time_val / 3600.0) as u8 % 24;
    let m = ((time_val % 3600.0) / 60.0) as u8;
    let s = time_val % 60.0;
    let time_string = format!("{:02}:{:02}:{:06.3}", h, m, s);
    (time_val, time_string, 24)
}

fn decode_mode3a_code(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let val = data[0..16].load_be::<u16>();
    let code = val & 0x0FFF;
    let a = (code >> 9) & 0b111;
    let b = (code >> 6) & 0b111;
    let c = (code >> 3) & 0b111;
    let d = code & 0b111;
    (format!("{}{}{}{}", a, b, c, d), 16)
}

fn decode_flight_level(data: &BitSlice<u8, Msb0>) -> (f64, usize) {
    let fl_raw = data[0..16].load_be::<i16>();
    let flight_level = fl_raw as f64 / 4.0;
    (flight_level, 16)
}

fn decode_air_speed(data: &BitSlice<u8, Msb0>) -> (Option<f64>, Option<f64>, usize) {
    let im = data[0..2].load::<u8>();
    let air_speed_raw = data[2..16].load_be::<u16>();

    match im {
        0 => (Some(air_speed_raw as f64 * 1.0), None, 16), // IAS in knots (LSB = 1 kt)
        1 => (None, Some(air_speed_raw as f64 * 0.001), 16), // Mach (LSB = 0.001 Mach)
        _ => (None, None, 16), // Invalid
    }
}

fn decode_magnetic_heading(data: &BitSlice<u8, Msb0>) -> (f64, usize) {
    let heading_raw = data[0..16].load_be::<u16>();
    let heading = heading_raw as f64 * (360.0 / 65536.0);
    (heading, 16)
}

fn decode_target_status(data: &BitSlice<u8, Msb0>) -> (String, String, String, String, usize) {
    let val = data[0..8].load::<u8>();

    let vfi = (val >> 6) & 0b11;
    let rab = (val >> 4) & 0b11;
    let gbs = (val >> 2) & 0b11;
    let nrm = val & 0b11;

    let vfi_map = ["Valid", "Invalid", "Reserved", "Reserved"];
    let rab_map = ["Reported by ADS-B", "Reported by RBM", "Reserved", "Reserved"];
    let gbs_map = ["No ground bit", "Ground bit set", "Reserved", "Reserved"];
    let nrm_map = ["Normal", "Degraded", "Reserved", "Reserved"];

    let vfi_desc = vfi_map.get(vfi as usize).unwrap_or(&"Unknown").to_string();
    let rab_desc = rab_map.get(rab as usize).unwrap_or(&"Unknown").to_string();
    let gbs_desc = gbs_map.get(gbs as usize).unwrap_or(&"Unknown").to_string();
    let nrm_desc = nrm_map.get(nrm as usize).unwrap_or(&"Unknown").to_string();

    (vfi_desc, rab_desc, gbs_desc, nrm_desc, 8)
}

fn decode_airborne_ground_vector(data: &BitSlice<u8, Msb0>) -> (f64, f64, usize) {
    let ground_speed_raw = data[0..16].load_be::<u16>();
    let track_angle_raw = data[16..32].load_be::<u16>();
    
    // LSB = 2^-14 NM/s = 1/256 kt (approx), convert to knots
    // Python version: ground_speed_raw * (2**-14) * 3600
    let ground_speed_kts = ground_speed_raw as f64 * (2_f64.powi(-14)) * 3600.0;
    let track_angle = track_angle_raw as f64 * (360.0 / 65536.0);

    (ground_speed_kts, track_angle, 32)
}

fn decode_target_identification(data: &BitSlice<u8, Msb0>) -> (String, usize) {
    let mut chars = String::new();
    for i in 0..8 {
        let start_bit = i * 6;
        let end_bit = start_bit + 6;
        let char_code = data[start_bit..end_bit].load_be::<u8>();
        let c = match char_code {
            1..=26 => (char_code + 64) as char,
            32 => ' ',
            48..=57 => char_code as char,
            _ => ' ',
        };
        chars.push(c);
    }
    (chars.trim().to_string(), 48)
}

fn skip_field(_data: &BitSlice<u8, Msb0>, octets: usize) -> usize {
    octets * 8
}

fn skip_variable_fx(data: &BitSlice<u8, Msb0>) -> usize {
    let mut pos = 0;
    loop {
        if pos + 8 > data.len() {
            break;
        }
        let fx = data[pos + 7];
        pos += 8;
        if !fx {
            break;
        }
    }
    pos
}

fn skip_compound_met_info(data: &BitSlice<u8, Msb0>) -> usize {
    if data.len() < 8 {
        return 8;
    }
    
    let fspec = data[0..8].load::<u8>();
    let mut bits_processed = 8;
    
    if fspec & 0x80 != 0 { bits_processed += 16; } // Wind Speed
    if fspec & 0x40 != 0 { bits_processed += 16; } // Wind Direction
    if fspec & 0x20 != 0 { bits_processed += 16; } // Temperature
    if fspec & 0x10 != 0 { bits_processed += 8; }  // Turbulence

    bits_processed
}

fn skip_compound_trajectory_intent(data: &BitSlice<u8, Msb0>) -> usize {
    if data.len() < 8 {
        return 8;
    }
    
    let rep = data[0..8].load::<u8>();
    8 + (rep as usize) * 15 * 8 // 1 octeto REP + N * 15 octetos
}

fn skip_repetitive_mode_s_mb(data: &BitSlice<u8, Msb0>) -> usize {
    if data.len() < 8 {
        return 8;
    }
    
    let rep = data[0..8].load::<u8>();
    8 + (rep as usize) * 8 * 8 // 1 octeto REP + N * 8 octetos
}

/// Decode a CAT21 payload (excluding CAT/LEN header) into strongly typed fields.
pub fn decode_cat21(category: u8, data: &BitSlice<u8, Msb0>) -> Cat21 {
    let mut decoded = Cat21 {
        category,
        ..Default::default()
    };

    let mut pos = 0;
    
    // Decode FSPEC (can have multiple octets)
    let mut fspec_data = Vec::new();
    let mut more_fspec = true;
    
    while more_fspec && pos < data.len() {
        if pos + 8 > data.len() {
            break;
        }

        let fspec_bits = data[pos..pos + 8].to_bitvec();
        for i in 0..7 {
            fspec_data.push(fspec_bits[i]);
        }
        more_fspec = fspec_bits[7];
        pos += 8;
    }

    // Process fields based on FSPEC
    for (frn_idx, &present) in fspec_data.iter().enumerate() {
        if !present {
            continue;
        }

        let frn = frn_idx + 1;

        if pos >= data.len() {
            break;
        }

        match frn {
            1 => {
                // Data Source Identification
                let (sac, sic, bits) = decode_data_source_id(&data[pos..]);
                decoded.sac = Some(sac);
                decoded.sic = Some(sic);
                pos += bits;
            }
            2 => {
                // Target Report Descriptor
                let (atp_desc, arc_desc, rc_desc, rab_desc, gbs_value, bits) = decode_target_report_descriptor(&data[pos..]);
                decoded.atp_description = Some(atp_desc);
                decoded.arc_description = Some(arc_desc);
                decoded.rc_description = Some(rc_desc);
                decoded.rab_description = Some(rab_desc);
                decoded.gbs = gbs_value;
                pos += bits;
            }
            3 => {
                // Track Number - skip
                pos += skip_field(&data[pos..], 2);
            }
            4 => {
                // Service Identification - skip
                pos += skip_field(&data[pos..], 1);
            }
            5 => {
                // Time of Applicability for Position - skip
                pos += skip_field(&data[pos..], 3);
            }
            6 => {
                // Position in WGS-84 Co-ordinates - skip
                pos += skip_field(&data[pos..], 6);
            }
            7 => {
                // Position in WGS-84 Co-ordinates High Resolution
                let (lat, lon, bits) = decode_wgs84_coords_high_res(&data[pos..]);
                decoded.latitude = Some(lat);
                decoded.longitude = Some(lon);
                pos += bits;
            }
            8 => {
                // Time of Applicability for Velocity - skip
                pos += skip_field(&data[pos..], 3);
            }
            9 => {
                // Air Speed
                let (ias, mach, bits) = decode_air_speed(&data[pos..]);
                decoded.ias = ias;
                decoded.mach = mach;
                pos += bits;
            }
            10 => {
                // True Air Speed - skip
                pos += skip_field(&data[pos..], 2);
            }
            11 => {
                // Target Address
                let (address, bits) = decode_target_address(&data[pos..]);
                decoded.icao_address = Some(address);
                pos += bits;
            }
            12 => {
                // Time of Message Reception of Position
                let (time_val, time_string, bits) = decode_time_of_reception_position(&data[pos..]);
                decoded.time_of_reception_position = Some(time_val);
                decoded.utc_time = Some(time_string);
                pos += bits;
            }
            13 => {
                // Time of Message Reception of Position-High Precision - skip
                pos += skip_field(&data[pos..], 4);
            }
            14 => {
                // Time of Message Reception for Velocity - skip
                pos += skip_field(&data[pos..], 3);
            }
            15 => {
                // Time of Message Reception of Velocity-High Precision - skip
                pos += skip_field(&data[pos..], 4);
            }
            16 => {
                // Geometric Height - skip
                pos += skip_field(&data[pos..], 2);
            }
            17 => {
                // Quality Indicators - skip
                pos += skip_variable_fx(&data[pos..]);
            }
            18 => {
                // MOPS Version - skip
                pos += skip_field(&data[pos..], 1);
            }
            19 => {
                // Mode 3/A Code
                let (code, bits) = decode_mode3a_code(&data[pos..]);
                decoded.mode3a_code = Some(code);
                pos += bits;
            }
            20 => {
                // Roll Angle - skip
                pos += skip_field(&data[pos..], 2);
            }
            21 => {
                // Flight Level
                let (fl, bits) = decode_flight_level(&data[pos..]);
                decoded.flight_level = Some(fl);
                decoded.altitude_ft = Some(fl * 100.0);
                decoded.altitude_m = Some(fl * 30.48);
                pos += bits;
            }
            22 => {
                // Magnetic Heading
                let (heading, bits) = decode_magnetic_heading(&data[pos..]);
                decoded.magnetic_heading = Some(heading);
                pos += bits;
            }
            23 => {
                // Target Status
                let (vfi, rab, gbs, nrm, bits) = decode_target_status(&data[pos..]);
                decoded.target_status_vfi = Some(vfi);
                decoded.target_status_rab = Some(rab);
                decoded.target_status_gbs = Some(gbs);
                decoded.target_status_nrm = Some(nrm);
                pos += bits;
            }
            24 => {
                // Barometric Vertical Rate - skip
                pos += skip_field(&data[pos..], 2);
            }
            25 => {
                // Geometric Vertical Rate - skip
                pos += skip_field(&data[pos..], 2);
            }
            26 => {
                // Airborne Ground Vector
                let (ground_speed, track_angle, bits) = decode_airborne_ground_vector(&data[pos..]);
                decoded.ground_speed_kts = Some(ground_speed);
                decoded.track_angle = Some(track_angle);
                pos += bits;
            }
            27 => {
                // Track Angle Rate - skip
                pos += skip_field(&data[pos..], 2);
            }
            28 => {
                // Time of Report Transmission - skip
                pos += skip_field(&data[pos..], 3);
            }
            29 => {
                // Target Identification
                let (ident, bits) = decode_target_identification(&data[pos..]);
                decoded.target_identification = Some(ident);
                pos += bits;
            }
            30 => {
                // Emitter Category - skip
                pos += skip_field(&data[pos..], 1);
            }
            31 => {
                // Met Information - skip
                pos += skip_compound_met_info(&data[pos..]);
            }
            32 => {
                // Selected Altitude - skip
                pos += skip_field(&data[pos..], 2);
            }
            33 => {
                // Final State Selected Altitude - skip
                pos += skip_field(&data[pos..], 2);
            }
            34 => {
                // Trajectory Intent - skip
                pos += skip_compound_trajectory_intent(&data[pos..]);
            }
            35 => {
                // Service Management - skip
                pos += skip_field(&data[pos..], 1);
            }
            36 => {
                // Aircraft Operational Status - skip
                pos += skip_field(&data[pos..], 1);
            }
            37 => {
                // Surface Capabilities and Characteristics - skip
                pos += skip_variable_fx(&data[pos..]);
            }
            38 => {
                // Message Amplitude - skip
                pos += skip_field(&data[pos..], 1);
            }
            39 => {
                // Mode S MB Data - skip
                pos += skip_repetitive_mode_s_mb(&data[pos..]);
            }
            40 => {
                // ACAS Resolution Advisory Report - skip
                pos += skip_field(&data[pos..], 7);
            }
            41 => {
                // Receiver ID - skip
                pos += skip_field(&data[pos..], 1);
            }
            42 => {
                // Data Ages - skip
                pos += skip_variable_fx(&data[pos..]);
            }
            43..=47 => {
                // Not Used
                pos += skip_variable_fx(&data[pos..]);
            }
            48 => {
                // Reserved Expansion Field - skip
                pos += skip_variable_fx(&data[pos..]);
            }
            49 => {
                // Special Purpose Field - skip
                pos += skip_variable_fx(&data[pos..]);
            }
            _ => {
                // Unknown or undefined fields - skip
                break;
            }
        }
    }

    decoded
}