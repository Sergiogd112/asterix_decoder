use bitvec::prelude::*;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde_json::Value;
use std::fs::File;
use std::io::Read;

mod cat21;
mod cat48;
mod geoutils;
use geoutils::CoordinatesWGS84;

fn json_to_py(py: Python, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(b.to_object(py)),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.to_object(py))
            } else if let Some(f) = n.as_f64() {
                Ok(f.to_object(py))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Invalid number",
                ))
            }
        }
        Value::String(s) => Ok(s.to_object(py)),
        Value::Array(a) => {
            let list = PyList::empty_bound(py);
            for item in a {
                list.append(json_to_py(py, item)?)?;
            }
            Ok(list.to_object(py))
        }
        Value::Object(o) => {
            let dict = PyDict::new_bound(py);
            for (key, value) in o {
                dict.set_item(key, json_to_py(py, value)?)?;
            }
            Ok(dict.to_object(py))
        }
    }
}

#[pyfunction(
    signature = (file_path, radar_lat, radar_lon, radar_alt, max_messages=None, debug_save_path=None)
)]
fn load(
    py: Python,
    file_path: String,
    radar_lat: f64,
    radar_lon: f64,
    radar_alt: f64,
    max_messages: Option<usize>,
    debug_save_path: Option<String>,
) -> PyResult<PyObject> {
    let mut file = File::open(file_path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let radar_coords = CoordinatesWGS84 {
        lat: radar_lat,
        lon: radar_lon,
        height: radar_alt,
    };

    let bv = buffer.view_bits::<Msb0>();
    let mut json_results: Vec<Value> = Vec::new();
    let mut current_pos = 0;
    let total_bits = bv.len();
    let mut message_count = 0;

    while current_pos + 24 <= total_bits {
        if let Some(max) = max_messages {
            if message_count >= max {
                break;
            }
        }

        let cat = bv[current_pos..current_pos + 8].load_be::<u8>();
        let length = bv[current_pos + 8..current_pos + 24].load_be::<u16>();

        if length < 3 {
            break;
        }

        let data_end = current_pos + (length as usize) * 8;

        if data_end > total_bits {
            break;
        }

        let data_slice = &bv[current_pos + 24..data_end];

        let json_value = match cat {
            21 => {
                let decoded = cat21::decode_cat21(data_slice);
                Some(serde_json::to_value(decoded).unwrap())
            }
            48 => {
                let decoded = cat48::decode_cat48(data_slice, Some(radar_coords));
                Some(serde_json::to_value(decoded).unwrap())
            }
            _ => None,
        };

        if let Some(value) = json_value {
            json_results.push(value);
            message_count += 1;
        }

        current_pos = data_end;
    }

    if let Some(path) = debug_save_path {
        let out_file = File::create(path)?;
        serde_json::to_writer_pretty(out_file, &json_results).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write debug file: {}", e))
        })?;
    }

    let list = PyList::empty_bound(py);
    for value in json_results {
        list.append(json_to_py(py, &value)?)?;
    }

    Ok(list.to_object(py))
}

/// A Python module implemented in Rust.
#[pymodule]
fn decoderrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load, m)?)?;
    Ok(())
}
