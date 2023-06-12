use geo::line_string;
use geo::LineString;
use ndarray::prelude::*;
use ndarray::ShapeError;
use rayon::prelude::*;

use super::SensParam;

pub fn smoothed_sensitivity_kernels(
    phsens: Array2<f32>,
    ampsens: Array2<f32>,
    sp: &SensParam,
    smooth: i64,
) -> [Array2<f32>; 2] {
    let alpha = 1. / (smooth.pow(2) as f32);

    let xy_pairs = sp.sens_loop();
    let avgsens_vec = xy_pairs
        .into_par_iter()
        .map(|[ix, iy]| {
            let x: f32 = sp.itvl.x(ix);
            let y: f32 = sp.itvl.x(iy);

            // use geo::line_string to make this
            let n = sp.itvl.nx();
            let xy = xy_line_string(ix, iy, n);
            let rx = xy[0].x..xy[1].x;
            let ry = xy[0].y..xy[1].y;
            let shape = (xy[1].x - xy[0].x, xy[1].y - xy[0].y);
            let phsens_part = phsens.slice(s![rx.clone(), ry.clone()]);
            let ampsens_part = ampsens.slice(s![rx.clone(), ry.clone()]);

            let xxyy_pairs: Vec<[usize; 2]> = rx
                .into_par_iter()
                .map(|xx| {
                    let ry = xy[0].y..xy[1].y;
                    ry.into_par_iter()
                        .map(|yy| [xx, yy])
                        .collect::<Vec<[usize; 2]>>()
                })
                .flatten()
                .collect();
            let wgt_vec = xxyy_pairs
                .into_par_iter()
                .map(|[ixx, iyy]| {
                    let xx: f32 = sp.itvl.x(ixx);
                    let yy: f32 = sp.itvl.x(iyy);
                    let distsq: f32 = alpha * ((xx - x).powi(2) + (yy - y).powi(2));
                    if distsq < 80. {
                        (-distsq).exp()
                    } else {
                        0.
                    }
                })
                .collect::<Vec<f32>>();
            let mut wgt_array = Array2::from_shape_vec(shape, wgt_vec).unwrap();
            wgt_array /= wgt_array.sum();
            // calculation below may be slow
            let avgph_val = (&wgt_array * &phsens_part).sum();
            let avgamp_val = (&wgt_array * &ampsens_part).sum();

            [avgph_val, avgamp_val]
        })
        .collect::<Vec<[f32; 2]>>();

    let avgsens = split_sens_vec_to_array2(sp.sens_dimension(), avgsens_vec).unwrap();
    avgsens
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
        .zip(amplitude)
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

    let sens = split_sens_vec_to_array2(sp.sens_dimension(), sens_vec).unwrap();
    sens
}

fn split_sens_vec_to_array2(
    shape: (usize, usize),
    sens_vec: Vec<[f32; 2]>,
) -> Result<[Array2<f32>; 2], ShapeError> {
    let sens_array = Array2::from(sens_vec);
    let phsens = Array2::from_shape_vec(shape, sens_array.column(0).to_vec())?;
    let ampsens = Array2::from_shape_vec(shape, sens_array.column(1).to_vec())?;

    Ok([phsens, ampsens])
}

fn xy_line_string(x: usize, y: usize, n: usize) -> LineString<usize> {
    let limit = 20;
    let xbeg = if x > limit { x - limit } else { 0 };
    let xend = if x + limit < n { x + limit } else { n };
    let ybeg = if y > limit { y - limit } else { 0 };
    let yend = if y + limit < n { y + limit } else { n };

    let line_string = line_string![(x: xbeg, y: ybeg), (x: xend, y: yend)];
    line_string
}
