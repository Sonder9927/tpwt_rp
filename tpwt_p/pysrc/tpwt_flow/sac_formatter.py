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


class Sac_Format:
    def __init__(self, data, evt, sta) -> None:
        self.data = Path(data)

        if (os.path.exists(sta) and os.path.exists(evt)):
            ic("will create SAC")
        else:
            raise FileNotFoundError('No station.lst or event.lst found.')

        self.sta = pd.read_csv(sta, delim_whitespace=True, names=["sta", "lo", "la"], index_col="sta")
        self.evt = pd.read_csv(evt, delim_whitespace=True, names=["evt", "lo", "la"], dtype={"evt": str}, index_col="evt")

    def get_SAC(self, target):
        target = Path(target)

        # clear and re-create
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        # get list of events directories
        cut_evts = list(self.data.glob("*/**"))

        def batch_event(cut_evt):
            """
            batch function to process every event
            move events directories
            format sac files
            """
            # move
            sac_evt = target / cut_evt.name[:12]
            shutil.copytree(cut_evt, sac_evt)

            # rename
            sacs = list(sac_evt.glob("*"))
            for sac_file in sacs:
                sac_path = format_sac(sac_file)
                self.ch_sac(sac_path)

        # batch process
        ic("batch processing...")
        with ThreadPoolExecutor(max_workers=4) as pool:
            pool.map(batch_event, cut_evts)

    def ch_sac(self, sac_path):
        """
        change head of sac file to generate dist information
        """
        # ch evla, evlo, evdp(optional) and stla, stlo, stel(optional)
        [evt_name, sta_name, channel, _] = sac_path.name.split('.')

        s = "wild echo off \n"
        s += "r {} \n".format(sac_path)
        s += f"ch evla {self.evt.la[evt_name]}\n"
        s += f"ch evlo {self.evt.lo[evt_name]}\n"
        # s += "ch evdp {}\n".format(self.evt['dp'][evt_name])
        s += f"ch stla {self.sta.la[sta_name]}\n"
        s += f"ch stlo {self.sta.lo[sta_name]}\n"
        # s += f"ch stel {self.sta['dp'][sta_name]}\n"
        s += f"ch kcmpnm {channel}\n"
        s += "wh \n"
        s += "q \n"

        os.putenv("SAC_DISPLAY_COPYRIGHT", "0")
        subprocess.Popen(['sac'], stdin=subprocess.PIPE).communicate(s.encode())


def format_sac(target):
    """
    rename and ch sac files
    """
    evt_name = target.parent.name
    sta_name = target.name.split('.')[1]
    new_name = f"{evt_name}.{sta_name}.LHZ.sac"

    target_new = target.parent / new_name
    shutil.move(target, target_new)
    return target_new
