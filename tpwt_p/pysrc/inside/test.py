from tpwt_r import Point
from icecream import ic

p = Point(1,1)
p1 = Point(3,1)
p2 = Point(1,5)

ic(p.is_ray_intersects_segment(p1, p2))
ic(p.lo)
