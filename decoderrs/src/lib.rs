use bitvec::prelude::*;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde_json::Value;
use std::fs::File;
use std::io::Read;

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

#[pyfunction(signature = (file_path, radar_lat, radar_lon, radar_alt, max_messages=None))]
fn load(
    py: Python,
    file_path: String,
    radar_lat: f64,
    radar_lon: f64,
    radar_alt: f64,
    max_messages: Option<usize>,
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
    let list = PyList::empty_bound(py);
    let mut current_pos = 0;
    let total_bits = bv.len();
    let mut message_count = 0;

    while current_pos + 24 <= total_bits {
        if let Some(max) = max_messages {
            if message_count >= max {
                break;
            }
        }

        let cat = bv[current_pos..current_pos + 8].load::<u8>();
        let length = bv[current_pos + 8..current_pos + 24].load::<u16>();

        if length < 3 {
            break;
        }

        let data_end = current_pos + (length as usize) * 8;

        if data_end > total_bits {
            break;
        }

        let data_slice = &bv[current_pos + 24..data_end];

        let decoded_message = match cat {
            48 => {
                let decoded = cat48::decode_cat48(data_slice, Some(radar_coords));
                let json_value = serde_json::to_value(decoded).unwrap();
                json_to_py(py, &json_value)?
            }
            _ => py.None(),
        };

        if !decoded_message.is_none(py) {
            list.append(decoded_message)?;
            message_count += 1;
        }

        current_pos = data_end;
    }

    Ok(list.to_object(py))
}

/// A Python module implemented in Rust.
#[pymodule]
fn decoderrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load, m)?)?;
    Ok(())
}
