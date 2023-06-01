from icecream import ic

from tpwt_p import tpwt_flow
from tpwt_p.param import Param
from tpwt_p.check import Check_In
# from tpwt_p.info_per import period_info
import tpwt_r


__author__ = "Sonder"


def evts_from_30_to_120(evt1, evt2):
    evt = tpwt_flow.Evt_Make(evt1, evt2)
    evt.concat()
    evt.cut_time_delta(param.filter["time_delta"])
    pattern = "%Y-%m-%dT%H:%M:%S"
    cat_form = "%Y/%m/%d,%H:%M:%S"
    evt.evt_cat(param.targets["evt_cat"], pattern, cat_form)
    lst_form = "%Y%m%d%H%M"
    evt.evt_lst(param.targets["evt_all_lst"], pattern, lst_form)


def evt_cut():
    data = tpwt_flow.Evt_Cut(param.targets["origin"])  # if set z_pattern to '1' the new file will be `file_1`
    data.cut_event(param.targets["cut_dir"], param.targets["evt_cat"], param.filter["time_delta"])  # if cut_from: use cut_from else: use self.only_Z_1Hz


def sac_format(bp):
    sac = tpwt_flow.Sac_Format(param.targets["cut_dir"], evt=param.targets["evt_all_lst"], sta=bp.sta)
    sac.make_sac(bp.sac)
    sac.filter_event_lst(bp.sac, bp.evt)


def tpwt_check(data: str):
    t = Check_In(data)
    message = t.check_form()
    ic(message)


def quanlity_control(bp):
    # data = tpwt_flow.Data_Filter(bp, param.model["periods"])
    data = tpwt_flow.Data_Filter(bp, [20, 25])
    # data.path = param.targets["path"]
    # data.aftan_snr(param.targets["path"])
    snr = param.filter["snr"][3]  # 15
    tcut = param.filter["tcut"][2]  # 8
    data.sta_dist(snr, tcut)
    # eq = data.eqlistper()
    return "eq"

def main(param_json: str):
    # start
    ic(tpwt_r.hello_name(__author__))

    global param
    # get parameters
    param = Param(param_json)
    state = param.state()
    bp = param.bound_param()  # bp.data = Path(bp.sac)

    # get event lst and cat from 30 to 120
    if state.check_state("evts"):
        evts_from_30_to_120(param.targets["evt30"], param.targets["evt120"])
        state.change_state("evts", False)

    # data cut event
    if state.check_state("cut"):
        search = ["*Z.sac", "*Z.SAC"]
        evt_cut(search)
        state.change_state("cut", False)

    # process sac files
    if state.check_state("sac"):
        sac_format(bp)
        state.change_state("sac", False)

    # check data format
    if state.check_state("check"):
        tpwt_check(bp.sac)

    # mass control
    if state.check_state("control"):
        eq = quanlity_control(bp)
        ic(eq)
        # state.change_state("control", False)

    # region = tpwt_r.Region(param.region)
    # # iterater
    # tpwt = tpwt_flow.TPWT_Iter(region, smooth, damping)
    # # tpwt.step_4()
    # # tpwt.step_5()
    # tpwt.create_nodes()
    # tpwt.sens()
    # # tpwt.kern100()
    # tpwt.kern300()
    # tpwt.find_bad()
    # # tpwt.kern160()
    # tpwt.kern360()

    # state.save()

    # # # checkboard
    # # cb = tpwt_flow.Check_Board()
    # # cb.check_board()

    # # per_info = period_info("target/TPWT_15snr_8tcut_65smooth_0.2damping", 26)

    # state.save()


if __name__ == "__main__":
    main("param.json")
