use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use sacio::{Sac, SacError, SacString};

#[pyclass(text_signature = "(sac_file)")]
/// Sac class
pub struct Ses {
    file: String,
    sac: Sac,
}

#[pymethods]
impl Ses {
    #[new]
    fn new(file: String) -> Self {
        let sac = match Sac::from_file(&file) {
            Ok(s) => s,
            Err(_) => panic!("Sac read Error!"),
        };
        Ses { file, sac }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("Info sac file: {}.", self.file))
    }

    #[getter]
    fn delta(&self) -> PyResult<f32> {
        Ok(self.sac.delta())
    }
    #[getter]
    fn disk_km(&self) -> PyResult<f32> {
        Ok(self.sac.dist_km())
    }
    #[getter]
    fn max_amp(&self) -> PyResult<f32> {
        Ok(self.sac.max_amp())
    }

    fn set_sac_head(
        &mut self,
        sta_name: &str,
        sta_evt: [f32; 6],
        channel: &str,
        target: String,
    ) -> PyResult<String> {
        let [stlo, stla, stel, evlo, evla, evdp] = sta_evt;
        // chang station name and channel
        self.sac.set_string(SacString::Station, sta_name);
        self.sac.set_string(SacString::Component, channel);

        // set location both of station and event
        self.sac.set_station_location(stla, stlo, stel).unwrap();
        to_pyerr(self.sac.set_event_location(evla, evlo, evdp))?;

        // save to the target file
        to_pyerr(self.sac.to_file(target))?;
        Ok(format!("Write to the sac file {}\n", self.file))
    }
}

fn to_pyerr<T>(res: Result<T, SacError>) -> Result<T, PyErr> {
    match res {
        Ok(res) => Ok(res),
        Err(_) => Err(PyException::new_err("Sac operate Error!")),
    }
}