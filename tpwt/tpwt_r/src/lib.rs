mod hello;
mod mark;
mod navi;

use crate::mark::sac_evt_sta::SES;
use crate::navi::point::Point;
use crate::navi::region::Region;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn tpwt_r(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello::hello, m)?)?;
    m.add_function(wrap_pyfunction!(hello::hello_name, m)?)?;
    m.add_class::<Point>()?;
    m.add_class::<Region>()?;
    m.add_class::<SES>()?;
    Ok(())
}
