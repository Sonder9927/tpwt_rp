from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
import subprocess

from tpwt_p.rose import glob_patterns, get_binuse, get_dirname, re_create_dir
from tpwt_p.gmt import gmt_amp, gmt_phase_time


Param_dist = namedtuple("Param_dist", "bp period sta_dist find_phvel_amp_eq correct_tt_select_data")

def process_periods_sta_dist(bp, periods: list):
    # re-create directory 'all_events'
    re_create_dir(Path(bp.all_events))

    sta_dist = "target/sta_dist.lst"
    # calc_distance to create sta_dist.lst
    calc_distance_eq = get_binuse('calc_distance_earthquake')

    cmd_string = 'echo shell start\n'
    cmd_string += f'{calc_distance_eq} {bp.evt} {bp.sta} {bp.sac}/ {sta_dist}\n'
    cmd_string += 'echo shell end'

    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())

    find_phvel_amp_eq = get_binuse('find_phvel_amp_earthquake')
    correct_tt_select_data = get_binuse('correct_tt_select_data')

    ps = [Param_dist(bp, per, sta_dist, find_phvel_amp_eq, correct_tt_select_data) for per in periods]

    # periods = [20, 25, 26]
    Pool(10).map(process_period_sta_dist, ps)


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
    calc_distance_find_eq(p.bp, p.sta_dist, p.period, p.find_phvel_amp_eq)
    plot_events_phase_time_and_amp(p.bp, p.period, p.correct_tt_select_data)


        
###############################################################################


def calc_distance_find_eq(bp, period, sta_dist, find_phvel_amp_eq):
    cmd_string = 'echo shell start\n'
    cmd_string += f'{find_phvel_amp_eq} '
    cmd_string += f'{period} {sta_dist} {bp.snr} {bp.dist} {bp.sac}/\n'
    cmd_string += f'mv {get_dirname("sec", period, bp.snr, bp.dist)} {bp.all_events}/\n'
    cmd_string += 'echo shell end'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())


def plot_events_phase_time_and_amp(bp, period, correct_tt_select_data):
    sec = Path(bp.all_events / get_dirname("sec", period, bp.snr, bp.dist))

    try:
        events = glob_patterns("glob", sec, ["*ph.txt", "*_v1"])
    except FileNotFoundError as error:
        print(error)
        return
    Param_phase = namedtuple("Param_phase",
        "region nsta stacut ref_lo ref_la tcut "
        "period event correct_tt_select_data")
        

    ps = [Param_phase(
        bp.region.original(), bp.nsta, bp.stacut,
        bp.ref_sta.lo, bp.ref_sta.la, bp.tcut,
        period, e, correct_tt_select_data) for e in events]
    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(plot_event_phase_time_and_amp, ps)


# process every event
# cannot use Thread
def plot_event_phase_time_and_amp(p):
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

        # chdir!!!!!!!!!!!!!!!!!

        gmt_phase_time(str(p.event), p.region)
        gmt_amp(p.event, p.region)

        # event_v1 = Path(event.parent) / (event.name + '_v1')
        # if event_v1.exists():
        #     plot_phase_time(event_v1, region)
        #     plot_amp(event_v1, region)
