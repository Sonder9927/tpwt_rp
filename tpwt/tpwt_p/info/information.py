from pathlib import Path

from tpwt_p.rose import glob_patterns

from .get_eqs import get_eqs_dict


class Info_Per:
    def __init__(self, data, period) -> None:
        self.data = Path(data)
        self.period = period
        self.targets = glob_patterns("rglob", self.data, [f"eqlistper{self.period}"])
        self.eqs = get_eqs_dict(self.targets)
