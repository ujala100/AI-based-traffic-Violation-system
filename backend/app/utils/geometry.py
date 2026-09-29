"""Pure geometry helpers (no OpenCV dependency, easy to unit test)."""
from __future__ import annotations
import math
from typing import Sequence, Tuple

Point = Tuple[float, float]


def side(p: Point, a: Point, b: Point) -> float:
    """Signed side of point p relative to directed line a->b (>0, <0, 0)."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def segments_intersect(p1: Point, p2: Point, q1: Point, q2: Point) -> bool:
    d1, d2 = side(p1, q1, q2), side(p2, q1, q2)
    d3, d4 = side(q1, p1, p2), side(q2, p1, p2)
    # crossing, or arriving exactly ON the line (d2 == 0) coming from one side
    crossed = d1 * d2 < 0 or (d2 == 0 and d1 != 0)
    return crossed and d3 * d4 <= 0


def point_in_polygon(p: Point, poly: Sequence[Point]) -> bool:
    if len(poly) < 3:
        return False
    x, y, inside = p[0], p[1], False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_between_deg(v1: Point, v2: Point) -> float:
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
    return math.degrees(math.acos(cos))
