import pandas as pd


def average(file: PosixPath) -> str:
    '''
    read the velocity and calculate the average value
    return avevel and title
    '''
    df = pd.read_csv(file, sep="\s+", header=None, names=["la", "lo", "vel"], engine="python")
    avgvel = df["vel"].sum() / len(df)
    return avgvel
