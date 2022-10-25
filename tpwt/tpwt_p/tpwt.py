from icecream import ic

from tpwt_p import tpwt_flow
from tpwt_p.param import get_param_json
from tpwt_p.check import Check_In
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
    evt.evt_lst(param.targets["evt_lst"], pattern, lst_form)


def evt_cut(patterns):
    data = tpwt_flow.Evt_Cut(param.targets["origin"])  # if set z_pattern to '1' the new file will be `file_1`
    data.get_Z_1Hz(param.targets["only_Z_1Hz"], patterns)  # get only_Z_1Hz/file_origin{z_pattern} and set self.only_Z_1Hz=Path(only_Z_1Hz)
    data.cut_event(param.targets["cut_dir"], param.targets["evt_cat"], param.filter["time_delta"])  # if cut_from: use cut_from else: use self.only_Z_1Hz


def sac_format(info: tpwt_r.Info):
    sac = tpwt_flow.Sac_Format(param.targets["cut_dir"], info.evt, info.sta)
    sac.get_SAC(info.sac)


def tpwt_check(data: str):
    t = Check_In(data)
    message = t.check_form()
    ic(message)


def mass_control(info):
    data = tpwt_flow.Data_Filter(info.sac, info.evt, info.sta, param.snr, param.tcut, param.nsta)
    data.tpwt_1()
    data.tpwt_2()
    data.tpwt_3()

def tpwt_run(param_json: str):
    # start
    ic(tpwt_r.hello_name(__author__))

    global param
    # get parameters
    param = get_param_json(param_json)

    # get event lst and cat from 30 to 120
    evts_from_30_to_120(param.targets["evt30"], param.targets["evt120"])

    # data cut event
    search = ["*Z.sac", "*Z.SAC"]
    evt_cut(search)

    # bound sac evt and sta to info
    info = tpwt_r.Info(param.targets)

    # process sac files
    sac_format(info)

    # check data format
    tpwt_check(info.data)

    # # mass control
    # mass_control(info.data)

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

    # # checkboard
    # cb = tpwt_flow.Check_Board()
    # cb.check_board()


if __name__ == "__main__":
    tpwt_run("param.json")
