# author: sonder
# created: 11 June 2022
# version: 1.3.a
'''
description:
plot velocity with scripts from liuhl
'''
from icecream import ic
import pandas as pd
from pathlib import Path
import pygmt

from pysrc.gmt import average

def make_cpt(file):
    # get range
    range = pygmt.info(data=file, incols=[2], per_column=True)
    ic(range)
    pygmt.makecpt(cmap="gray", series=[2.5, range[0], .1], continuous="", output=f"plot/span_Vel/g.cpt")
    #pygmt.makecpt(cmap="gray", series=[2.5, range[0], .1], continuous="", output=f"plot/span_Vel/g{per}.cpt")
    #pygmt.makecpt(cmap="gray", series=[2.5, 3.5, .1], continuous="", output=f"plot/span_Vel/g.cpt")
    #pygmt.makecpt(cmap="plot/Vc_1.8s.cpt", series=range, background="", output=f"plot/span_Vel/Icpt{per}.cpt")
    pygmt.makecpt(cmap="plot/Vc_1.8s.cpt", series=range, background="", output=f"plot/span_Vel/Icpt.cpt")

def make_gra(region, TOPO_GRA):
    TOPO_GRD = 'plot/span_Vel/topo.grd'
    TOPO_GRD2 = 'plot/span_Vel/topo.grd2'

    pygmt.grdcut(grid="plot/ETOPO1.grd", region=region, outgrid=TOPO_GRD)
    pygmt.grdsample(grid=TOPO_GRD, outgrid=TOPO_GRD2, spacing="0.01", region=region)
    pygmt.grdgradient(grid=TOPO_GRD2, azimuth=45, outgrid=TOPO_GRA, normalize="t", verbose="")


def dp_title_fname_tmpgrd(region, grid):
    # get title of figure
    avgvel = average(grid)
    title = "%s vel=%5.4f" % (grid.name, avgvel)
    ps = grid.parents
    fname = f"plot/figs/grid_{ps[-3].name}_Vel"
    if "check" in ps[-1].name:
        fname += "_check.png"
    else:
        fname += ".png"

    make_cpt(grid)

    # grid from TOMO_VEL will used in grdimage
    pygmt.blockmean(
        data = grid,
        region = region,
        spacing = "0.01",
        outfile = "plot/span_Vel/ttmp"
    )

    pygmt.surface(
        data = "plot/span_Vel/ttmp",
        outgrid = "plot/span_Vel/tmp.grd",
        region = region,
        spacing = "0.01",
    )

    pygmt.grdsample(
        grid = "plot/span_Vel/tmp.grd",
        spacing = "0.01",
        outgrid = "plot/span_Vel/tmp2.grd",
    )
    return title, fname

def dp_grid(region, grid):

    # get TOPO_GRA
    TOPO_GRA = 'plot/span_Vel/topo.gradient'
    make_gra(region, TOPO_GRA)

    # get title, fname and create tmp2.grd
    title, fname = dp_title_fname_tmpgrd(region, grid)
    ic(title)
    ic(fname)

    # Initial the intance
    fig = pygmt.Figure()

    fig.grdimage(
        grid = "plot/span_Vel/topo.grd2",
        shading = TOPO_GRA,
        cmap = f"plot/span_Vel/g.cpt",
    )

    # grdimage
    fig.grdimage(
        grid = "plot/span_Vel/tmp2.grd",
        cmap = f"plot/span_Vel/Icpt.cpt",
        shading = TOPO_GRA,
    )

    # plot china textonics
    fig.plot(data="plot/China_tectonic.dat", pen="1p,black,-")
    # plot CN-faults
    fig.plot(data="plot/CN-faults.dat", pen="1p,black,-")
    # plot weihe
    #fig.plot(data="plot/weihe1.txt", pen="thick,black,-")
    #fig.plot(data="plot/weihe2.txt", pen="thick,black,-")

    # plot station
    df_station = pd.read_csv("plot/station.lst", sep="\s+", header=None, names=["lo", "la"], index_col=0, engine="python")
    fig.plot(
        data = df_station,
        style = "t0.2",
        color = "red",
    )

    # plot
    fig.coast(
        frame = [f'WSne+t"{title}"', "xa0.6f0.1", "ya0.4f0.1"],
        area_thresh = 1000,
        shorelines = ["1/0.8p,black", "2/0.5p,black"],
        resolution = "f",
    )
    # plot colorbar
    fig.colorbar(
        #cmap = f"plot/span_Vel/Icpt{per}.cpt",
        cmap = f"plot/span_Vel/Icpt.cpt",
        position = "jBC+w10c/0.3c+o0c/-2c+m",
        frame = "xa0.05f0.05",
    )

    fig.savefig(fname)


# hou mian you hua:
# jiang grid he check feng zhuang jin yi ge struct
def plot_Vel(check=False):
    region= [118.5, 122.5, 29, 32.6]
    ic(region)

    work = Path("./")
    if check:
        grid_list = list(work.glob("**/**/new_2d*/check*/grid.*"))
    else:
        grid_list = list(work.glob("**/**/new_2d*/grid.*"))

    # grid_list = [i for i in grid_list if i.suffix == ".ave"]
    grid_list = [i for i in grid_list if not i.suffix == ".ave"]
    for grid in grid_list:
        dp_grid(region, grid)

if __name__ == "__main__":
    ic("Hello Sonder.")
    plot_Vel()
    ic("Good luck!")
