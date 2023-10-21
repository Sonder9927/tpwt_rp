from icecream import ic

from . import tpwt_flow
from .check import Check_In

# from tpwt_p.info_per import period_info
import tpwt_r


__author__ = "Sonder"


def evts_from_30_to_120(param):
    evt = tpwt_flow.Evt_Make(
        param.target("evt30"),
        param.target("evt120"),
        param.parameter("timedelta"),
    )
    # evt.concat()
    # evt.cut_time_delta(param.parameter("timedelta"))
    cat_form = "%Y/%m/%d,%H:%M:%S"
    # evt.evt_cat(param.target("evt_cat"), pattern, cat_form)
    evt.extract(1, cat_form, param.target("evt_cat"))
    lst_form = "%Y%m%d%H%M"
    # evt.evt_lst(param.target("evt_all_lst"), pattern, lst_form)
    evt.extract(4, lst_form, param.target("evt_all_lst"))
    evt.extract(5, lst_form, "TPWT/info/event_mag.lst")


def evt_cut(param):
    data = tpwt_flow.Evt_Cut(
        param.target("og_data")
    )  # if set z_pattern to '1' the new file will be `file_1`
    data.cut_event(
        param.target("cut_dir"),
        param.target("evt_cat"),
        param.parameter("time_delta"),
    )  # if cut_from: use cut_from else: use self.only_Z_1Hz


def sac_format(param):
    sac = tpwt_flow.Sac_Format(
        param.target("cut_dir"),
        evt=param.target("evt_all_lst"),
        sta=param.target("sta_lst"),
    )
    sac.make_sac(param.target("sac"))
    sac.filter_event_lst(param.target("sac"), param.target("evt_lst"))


def tpwt_check(data: str):
    t = Check_In(data)
    message = t.check_form()
    ic(message)


def quanlity_control(param):
    # data = tpwt_flow.Data_Filter(bp, param.model["periods"])
    data = tpwt_flow.Data_Filter(param)
    data.filter()


def tpwt_iter(param):
    tpwt = tpwt_flow.TPWT_Iter(param)
    tpwt.iter()


def mcmc(param):
    periods = [
        8, 10, 12, 14, 16, 18,
        20, 25, 30, 35, 40, 45, 50,
        60, 70, 80, 90, 100, 111, 125, 143,
    ]  # fmt: skip
    mc = tpwt_flow.MCMC(param)
    mc.mc_init("TPWT/utils/moho.lst", periods)  # , clip=True)


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
    quanlity_control(param)

    # tpwt
    tpwt_iter(param)

    # mc
    mcmc(param)


if __name__ == "__main__":
    main("param.json")
