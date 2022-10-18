from icecream import ic
from pathlib import Path
import tpwt_r

# ic(tpwt_r.hello_name("Sonder"))

def tpwt(param_json: str):
    # get parameters
    param = get_param(param_json)

    # get event lst and cat from 30 to 120
    evt = Evt_File(evt_30, evt_120)
    evt.concat()
    evt.evt_cut(time_delta)
    evt.event_cat(param.evt_cat, cat_pattern)
    evt.event_lst(param.evt_lst, lst_pattern)

    # data cut event
    data = Evt_Cut(param.data, search_patterns, z_pattern)  # set z_pattern to '_1'
    data.get_Z_1Hz(param.only_Z_1Hz)  # get only_Z_1Hz/file_origin{z_pattern} and set self.only_Z_1Hz=Path(only_Z_1Hz)
    data.cut_event(param.cut_dir, param.evt_cat[, param.only_Z_1Hz])  # if cut_from: use cut_from else: use self.only_Z_1Hz

    # process sac files
    sac = Sac_Format(param.cut_dir, param.evt_lst, param.sta_lst)
    sac.get_SAC(param.sac)

    # check data format
    tpwt_check(param.sac)

    # mass control
    data = Data_Filter(param.sac, param.evt_lst, param.sta_lst, param.snr, param.tcut, param.nsta)
    data.tpwt_1()
    data.tpwt_2()
    data.tpwt_3()

    region = tpwt_r.Region(param.region)
    # iterater
    tpwt = TPWT_Iter(region, smooth, damping)
    # tpwt.step_4()
    # tpwt.step_5()
    tpwt.create_nodes()
    tpwt.sens()
    tpwt.kern300()
    tpwt.find_bad()
    tpwt.kern360()

    # checkboard
    cb = Check_Board()
    cb.check_board()


if __name__ == "__main__":
    tpwt_r.hello()
