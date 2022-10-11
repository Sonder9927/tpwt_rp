# author: sonder
# created: 11 June 2022
# version: 1.3.0
import pygmt
from icecream import ic
from pathlib import Path
import pandas as pd

from pysrc.gmt import average


def make_cpt(VEL_CPT):
    pygmt.makecpt(cmap="plot/gridvel_6_v3.cpt", series=[-10, 10, 0.05], background="", continuous="", output=VEL_CPT)
    #pygmt.makecpt(cmap="seis", series=[3.3, 3.9, 0.1], background="", continuous="", output="plot/test2.cpt")
    pygmt.makecpt(cmap="hot", series=[0, 80, 2.5], background="", continuous="", output="plot/span_AS/std.cpt")


def make_gra(region, TOPO_GRA):
    TOPO_GRD = 'plot/span_AS/topo.grd'
    TOPO_GRD2 = 'plot/span_AS/topo.grd2'

    pygmt.grdcut(grid="plot/ETOPO1.grd", region=region, outgrid=TOPO_GRD)
    pygmt.grdsample(grid=TOPO_GRD, outgrid=TOPO_GRD2, spacing="0.01", region=region)
    pygmt.grdgradient(grid=TOPO_GRD2, azimuth=45, outgrid=TOPO_GRA, normalize="t", verbose="")


def dp_title_fname_tmpgrd_stdgrd(region, grid, std):
    # get TOMO_VEL file and format title
    avgvel = average(grid)
    title = "%s vel=%5.4f" % (grid.name, avgvel)
    ps: list = grid.parents
    fname = f"plot/figs/grid_{ps[-3].name}_AS.png"

    # grid from TOMO_VEL will used in grdimage
    pygmt.blockmean(
        data = str(grid) + ".ave",
        region = region,
        spacing = "0.25/0.25",
        outfile = "plot/span_AS/ttmp"
    )

    pygmt.surface(
        data = "plot/span_AS/ttmp",
        outgrid = "plot/span_AS/tmp.grd",
        region = region,
        spacing = "0.5",
    )

    pygmt.grdsample(
        grid = "plot/span_AS/tmp.grd",
        spacing = "0.01",
        outgrid = "plot/span_AS/tmp2.grd",
    )
    # grid from stdfile will used in grdimage
    pygmt.blockmean(
        data = std,
        region = region,
        spacing = "0.25/0.25",
        outfile = "plot/span_AS/stdtmp"
    )

    pygmt.surface(
        data = "plot/span_AS/stdtmp",
        outgrid = "plot/span_AS/std.grd",
        region = region,
        spacing = "0.5",
    )

    pygmt.grdsample(
        grid = "plot/span_AS/std.grd",
        spacing = "0.02",
        outgrid = "plot/span_AS/std.grd2",
    )
    return title, fname


def dp_grid(region, grid, std, projection, VEL_CPT, TOPO_GRA):
    # get title and create tmp2.grd
    title, fname = dp_title_fname_tmpgrd_stdgrd(region, grid, std)
    ic(title)
    ic(fname)

    # Initial the intance
    fig = pygmt.Figure()

    # Define figure configuration
    pygmt.config(
        MAP_FRAME_TYPE = "plain",
        MAP_TITLE_OFFSET = "0.25p",
        MAP_DEGREE_SYMBOL = "none",
    )

    # plot
    fig.coast(
        region = region,
        projection = projection,
        frame = [f'WSne+t"{title}"', "xa2f2", "ya2f2"],
        area_thresh = 10000,
        land = "white",
        shorelines = "",
        resolution = "l",
    )

    # grdimage
    fig.grdimage(
        grid = "plot/span_AS/tmp2.grd",
        cmap = VEL_CPT,
        shading = TOPO_GRA,
    )

    # plot china textonics
    fig.plot(data="plot/China_tectonic.dat", pen="thick,black,-")
    # plot weihe
    fig.plot(data="plot/weihe1.txt", pen="thick,black,-")
    fig.plot(data="plot/weihe2.txt", pen="thick,black,-")

    # plot station
    df_station = pd.read_csv("plot/station.lst", sep="\s+", header=None, names=["lo", "la"], index_col=0, engine="python")
    fig.plot(
        data = df_station,
        pen = "black",
        style = "t0.1c",
        color = "blue",
    )

    # plot colorbar
    fig.colorbar(
        cmap = VEL_CPT,
        position = "jMR+v+w6c/0.2c+o-1c/0c+m",
        frame = "xa2f2"
    )

    return fig, fname 


# preparing
def dp_std(fig, region, projection):
    
    # plot
    fig.coast(
        region = region,
        projection = projection,
        frame = ['WSne+t"std"', "xa2f2", "ya2f2"],
        area_thresh = 10000,
        land = "white",
        shorelines = "",
        # yshift = "-12",
        resolution = "l",
    )

    # grdimage
    fig.grdimage(
        grid = "plot/span_AS/std.grd2",
        cmap = "plot/span_AS/std.cpt",
    )
	
    # grdimage
    fig.grdcontour(
	    grid = "plot/span_AS/std.grd2",
        interval = "18,20,25,30",
        annotation = "18,20,25,30",
        pen = "black,-",
    )

    # plot china textonics
    fig.plot(data="plot/China_tectonic.dat", pen="thick,black,-")
    # plot weihe
    fig.plot(data="plot/weihe1.txt", pen="thick,black,-")
    fig.plot(data="plot/weihe2.txt", pen="thick,black,-")

    # plot colorbar
    fig.colorbar(
        cmap = "plot/span_AS/std.cpt",
        position = "jMR+v+w6c/0.2c+o-1c/0c+m",
        frame = "xa20f20"
    )
    return fig


def dp_plot(region, grid, std, VEL_CPT, TOPO_GRA):

    projection = "m{}/{}/0.7i".format(region[0], region[2])

    # create an instance of the Figure class and plot grid
    fig, fname = dp_grid(region, grid, std, projection, VEL_CPT, TOPO_GRA)

    # move
    fig.shift_origin(yshift = "-12c")

    # plot std
    fig = dp_std(fig, region, projection)

    # save figure
    fig.savefig(fname)


def dp_AS():
    region= [118.5, 122.5, 29, 32.6]
    ic(region)

    # setting
    TOPO_GRA = 'plot/span_AS/topo.gradient'
    VEL_CPT = 'plot/span_AS/test.cpt'

    # grdgradient to get TOPO_GRA
    make_gra(region, TOPO_GRA)
    # makecpt to get VEL_CPT
    make_cpt(VEL_CPT)

    # period figure
    #per = [20, 25, 26, 28, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]
    work = Path("./")
    grid_list = list(work.glob("**/**/new_2d*/grid.*"))
    grid_list = [i for i in grid_list if not i.suffix == ".ave"]
    std_list = list(work.glob("**/**/new_2d*/stddev.*_v2"))
    for (grid, std) in zip(grid_list, std_list):
        dp_plot(region, grid, std, VEL_CPT, TOPO_GRA)

if __name__ == "__main__":
    ic("Hello Sonder.")
    dp_AS()
    ic("Good luck!")
