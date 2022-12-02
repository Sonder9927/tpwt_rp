# from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
import shutil

from tpwt_p.rose import re_create_dir, remove_targets, get_dirname

from .tpwt_fns import(
    sensitivity_TPWT, rdsetupsimul_phamp_from_earthquake_TPWT,
    sort_files_for_iter, simanner_TPWT_run, find_bad_kern, simanner_and_gridgenvar
)


def inverse_pre(params):
    # multiprocessing
    Pool(10).map(batch_period_phampcor, params)

###############################################################################
def inverse_run(method="rswt", params=[]):
    # check if TPWT output dir exists
    if not (td := params[0].tpwt_dir.exists()):
        err = f'TPWT output directory {td} is not found.'
        err += 'Please confirm the initilialization is successful.'
        raise FileNotFoundError(err)
    if method in ['tpwt', 'TPWT']:
        tpwt_run(params)
    elif method in ['rswt', 'RSWT']:
        rswt_run(params)
    else:
        raise KeyError("Please choice TPWT or RSWT.")


def tpwt_run(params):
    # multiprocessing
    Pool(10).map(batch_period_grid, params)


def rswt_run(params):
    # multiprocessing
    Pool(10).map(batch_period_grid, params)

###############################################################################
"""
batch function
"""

def batch_period_phampcor(p):
    # sensitivity (this is rayleigh edition)
    sensitivity_TPWT(p.per, p.vel, p.smooth, "rayleigh", out_dir=p.sens_dir)

    # flag phamp
    sens_dat = Path.cwd() / p.sens_dir / f"sens{p.per}s{p.smooth}km.dat"
    sec_snr_dis = Path(p.all_events) / f"{p.per}sec_{p.snr}snr_{p.dist}dis"
    rdsetupsimul_phamp_from_earthquake_TPWT(p.per, p.vel, p.snr,
        p.dist, p.nsta, p.smooth, p.damping,
        str(p.eqlistper), str(sens_dat), str(sec_snr_dis))

    # sort files and get stationid.dat
    sort_files_for_iter(p.per, p.nodes, p.staid, sens_dat, p.tpwt_dir)

def batch_period_grid(p):
    # RSWT
    per = p.per
    per_dir = p.tpwt_dir / f"per{per}"
    # will mkdir res_dir in where put result grid data
    res_dir = "rswt"
    kern = [100, 160]

    damp = str(p.damping).split('.')[1]
    avgvel1: str = first_iter_in_per_dir(p.per, p.smooth, damp, per_dir, res_dir, kern[0])

    eqfine_to_res_dir(kern[0], per_dir/res_dir,
        per=per, ampcut=p.ampcut, tcut=p.tcut, stacut=p.stacut)

    # go into output directory, default is new_2d
    second_iter_in_res_dir(kern[1], per, avgvel1, p.snr, p.dist, p.nsta, p.smooth, p.damping, damp,
        p.region, per_dir/res_dir, sec_dir=get_dirname("sec", period=per, snr=p.snr, dist=p.dist))

###############################################################################

def first_iter_in_per_dir(per, smooth, damp, per_dir, res_dir, kern) -> str:
    """
    process data generated from step 4
    in TPWT_param/per
    """
    if (eq := per_dir/f'eqlistper{per}').exists():
        re_create_dir(res_dir)
    else:
        err = f'No {eq} found!'
        err += 'Please confirm the initilialization is successful.'
        raise FileNotFoundError(err)

    ## simannerr100
    simanner_TPWT_run(eq, kern)

    # return avgvel and std
    vel_f = f"velarea.{per}.1.{smooth}.{damp}.sa{kern}kern"
    with open(vel_f, 'r') as f:
        velarea = f.readline()
    
    return velarea.split()[1]


def eqfine_to_res_dir(kern, res_dir, *, per, ampcut, tcut, stacut, tevtrmscut=None, ampevtrmscut=None):
    # get eqlistper.fine
    find_bad_kern(kern, per=per, ampcut=ampcut, tcut=tcut, stacut=stacut)

    # get linenum of eqlistper.fine
    eq_fine = res_dir / r'eqlistper.fine'
    with open(eq_fine, 'r') as f1:
        content_list = f1.readlines()
    # update eqlistper{per}
    with open(f'{res_dir}/eqlistper{per}.update', 'w+') as f2:
        for c in content_list[:-14]:
            f2.write(c)

    copy_list = ['stationid.dat', 'invrsnodes']
    for cf in copy_list:
        shutil.copy(cf, res_dir/cf)


def second_iter_in_res_dir(kern, per, vel, snr, dist, nsta, smooth, damping, damp,
    region, res_dir, sec_dir, wave_type="rayleigh"):
    sensitivity_TPWT(per, vel, smooth, wave_type, out_dir=res_dir)

    # do rdsetupsimul phamp again
    eqlistper = res_dir / f'eqlistper{per}.update'
    sens_dat = res_dir / f"sens{per}s{smooth}km.dat"
    rdsetupsimul_phamp_from_earthquake_TPWT(per, vel, snr, dist, nsta, smooth, damping,
        str(eqlistper), str(sens_dat), str(sec_dir))

    rm_list = [
        eqlistper,
        f'resmax{per}.dat',
        f'eqlistper.fine',
        f'phampcor.v3.{per}',
    ]
    remove_targets(rm_list)
    eqlistper = f'eqlistper{per}'
    shutil.move(f'eqlistper.v3.{per}', eqlistper)

    simanner_and_gridgenvar(kern, per, smooth, damp, region, eqlistper)

