from tpwt_p.tpwt import *
from tpwt_r import load_param


def main(param_json: str):
    param = load_param(param_json)
    mcmc(param)


if __name__ == "__main__":
    main("param.json")
