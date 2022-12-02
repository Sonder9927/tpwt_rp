from pathlib import Path
import demjson

from tpwt_r import Point, Region


class State:
    def __init__(self, target: str) -> None:
        self.target = target
        self.state = param_parse(target)

    def __repr__(self) -> str:
        return f"State:\n  target: {self.target}\n  state: {self.state}"

    def check_state(self, state: str) -> bool:
        return self.state.get(state)

    def change_state(self, state: str, info: bool):
        self.state[state] = info

    def save(self, target=None):
        t = target or self.target
        demjson.encode_to_file(t, self.state, overwrite=True)


###############################################################################


class Bound_Param:
    def __init__(self, pt: dict, pf: dict, pm: dict) -> None:
        self.work_dir = Path.cwd()
        # targets
        self.sac = pt["sac"]
        self.data = Path(self.sac)
        self.evt = pt["evt_lst"]
        self.sta = pt["sta_lst"]
        self.all_events = pt["all_events"]
        # filter
        self.dist = pf["dist"]
        self.nsta = pf["nsta"]
        self.stacut = pf["stacut_per"]
        # model
        self.region = Region(pm["region"])
        self.ref_sta = Point(pm["ref_sta"])

    def set_period(self, p):
        self.period = p

    def set_snr_tcut(self, snr, tcut):
        self.snr = snr
        self.tcut = tcut


###############################################################################


# json
def param_parse(f: str) -> dict:
    """
    Get parameters from json data file.
    """
    return demjson.decode_file(f)
