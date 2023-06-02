pub struct SensParam {
    pub phvel: f32,
    pub smooth: i64,
    pub itvl: Interval,
    imax: usize,
}

impl SensParam {
    pub fn new(phvel: f32, smooth: i64) -> Self {
        // default
        let imax = 400;
        let itvl = Interval::new(-1500., 1500., 10.);

        SensParam {
            phvel,
            smooth,
            itvl,
            imax,
        }
    }

    pub fn itvl_x(&self, x: usize) -> f32 {
        self.itvl.x(x)
    }

    pub fn sens_dimension(&self) -> (usize, usize) {
        (self.imax, self.imax)
    }
}

// divide

pub struct Interval {
    begin: f32,
    end: f32,
    delta: f32,
}

impl Interval {
    pub fn new(begin: f32, end: f32, delta: f32) -> Self {
        Interval { begin, end, delta }
    }

    pub fn dx(&self) -> f32 {
        self.delta
    }

    pub fn nx(&self) -> usize {
        (((self.end - self.begin) / self.delta) as i64 + 1) as usize
    }

    pub fn x(&self, id: usize) -> f32 {
        id as f32 * self.delta + self.begin
    }
}