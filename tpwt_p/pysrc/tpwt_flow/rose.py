from pathlib import Path
import shutil


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
        raise AttributeError(e)

    if lst:
        return lst
    else:
        e = f"No file found in {path} with patterns {patterns}."
        raise FileNotFoundError(e)


def re_create_dir(target: str):
    """
    Re-create the dir given if it exists, or create it.
    """
    d = Path(target)
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def remove_files(targets: list):
    """
    remove a list of targets
    """
    for target in targets:
        t = Path(target)
        if t.is_dir():
            shutil.rmtree(target)
        elif t.is_file():
            t.unlink()
