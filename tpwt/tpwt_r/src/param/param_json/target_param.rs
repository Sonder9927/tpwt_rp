use serde::Deserialize;

use pyo3::prelude::*;

// #[derive(Debug)]
pub enum ParamString {
    OgData,
    Evt30,
    Evt120,
    EvtCat,
    EvtLst,
    StaLst,
    CutDir,
    Sac,
    Path,
    AllEvents,
    Sens,
    State,
}

#[pyclass]
#[derive(Deserialize, Debug)]
pub struct TargetParam {
    state: String,
    og_data: String,
    evt30: String,
    evt120: String,
    evt_cat: String,
    evt_lst: String,
    sta_lst: String,
    cut_dir: String,
    sac: String,
    path: String,
    all_events: String,
    sens: String,
}
impl TargetParam {
    pub fn get(&self, key: ParamString) -> &str {
        match key {
            ParamString::OgData => &self.og_data,
            ParamString::Evt30 => &self.evt30,
            ParamString::Evt120 => &self.evt120,
            ParamString::EvtCat => &self.evt_cat,
            ParamString::EvtLst => &self.evt_lst,
            ParamString::StaLst => &self.sta_lst,
            ParamString::CutDir => &self.cut_dir,
            ParamString::Sac => &self.sac,
            ParamString::Path => &self.path,
            ParamString::AllEvents => &self.all_events,
            ParamString::Sens => &self.sens,
            ParamString::State => &self.state,
        }
    }
}
