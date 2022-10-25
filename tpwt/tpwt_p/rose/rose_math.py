from tpwt_p.rose import read_xyz


def average(f) -> float:
    '''
    read the velocity and calculate the average value
    return avevel and title
    '''
    df = read_xyz(f)
    avgvel = df.vel.sum() / len(df)
    return avgvel


###############################################################################
