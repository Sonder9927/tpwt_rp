use serde::Deserialize;

use pyo3::prelude::*;

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct FilterParam {
    pub snr: i32,
    pub tcut: i32,
    pub time_delta: i32,
    pub dist: i32,
    pub nsta: i32,
    pub stacut_per: f64,
    pub ampcut: f64,
    pub tevtrmscut: f64,
    pub ampevtrmscut: f64,
    pub channel: String,
    pub dcheck: f64,
    pub dvel: f64,
}
