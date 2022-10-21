from icecream import ic
import datetime as dt
import pandas as pd


class Evt_Files:
    def __init__(self, evt1, evt2):
        self.evt1 = pd.read_csv(evt1, usecols=["time", "latitude", "longitude"])
        self.evt2 = pd.read_csv(evt2, usecols=["time", "latitude", "longitude"])
        self.state = "NONE"

    def info(self):
        return f"The state of evt is {self.state},\nevt:\n{self.evt}"

    def concat(self):
        self.evt = pd.concat([self.evt1, self.evt2]).drop_duplicates(keep=False)
        self.state = "CONCATTED"

    def cut_time_delta(self, time_delta):
        if self.state != "CONCATTED":
            ic(f"evt is {self.state}, not CONCATTED.")
            return

        evt = self.evt
        evt.index = pd.to_datetime(evt["time"])
        temp = sorted(evt.index)

        drop_lst = set()
        for i in range(len(temp)-1):
            du = (temp[i+1] - temp[i]).total_seconds()
            if du < time_delta:
                drop_lst.update(temp[i: i+2])

        self.evt = evt.drop(drop_lst)

    def evt_cat(self, cat, pattern, form):
        evt = self.evt["time"].apply(lambda x: time_convert(str(x)[:19], pattern, form))
        evt.to_csv(cat, sep=" ", header=False, index=False)
        ic("Sucessfully get", cat)

    def evt_lst(self, lst, pattern, form):
        evt = self.evt
        evt["time"] = evt["time"].apply(lambda x: time_convert(str(x)[:19], pattern, form))
        evt[["longitude","latitude"]] = self.evt[["latitude","longitude"]]
        evt.to_csv(lst, sep=" ", header=False, index=False)
        ic("Sucessfully get", lst)


def time_convert(val: str, pattern:str, form: str) -> str:
    time = dt.datetime.strptime(val, pattern)
    return dt.datetime.strftime(time, form)
