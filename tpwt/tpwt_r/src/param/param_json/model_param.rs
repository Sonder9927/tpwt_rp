use serde::Deserialize;

use pyo3::prelude::*;

use crate::navi::region::Region;

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct ModelParam {
    pub periods: Vec<i32>,
    pub vels: Vec<f64>,
    pub region: Region,
    pub ref_sta: [f64; 2],
}

