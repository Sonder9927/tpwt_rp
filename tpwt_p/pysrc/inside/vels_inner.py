from scipy.spatial import ConvexHull
from icecream import ic
import tpwt_r
import numpy as np
import pandas as pd


def clock_sorted(points):
    from functools import reduce
    import math, operator
    center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), points), [len(points)]*2))
    clock = sorted(points, key=lambda p: (-135 -math.degrees(math.atan2(*tuple(map(operator.sub, p, center))[::-1])))%360, reverse=True)
    return clock


def get_sta_boundary_points(f):
    stas = pd.read_csv(f, delim_whitespace=True, usecols=[1, 2], names=["lo", "la"])
    points = np.array(stas[["lo", "la"]])
    hull = ConvexHull(points)

    return points[hull.vertices]


# write this function to a method of class Point using rust
# see my tpwt_r/src/lib.rs
# def is_ray_intersects_segment(p, p1, p2):
#     """
#     check two lines of `y=p.la` and line crossing p1 and p2.
#     """
#     special_case: list[bool] = [
#         p1.la == p2.la,
#         (p1.la >= p.la) and (p2.la >= p.la),
#         (p1.la <= p.la) and (p2.la <= p.la),
#         (p1.lo < p.lo) and (p2.lo < p.lo),
#     ]
#     if any(special_case):
#         return False

#     x_position = p2.lo - (p2.lo - p1.lo) * (p2.la - p.la) / (p2.la - p1.la)
#     if x_position < p.lo:
#         return False

#     return True


def times_of_crossing_boundary(point, points):
    times_r = 0
    # times_p = 0
    for i in range(len(points)):
        r_start = points[i]
        if i == len(points)-1:
            r_end = points[0]
        else:
            r_end = points[i+1]

        if point.is_ray_intersects_segment(r_start, r_end):
            times_r += 1
        # if is_ray_intersects_segment(point, r_start, r_end):
        #     times_p += 1

    return times_r


def get_inter_points(grid_file: str, points: list):
    vels: pd.DataFrame = pd.read_csv(grid_file, delim_whitespace=True, names=["lo", "la", "vel"])
    lo = [i.lo for i in points]
    la = [i.la for i in points]
    vels_in_rect: pd.DataFrame = vels[
        (vels["la"] < max(la))
        & (vels["la"] > min(la))
        & (vels["lo"] < max(lo))
        & (vels["lo"] > min(lo))
    ]
    # ic(len(vels_in_rect))
    total_avg = vels.vel.mean()
    rect_avg = vels_in_rect.vel.mean()
    ic(total_avg, rect_avg)

    point_inner = []
    for i in vels_in_rect.index:
        point = tpwt_r.Point(vels_in_rect.lo[i], vels_in_rect.la[i])

        times = times_of_crossing_boundary(point, points)
        if times % 2 == 1:
            point_inner.append([point, vels_in_rect.vel[i]])

    df = pd.DataFrame(data=[[i[0].lo, i[0].la,i[1]] for i in point_inner], columns=["lo", "la", "vel"])
    # ic(point_inner[0])

    return df


def main(grid_dir, sta_file):
    boundary_points = get_sta_boundary_points(sta_file)  # default is clock
    # po = clock_sorted(boundary_points)  # no need

    points = [tpwt_r.Point(p[0], p[1]) for p in boundary_points]
    data_inner = get_inter_points(grid_dir, points)
    # ic(data_inner)

    total_numbers = len(data_inner.index)
    avgvel = data_inner.vel.mean()
    ic(avgvel, total_numbers)


if __name__ == '__main__':
    main("./tpwt.26.360", "station.lst")
