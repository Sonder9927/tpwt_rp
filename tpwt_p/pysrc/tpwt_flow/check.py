from pathlib import Path

def rglob_patterns(path: Path, patterns:list) -> list:
    lst = []
    for pattern in patterns:
        lst += list(path.rglob(pattern))

    if lst:
        return lst
    else:
        e = f"No file found in {path} with patterns {patterns}."
        raise FileNotFoundError(e)
