use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use sacio::{Sac, SacError, SacString};

/// Class SacEvtSta
#[pyclass(text_signature = "(sac_file)")]
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
        Ok(format!("Info sac file: {}.", &self.file))
    }

    #[getter]
    fn delta(&self) -> PyResult<f32> {
        Ok(self.sac.delta())
    }
    #[getter]
    fn dist_km(&self) -> PyResult<f32> {
        Ok(self.sac.dist_km())
    }
    #[getter]
    fn station_name(&self) -> PyResult<String> {
        Ok(self.sac.string(SacString::Station).to_string())
    }
    #[getter]
    fn max_amp(&self) -> PyResult<f32> {
        Ok(self.sac.max_amp())
    }

    fn set_sac_head(&mut self, sta_name: &str, sta_evt: [f32; 6], channel: &str) {
        let [stlo, stla, stel, evlo, evla, evdp] = sta_evt;
        // change station name and channel
        self.sac.set_string(SacString::Station, sta_name);
        self.sac.set_string(SacString::Component, channel);

        // set location both of station and event
        self.sac.set_station_location(stla, stlo, stel).unwrap();
        self.sac.set_event_location(evla, evlo, evdp).unwrap();
    }

    fn to_file(&mut self, target: Option<&str>) -> PyResult<String> {
        // save to the target file if target given
        let ffrom: &str = &self.file;
        let fto = if let Some(t) = target { t } else { &self.file };
        to_pyerr(self.sac.to_file(fto))?;
        Ok(f!("Setted head of {ffrom} to file {fto}."))
    }
}

fn to_pyerr<T>(res: Result<T, SacError>) -> Result<T, PyErr> {
    match res {
        Ok(res) => Ok(res),
        Err(_) => Err(PyException::new_err("Sac operate Error!")),
    }
}
