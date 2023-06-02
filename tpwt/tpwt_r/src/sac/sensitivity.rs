pub mod sens;
pub mod sac_peak;

use pyo3::prelude::*;

use std::fs::File;
use std::io::Write;
use std::path::Path;

#[pyfunction]
pub fn sac_sens(sac_file: &str, phvel: f32, smooth: i64, sens_file: &str) -> PyResult<()> {
    let [freq, amplitude] = sac_peak::get_peak_data(sac_file);
    // let res: Vec<(f32, f32)> = freq.into_iter().zip(amplitude.into_iter()).collect();
    // Ok(res)
    // let nfreq = freq.len();

    let sp = sens::SensParam::new(phvel, smooth);
    let [phsens, ampsens] = sens::_unsmoothed_sensitivity_kernels(freq, amplitude, &sp);
    let [avgphsens, avgampsens] = sens::smoothed_sensitivity_kernels(phsens, ampsens, &sp, smooth);

    // let sumamp: f32 = amplitude.iter().sum();
    // let amplitude: Vec<f32> = amplitude.iter().map(|x| x / sumamp).collect();
    // let x_itvl = interval::Interval::new(-1500., 1500., 10.);
    // let x_n: usize = x_itvl.n();
    // let y_itvl = interval::Interval::new(-1500., 1500., 10.);
    // let y_n: usize = y_itvl.n();

    // let maxix = 400;
    // let maxiy = 400;
    // let mut phsens = Array2::<f32>::zeros((maxix, maxiy));
    // let mut avgphsens = Array2::<f32>::zeros((maxix, maxiy));
    // let mut ampsens = Array2::<f32>::zeros((maxix, maxiy));
    // let mut avgampsens = Array2::<f32>::zeros((maxix, maxiy));
    // let mut wgttemp = Array2::<f32>::zeros((maxix, maxiy));

    // let pi = std::f32::consts::PI;
    // let radius = 6371 as f32;
    // for (&ifreq, &iamp) in freq.iter().zip(amplitude.iter()) {
    //     let period = 1. / ifreq;
    //     let lambda = period * phvel;
    //     let kk = 2. * pi / lambda * radius;
    //     for ix in 0..x_n {
    //         let x: f32 = x_itvl.x(ix);
    //         let delta1 = x;
    //         for iy in 0..y_n {
    //             let y: f32 = y_itvl.x(iy);
    //             let delta2 = if delta1 == 0. && y == 0. {
    //                 (x_itvl.dx().powi(2) + y_itvl.dx().powi(2)).sqrt()
    //             } else {
    //                 (x.powi(2) + y.powi(2)).sqrt()
    //             };

    //             // let angle: f32 = (-y).atan2(-x) * 180. / pi;
    //             // let angle = if angle < 0. { angle } else { angle + 360. };
    //             // let iangle = angle as i32;

    //             phsens[[ix, iy]] += (-2. * iamp * kk.powi(2))
    //                 * (kk * (delta1 + delta2) / radius + pi / 4.).sin()
    //                 / (8. * pi * kk * ((delta2 / radius).sin()).abs()).sqrt()
    //                 * (x_itvl.dx() * y_itvl.dx() / radius.powi(2));

    //             ampsens[[ix, iy]] += (-2. * iamp * kk.powi(2))
    //                 * (kk * (delta1 + delta2) / radius + pi / 4.).cos()
    //                 / (8. * pi * kk * ((delta2 / radius).sin()).abs()).sqrt()
    //                 * (x_itvl.dx() * y_itvl.dx() / radius.powi(2));
    //         }
    //     }
    // }

    // // unsmoothed sensitivity kernels saved to `sens_file`
    // let unsmoothed_file = Path::new("smooth.dat");
    // let content = "301 -1500. 10.";
    // let content1 = (x_n, y_n, phsens, ampsens);

    // smooth

    let out_path = Path::new(sens_file);
    let mut f = File::create(out_path)?;
    let content = "301 -1500. 10.\n301 -1500. 10.\n";

    f.write_all(content.as_bytes())?;

    // let alpha: f32 = 1. / (smooth.pow(2) as f32);

    let n = sp.itvl.nx();
    for ix in 0..n {
        for iy in 0..n {
            let x: f32 = sp.itvl_x(ix);
            let y: f32 = sp.itvl_x(iy);
            // let mut wgtsum = 0.;

            // // use geo::line_string to make this
            // let xy = interval::xy_line_string(ix, iy, x_n, y_n);

            // for ixx in xy[0].x..xy[1].x {
            //     for iyy in xy[0].y..xy[1].y {
            //         let xx: f32 = x_itvl.x(ixx);
            //         let yy: f32 = y_itvl.x(iyy);
            //         let distsq: f32 = alpha * ((xx).powi(2) + (yy).powi(2));
            //         if distsq < 80. {
            //             let v = (-distsq).exp();
            //             wgttemp[[ixx, iyy]] = v;
            //             wgtsum += v;
            //         }
            //     }
            // }
            // for ixx in xy[0].x..xy[1].x {
            //     for iyy in xy[0].y..xy[1].y {
            //         avgphsens[[ix, iy]] += phsens[[ixx, iyy]] * wgttemp[[ixx, iyy]] / wgtsum;
            //         avgampsens[[ix, iy]] += ampsens[[ixx, iyy]] * wgttemp[[ixx, iyy]] / wgtsum;
            //     }
            // }
            
            let content = format!(
                "{:.3} {:.3} {:e} {:e}\n",
                x,
                y,
                avgphsens[[ix, iy]],
                avgampsens[[ix, iy]]
            );

            f.write_all(content.as_bytes())?;
        }
    }

    Ok(())
}
