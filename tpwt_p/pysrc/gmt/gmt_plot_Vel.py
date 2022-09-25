# author: sonder
# created: 11 June 2022
# version: 1.2.b

'''
description:
plot velocity with scripts from Liu hl.
'''

import pygmt
from icecream import ic
import os
import pandas as pd
import threading


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


def dp_title_and_tmpgrd(per, region, TOMO_VEL):

    # get title of figure
    _, title = average(TOMO_VEL)

    make_cpt(TOMO_VEL)

    # grid from TOMO_VEL will used in grdimage
    pygmt.blockmean(
        data = TOMO_VEL,
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
    return title


def dp_grid(per, region, TOMO_VEL):

    # get TOPO_GRA
    TOPO_GRA = 'plot/span_Vel/topo.gradient'
    make_gra(region, TOPO_GRA)

    # get title and create tmp2.grd
    title = dp_title_and_tmpgrd(per, region, TOMO_VEL)
    ic(title)

    # Initial the intance
    fig = pygmt.Figure()


    fig.grdimage(
        grid = "plot/span_Vel/topo.grd2",
        shading = TOPO_GRA,
        cmap = f"plot/span_Vel/g.cpt",
    )

    #pygmt.grdclip(
    #    grid = "data/boundry.dat",
    #    region = region,
    #)

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
    df_station = pd.read_csv("plot/station.lst", sep="\s+", header=None, names=["la", "lo"], index_col=0, engine="python")
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

    return fig


def dp_plot(per, region, tpwpath, check=False):

    # get TOMO_VEL file and format title
    tpw_path = '{}/{}/new_2d'.format(tpwpath, per)
    TOMO_VEL = "not exists"
    files = os.listdir(tpw_path)
    for f in files:
        if check:
            if "check" in f and os.path.isdir("{}/{}".format(tpw_path, f)):
                for ff in os.listdir(f"{tpw_path}/{f}"):
                    if "grid." in ff and not ff.endswith(".ave"):
                        ic(check)
                        ic(ff)
                        TOMO_VEL = "{}/{}/{}".format(tpw_path, f, ff)
                        break
                break
                        
        else:
            if "grid." in f and not f.endswith(".ave"):
                ic(f)
                TOMO_VEL = "{}/{}".format(tpw_path, f)
                break
    ic(TOMO_VEL)
    # create an instance of the Figure class and plot grid
    fig = dp_grid(per, region, TOMO_VEL)

    # save figure
    if check:
        fig.savefig(f"plot/fig/grid{per}_vel_check.png")
    else:
        fig.savefig(f"plot/fig/grid{per}_vel.png")
    ic(per, "complete")

def plot_Vel():
    area= []
    ic(area)

    # period figure
    for tpw in os.listdir():
        if "TPW_" in tpw:
            tpwpath = tpw
            break
    for per in os.listdir(tpwpath):
        threads = []
        #threads.append(threading.Thread(target=dp_plot, args=(per, area, tpwpath)))
        threads.append(threading.Thread(target=dp_plot, args=(per, area, tpwpath, True)))
        for t in threads:
            t.start()
            t.join()
    #dp_plot(per, area)
    #dp_plot(per, area, check=True)

if __name__ == "__main__":
    ic("Hello Sonder.")
    plot_Vel()
    ic("Good luck!")
