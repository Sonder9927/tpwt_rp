mod sac_peak;
mod sens;

use pyo3::prelude::*;

use rayon::prelude::*;
use sacio::Sac;
use std::fs::File;
use std::io::Write;

#[pyfunction]
pub fn sac_sens_new_period(sac_name: &str, period: f32) {
    // create data
    let b = 0;
    let dt = 1;
    let npts = 2000;
    let pi2 = 2. * std::f32::consts::PI;
    let data = (b..npts)
        .into_par_iter()
        .map(|i| (pi2 * (i as f32) / period).cos())
        .collect();

    // create sac file
    let mut sac = Sac::from_amp(data, b as f64, dt as f64);
    sac.to_file(sac_name).unwrap();
}

#[pyfunction]
pub fn sac_sens(sac_file: &str, phvel: f32, smooth: i64, sens_file: &str) -> PyResult<()> {
    let [freq, amplitude] = sac_peak::get_peak_data(sac_file);

    let sp = sens::SensParam::new(phvel, smooth);
    let [phsens, ampsens] = sens::_unsmoothed_sensitivity_kernels(freq, amplitude, &sp);
    let [avgphsens, avgampsens] = sens::smoothed_sensitivity_kernels(phsens, ampsens, &sp, smooth);

    // write to file
    let mut f = File::create(sens_file)?;

    let n = sp.itvl.nx();
    let nn = n as i32;
    let beg = sp.itvl.x(0);
    let delta = sp.itvl.dx();
    let content = f!(" {nn} {beg} {delta} \n");
    f.write(content.as_bytes())?;
    f.write(content.as_bytes())?;

    for ix in 0..n {
        let x = sp.itvl.x(ix);
        for iy in 0..n {
            let y = sp.itvl.x(iy);
            let phv = avgphsens[[ix, iy]];
            let ampv = avgampsens[[ix, iy]];
            let content = f!(" {x} {y} {phv:.7e} {ampv:.7e}\n");
            f.write(content.as_bytes())?;
        }
    }

    Ok(())
}
