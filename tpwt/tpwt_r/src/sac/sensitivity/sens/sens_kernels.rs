use geo::line_string;
use geo::LineString;
use ndarray::prelude::*;
use rayon::prelude::*;

use super::SensParam;

pub fn smoothed_sensitivity_kernels(
    phsens: Array2<f32>,
    ampsens: Array2<f32>,
    sp: &SensParam,
    smooth: i64,
) -> [Array2<f32>; 2] {
    let dim: (usize, usize) = sp.sens_dimension();
    let mut avgphsens = Array2::<f32>::zeros(dim);
    let mut avgampsens = Array2::<f32>::zeros(dim);

    let alpha: f32 = 1. / (smooth.pow(2) as f32);

    let n = sp.itvl.nx();
    for ix in 0..n {
        for iy in 0..n {
            // let x: f32 = sp.itvl_x(ix);
            // let y: f32 = sp.itvl_x(ix);
            let mut wgttemp = Array2::<f32>::zeros(dim);

            // use geo::line_string to make this
            let xy = xy_line_string(ix, iy, n);

            for ixx in xy[0].x..xy[1].x {
                for iyy in xy[0].y..xy[1].y {
                    let xx: f32 = sp.itvl_x(ixx);
                    let yy: f32 = sp.itvl_x(iyy);
                    let distsq: f32 = alpha * ((xx).powi(2) + (yy).powi(2));
                    if distsq < 80. {
                        let v = (-distsq).exp();
                        wgttemp[[ixx, iyy]] = v;
                    }
                }
            }
            wgttemp /= wgttemp.sum();

            // for ixx in xy[0].x..xy[1].x {
            //     for iyy in xy[0].y..xy[1].y {
            //         avgphsens[[ix, iy]] += phsens[[ixx, iyy]] * wgttemp[[ixx, iyy]] / wgtsum;
            //         avgampsens[[ix, iy]] += ampsens[[ixx, iyy]] * wgttemp[[ixx, iyy]] / wgtsum;
            //     }
            // }
            avgphsens[[ix, iy]] += (phsens.clone() * wgttemp.clone()).sum();
            avgampsens[[ix, iy]] += (ampsens.clone() * wgttemp).sum();
        }
    }

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
    let radius = 6371.0_f32;

    let dim = sp.sens_dimension();
    let mut phsens = Array2::<f32>::zeros(dim);
    let mut ampsens = Array2::<f32>::zeros(dim);

    for (&ifreq, &iamp) in freq.iter().zip(amplitude.iter()) {
        let period = 1. / ifreq;
        let lambda = period * sp.phvel;
        let kk = 2. * pi / lambda * radius;
        let n: usize = sp.itvl.nx();
        let dx2: f32 = sp.itvl.dx().powi(2);
        for ix in 0..n {
            let x: f32 = sp.itvl_x(ix);
            let delta1 = x;
            for iy in 0..n {
                let y: f32 = sp.itvl_x(iy);
                let delta2 = if delta1 == 0. && y == 0. {
                    (dx2 * 2.).sqrt()
                } else {
                    // (x.powi(2) + y.powi(2)).sqrt()
                    x.hypot(y)
                };

                // let angle: f32 = (-y).atan2(-x) * 180. / pi;
                // let angle = if angle < 0. { angle } else { angle + 360. };
                // let iangle = angle as i32;

                phsens[[ix, iy]] += (-2. * iamp * kk.powi(2))
                    * (kk * (delta1 + delta2) / radius + pi / 4.).sin()
                    / (8. * pi * kk * ((delta2 / radius).sin()).abs()).sqrt()
                    * (dx2 / radius.powi(2));

                ampsens[[ix, iy]] += (-2. * iamp * kk.powi(2))
                    * (kk * (delta1 + delta2) / radius + pi / 4.).cos()
                    / (8. * pi * kk * ((delta2 / radius).sin()).abs()).sqrt()
                    * (dx2 / radius.powi(2));
            }
        }
    }

    [phsens, ampsens]
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
