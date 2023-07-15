from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
import shutil

from tpwt_p.rose import re_create_dir  # pyright: ignore


def mkdir_grids(input_dir, output_dir, region, dgrid=[0.5, 0.5], periods=None):
    in_path = Path(input_dir)
    if periods is None:
        # extract periods of files in path
        # pers = [int(f.name.split("_")[-1]) for f in in_path.glob("**/*")]
        pers = [f.name.split("_")[-1] for f in in_path.glob("**/*")]
    else:
        pers = periods

    out_path = Path(output_dir)

    lonmax = region.east + 2
    lonmin = region.west - 2
    latmax = region.north + 2
    latmin = region.south - 2
    [dlon, dlat] = dgrid

    nlat = int((latmax - latmin) / dlat) + 1
    nlon = int((lonmax - lonmin) / dlon) + 1
    lons = [ilon * dlon + lonmin for ilon in range(nlon)]
    lats = [ilat * dlat + latmin for ilat in range(nlat)]
    grids = np.array([[ilon, ilat] for ilon in lons for ilat in lats])

    # make phase vel dict
    per_VS = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for per in pers:
            future = executor.submit(per_vel_std, in_path, per)
            per_vs = future.result()
            np_vs = [i.reshape((nlon, nlat)) for i in per_vs]
            per_VS |= {per: [np_vs]}

    with ThreadPoolExecutor(max_workers=10) as executor:
        for [lon, lat] in grids:
            per_vel = None
            gp = re_create_dir(out_path / rf"{lon:.2f}_{lat:.2f}")
            executor.submit(mc_init, in_path, gp, *vel_std)


def per_vel_std(grid_path: Path, per: str):
    ant_path = grid_path / "ant_grids"
    tpwt_path = grid_path / "tpwt_grids"

    ant_vel_grid = ant_path / f"ant_{per}"
    tpwt_vel_grid = tpwt_path / f"tpwt_{per}"
    vel_grids = [ant_vel_grid, tpwt_vel_grid]
    vels_df = pd.DataFrame(
        {
            f"col_{i}": pd.read_csv(
                f, delim_whitespace=True, usecols=[2], names=["vel"]
            ).vel
            for i, f in enumerate(vel_grids)
            if f.exists()
        }
    )
    vel = vels_df.to_numpy().mean(axis=1)
    tpwt_std_grid = tpwt_path / f"tpwt_std_{per}"
    std_df = pd.read_csv(
        tpwt_std_grid, delim_whitespace=True, usecols=[2], names=["vel"]
    )
    std = std_df.to_numpy()

    return vel, std


def mc_init(grid_path: Path, init_path: Path, pers):
    shutil.copy("TPWT/utils/mc_DRAM_T.dat", init_path / r"input_DRAM_T.dat")
    shutil.copy("TPWT/utils/mc_PARAM.inp", init_path / r"para.inp")
    grid_phase = init_path / r"phase.input"
    with open(grid_phase, "w"):
        mc_phase(init_path, pers)
