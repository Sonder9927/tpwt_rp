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

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from collections import namedtuple
from pathlib import Path
from icecream import ic
import pandas as pd
import os, shutil
import subprocess

from tpwt_p.rose import glob_patterns, re_create_dir
from .obs_mod import Obs


Param_evt = namedtuple("Param_evt", "out_dir cut_evt evt stas channel")

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
        ic(self.channel)

    def evt_to_point(self, evt: str) -> Pos:
        return Pos(x=self.evt.lo[evt], y=self.evt.la[evt])

    def sta_to_points(self) -> dict[str, Pos]:
        dl = self.sta.index
        dd = [Pos(x=self.sta.lo[i], y=self.sta.la[i]) for i in dl]
        return dict(zip(dl, dd))

    def get_SAC(self, target):
        # clear and re-create
        self.target = re_create_dir(target)

        # get list of events directories
        cut_evts = glob_patterns("glob", self.data, ["*/**"])
        stas = self.sta_to_points()

        ps = [Param_evt(self.target, i, self.evt_to_point(i.name[:12]), stas, self.channel) for i in cut_evts]

        # batch process
        ic("batch processing...")
        Pool(10).map(batch_event, ps)

    def ch_sac(self, target: Path):
        """
        change head of sac file to generate dist information
        """
        # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)
        [evt_name, sta_name, _] = target.stem.split('.')

        s = "wild echo off \n"
        s += "r {} \n".format(target)
        s += f"ch evla {self.evt.la[evt_name]}\n"
        s += f"ch evlo {self.evt.lo[evt_name]}\n"
        # s += "ch evdp {}\n".format(self.evt['dp'][evt_name])
        s += f"ch stla {self.sta.la[sta_name]}\n"
        s += f"ch stlo {self.sta.lo[sta_name]}\n"
        # s += f"ch stel {self.sta['dp'][sta_name]}\n"
        s += f"ch kcmpnm {self.channel}\n"
        s += "wh \n"
        s += "q \n"

        os.putenv("SAC_DISPLAY_COPYRIGHT", "0")
        subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())

def batch_event(p):
    """
    batch function to process every event
    move events directories
    format sac files
    """
    # move
    sac_evt = p.out_dir / p.cut_evt.name[:12]
    shutil.copytree(p.cut_evt, sac_evt)

    # process every sac file
    sacs = glob_patterns("glob", sac_evt, ["*"])

    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(rename_ch, [p]*len(sacs), sacs)


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


def ch_obspy(target: Path, evt: Pos, sta: Pos, channel):
    """
    change head of sac file to generate dist information
    """
    # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)
    obs = Obs(target, evt, sta, channel)
    obs.ch_obs()


def rename_ch(p: Param_evt, sac):
    # rename
    res = format_sac_name(sac, p.channel)
    shutil.move(sac, res.sac)

    # change head
    ch_obspy(res.sac, p.evt, p.stas[res.sta], p.channel)
