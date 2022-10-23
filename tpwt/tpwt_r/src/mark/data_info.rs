use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass(text_signature = "(info)")]
/// Region class
pub struct Info {
    data: String,
    evt: String,
    sta: String,
}
#[pymethods]
impl Info {
    #[new]
    fn new(info: HashMap<String, &str>) -> Self {
        Info {
            data: info["sac"].to_string(),
            evt: info["evt_lst"].to_string(),
            sta: info["sta_lst"].to_string(),
        }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "Info\n  data: {}\n  event: {}\n  station: {}",
            self.data, self.evt, self.sta
        ))
    }

    #[getter]
    fn sac(&self) -> PyResult<String> {
        Ok(String::from(&self.data))
    }
    #[getter]
    fn data(&self) -> PyResult<String> {
        Ok(String::from(&self.data))
    }
    #[getter]
    fn sta(&self) -> PyResult<String> {
        Ok(String::from(&self.sta))
    }
    #[getter]
    fn evt(&self) -> PyResult<String> {
        Ok(String::from(&self.evt))
    }
}
