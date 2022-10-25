from pathlib import Path


def check_exists(target):
    t = Path(target)
    if t.exists():
        pass
    else:
        de = f"Target {target} not found."
        raise FileNotFoundError(de)
