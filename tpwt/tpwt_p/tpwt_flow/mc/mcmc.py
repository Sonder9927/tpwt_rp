from .grid_data import mkdir_grids_path


class MCMC:
    def __init__(self, param) -> None:
        self.param = param

    def mc_init(self):
        mkdir_grids_path("target/grids", "target/mcmc")
