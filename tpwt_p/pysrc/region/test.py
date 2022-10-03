from tpwt_r import Point
from tpwt_r import Region
from icecream import ic

def tet_point():
    p = Point(1,1)
    p1 = Point(3,1)
    p2 = Point(1,5)

    ic(p.is_ray_intersects_segment(p1, p2))
    ic(p.lo)


def test_region():
    area = {"west": 10, "east": 20, "north": 25, "south":15}
    region = Region(area)
    ic(region.north)
    ic(region.original())
    ic(region.expanded(y=10,x=5))
    region.expand(y=5, z=10)
    ic(region.original())

if __name__ == "__main__":
    test_region()
