from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import subprocess

from tpwt_p.rose import glob_patterns, get_binuse, get_dirname, re_create_dir
from tpwt_p.gmt import gmt_amp, gmt_phase_time


def process_periods_sta_dist(bp, periods: list, work: Path):
    # re-create directory 'all_events'
    re_create_dir(Path(bp.all_events))

    # process every period
    n = len(periods)
    with ProcessPoolExecutor(max_workers=4) as pool:
        pool.map(process_period_sta_dist, [bp]*n, periods, [work]*n)


###############################################################################


def calc_distance_find_eq(p):
    calc_distance_eq = get_binuse('calc_distance_earthquake')
    find_phvel_amp_eq = get_binuse('find_phvel_amp_earthquake')

    cmd_string = 'echo shell start\n'
    cmd_string += f'{calc_distance_eq} {p.evt} {p.sta} {p.sac}/\n'
    cmd_string += f'{find_phvel_amp_eq} '
    cmd_string += f'{p.period} sta_dist.lst {p.snr} {p.dist} {p.sac}/\n'
    cmd_string += f'mv {p.period}sec_{p.snr}snr_{p.dist}dis {p.all_events}/\n'
    cmd_string += 'echo shell end'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())


def plot_event_phase_time_and_amp(p, event: Path, work: Path):
    """
    plot phase time
    plot amp
    """
    stanum = len(open(event, 'r').readlines())

    if stanum >= p.nsta:
        correct_tt_select_data = get_binuse('correct_tt_select_data', bin_from=work)

        cmd_string = 'echo shell start\n'
        cmd_string += f'{correct_tt_select_data} '
        cmd_string += f'{event} {p.period} {p.nsta} {p.stacut} '
        cmd_string += f'{p.ref_sta.lo} {p.ref_sta.la} {p.tcut}\n'
        cmd_string += 'echo shell end'
        subprocess.Popen(
            ['bash'],
            stdin = subprocess.PIPE
        ).communicate(cmd_string.encode())

        # chdir!!!!!!!!!!!!!!!!!

        region = p.region.original()

        gmt_phase_time(str(event), region)
        gmt_amp(event, region)

        # event_v1 = Path(event.parent) / (event.name + '_v1')
        # if event_v1.exists():
        #     plot_phase_time(event_v1, region)
        #     plot_amp(event_v1, region)
        

def plot_events_phase_time_and_amp(p, work):
    sec = Path(p.all_events / get_dirname("sec", p.period, p.snr, p.dist))
    events = glob_patterns("glob", sec, ["*ph.txt", "_v1"])

    # process every event
    # cannot use Thread
    n = len(events)
    with ProcessPoolExecutor(max_workers=4) as pool:
        pool.map(plot_event_phase_time_and_amp, [p]*n, events, [work]*n)


def process_period_sta_dist(bp, period, work):
    """
    batch function for process_periods_sta_dist
    """
    # bind period to bp
    bp.set_period(period)

    calc_distance_find_eq(bp)

    plot_events_phase_time_and_amp(bp, work)
