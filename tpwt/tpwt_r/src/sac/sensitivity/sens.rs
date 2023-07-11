pub mod sens_param;
mod smooth_kernel;

use ndarray::ShapeError;
use rayon::prelude::*;
pub use sens_param::SensParam;

use ndarray::prelude::*;

pub fn smoothed_sensitivity_kernels(
    freq: Vec<f32>,
    amplitude: Vec<f32>,
    sp: &SensParam,
    smooth: i64,
) -> [Array2<f32>; 2] {
    let [phsens, ampsens] = _unsmoothed_sensitivity_kernels(freq, amplitude, sp);

    let smoother = smooth_kernel::SmoothKernel::new(smooth, sp.itvl.dx());
    let avgphsens = smoother.forward(phsens.view());
    let avgampsens = smoother.forward(ampsens.view());

    [avgphsens, avgampsens]
}

pub fn _unsmoothed_sensitivity_kernels(
    freq: Vec<f32>,
    amplitude: Vec<f32>,
    sp: &SensParam,
) -> [Array2<f32>; 2] {
    let sumamp = amplitude.par_iter().sum::<f32>();
    let amplitude: Vec<f32> = amplitude.par_iter().map(|x| x / sumamp).collect();

    let pi = std::f32::consts::PI;
    let frac_pi_4 = std::f32::consts::FRAC_PI_4;
    let radius = 6371.0_f32;

    let kk_amp: Vec<_> = freq
        .into_par_iter()
        .zip(amplitude.into_par_iter())
        .map(|(ifreq, iamp)| {
            let period = 1. / ifreq;
            let lambda = period * sp.phvel;
            let kk = 2. * pi / lambda.floor() * radius; // use lambda.floor() is very important.
            (kk, iamp)
        })
        .collect();

    let dx2: f32 = sp.itvl.dx().powi(2);
    let xy_pairs = sp.sens_loop();
    let sens_vec = xy_pairs
        .into_par_iter()
        .map_with(kk_amp, |ka, [ix, iy]| {
            let x: f32 = sp.itvl.x(ix);
            let delta1 = x;
            let y: f32 = sp.itvl.x(iy);
            let delta2 = if x == 0. && y == 0. {
                (dx2 * 2.).sqrt()
            } else {
                x.hypot(y) // which is equal to `(x.powi(2) + y.powi(2)).sqrt()`
            };
            let ph_amp_vals: Vec<[f32; 2]> = ka
                .par_iter()
                .map(|(ik, iamp)| {
                    let ph_val = (-2. * iamp * ik.powi(2))
                        * (ik * (delta1 + delta2) / radius + frac_pi_4).sin()
                        / (8. * pi * ik * (delta2 / radius).sin().abs()).sqrt()
                        * (dx2 / radius.powi(2));
                    let amp_val = (-2. * iamp * ik.powi(2))
                        * (ik * (delta1 + delta2) / radius + frac_pi_4).cos()
                        / (8. * pi * ik * (delta2 / radius).sin().abs()).sqrt()
                        * (dx2 / radius.powi(2));

                    [ph_val, amp_val]
                })
                .collect();
            let ph_amp_val = Array2::from(ph_amp_vals).sum_axis(Axis(0));
            let ph_val = ph_amp_val.get(0).unwrap();
            let amp_val = ph_amp_val.get(1).unwrap();
            [*ph_val, *amp_val]
        })
        .collect::<Vec<[f32; 2]>>();

    split_sens_vec_to_array2(sp.sens_dimension(), sens_vec).unwrap()
}

pub fn split_sens_vec_to_array2(
    shape: (usize, usize),
    sens_vec: Vec<[f32; 2]>,
) -> Result<[Array2<f32>; 2], ShapeError> {
    let sens_array = Array2::from(sens_vec);
    let phsens = Array2::from_shape_vec(shape, sens_array.column(0).to_vec())?;
    let ampsens = Array2::from_shape_vec(shape, sens_array.column(1).to_vec())?;

    Ok([phsens, ampsens])
}
