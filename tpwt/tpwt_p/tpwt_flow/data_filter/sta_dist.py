from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
import subprocess, shutil

from tpwt_p.rose import glob_patterns, get_binuse, get_dirname, re_create_dir
from tpwt_p.gmt import gmt_amp, gmt_phase_time


Param_dist = namedtuple("Param_dist",
    "bp_dist bp_v1 period sta_dist find_phvel_amp_eq correct_tt_select_data")
Param_phase_amp = namedtuple("Param_phase_amp", "event region")


def process_periods_sta_dist(bp, periods: list):
    # re-create directory 'all_events'
    all_events = Path(bp.all_events)
    re_create_dir(all_events)

    sta_dist = r"target/sta_dist.lst"
    # calc_distance to create sta_dist.lst
    calculate_sta_dist(bp.evt, bp.sta, bp.sac, sta_dist)

    # some parameters
    bp_dist = {
        "snr": bp.snr,
        "dist": bp.dist,
        "sac": bp.sac,
        "all_events": bp.all_events,
    }
    bp_v1 = {
        "ref_lo": bp.ref_sta.lo,
        "ref_la": bp.ref_sta.la,
        "tcut": bp.tcut,
        "nsta": bp.nsta,
        "stacut": bp.stacut,
    }

    find_phvel_amp_eq = get_binuse('find_phvel_amp_earthquake')
    correct_tt_select_data = get_binuse('correct_tt_select_data')

    # get all_events/sec_dir/evt.ph.txt(_v1)
    ps = [Param_dist(bp_dist, bp_v1, per, sta_dist,
        find_phvel_amp_eq, correct_tt_select_data) for per in periods]

    pool1 = Pool(10)
    pool1.map(process_period_sta_dist, ps)
    Path(sta_dist).unlink()

    # plot phase time and amp of all events
    events = glob_patterns("glob", all_events, ["*/*ph.txt*"])
    region = bp.region.original()
    ps = [Param_phase_amp(e, region) for e in events]
    pool2 = Pool(10)
    pool2.map(event_phase_time_and_amp, ps)


###############################################################################
def calculate_sta_dist(evt, sta, sac, sta_dist):
    """
    calc_distance to create sta_dist.lst
    """
    calc_distance_eq = get_binuse('calc_distance_earthquake')

    cmd_string = 'echo shell start\n'
    cmd_string += f'{calc_distance_eq} {evt} {sta} {sac}/ {sta_dist}\n'
    cmd_string += 'echo shell end'

    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())


###############################################################################
"""
batch function
"""


# process every period
def process_period_sta_dist(p: Param_dist):
    """
    batch function for process_periods_sta_dist
    """
    # bind period to bp
    calc_distance_find_eq(p.bp_dist, p.period,  p.sta_dist, p.find_phvel_amp_eq)

    sec = Path(p.bp_dist["all_events"] / get_dirname("sec",
        period=p.period, snr=p.bp_dist["snr"], dist=p.bp_dist["dist"]))

    all_periods_sec(p.bp_v1, sec, p.period, p.correct_tt_select_data)

        
###############################################################################


def calc_distance_find_eq(bp, period, sta_dist, find_phvel_amp_eq):
    cmd_string = 'echo shell start\n'
    cmd_string += f'{find_phvel_amp_eq} '
    cmd_string += f'{period} {sta_dist} {bp["snr"]} {bp["dist"]} {bp["sac"]}/\n'
    cmd_string += 'echo shell end'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())
    shutil.move(get_dirname("sec", period=period, snr=bp["snr"], dist=bp["dist"]), bp["all_events"])


def all_periods_sec(bp, sec, period, correct_tt_select_data):
    # ["*ph.txt", "*_v1"]
    events = glob_patterns("glob", sec, ["*ph.txt"])
    Param_v1 = namedtuple("Param_v1",
        "nsta stacut ref_lo ref_la tcut period event correct_tt_select_data")

    ps = [Param_v1(
        bp["nsta"], bp["stacut"], bp["ref_lo"], bp["ref_la"], bp["tcut"], 
        period, e, correct_tt_select_data) for e in events]
    with ThreadPoolExecutor(max_workers=10) as pt:
        pt.map(ph_txt_v1, ps)


# process every event
# cannot use Thread
def ph_txt_v1(p):
    """
    batch function
    plot phase time
    plot amp
    """
    stanum = len(open(p.event, 'r').readlines())

    if stanum >= p.nsta:
        cmd_string = 'echo shell start\n'
        cmd_string += f'{p.correct_tt_select_data} '
        cmd_string += f'{p.event} {p.period} {p.nsta} {p.stacut} '
        cmd_string += f'{p.ref_lo} {p.ref_la} {p.tcut}\n'
        cmd_string += 'echo shell end'
        subprocess.Popen(
            ['bash'],
            stdin = subprocess.PIPE
        ).communicate(cmd_string.encode())


###############################################################################


def event_phase_time_and_amp(p: Param_phase_amp):
    """
    plot phase time and amp of all events with region
    """
    if p.event.stat().st_size != 0:
        gmt_phase_time(p.event, p.region)
        gmt_amp(p.event, p.region)

