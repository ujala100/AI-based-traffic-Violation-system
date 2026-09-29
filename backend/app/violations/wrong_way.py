from __future__ import annotations
from typing import Optional

from app.models.entities import TrackedObject, ViolationCandidate
from app.tracking.track_store import Trajectory
from app.utils.geometry import angle_between_deg, point_in_polygon
from app.violations.base import FrameContext, ViolationRule


class WrongWayRule(ViolationRule):
    """Net motion over a time window points against the configured allowed direction."""
    name = "Wrong-Way Movement"

    def evaluate(self, obj: TrackedObject, traj: Trajectory, ctx: FrameContext) -> Optional[ViolationCandidate]:
        p = self.params
        zone = p.get("zone") or []
        if zone and not point_in_polygon(obj.ground_point, [tuple(x) for x in zone]):
            return None
        vec, dist = traj.displacement_vector(p.get("window_seconds", 2.0))
        min_disp = p.get("min_displacement_px", 60)
        if dist < min_disp:
            return None
        allowed = tuple(p.get("allowed_direction", [1, 0]))
        angle = angle_between_deg(vec, allowed)
        tol = p.get("angle_tolerance_deg", 100)
        if angle <= tol:
            return None
        angle_score = min(1.0, (angle - tol) / max(1.0, 180 - tol) * 0.5 + 0.5)
        disp_score = min(1.0, dist / (2 * min_disp))
        vconf = obj.conf * angle_score * (0.6 + 0.4 * disp_score)
        return ViolationCandidate(self.name, obj.conf, round(vconf, 4),
                                  {"angle_deg": round(angle, 1), "displacement_px": round(dist, 1)})
