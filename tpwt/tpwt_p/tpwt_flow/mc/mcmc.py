from .grid_data import mkdir_grids_path


class MCMC:
    def __init__(self, param) -> None:
        self.param = param

    def mc_init(self, moho_file, periods):
        mkdir_grids_path("target/grids", moho_file, "target/mcmc", periods)
