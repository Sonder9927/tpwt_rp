# author: sonder
# created: 11 June 2022
# version: 1.2
import pygmt
from icecream import ic
import os
import pandas as pd

"""
plot std and average std
"""

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


def average(file):
    '''
    read the velocity and calculate the average value
    return avevel and title
    '''
    df = pd.read_csv(file, sep="\s+", header=None, names=["la", "lo", "vel"], engine="python")
    avevel = df["vel"].sum() / len(df)
    title = os.path.basename(file)
    title = "%s vel=%5.4f" % (title, avevel)
    return avevel, title

def dp_title_tmpgrd_stdgrd(per, region, tpwpath):
    # get TOMO_VEL file and format title
    files = os.listdir('{}/{}/new_2d'.format(tpwpath, per))
    for f in files:
        if "grid." in f and not f.endswith(".ave"):
            ic(f)
            TOMO_VEL = "{}/{}/new_2d/{}".format(tpwpath, per, f)
            _, title = average(TOMO_VEL)
        elif f.endswith("_v2"):
            ic(f)
            stdfile = "{}/{}/new_2d/{}".format(tpwpath, per, f)

    # grid from TOMO_VEL will used in grdimage
    pygmt.blockmean(
        data = TOMO_VEL + ".ave",
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
        data = stdfile,
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
    return title

def dp_grid(per, region, projection, VEL_CPT, TOPO_GRA, tpwpath):
    # get title and create tmp2.grd
    title = dp_title_tmpgrd_stdgrd(per, region, tpwpath)
    ic(title)

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
    df_station = pd.read_csv("plot/station.lst", sep="\s+", header=None, names=["la", "lo"], index_col=0, engine="python")
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

    return fig 

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
#yshift = "-12",
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

def dp_plot(per, region, VEL_CPT, TOPO_GRA, tpwpath):

    projection = "m{}/{}/0.7i".format(region[0], region[2])

    # create an instance of the Figure class and plot grid
    fig = dp_grid(per, region, projection, VEL_CPT, TOPO_GRA, tpwpath)

    # move
    fig.shift_origin(yshift = "-12c")

    # plot std
    fig = dp_std(fig, region, projection)

    # save figure
    fig.savefig(f"plot/fig/grid{per}_ave_with_stddev.png")
    ic(per, "complete")

def main():
    region = []
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
    for tpw in os.listdir():
        if "TPWT_" in tpw:
            tpwpath =  tpw
            break
    for per in os.listdir(tpwpath):
        dp_plot(per, region, VEL_CPT, TOPO_GRA, tpwpath)

if __name__ == "__main__":
    ic("Hello Sonder.")
    main()
    ic("Good luck!")
