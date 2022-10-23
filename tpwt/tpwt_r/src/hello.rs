use pyo3::prelude::{pyfunction, PyResult};

#[pyfunction]
pub fn hello() {
    println!("Hello tpwt, this is Rust!")
}
#[pyfunction]
pub fn hello_name(name: &str) -> PyResult<String> {
    Ok("Hello ".to_string() + name + ".\nThis is tpwt using Rust from Python.\nGood Luck!")
}
