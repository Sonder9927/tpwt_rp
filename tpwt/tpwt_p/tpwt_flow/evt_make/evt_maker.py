from icecream import ic
import datetime as dt
from icecream.coloring import Error
import pandas as pd


class Evt_Make:
    def __init__(self, evt1, evt2, time_delta):
        self.pattern = "%Y-%m-%dT%H:%M:%S"
        self.header = ["time", "latitude", "longitude", "depth", "mag"]
        self.evt1 = pd.read_csv(evt1, usecols=self.header)
        self.evt2 = pd.read_csv(evt2, usecols=self.header)
        self._cut_time_delta(time_delta)
        ic("Hello, this is EVT maker.")

    def _cut_time_delta(self, time_delta):
        evt = pd.concat([self.evt1, self.evt2]).drop_duplicates(keep=False)
        if evt is None:
            raise ValueError
        evt.index = pd.to_datetime(evt["time"])
        temp = sorted(evt.index)

        drop_lst = set()
        for i in range(len(temp) - 1):
            du = (temp[i + 1] - temp[i]).total_seconds()
            if du < time_delta:
                drop_lst.update(temp[i: i + 2])

        self.evt = evt.drop(drop_lst)

    def extract(self, hn, form, fn):
        evt = self.evt[self.header[:hn]]
        evt["time"] = evt["time"].apply(
            lambda x: time_convert(str(x)[:19], self.pattern, form)
        )
        if hn >= 3:
            evt[["longitude", "latitude"]] = self.evt[
                ["latitude", "longitude"]
            ]
        evt.to_csv(fn, sep=" ", header=False, index=False)
        ic("Sucessfully get", fn)


def time_convert(val: str, pattern: str, form: str) -> str:
    time = dt.datetime.strptime(val, pattern)
    return dt.datetime.strftime(time, form)
