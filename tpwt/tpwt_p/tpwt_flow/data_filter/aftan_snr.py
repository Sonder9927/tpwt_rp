from concurrent.futures import ProcessPoolExecutor
from icecream import ic
from pathlib import Path
import subprocess
import os

from tpwt_p.rose import glob_patterns, get_binuse

def process_events_aftan_snr(sac: Path, path: str, work: Path):
    """
    touch flag_aftan and flag_SNR in sac/event/
    and
    output is ./path/
    """
    dir_ref = work / path
    # filelist = 'filelist'

    # go into sac data directory
    events = glob_patterns("glob", sac, ['**'])

    with ProcessPoolExecutor(max_workers=10) as pool:
        pool.map(process_event_aftan_and_SNR, events, [dir_ref]*len(events), [work]*len(events))


###############################################################################


def aftani_c_pgl_TPWT_run(dir_ref: Path, sac_file: str, work: Path):
    content = "0 2.5 5.0 10 250 20 1 0.5 0.2 2 "  # zui hou you ge kong ge...
    content += sac_file
    param_dat = 'param.dat'
    with open(param_dat, 'w') as p:
        p.write(content)

    sac_parts = sac_file.split('.')
    ref = dir_ref / '{0[0]}_{0[1]}.PH_PRED'.format(sac_parts)

    # spectral_snr_TPWT
    aftani_c_pgl_TPWT = get_binuse('aftani_c_pgl_TPWT', bin_from=work)

    cmd_string = f'{aftani_c_pgl_TPWT} {param_dat} {ref}\n'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())


def process_event_aftan_and_SNR(event: Path, dir_ref: Path, work: Path, filelist='filelist'):
    """
    batch function for process_events_flag_aftan_and_SNR
    """
    os.chdir(str(event))

    sacs = glob_patterns("glob", Path("./"), ['.sac'])

    with open(filelist, 'w+') as f:
        for sac in sacs:
            sf = sac.name
            # filelist
            f.write(sf + '\n')
            # aftan
            aftani_c_pgl_TPWT_run(dir_ref, sf, work)

    # spectral_snr_TPWT
    spectral_snr_TPWT = get_binuse('spectral_snr_TPWT', bin_from=work)

    cmd_string = f'{spectral_snr_TPWT} {filelist} > temp.dat \n'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())

    ic(event.name, "done.")
