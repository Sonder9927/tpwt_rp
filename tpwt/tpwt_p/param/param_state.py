import demjson

from tpwt_p.check import check_exists


class Param:

    def __init__(self, target: str) -> None:
        self.target = check_exists(target)
        p = param_parse(target)
        self.targets = p["targets"]
        self.filter = p["filter"]
        self.model = p["model"]
        self.inverse = p["model"]
        self.state = State(self.targets["state"])

    def __str__(self):
        return "This is a parameters class."


class State:
    def __init__(self, target: str) -> None:
        self.target = check_exists(target)
        self.state = param_parse(target)

    def __repr__(self) -> str:
        return f"State:\n  target: {self.target}\n  state: {self.state}"

    def check_state(self, state: str) -> bool:
        return self.state.get(state)

    def change_state(self, state: str, info: bool):
        self.state[state] = info

    def save(self, target=""):
        t = target or self.target
        demjson.encode_to_file(str(t), self.state, overwrite=True)


# json
def param_parse(f: str) -> dict:
    """
    Get parameters from json data file.
    """
    return demjson.decode_file(f)
