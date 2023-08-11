import pygmt


def grid_sample(data, region, spacing=0.5):
    temp = "temp"
    # blockmean
    pygmt.blockmean(data, outfile=temp, region=region, spacing=0.5)
    # surface
    pygmt.surface(data=temp, outgrid=temp, region=region, spacing=0.5)
    # grdsample
    pygmt.grdsample(
        grid=temp,
        spacing=spacing,
        outgrid=temp,
    )
    data = pygmt.grd2xyz(temp)
    return data
