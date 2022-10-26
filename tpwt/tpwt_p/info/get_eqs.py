from pathlib import Path
import linecache

from tpwt_p.rose import average, average_inner

from tpwt_p.rose import glob_patterns

class Eq_Per:
    def __init__(self, eq: Path) -> None:
        self.eq = eq

    def __repr__(self) -> str:
        de = f"Eqs:\n  eqlistper: {self.eq}\n  path_list: {self.path_list}"
        return de

    def grid(self) -> Path:
        ptn = r"grid.*"
        if self.grid_target:
            grids = glob_patterns("glob", Path(self.eq.parent), [ptn])
            grids = [i for i in grids if i.suffix != "ave"]
            if len(grids) == 1:
                self.grid_target = grids[0]
            else:
                raise FileNotFoundError(f"No unique target file found with pattern {ptn}")

        return self.grid_target

    def paths(self) -> list[Path]:
        if self.path_list:
            lines = linecache.getlines(str(self.eq))
            linecache.clearcache()
            ps = [n for i in lines if (n := Path(i.replace("\n", "").replace(" ", ""))).suffix == "sac"]
            self.path_list = ps

        return self.path_list

    def avg_vel(self) -> float:
        if self.avgvel:
            self.avgvel = average(self.grid())

        return self.avgvel

    def avg_vel_inner(self, ps) -> float:
        _, avgvel_inner = average_inner(self.grid(), ps)

        return avgvel_inner



def get_eqs_dict(eqs: list) -> dict[str, Eq_Per]:
    eqs_dict = dict()
    for eq in eqs:
        lines = linecache.getlines(eq)
        linecache.clearcache()
        ps = [n for i in lines if (n := Path(i.replace("\n", "").replace(" ", ""))).suffix == "sac"]
        eqs_dict[eq.parent.name] = Eq_Per(eq)

    return eqs_dict
