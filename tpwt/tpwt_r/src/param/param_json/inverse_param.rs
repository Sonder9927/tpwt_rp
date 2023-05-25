use serde::Deserialize;

use pyo3::prelude::*;

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct InverseParam {
    pub smooth: i32,
    pub damping: f64,
}
