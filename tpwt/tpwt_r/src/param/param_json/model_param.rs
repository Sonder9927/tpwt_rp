// use ndarray::Array2;
use rayon::prelude::*;
use serde::Deserialize;

use pyo3::prelude::*;

use crate::navi::region::Region;

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct ModelParam {
    pub periods: Vec<i32>,
    pub vels: Vec<f64>,
    // vps: Array2<f64>,
    pub ref_sta: [f64; 2],
    region: Region,
}

impl ModelParam {
    pub fn vp_pairs(&self) -> Vec<(f64, i32)> {
        let v = self.vels.clone();
        let p = self.periods.clone();
        if v.len() == p.len() {
            let vps: Vec<(f64, i32)> = v.into_par_iter().zip(p.into_par_iter()).collect();
            vps
        } else {
            panic!("#vels /= #periods");
        }
    }
    pub fn region(&self) -> Region {
        self.region.clone()
    }
}
