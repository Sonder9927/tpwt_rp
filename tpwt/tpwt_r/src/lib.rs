mod hello;
mod navi;
mod param;
mod sac;

use crate::navi::Point;
use crate::navi::Region;
use crate::sac::Ses;

use pyo3::prelude::*;

#[macro_use]
extern crate fstrings;

/// A Python module implemented in Rust.
#[pymodule]
fn tpwt_r(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello::hello, m)?)?;
    m.add_function(wrap_pyfunction!(hello::hello_name, m)?)?;

    m.add_function(wrap_pyfunction!(sac::sac_sens_new_period, m)?)?;
    m.add_function(wrap_pyfunction!(sac::sac_sens, m)?)?;

    m.add_function(wrap_pyfunction!(navi::geo_xyz::convex_hull, m)?)?;
    m.add_function(wrap_pyfunction!(navi::geo_xyz::points_in_hull, m)?)?;

    m.add_function(wrap_pyfunction!(param::load_param, m)?)?;
    m.add_class::<Ses>()?;
    m.add_class::<Point>()?;
    m.add_class::<Region>()?;
    Ok(())
}
