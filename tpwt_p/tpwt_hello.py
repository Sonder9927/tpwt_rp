from icecream import ic
from pysrc import tpwt_flow
import tpwt_r

from pysrc.param import get_param


__author__ = "Sonder"


def tpwt(param_json: str):
    # start
    ic(tpwt_r.hello_name(__author__))

    # get parameters
    param = get_param(param_json)

    # get event lst and cat from 30 to 120
    [evt30, evt120] = param.evt_files
    evt = tpwt_flow.Evt_Files(evt30, evt120)
    evt.concat()
    evt.cut_time_delta(param.time_delta)
    # ic(evt.info())
    pattern = "%Y-%m-%dT%H:%M:%S"
    cat_form = "%Y/%m/%d,%H:%M:%S"
    evt.evt_cat(param.evt_cat, pattern, cat_form)
    lst_form = "%Y%m%d%H%M"
    evt.evt_lst(param.evt_lst, pattern, lst_form)

    # data cut event
    z_pattern = "1"
    data = tpwt_flow.Evt_Cut(param.data, search_patterns, z_pattern)  # if set z_pattern to '1' the new file will be `file_1`
    data.get_Z_1Hz(param.only_Z_1Hz)  # get only_Z_1Hz/file_origin{z_pattern} and set self.only_Z_1Hz=Path(only_Z_1Hz)
    data.cut_event(param.cut_dir, param.evt_cat)  # if cut_from: use cut_from else: use self.only_Z_1Hz

    # process sac files
    sac = tpwt_flow.Sac_Format(param.cut_dir, param.evt_lst, param.sta_lst)
    sac.get_SAC(param.sac)

    # check data format
    tpwt_check(param.sac)

    # mass control
    data = tpwt_flow.Data_Filter(param.sac, param.evt_lst, param.sta_lst, param.snr, param.tcut, param.nsta)
    data.tpwt_1()
    data.tpwt_2()
    data.tpwt_3()

    region = tpwt_r.Region(param.region)
    # iterater
    tpwt = tpwt_flow.TPWT_Iter(region, smooth, damping)
    # tpwt.step_4()
    # tpwt.step_5()
    tpwt.create_nodes()
    tpwt.sens()
    # tpwt.kern100()
    tpwt.kern300()
    tpwt.find_bad()
    # tpwt.kern160()
    tpwt.kern360()

    # checkboard
    cb = tpwt_flow.Check_Board()
    cb.check_board()


if __name__ == "__main__":
    tpwt_r.hello()
    tpwt("param.json")
