from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil

import pandas as pd
from tpwt_p.rose import merge_periods_data, re_create_dir  # pyright: ignore


def mkdir_grids_path(grids_dir, output_dir):
    gp = Path(grids_dir)
    out_path = re_create_dir(output_dir)
    # make dict of grid phase vel of every period
    merged_vel = merge_periods_data(gp, "vel")
    # make dict of grid std of every period
    merged_std = merge_periods_data(gp, "std")
    # merge vel and std
    merged_data = pd.merge(merged_vel, merged_std, on=["x", "y"], how="left")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _, vs in merged_data.iterrows():
            executor.submit(init_grid_path, vs.to_dict(), out_path)


def init_grid_path(vs: dict[str, float], out_path: Path):
    # mkdir grid path
    lo = vs["x"]
    la = vs["y"]
    init_path = out_path / f"{lo:.2f}_{la:.2f}"
    init_path.mkdir()

    # set input files
    shutil.copy("TPWT/utils/mc_DRAM_T.dat", init_path / r"input_DRAM_T.dat")
    shutil.copy("TPWT/utils/mc_PARAM.inp", init_path / r"para.inp")
    grid_phase = init_path / r"phase.input"
    lines = []
    for i, v in vs.items():
        if "vel_" in i:
            per = i[4:]
            std = vs.get(f"std_{per}") or 10
            lines.append(f"2 1 1 {per} {v} {std}\n")
    with open(grid_phase, "w") as f:
        f.write("2 1\n")
        for line in sorted(lines):
            f.write(line)
        f.write("0\n0")
