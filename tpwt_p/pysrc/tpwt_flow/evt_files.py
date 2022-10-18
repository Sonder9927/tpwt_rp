from concurrent.futures import ThreadPoolExecutor
from icecream import ic
from pathlib import Path
import datetime as dt
import pandas as pd
import os, shutil
import subprocess

from pysrc.tpwt import get_binuse

class Evt_Files:
    def __init__(self, evt1, evt2):
        self.evt1 = pd.read_csv(evt1, usecols=["time", "latitude", "longitude"])
        self.evt2 = pd.read_csv(evt2, usecols=["time", "latitude", "longitude"])

    def evt(self):
        return self.evt

    def evt_concat(self):
        evt = pd.concat([self.evt1, self.evt2]).drop_duplicates(keep=False)
        evt.index = pd.to_datetime(evt["time"])
        self.evt = evt

    def evt_cut(self, time_delta):
        temp = sorted(self.evt.index)

        drop_lst = set()
        for i in range(len(temp)-1):
            du = (temp[i+1] - temp[i]).total_seconds()
            if du < time_delta:
                drop_lst.update(temp[i: i+2])

        self.evt.drop(drop_lst, inplace=True)

    def get_cat(self, cat, cat_pattern):
        evt = self.evt["time"].apply(lambda x: time_convert(str(x)[:19], cat_pattern))
        evt.to_csv(cat, sep=" ", header=False, index=False)

    def get_lst(self, lst, lst_pattern):
        evt = self.evt
        evt["time"] = evt["time"].apply(lambda x: time_convert(str(x)[:19], lst_pattern))
        evt[["longitude","latitude"]] = self.evt[["latitude","longitude"]]
        evt.to_csv(lst, sep=" ", header=False, index=False)


def time_convert(val: str, form: str) -> str:
    time = dt.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
    return dt.datetime.strftime(time, form)



