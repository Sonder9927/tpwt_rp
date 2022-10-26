from tpwt_p.rose import read_xyz


def average(f) -> float:
    '''
    read the velocity and calculate the average value
    return avevel and title
    '''
    ns = ["lo", "la", "vel"]
    df = read_xyz(f, ns)
    avgvel = df.vel.sum() / len(df)
    return avgvel


###############################################################################
