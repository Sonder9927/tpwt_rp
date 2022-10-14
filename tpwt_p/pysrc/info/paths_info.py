from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from icecream import ic
from threading import Lock
import linecache

# My scripts
# functions
from pysrc.get_param import get_param_json


"""
plot ray path
"""


class Paths:
    def __init__(self, per: float, paths: list) -> None:
        self.period = per 
        self.paths = paths

    def len(self) -> int:
        return len(self.paths)


def get_path(per, lock):
    eqlistpers = list(Path.cwd().glob(f'TPW_*/{per}/**/eqlistper{per}'))
    if len(eqlistpers) == 1:
        eqlistper = eqlistpers[0]
        ic(eqlistper)

        lines = linecache.getlines(eqlistper)
        linecache.clearcache()
        ps = [n[-26:] for i in lines if ".sac" in (n := i.replace("\n", "").replace(" ", ""))]
        ps = Paths(per, ps)
        ic(per, ps.len())

        lock.acquire()
        paths_dict[per] = ps
        lock.release()

    else:
        raise FileNotFoundError(f"There is more than one object file:\n{eqlistpers}")

def get_paths_of_all_periods(param_json):
    # instancs a parameters class
    # get parameters
    param = get_param_json(param_json)
    periods: list = param['immutables']['periods']

    global paths_dict
    paths_dict: dict = {}
    # check if station and event lists and eqlistper exists.
    lock = Lock()
    with ThreadPoolExecutor(max_workers=4) as pool:
        # more details to save time, dont use this way
        pool.map(get_path, periods, [lock]*len(periods))


if __name__ == "__main__":
    get_paths_of_all_periods("param.json")
