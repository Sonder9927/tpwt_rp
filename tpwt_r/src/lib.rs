mod clip;
mod hello;

use crate::clip::point::Point;
use crate::clip::region::Region;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn tpwt_r(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello::hello, m)?)?;
    m.add_function(wrap_pyfunction!(hello::hello_name, m)?)?;
    m.add_class::<Point>()?;
    m.add_class::<Region>()?;
    Ok(())
}
