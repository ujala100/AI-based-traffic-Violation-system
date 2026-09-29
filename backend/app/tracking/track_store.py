"""Keeps per-vehicle trajectory history."""
from __future__ import annotations
from collections import deque
from typing import Deque, Dict, Iterable, Optional, Tuple

from app.models.entities import TrackedObject
from app.utils.geometry import Point, distance


class Trajectory:
    def __init__(self, maxlen: int = 900) -> None:
        self.points: Deque[Tuple[float, Point]] = deque(maxlen=maxlen)
        self.first_seen: Optional[float] = None
        self.last_seen: Optional[float] = None
        self.vehicle_type: str = ""

    def add(self, ts: float, pt: Point) -> None:
        if self.first_seen is None:
            self.first_seen = ts
        self.last_seen = ts
        self.points.append((ts, pt))

    @property
    def last_two(self) -> Optional[Tuple[Point, Point]]:
        if len(self.points) < 2:
            return None
        return self.points[-2][1], self.points[-1][1]

    def window(self, seconds: float) -> list:
        if not self.points:
            return []
        end = self.points[-1][0]
        return [p for p in self.points if end - p[0] <= seconds]

    def displacement_vector(self, seconds: float) -> Tuple[Point, float]:
        w = self.window(seconds)
        if len(w) < 2:
            return (0.0, 0.0), 0.0
        a, b = w[0][1], w[-1][1]
        return (b[0] - a[0], b[1] - a[1]), distance(a, b)

    def max_movement(self, seconds: float) -> float:
        """Max distance from the window's first point (robust 'is stationary' test)."""
        w = self.window(seconds)
        if len(w) < 2:
            return 0.0
        a = w[0][1]
        return max(distance(a, p[1]) for p in w)


class TrackStore:
    def __init__(self, stale_after_s: float = 5.0) -> None:
        self._t: Dict[int, Trajectory] = {}
        self.stale_after_s = stale_after_s

    def update(self, objs: Iterable[TrackedObject]) -> None:
        now = 0.0
        for o in objs:
            tr = self._t.setdefault(o.track_id, Trajectory())
            tr.vehicle_type = o.cls_name
            tr.add(o.ts, o.ground_point)
            now = max(now, o.ts)
        for tid in [k for k, v in self._t.items() if v.last_seen is not None and now - v.last_seen > self.stale_after_s]:
            del self._t[tid]

    def get(self, track_id: int) -> Trajectory:
        return self._t[track_id]

    def __len__(self) -> int:
        return len(self._t)
