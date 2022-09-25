use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}
#[pyfunction]
fn hello() {
    println!("Hello, this is tpwt using Rust from Python!")
}
#[pyfunction]
fn hello_name(name: &str) -> PyResult<String> {
    Ok("Hello, ".to_owned() + name + "!")
}

/// A Python module implemented in Rust.
#[pymodule]
fn tpwt_rp(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    m.add_function(wrap_pyfunction!(hello_name, m)?)?;
    Ok(())
}

