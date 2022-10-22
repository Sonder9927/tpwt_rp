from pathlib import Path


# get bin for using
def get_binuse(c: str, bin_from='./'):
    b = Path(bin_from) / 'TPWT/bin' / c
    if b.exists():
        return b
    else:
        e = f"The binary {b} doesn't exist."
        raise FileNotFoundError(e)
