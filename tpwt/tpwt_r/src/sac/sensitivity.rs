pub mod sens;
pub mod sac_peak;

use pyo3::prelude::*;

use rayon::prelude::*;
use std::path::Path;
use std::io::Write;
use std::fs::File;
use sacio::Sac;

#[pyfunction]
pub fn sac_sens_new_period(sac_name: &str, period: f32) {
    // create data
    let b = 0;
    let dt = 1;
    let npts = 2000;
    let pi2 = 2. * std::f32::consts::PI;
    let data = (b..npts)
        .into_iter()
        .map(|i| (pi2 * (i as f32) / period).cos())
        .collect();

    // create sac file
    let mut sac = Sac::from_amp(data, b as f64, dt as f64);
    sac.to_file(sac_name).unwrap();
}
#[pyfunction]
pub fn sac_sens(sac_file: &str, phvel: f32, smooth: i64, sens_file: &str) -> PyResult<()> {
    let [freq, amplitude] = sac_peak::get_peak_data(sac_file);
    println_f!("freq:\n{freq:?}");
    println_f!("amplitude:\n{amplitude:?}");

    // let sp = sens::SensParam::new(phvel, smooth);
    // let [phsens, ampsens] = sens::_unsmoothed_sensitivity_kernels(freq, amplitude, &sp);
    // let [avgphsens, avgampsens] = sens::smoothed_sensitivity_kernels(phsens, ampsens, &sp, smooth);

    Ok(())
}
