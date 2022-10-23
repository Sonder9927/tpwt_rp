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
from pathlib import Path
from icecream import ic
import pandas as pd
import os, shutil
import subprocess

from tpwt_p.rose import glob_patterns, re_create_dir
from .obs_mod import Obs


class Sac_Format:
    def __init__(self, data, evt, sta) -> None:
        self.data = Path(data)
        self.channel = "LHZ"
        self.evt = pd.read_csv(evt, delim_whitespace=True, names=["evt", "lo", "la"], dtype={"evt": str}, index_col="evt")
        self.sta = pd.read_csv(sta, delim_whitespace=True, names=["sta", "lo", "la"], index_col="sta")
        ic(f"Hello, this is SAC formatter, channel is {self.channel}.")

    def get_SAC(self, target):
        # clear and re-create
        self.target = re_create_dir(target)

        # get list of events directories
        cut_evts = glob_patterns("glob", self.data, ["*/**"])

        def batch_event(cut_evt):
            """
            batch function to process every event
            move events directories
            format sac files
            """
            # move
            sac_evt = self.target / cut_evt.name[:12]
            shutil.copytree(cut_evt, sac_evt)

            # rename
            sacs = glob_patterns("glob", sac_evt, ["*"])
            for sac in sacs:
                sac_new = format_sac_name(sac, self.channel)
                shutil.move(sac, sac_new)
                self.ch_obspy(sac_new)

        # batch process
        ic("batch processing...")
        with ThreadPoolExecutor(max_workers=4) as pool:
            pool.map(batch_event, cut_evts)

    def ch_obspy(self, target: Path):
        """
        change head of sac file to generate dist information
        """
        # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)
        [evt_name, sta_name, _] = target.stem.split('.')

        ep = [self.evt.lo[evt_name], self.evt.la[evt_name]]
        sp = [self.sta.lo[sta_name], self.sta.la[sta_name]]
        obs = Obs(target, ep, sp, self.channel)
        # change the original file if no argument given
        obs.ch_obs()

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


def format_sac_name(target, channel):
    """
    rename and ch sac files
    """
    evt_name = target.parent.name
    sta_name = target.name.split('.')[1]
    new_name = f"{evt_name}.{sta_name}.{channel}.sac"

    target_new = target.parent / new_name
    return target_new
