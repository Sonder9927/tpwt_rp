from pathlib import Path


def check_exists(target) -> Path:
    t = Path(target)
    if t.exists():
        return t
    else:
        de = f"Target {target} not found."
        raise FileNotFoundError(de)

def check_protective(target) -> Path:
    protects = ["TPWT", "target", "tpwt_p", "tpwt_r", "justfile"]
    if str(target) in protects:
        err = rf"`{target}` is protective."
        raise PermissionError(err)
    else:
        return Path(target)
