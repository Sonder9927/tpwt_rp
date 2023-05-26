# get_SAC.py
# author : Sonder Merak Winona
# created: 6th April 2022
# version: 1.3

'''
This script will move events directories having 14 numbers in cut_dir to sac_dir
and batch rename a group of sac files in given directory renamed with 12 numbers.

From 
TE.BD917.00.HHZ.D.2022001105112.sac
To
event.station.LHZ.sac

Then add information of both event and station to head of sac files in SAC directory
'''

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from icecream import ic
import pandas as pd
import os, shutil
import subprocess

from tpwt_p.rose import glob_patterns, re_create_dir
from .obs_mod import Obs


class Pos:
    def __init__(self, x, y, z=None) -> None:
        self.x = x
        self.y = y
        self.z = z

class Sac_Format:
    def __init__(self, data, *, evt, sta) -> None:
        self.data = Path(data)
        self.channel = "LHZ"
        self.evt = pd.read_csv(evt,
            delim_whitespace=True, names=["evt", "lo", "la", "dp"], dtype={"evt": str},
            header=None, index_col="evt")
        self.sta = pd.read_csv(sta,
            delim_whitespace=True, names=["sta", "lo", "la"],
            header=None, index_col="sta")
        ic(f"Hello, this is SAC formatter")

    def evt_to_point(self, evt: str) -> Pos:
        return Pos(x=self.evt.x[evt], y=self.evt.y[evt], z=self.evt.z[evt])

    def sta_to_points(self) -> dict[str, Pos]:
        dk = self.sta.index
        dv = [Pos(x=self.sta.x[i], y=self.sta.y[i]) for i in dk]
        return dict(zip(dk, dv))

    def format_to_dir(self, dir: str):
        # clear and re-create
        target = re_create_dir(dir)

        # get list of events directories
        cut_evts = glob_patterns("glob", self.data, ["*/**"])
        stas = self.sta_to_points()
        err_sta = set()

        with ProcessPoolExecutor(max_workers=5) as executor:
            for e in cut_evts:
                ep = self.evt_to_point(e.name[:12])
                future = executor.submit(batch_event, target, e, ep, stas, self.channel)
                err_sta.update(future.result())
        ic(err_sta)


def batch_event(out_dir, cut_evt, ep, stas, channel):
    """
    batch function to process every event
    move events directories
    format sac files
    """
    # move
    sac_evt = out_dir / cut_evt.name[:12]
    shutil.copytree(cut_evt, sac_evt)

    # process every sac file
    sacs = glob_patterns("glob", sac_evt, ["*"])
    err_sta = set()

    with ThreadPoolExecutor(max_workers=10) as pool:
        for sac in sacs:
            future = pool.submit(rename_ch, sac, ep, stas, channel)
            res = future.result()
            if res:
                err_sta .update(res)
    return err_sta


###############################################################################


def format_sac_name(target: Path, channel):
    """
    rename and ch sac files
    """
    evt_name = target.parent.name
    sta_name = target.name.split('.')[1].upper()
    new_name = f"{evt_name}.{sta_name}.{channel}.sac"

    target_new = target.parent / new_name

    return sta_name, target_new


def ch_sac(target: Path, evt: Pos, sta: Pos, sta_name, channel):
    """
    change head of sac file to generate dist information
    """
    # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)

    s = "wild echo off \n"
    s += "r {} \n".format(target)
    s += f"ch evlo {evt.x}\n"
    s += f"ch evla {evt.y}\n"
    s += f"ch evdp {evt.z}\n"
    s += f"ch stlo {sta.x}\n"
    s += f"ch stla {sta.y}\n"
    # s += f"ch stel {sta.z}\n"
    s += f"ch kcmpnm {channel}\n"
    s += f"ch kstnm {sta_name}\n"
    s += "wh \n"
    s += "q \n"

    os.putenv("SAC_DISPLAY_COPYRIGHT", "0")
    subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())


def ch_obspy(target: Path, evt: Pos, sta: Pos, channel):
    """
    change head of sac file to generate dist information
    """
    # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)
    obs = Obs(target, evt, sta, channel)
    obs.ch_obs()


def rename_ch(sac, ep, stas, channel):
    # rename
    sta_name, sac_new = format_sac_name(sac, channel)

    # change head
    sp = stas.get(sta_name)
    if sp == None:
        return sta_name
    else:
        shutil.move(sac, sac_new)
        ch_sac(sac_new, ep, sp, sta_name, channel)
        # ch_obspy(res.sac, p.evt, p.stas[res.sta], p.channel)
        return None
        
