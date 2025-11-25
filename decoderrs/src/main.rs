use serde::Serialize;
use std::env;
use std::fs::File;
use std::io::Read;
use std::time::Instant;

use bitvec::prelude::*;

mod cat21;
mod cat48;
mod geoutils;

use geoutils::CoordinatesWGS84;

/// Union type storing either CAT21 or CAT48 decoded payloads.
#[derive(Debug, Serialize)]
#[serde(untagged)]
enum AsterixMessage {
    Cat21(Box<cat21::Cat21>),
    Cat48(Box<cat48::Cat48>),
}

/// Parse CLI flags that control which datasets to decode and optional limits.
fn parse_args() -> (bool, bool, bool, bool, Option<usize>) {
    let mut test_radar = false;
    let mut test_adsb = false;
    let mut test_all = false;
    let mut parallel = false; // currently unused, kept for parity with Python
    let mut max_messages: Option<usize> = None;

    let mut args = env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--test-radar" => test_radar = true,
            "--test-adsb" => test_adsb = true,
            "--test-all" => test_all = true,
            "--parallel" => parallel = true,
            "--max-messages" => {
                if let Some(val) = args.next() {
                    if let Ok(n) = val.parse::<usize>() {
                        max_messages = Some(n);
                    }
                }
            }
            _ => {}
        }
    }

    (test_radar, test_adsb, test_all, parallel, max_messages)
}

/// Decode every ASTERIX message in a capture file into strongly typed enums.
fn load_from_file(
    file_path: &str,
    radar_coords: CoordinatesWGS84,
    max_messages: Option<usize>,
) -> Result<Vec<AsterixMessage>, Box<dyn std::error::Error>> {
    let mut f = File::open(file_path)?;
    let mut buffer = Vec::new();
    f.read_to_end(&mut buffer)?;

    let bv = buffer.view_bits::<Msb0>();
    let mut results: Vec<AsterixMessage> = Vec::new();

    let mut current_pos = 0usize;
    let total_bits = bv.len();
    println!("Total bits in file: {}", total_bits);
    let mut message_count = 0usize;

    while current_pos + 24 <= total_bits {
        if let Some(max) = max_messages {
            if message_count >= max {
                break;
            }
        }

        let cat = bv[current_pos..current_pos + 8].load_be::<u8>();
        let length_bits = &bv[current_pos + 8..current_pos + 24];

        // Extract the 15-bit length value by interpreting as 16-bit big-endian and masking out MSB
        let length = length_bits.load_be::<u16>() & 0x7FFF;

        if length < 3 {
            break;
        }

        let data_end = current_pos + (length as usize) * 8;
        if data_end > total_bits {
            break;
        }

        let data_slice = &bv[current_pos + 24..data_end];

        match cat {
            21 => {
                let decoded = cat21::decode_cat21(cat, data_slice);
                results.push(AsterixMessage::Cat21(Box::new(decoded)));
                message_count += 1;
            }
            48 => {
                let decoded = cat48::decode_cat48(cat, data_slice, Some(radar_coords));
                results.push(AsterixMessage::Cat48(Box::new(decoded)));
                message_count += 1;
            }
            _ => {
                // unsupported category; skip
            }
        }

        current_pos = data_end;
    }
    println!("Total messages decoded: {}", message_count);
    Ok(results)
}

/// Entry point that mirrors the Python benchmarks and writes JSON snapshots.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (test_radar, test_adsb, test_all, _parallel, max_messages) = parse_args();

    println!("Test Radar: {}", test_radar);
    println!("Test ADS-B: {}", test_adsb);
    println!("Test All: {}", test_all);

    let start = Instant::now();

    // Radar coordinates: convert degrees to radians like Python
    let radar_lat = (41.0 + 18.0 / 60.0 + 2.5184 / 3600.0) * std::f64::consts::PI / 180.0;
    let radar_lon = (2.0 + 6.0 / 60.0 + 7.4095 / 3600.0) * std::f64::consts::PI / 180.0;
    let radar_alt = 27.25_f64;
    let coords_radar = CoordinatesWGS84 {
        lat: radar_lat,
        lon: radar_lon,
        height: radar_alt,
    };

    let mut decoded_messages: Vec<AsterixMessage> = Vec::new();

    if test_radar {
        decoded_messages = load_from_file(
            "../Test_Data/datos_asterix_radar.ast",
            coords_radar,
            max_messages,
        )?;
    }
    if test_adsb {
        decoded_messages = load_from_file(
            "../Test_Data/datos_asterix_adsb.ast",
            coords_radar,
            max_messages,
        )?;
    }
    if test_all {
        decoded_messages = load_from_file(
            "../Test_Data/datos_asterix_combinado.ast",
            coords_radar,
            max_messages,
        )?;
    }

    println!("Decoded {} messages", decoded_messages.len());
    println!("Elapsed Time: {} s", start.elapsed().as_secs_f64());

    // Export to JSON file for now (pretty-printed)
    let out_file = File::create("decoded_from_rust.json")?;
    serde_json::to_writer_pretty(out_file, &decoded_messages)?;
    println!("Wrote decoded messages to decoded_from_rust.json");

    Ok(())
}
