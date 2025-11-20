use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::fs::File;
use std::io::Read;
use bitvec::prelude::*;
use serde_json::Value;

mod cat48;

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

#[pyfunction]
fn load(py: Python, file_path: String) -> PyResult<PyObject> {
    let mut file = File::open(file_path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let bv = buffer.view_bits::<Msb0>();
    let list = PyList::empty_bound(py);
    let mut current_pos = 0;
    let total_bits = bv.len();

    while current_pos + 24 <= total_bits {
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
                let decoded = cat48::decode_cat48(data_slice);
                let json_value = serde_json::to_value(decoded).unwrap();
                json_to_py(py, &json_value)?
            }
            _ => py.None(),
        };

        if !decoded_message.is_none(py) {
            list.append(decoded_message)?;
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
