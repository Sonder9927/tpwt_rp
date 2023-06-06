use pyo3::prelude::*;
use rayon::prelude::*;
use sacio::Sac;

#[pyfunction]
pub fn sac_sens_new(period: f32, sac_name: &str) {
    // create data
    let b = 0;
    let dt = 1;
    let npts = 2000;
    let pi2 = 2. * std::f32::consts::PI;
    let data = (b..npts)
        .into_par_iter()
        .map(|i| (pi2 * (i as f32) / (1. / period)).cos())
        .collect();

    // create sac file
    let mut sac = Sac::from_amp(data, b as f64, dt as f64);
    sac.to_file(sac_name).unwrap();
}
