from pathlib import Path
import pandas as pd
import shutil


# get bin for using
def get_binuse(c: str, bin_from='./') -> Path:
    b = Path(bin_from) / 'TPWT/bin' / c
    if b.exists():
        return b
    else:
        e = f"The binary {b} doesn't exist."
        raise FileNotFoundError(e)

###############################################################################

def glob_patterns(method: str, path: Path, patterns: list) -> list:
    """
    Find files with the pattern in the list given as patterns
    by methods `glob` or `rglob`.
    """
    lst = []
    if method == "rglob":
        for pattern in patterns:
            lst += list(path.rglob(pattern))
    elif method == "glob":
        for pattern in patterns:
            lst += list(path.glob(pattern))
    else:
        e = f"Please use 'glob' or 'rglob' to find files with patterns."
        raise KeyError(e)

    if lst:
        return lst
    else:
        e = f"No file found in {path} with patterns {patterns}."
        raise FileNotFoundError(e)


###############################################################################


def get_dirname(target: str, *, snr, tcut, smooth, damping, period, dist):
    de = "Please point out the arguments: "
    if target in ["TPWT", "tpwt"]:
        if all([snr, tcut, smooth, damping]):
            return get_tpwt_dirname(snr, tcut, smooth, damping)
        else:
            raise KeyError(de + "snr, tcut, smooth, damping")
    elif target == "sec":
        if all([period, snr, dist]):
            return get_sec_dirname(period, snr, dist)
        else:
            raise KeyError(de + "period, snr, dist")
    else:
        raise KeyError(f"Not support for `{target}`.")


def get_sec_dirname(period, snr, dist) -> Path:
    return Path(f'{period}sec_{snr}snr_{dist}dis')


def get_tpwt_dirname(snr, tcut, smooth, damping) -> Path:
    return Path(f'TPWT_{snr}_snr_{tcut}tcut_{smooth}smooth_{damping}damping')


###############################################################################


def re_create_dir(target) -> Path:
    """
    Re-create the dir given if it exists, or create it.
    """
    d = protective(target)
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def protective(target) -> Path:
    protects = ["TPWT", "target", "tpwt_p", "tpwt_r", "justfile"]
    if str(target) in protects:
        err = rf"`{target}` is protective."
        raise PermissionError(err)
    else:
        return Path(target)


def remove_targets(targets: list):
    """
    remove a list of targets
    """
    for target in targets:
        t = protective(target)
        if t.is_dir():
            shutil.rmtree(target)
        elif t.is_file():
            t.unlink()


###############################################################################


def read_xyz(f, ns: list[str]) -> pd.DataFrame:
    return pd.read_csv(f, delim_whitespace=True, usecols=[0, 1, 2], header=None, names=ns)


def read_xy(f) -> pd.DataFrame:
    return pd.read_csv(f, delim_whitespace=True, header=None, usecols=[1, 2], names=["lo", "la"])


###############################################################################

