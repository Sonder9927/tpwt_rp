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
from collections import namedtuple
from pathlib import Path
from icecream import ic
import pandas as pd
import os, shutil
import subprocess

from tpwt_p.rose import glob_patterns, re_create_dir
from .obs_mod import Obs


class Pos:
    def __init__(self, x, y) -> None:
        self.lo = x
        self.la = y

class Sac_Format:
    def __init__(self, data, *, evt, sta) -> None:
        self.data = Path(data)
        self.channel = "LHZ"
        self.evt = pd.read_csv(evt, delim_whitespace=True, names=["evt", "lo", "la", "dp"], dtype={"evt": str}, index_col="evt")
        self.sta = pd.read_csv(sta, delim_whitespace=True, names=["sta", "lo", "la"], index_col="sta")
        ic(f"Hello, this is SAC formatter")

    def evt_to_point(self, evt: str) -> Pos:
        return Pos(x=self.evt.lo[evt], y=self.evt.la[evt])

    def sta_to_points(self) -> dict[str, Pos]:
        dk = self.sta.index
        dv = [Pos(x=self.sta.lo[i], y=self.sta.la[i]) for i in dk]
        return dict(zip(dk, dv))

    def format_to_dir(self, dir: str):
        # clear and re-create
        target = re_create_dir(dir)

        # get list of events directories
        cut_evts = glob_patterns("glob", self.data, ["*/**"])
        stas = self.sta_to_points()

        with ProcessPoolExecutor(max_workers=5) as executor:
            for e in cut_evts:
                ep = self.evt_to_point(e.name[:12])
                executor.submit(batch_event, target, e, ep, stas, self.channel)


def batch_event(out_dir, cut_evt, evt, stas, channel):
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

    with ThreadPoolExecutor(max_workers=10) as pool:
        for sac in sacs:
            pool.submit(rename_ch, sac, evt, stas, channel)


###############################################################################


def format_sac_name(target: Path, channel):
    """
    rename and ch sac files
    """
    evt_name = target.parent.name
    sta_name = target.name.split('.')[1]
    new_name = f"{evt_name}.{sta_name}.{channel}.sac"

    target_new = target.parent / new_name

    Param_sac = namedtuple("Param_sac", "sta sac")

    return Param_sac(sta_name, target_new)


def ch_sac(target: Path, evt: Pos, sta: Pos, sta_name, channel):
    """
    change head of sac file to generate dist information
    """
    # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)

    s = "wild echo off \n"
    s += "r {} \n".format(target)
    s += f"ch evla {evt.la}\n"
    s += f"ch evlo {evt.lo}\n"
    # s += "ch evdp {}\n".format(self.evt['dp'][evt_name])
    s += f"ch stla {sta.la}\n"
    s += f"ch stlo {sta.lo}\n"
    # s += f"ch stel {sta['dp'][sta_name]}\n"
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


def rename_ch(sac, evt, stas, channel):
    # rename
    res = format_sac_name(sac, channel)
    shutil.move(sac, res.sac)

    # change head
    ch_sac(res.sac, evt, stas[res.sta], res.sta, channel)
    # ch_obspy(res.sac, p.evt, p.stas[res.sta], p.channel)
