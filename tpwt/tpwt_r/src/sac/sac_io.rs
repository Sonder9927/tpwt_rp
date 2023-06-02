use pyo3::prelude::*;
use sacio::Sac;

#[pyfunction]
pub fn sac_new(sac_name: &str, data: Vec<f32>, b: f64, dt: f64) {
    let mut sac = Sac::from_amp(data, b, dt);
    let _ = sac.to_file(sac_name);
}
