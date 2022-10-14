from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from icecream import ic
import pandas as pd
import threading
import pygmt
import os, shutil
import subprocess
import linecache

# My scripts
# functions
from pysrc.get_param import get_param_json

# classes
from pysrc.get_param import Param

"""
plot ray path
"""


def get_plot_data(p: Param, eqlistper: str):
    """
    get x, y of both events and stations    
    """
    # with open(eqlistper, 'r') as f:
    #     f.readlines()
    lines = linecache.getlines(eqlistper)
    linecache.clearcache()
    eqs = [n[-26:] for i in lines if ".sac" in (n := i.replace("\n", "").replace(" ", ""))]

    # get information of stations and events
    sta = pd.read_csv(p.sta, delim_whitespace=True, names=["sta", "lo", "la"], index_col="sta")
    evt = pd.read_csv(p.evt, delim_whitespace=True, names=["evt", "lo", "la"], dtype={"evt": str}, index_col="evt")

    evt_sta_x = []
    evt_sta_y = []
    evts = set()
    stas = set()
    sta_x = []
    sta_y = []
    lock = threading.Lock()

    def get_evt_sta_position(eq):
        """
        get x, y of both event and station in each eq
        """
        [evt_name, sta_name] = eq.split('.')[:2]
        ex, ey = evt["lo"][evt_name], evt["la"][evt_name]
        sx, sy = sta["lo"][sta_name], sta["la"][sta_name]
        with lock:
            evts.add(evt_name)
            evt_sta_x.append([ex, sx])
            evt_sta_y.append([ey, sy])

            stas.add(sta_name)
            sta_x.append(sx)
            sta_y.append(sy)

    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(get_evt_sta_position, eqs)

    title = f"{len(eqs)}paths-{len(evts)}events-{len(stas)}stations"
    path_data = {"x": evt_sta_x, "y": evt_sta_y}
    sta_data = {"x": sta_x, "y": sta_y}
    return title, pd.DataFrame(path_data), pd.DataFrame(sta_data)


def gmt_plot_path(title, region, path_data, sta_data):
    """
    pygmt plot ray path and stations in the region
    """
    lon0 = (region["west"] + region["east"]) / 2
    lat0 = (region["sourth"] + region["north"]) / 2

    # Initial the intance
    fig = pygmt.Figure()
    # plot
    fig.coast(
        projection = f"M{lon0}/{lat0}/5i",
        region = [region[i] for i in ["west", "east", "sourth", "north"]],
        frame = [f'WSne+t"{title}"', "xa2f2", "ya2f2"],
        area_thresh = 10_000,
        shorelines = "",
        land = "white",
        resolution = "l",
    )

    # plot ray paths
    ic(path_data.head())
    for d in path_data.index:
        fig.plot(x=path_data["x"][d], y=path_data["y"][d], pen="0.1p,black")

    # plot stations
    fig.plot(data=sta_data, style="t0.1c", color="blue", pen="black")

    return fig


def plot_path(param: Param, eqlistper: str):
    title, path_data, sta_data = get_plot_data(param, eqlistper)

    fig = gmt_plot_path(title, param.region, path_data, sta_data)
    # save figure
    fig.savefig(f"ray_path_period{param.period}.png")


def gmt_tpwt_path(param_json: str, periods: list):
    # instancs a parameters class
    p = Param
    # get parameters
    param = get_param_json(param_json)
    # files
    p_f = param['files']
    p.evt = p_f["evt"]
    p.sta = p_f["sta"]
    p.output = p_f['output']
    # immutables
    p_immu = param['immutables']
    p.region = p_immu['region']

    # check if station and event lists and eqlistper exists.
    if (os.path.exists(p.sta) and os.path.exists(p.evt)):
        with ThreadPoolExecutor(max_workers=5) as pool:
            for period in periods:
                p.period = period
                eqlistper = list(Path('./').glob(f'TPWT_*/{period}/{p.output}/eqlistper{period}'))[0]
                ic(str(eqlistper))
                # more details to save time, dont use this way
                if eqlistper.exists:
                    pool.submit(plot_path, p, str(eqlistper))
                else:
                    raise FileNotFoundError(f"No eqlistper{period} found")
    else:
        raise Exception('No station.lst or event.lst found.')


if __name__ == "__main__":
    gmt_tpwt_path("param.json", periods=[26])
