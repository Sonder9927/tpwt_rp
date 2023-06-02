from icecream import ic

# from .tpwt_p import tpwt_flow
from . import tpwt_flow
from .check import Check_In
# from tpwt_p.info_per import period_info
import tpwt_r


__author__ = "Sonder"


def evts_from_30_to_120(param):
    evt = tpwt_flow.Evt_Make(param.target("evt30"), param.target("evt120"))
    evt.concat()
    evt.cut_time_delta(param.parameter("time_delta"))
    pattern = "%Y-%m-%dT%H:%M:%S"
    cat_form = "%Y/%m/%d,%H:%M:%S"
    evt.evt_cat(param.target("evt_cat"), pattern, cat_form)
    lst_form = "%Y%m%d%H%M"
    evt.evt_lst(param.target("evt_all_lst"), pattern, lst_form)


def evt_cut(param):
    data = tpwt_flow.Evt_Cut(param.target("og_data"))  # if set z_pattern to '1' the new file will be `file_1`
    data.cut_event(param.target("cut_dir"), param.target("evt_cat"), param.parameter("time_delta"))  # if cut_from: use cut_from else: use self.only_Z_1Hz


def sac_format(param):
    sac = tpwt_flow.Sac_Format(
            param.target("cut_dir"), 
            evt=param.target("evt_all_lst"), 
            sta=param.target("sta_lst"))
    sac.make_sac(param.target("sac"))
    sac.filter_event_lst(param.target("sac"), param.target("evt_lst"))


def tpwt_check(data: str):
    t = Check_In(data)
    message = t.check_form()
    ic(message)


def quanlity_control(param):
    # data = tpwt_flow.Data_Filter(bp, param.model["periods"])
    data = tpwt_flow.Data_Filter(param, [20, 25])
    # data.path = param.targets["path"]
    # data.aftan_snr(param.targets["path"])
    snr = param.parameter("snr")
    tcut = param.parameter("tcut")
    data.sta_dist(snr, tcut)
    # eq = data.eqlistper()
    return "eq"

def main(param_json: str):
    # start
    ic(tpwt_r.hello_name(__author__))

    # get parameters
    param = tpwt_r.load_param(param_json)

    # get event lst and cat from 30 to 120
    evts_from_30_to_120(param)

    # data cut event
    evt_cut(param)

    # process sac files
    sac_format(param)

    # check data format
    tpwt_check(param.target("sac"))

    # mass control
    eq = quanlity_control(param)
    ic(eq)
        # state.change_state("control", False)

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
