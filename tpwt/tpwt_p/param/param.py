from tpwt_p.check import check_exists

from .cls_for_param import State, Bound_Param, param_parse


class Param:

    def __init__(self, target: str) -> None:
        self.target = check_exists(target)
        p = param_parse(target)
        self.targets = p["targets"]
        self.filter = p["filter"]
        self.model = p["model"]

    def __str__(self):
        return "This is a parameters class."

    def state(self) -> State:
        check_exists(t := self.targets["state"])
        return State(t)

    def bound_param(self) -> Bound_Param:
        return Bound_Param(self.targets, self.filter, self.model)

