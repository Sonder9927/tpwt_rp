from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil

import pandas as pd
from tpwt_p.gmt import grid_sample
from tpwt_p.rose import (
    merge_periods_data,
    points_boundary,
    points_inner,
    re_create_dir,
)


def mkdir_grids_path(
    grids_dir: str, moho_file: str, output_dir, periods, sta_file
):
    gp = Path(grids_dir)
    out_path = re_create_dir(output_dir)
    # sample moho grid
    moho_sta = pd.read_csv(
        moho_file,
        header=None,
        delim_whitespace=True,
        usecols=[0, 1, 2],
        names=["x", "y", "z"],
    )
    moho_sta = moho_sta[["y", "x", "z"]]
    moho_data = grid_sample(
        moho_sta, region=[115, 123, 26.5, 35.5], spacing=0.5
    )
    # make dict of grid phase vel of every period
    merged_vel = merge_methods_periods(gp, "vel")
    # make dict of grid std of every period
    merged_std = merge_methods_periods(gp, "std")

    # merge vel and std
    merged_data = pd.merge(merged_vel, merged_std, on=["x", "y"], how="left")
    merged_data = pd.merge(merged_data, moho_data, on=["x", "y"], how="left")
    if sta_file is None:
        merged_inner = merged_data
    else:
        sta = pd.read_csv(
            sta_file,
            index_col=None,
            header=None,
            usecols=[1, 2],
            delim_whitespace=True,
        )
        boundary = points_boundary(sta)
        merged_inner = points_inner(merged_data, boundary=boundary)
    with ThreadPoolExecutor(max_workers=10) as pool:
        utils = Path("TPWT/utils")
        # models
        pool.submit(shutil.copytree, utils / "models", out_path / "models")
        for _, vs in merged_inner.iterrows():
            pool.submit(init_grid_path, vs.to_dict(), out_path, periods, utils)


def init_grid_path(
    vs: dict[str, float], out_path: Path, periods: list[int], utils: Path
):
    # mkdir grid path
    lo = vs["x"]
    la = vs["y"]
    init_path = out_path / f"{lo:.2f}_{la:.2f}"
    init_path.mkdir()

    # # litmod
    # shutil.copy(utils / "mc_LITMOD", init_path / r"LITMOD")
    # dram T
    shutil.copy(utils / "mc_DRAM_T.dat", init_path / r"input_DRAM_T.dat")
    # param
    shutil.copy(utils / "mc_PARAM.inp", fin := init_path / r"para.inp")
    moho = vs.get("z") or 20
    with open(fin, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if line.startswith(st := "0 1"):
                f.write(f"{st} {moho-5:2.5f} {moho+5:2.5f}\n")
            else:
                f.write(line)

    # phase
    grid_phase = init_path / r"phase.input"
    lines = []
    for per in sorted(periods):
        vel = vs.get(f"vel_{per}")
        if vel is None:
            raise ValueError(f"No grid data of period {per}")
        std = vs.get(f"std_{per}") or 20
        lines.append(f"2 1 1 {per:>3} {vel:f} {std * .001:f}\n")
    lines.insert(0, f"1 {len(lines)}\n")
    lines.append("0\n0")

    with open(grid_phase, "w") as f:
        # f.write(f"1 {len(lines)}\n")
        # for line in lines:
        #     f.write(line)
        # f.write("0\n0")
        f.writelines(lines)


def merge_methods_periods(gp: Path, identifier: str):
    merged_ant = merge_periods_data(gp, "ant", identifier)
    merged_tpwt = merge_periods_data(gp, "tpwt", identifier)
    if merged_tpwt is None:
        raise ValueError(f"No grid info for id: {identifier}")
    if merged_ant is not None:
        merged_data = pd.merge(
            merged_ant,
            merged_tpwt,
            on=["x", "y"],
            how="left",
        )
        for c in merged_data.columns:
            if "_x" in c:
                col_name = c[:-2]
                col_new = (
                    merged_data[f"{col_name}_x"] + merged_data[f"{col_name}_y"]
                ) / 2
                merged_data[col_name] = col_new
    else:
        merged_data = merged_tpwt

    return merged_data
