from icecream import ic
import pandas as pd


# ic.disable()
def average(f) -> str:
    '''
    read the velocity and calculate the average value
    return avevel and title
    '''
    ic(f)
    df = pd.read_csv(f, sep="\s+", header=None, names=["la", "lo", "vel"])
    avgvel = df["vel"].sum() / len(df)
    return avgvel
