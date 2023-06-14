from tpwt_p.rose import read_xyz


def average(f) -> float:
    """
    read the velocity and calculate the average value
    return avevel and title
    """
    ns = ["lo", "la", "vel"]
    df = read_xyz(f, ns)
    avgvel = df.vel.sum() / len(df)
    return avgvel


###############################################################################
def dicts_of_per_vel(pers: list, vels: list) -> list[dict[str, float]]:
    if (l := len(pers)) == len(vels):
        return [{"per": pers[n], "vel": vels[n]} for n in range(l)]
    else:
        raise ValueError("#periods != #vels, please check parameters lists.")
