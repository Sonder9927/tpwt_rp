from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd
import shutil

from tpwt_p.rose import re_create_dir  # pyright: ignore


def merge_periods_data(grid_path: Path, identifier: str):
    merged_data = None
    for f in grid_path.glob(f"*/*{identifier}*"):
        per = f.stem.split("_")[-1]
        col_name = f"{identifier}_{per}"
        data = pd.read_csv(
            f, header=None, delim_whitespace=True, names=["x", "y", col_name]
        )
        # identifier = f"_{per}"
        if merged_data is None:
            merged_data = data
        else:
            merged_data = pd.merge(
                merged_data,
                data,
                on=["x", "y"],
                how="left",
            )

        if col_name not in merged_data.columns:
            col_new = (
                merged_data[f"{col_name}_x"] + merged_data[f"{col_name}_y"]
            ) / 2
            merged_data[col_name] = col_new

    if merged_data is not None:
        return merged_data
    else:
        raise ValueError("No grid data into!")


def mkdir_grids_path(grid_dir, output_dir):
    gp = Path(grid_dir)
    out_path = re_create_dir(output_dir)
    # make grid phase vel of every period dict
    merged_vel = merge_periods_data(gp, "vel")
    merged_std = merge_periods_data(gp, "std")
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
    lines = ["2 1\n"]
    for i, v in vs.items():
        if "vel_" in i:
            per = i[4:]
            std = vs.get(f"std_{per}") or 10
            lines.append(f"2 1 1 {per} {v} {std}\n")
    lines += ["0\n0"]
    with open(grid_phase, "w") as f:
        for line in lines:
            f.write(line)
