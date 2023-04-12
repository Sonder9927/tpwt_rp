use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use sacio::{Sac, SacError, SacString};

#[pyclass(text_signature = "(info)")]
/// Region class
pub struct Ses {
    file: String,
}

#[pymethods]
impl Ses {
    #[new]
    fn new(file: &str) -> Self {
        Ses {
            file: file.to_string(),
        }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("Info sac file: {}.", self.file))
    }

    #[getter]
    fn disk_km(&self) -> PyResult<String> {
        let sac = to_pyerr(Sac::from_file(&self.file))?;
        // let sac = read_sac(&self.file)?;
        Ok(format!(
            "Read disk {}km from sac file {}.",
            sac.dist_km(),
            self.file
        ))
    }

    // fn set_sac_head(&self, sta_name: String, stlo: f32, stla: f32, evlo: f32, evla: f32, target: String) -> PyResult<String> {
    fn set_sac_head(
        &self,
        sta_name: &str,
        sta_evt: [f32; 6],
        channel: &str,
        target: String,
    ) -> PyResult<String> {
        // let mut sac = read_sac(&self.file)?;
        let mut sac = to_pyerr(Sac::from_file(&self.file))?;
        let [stlo, stla, stel, evlo, evla, evdp] = sta_evt;
        sac.set_string(SacString::Station, sta_name);
        sac.set_string(SacString::Component, channel);
        to_pyerr(sac.set_station_location(stla, stlo, stel))?;
        to_pyerr(sac.set_event_location(evla, evlo, evdp))?;

        // sac.compute_dist_az();
        to_pyerr(sac.to_file(target))?;
        // write_sac(sac, &target)?;
        Ok(format!("Write to the sac file {}\n", self.file))
    }
}

fn to_pyerr<T>(res: Result<T, SacError>) -> Result<T, PyErr> {
    match res {
        Ok(res) => Ok(res),
        Err(_) => Err(PyException::new_err("Sac Error!")),
    }
}

// fn read_sac(file: &str) -> Result<Sac, PyErr> {
//     match Sac::from_file(file) {
//         Ok(sac) => Ok(sac),
//         Err(_) => return Err(PyFileNotFoundError::new_err("Not found sac file!")),
//     }
// }

// fn write_sac(mut sac: Sac, file: &str) -> Result<(), PyErr> {
//     match sac.to_file(file) {
//         Ok(()) => Ok(()),
//         Err(_) => {
//             return Err(PyFileNotFoundError::new_err(format!(
//                 "Failed to write sac file {}",
//                 file
//             )))
//         }
//     }
// }
