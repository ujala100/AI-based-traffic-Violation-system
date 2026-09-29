from __future__ import annotations
from typing import Dict, Optional

from app.models.entities import TrackedObject, ViolationCandidate
from app.tracking.track_store import Trajectory
from app.utils.geometry import point_in_polygon
from app.violations.base import FrameContext, ViolationRule


class UnsafeStoppingRule(ViolationRule):
    """Stationary inside restricted zone for > threshold seconds."""
    name = "Unsafe Stopping"

    def evaluate(self, obj: TrackedObject, traj: Trajectory, ctx: FrameContext) -> Optional[ViolationCandidate]:
        p = self.params
        zone = [tuple(x) for x in p.get("zone", [])]
        if not point_in_polygon(obj.ground_point, zone):
            return None
        thr = float(p.get("threshold_seconds", 10))
        if traj.first_seen is None or ctx.ts - traj.first_seen < thr:
            return None
        # Must have stayed in one spot for the whole last `thr` seconds
        if traj.max_movement(thr) > p.get("max_movement_px", 8):
            return None
        # (Zone membership for the full window is approximated by tiny movement + currently inside.)
        vconf = obj.conf * 0.95
        return ViolationCandidate(self.name, obj.conf, round(vconf, 4), {"stationary_s": thr})
