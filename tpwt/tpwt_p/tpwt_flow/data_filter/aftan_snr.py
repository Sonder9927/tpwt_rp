from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
from icecream import ic
import subprocess
import os

from tpwt_p.rose import glob_patterns, get_binuse


Param_as = namedtuple("Param_as", "event dir_ref work spectral_snr_TPWT aftani_c_pgl_TPWT")


def process_events_aftan_snr(sac_dir: Path, path: str, work: Path):
    """
    aftan and SNR in sac/event/
    and
    output is target/path/
    """
    dir_ref = work / path
    # filelist = 'filelist'

    # spectral_snr_TPWT
    spectral_snr_TPWT = get_binuse('spectral_snr_TPWT', bin_from=work)


    events = glob_patterns("glob", sac_dir, ['20*/'])
    # aftani_c_pgl_TPWT
    aftani_c_pgl_TPWT = get_binuse('aftani_c_pgl_TPWT', bin_from=work)

    ps = [Param_as(e, dir_ref, work, spectral_snr_TPWT, aftani_c_pgl_TPWT) for e in events]

    Pool(10).map(process_event_aftan_and_SNR, ps)


###############################################################################


def process_event_aftan_and_SNR(p):
    """
    batch function for process_events_flag_aftan_and_SNR
    """
    sacs = glob_patterns("glob", p.event, ['*.sac'])

    filelist='filelist'

    # go into sac data directory
    os.chdir(str(p.event))

    with open(filelist, 'w+') as f:
        for sac in sacs:
            sf = sac.name
            # filelist
            f.write(sf + '\n')
            # aftan
            aftani_c_pgl_TPWT_run(p.dir_ref, sf, p.aftani_c_pgl_TPWT)

    cmd_string = f'{p.spectral_snr_TPWT} {filelist} > temp.dat \n'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())

    ic(p.event.name, "done.")
    os.chdir(str(p.work))


def aftani_c_pgl_TPWT_run(dir_ref: Path, sac_file: str, aftani_c_pgl_TPWT):
    content = "0 2.5 5.0 10 250 20 1 0.5 0.2 2 "  # zui hou you ge kong ge...
    content += sac_file
    param_dat = 'param.dat'
    with open(param_dat, 'w') as p:
        p.write(content)

    sac_parts = sac_file.split('.')
    ref = dir_ref / '{0[0]}_{0[1]}.PH_PRED'.format(sac_parts)

    cmd_string = f'{aftani_c_pgl_TPWT} {param_dat} {ref}\n'
    subprocess.Popen(
        ['bash'],
        stdin = subprocess.PIPE
    ).communicate(cmd_string.encode())
