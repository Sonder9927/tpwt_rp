from icecream import ic
from pysrc import tpwt_flow
import tpwt_r

from pysrc.param import get_param_json


__author__ = "Sonder"


def evts_from_30_to_120(evt1, evt2):
    evt = tpwt_flow.Evt_Files(evt1, evt2)
    evt.concat()
    evt.cut_time_delta(param.filter["time_delta"])
    pattern = "%Y-%m-%dT%H:%M:%S"
    cat_form = "%Y/%m/%d,%H:%M:%S"
    evt.evt_cat(param.targets["evt_cat"], pattern, cat_form)
    lst_form = "%Y%m%d%H%M"
    evt.evt_lst(param.targets["evt_lst"], pattern, lst_form)


def evt_cut(patterns, suffix):
    data = tpwt_flow.Evt_Cut(param.targets["origin"])  # if set z_pattern to '1' the new file will be `file_1`
    data.get_Z_1Hz(param.targets["only_Z_1Hz"], patterns, suffix)  # get only_Z_1Hz/file_origin{z_pattern} and set self.only_Z_1Hz=Path(only_Z_1Hz)
    data.cut_event(param.targets["cut_dir"], param.targets["evt_cat"], param.filter["time_delta"])  # if cut_from: use cut_from else: use self.only_Z_1Hz


def tpwt(param_json: str):
    # start
    ic(tpwt_r.hello_name(__author__))

    global param
    # get parameters
    param = get_param_json(param_json)

    # get event lst and cat from 30 to 120
    [evt30, evt120] = param.targets["evt2"]
    evts_from_30_to_120(evt30, evt120)

    # data cut event
    suffix = "1"
    search = ["*Z.sac", "*Z.SAC"]
    evt_cut(search, suffix)

    # # process sac files
    # sac = tpwt_flow.Sac_Format(param.cut_dir, param.evt_lst, param.sta_lst)
    # sac.get_SAC(param.sac)

    # # check data format
    # tpwt_check(param.sac)

    # # mass control
    # data = tpwt_flow.Data_Filter(param.sac, param.evt_lst, param.sta_lst, param.snr, param.tcut, param.nsta)
    # data.tpwt_1()
    # data.tpwt_2()
    # data.tpwt_3()

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
    tpwt_r.hello()
    tpwt("param.json")
