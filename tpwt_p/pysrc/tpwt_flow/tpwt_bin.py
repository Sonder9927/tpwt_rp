from pathlib import Path
# get bin for using
def get_binuse(b: str, bin_from='./'):
    return Path(bin_from) / 'TPWT/bin' / b
