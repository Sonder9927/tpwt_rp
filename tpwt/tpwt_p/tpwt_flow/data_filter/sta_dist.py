from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
import subprocess

from tpwt_p.rose import glob_patterns, get_binuse, get_dirname, re_create_dir
from tpwt_p.gmt import gmt_amp, gmt_phase_time

from icecream import ic

def process_periods_sta_dist(bp, periods: list, work: Path):
    # re-create directory 'all_events'
    re_create_dir(Path(bp.all_events))

    sta_dist = "target/sta_dist.lst"
    # calc_distance to create sta_dist.lst
    calc_distance_eq = get_binuse('calc_distance_earthquake')

    cmd_string = 'echo shell start\n'
    cmd_string += f'{calc_distance_eq} {bp.evt} {bp.sta} {bp.sac}/ {sta_dist}\n'
    cmd_string += 'echo shell end'

    # subprocess.Popen(
    #     ['bash'],
    #     stdin = subprocess.PIPE
    # ).communicate(cmd_string.encode())

    # process every period
    def process_period_sta_dist(period):
        """
        batch function for process_periods_sta_dist
        """
        # bind period to bp
        # calc_distance_find_eq(bp, sta_dist, period)
        plot_events_phase_time_and_amp(bp, period, work)
        ic()

    # periods = [20, 25, 26]
    with ThreadPoolExecutor(max_workers=5) as pool:
        pool.map(process_period_sta_dist, periods)


###############################################################################


def calc_distance_find_eq(p, sta_dist, period):
    find_phvel_amp_eq = get_binuse('find_phvel_amp_earthquake')
    cmd_string = 'echo shell start\n'
    cmd_string += f'{find_phvel_amp_eq} '
    cmd_string += f'{period} {sta_dist} {p.snr} {p.dist} {p.sac}/\n'
    cmd_string += f'mv {get_dirname("sec", period, p.snr, p.dist)} {p.all_events}/\n'
    cmd_string += 'echo shell end'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())


def plot_events_phase_time_and_amp(p, period, work):
    sec = Path(p.all_events / get_dirname("sec", period, p.snr, p.dist))

    try:
        events = glob_patterns("glob", sec, ["*ph.txt", "_v1"])
    except FileNotFoundError as error:
        print(error)
        return

    # process every event
    # cannot use Thread
    def plot_event_phase_time_and_amp(event: Path):
        """
        batch function
        plot phase time
        plot amp
        """
        stanum = len(open(event, 'r').readlines())

        if stanum >= p.nsta:
            correct_tt_select_data = get_binuse('correct_tt_select_data', bin_from=work)

            cmd_string = 'echo shell start\n'
            cmd_string += f'{correct_tt_select_data} '
            cmd_string += f'{event} {period} {p.nsta} {p.stacut} '
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
        

    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(plot_event_phase_time_and_amp, events)
