use sacio::Sac;

pub fn get_peak_data(sac_file: &str) -> [Vec<f32>; 2] {
    let sac = Sac::from_file(sac_file).unwrap();

    let npts = sac.npts() as usize;
    let b = sac.b();
    let del = sac.delta();
    let y = sac.y;

    let mut peak: f32 = y[0];
    let mut ipeak: usize = b as usize;
    for (idx, &val) in y.iter().enumerate() {
        if val > peak {
            peak = val;
            ipeak = idx;
        }
    }

    // get ip1
    let begin: usize = if ipeak < (b + 140.0) as usize {
        b as usize
    } else {
        ipeak - 140
    };
    let mut y_left = Vec::from(&y[begin..ipeak]);
    y_left.reverse();
    let ip1 = ipeak - get_ip(y_left);
    // get ip2
    let end: usize = if ipeak + 140 > npts {
        npts
    } else {
        ipeak + 140
    };
    let y_right = Vec::from(&y[ipeak..end]);
    let ip2 = ipeak + get_ip(y_right);

    let peak_id: Vec<f32> = (ip1..ip2).map(|ip| b + (ip as f32) * del).collect();
    let peak_val = Vec::from(&y[ip1..ip2]);

    [peak_id, peak_val]
}

fn get_ip(y: Vec<f32>) -> usize {
    let mut ip: usize = 0;
    for i in 1..y.len() {
        ip = i + 1;
        if y[i + 1] > y[i] {
            break;
        }
    }
    ip
}
