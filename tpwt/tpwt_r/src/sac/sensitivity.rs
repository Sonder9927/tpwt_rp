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
    let [avgphsens, avgampsens] = sens::smoothed_sensitivity_kernels(freq, amplitude, &sp, smooth);

    // write to file
    let mut f = File::create(sens_file)?;

    // head
    let n = sp.itvl.nx();
    let beg = sp.itvl.x(0);
    let delta = sp.itvl.dx();
    let content = f!(" {n} {beg} {delta} \n");
    f.write_all(content.as_bytes())?;
    f.write_all(content.as_bytes())?;

    // smoothed sens
    let avgsens = sp
        .sens_loop()
        .into_par_iter()
        .map(|[ix, iy]| {
            let x = sp.itvl.x(ix);
            let y = sp.itvl.x(iy);
            let avgph_val = avgphsens[[ix, iy]];
            let avgamp_val = avgampsens[[ix, iy]];
            f!(" {x} {y} {avgph_val:.7e} {avgamp_val:.7e}\n")
        })
        .collect::<Vec<String>>();

    for s in avgsens {
        f.write_all(s.as_bytes())?;
    }

    Ok(())
}
