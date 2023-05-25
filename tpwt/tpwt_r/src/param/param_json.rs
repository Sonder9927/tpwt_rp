use serde::Deserialize;
use serde_json;

use pyo3::prelude::*;
use std::collections::HashMap;
// use std::error::Error;
use std::fs::File;
use std::io::BufReader;
// use std::path::Path;

#[pyfunction]
pub fn load_param(path: &str) -> PyResult<Param> {
    // deserialize param from json file.
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let p = serde_json::from_reader(reader).unwrap();
    Ok(p)
}

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct Param {
    files: HashMap<String, String>,
    vels: HashMap<i32, f64>,
}

impl Param {
    pub fn file(&self, f: &str) -> &str {
        &self.files[f]
    }
    pub fn vel(&self, per: i32) -> f64 {
        self.vels[&per]
    }
}
