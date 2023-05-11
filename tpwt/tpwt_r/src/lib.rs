mod hello;
mod sac;
mod navi;

use crate::sac::sac_evt_sta::Ses;
use crate::navi::point::Point;
use crate::navi::region::Region;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn tpwt_r(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello::hello, m)?)?;
    m.add_function(wrap_pyfunction!(hello::hello_name, m)?)?;
    m.add_function(wrap_pyfunction!(sac::sac_new, m)?)?;
    m.add_function(wrap_pyfunction!(sac::sac_sens, m)?)?;
    m.add_class::<Ses>()?;
    m.add_class::<Point>()?;
    m.add_class::<Region>()?;
    Ok(())
}
