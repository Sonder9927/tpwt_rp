mod filter_param;
mod inverse_param;
mod model_param;
mod target_param;

use filter_param::FilterParam;
use inverse_param::InverseParam;
use model_param::ModelParam;
use target_param::{ParamString, TargetParam};

use rayon::prelude::*;
use serde::Deserialize;
use serde_json;

use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;
// use std::error::Error;
use std::fs::File;
use std::io::BufReader;
// use std::path::Path;

#[pyfunction]
pub fn load_param(path: &str) -> PyResult<Param> {
    println_f!("Loading Param from file {path}...");
    // deserialize param from json file.
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let p = serde_json::from_reader(reader).unwrap();
    println!("Loading completed!");
    Ok(p)
}

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct Param {
    inverse: InverseParam,
    filter: FilterParam,
    targets: TargetParam,
    model: ModelParam,
}

#[pymethods]
impl Param {
    // inverse
    pub fn damping(&self) -> PyResult<f64> {
        Ok(self.inverse.damping)
    }
    pub fn smooth(&self) -> PyResult<i32> {
        Ok(self.inverse.smooth)
    }

    // filter
    pub fn snr(&self) -> PyResult<i32> {
        Ok(self.filter.snr)
    }
    pub fn tcut(&self) -> PyResult<i32> {
        Ok(self.filter.tcut)
    }
    pub fn time_delta(&self) -> PyResult<i32> {
        Ok(self.filter.time_delta)
    }
    pub fn dist(&self) -> PyResult<i32> {
        Ok(self.filter.dist)
    }
    pub fn nsta(&self) -> PyResult<i32> {
        Ok(self.filter.nsta)
    }
    pub fn stacut_per(&self) -> PyResult<f64> {
        Ok(self.filter.stacut_per)
    }
    pub fn ampcut(&self) -> PyResult<f64> {
        Ok(self.filter.ampcut)
    }
    pub fn tevtrmscut(&self) -> PyResult<f64> {
        Ok(self.filter.tevtrmscut)
    }
    pub fn ampevtrmscut(&self) -> PyResult<f64> {
        Ok(self.filter.ampevtrmscut)
    }
    pub fn dcheck(&self) -> PyResult<f64> {
        Ok(self.filter.dcheck)
    }
    pub fn dvel(&self) -> PyResult<f64> {
        Ok(self.filter.dvel)
    }
    pub fn channel(&self) -> PyResult<String> {
        Ok(self.filter.channel.to_string())
    }

    // targets
    pub fn target(&self, f: &str) -> PyResult<&str> {
        match f {
            "og_data" => Ok(self.targets.get(ParamString::OgData)),
            "evt30" => Ok(self.targets.get(ParamString::Evt30)),
            "evt120" => Ok(self.targets.get(ParamString::Evt120)),
            "evt_cat" => Ok(self.targets.get(ParamString::EvtCat)),
            "evt_lst" => Ok(self.targets.get(ParamString::EvtLst)),
            "sta_lst" => Ok(self.targets.get(ParamString::StaLst)),
            "cut_dir" => Ok(self.targets.get(ParamString::CutDir)),
            "sac" => Ok(self.targets.get(ParamString::Sac)),
            "path" => Ok(self.targets.get(ParamString::Path)),
            "all_events" => Ok(self.targets.get(ParamString::AllEvents)),
            "sens" => Ok(self.targets.get(ParamString::Sens)),
            "state" => Ok(self.targets.get(ParamString::State)),
            _ => Err(PyKeyError::new_err("Key Error!")),
        }
    }
    // model
    pub fn vps(&self) -> PyResult<Vec<(f64, i32)>> {
        let v = self.model.vels.clone();
        let p = self.model.periods.clone();
        let vps: Vec<(f64, i32)> = v.into_par_iter().zip(p.into_par_iter()).collect();
        Ok(vps)
    }
    pub fn region(&self) -> PyResult<[f64; 4]> {
        self.model.region.to_list()
    }
    pub fn ref_sta(&self) -> PyResult<[f64; 2]> {
        Ok(self.model.ref_sta)
    }
}
