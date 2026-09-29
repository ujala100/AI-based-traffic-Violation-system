from __future__ import annotations
from typing import Optional

from app.models.entities import SignalState, TrackedObject, ViolationCandidate
from app.tracking.track_store import Trajectory
from app.utils.geometry import segments_intersect, side
from app.violations.base import FrameContext, ViolationRule


class RedLightRule(ViolationRule):
    """Vehicle path segment (prev->curr ground point) crosses stop line while signal is RED."""
    name = "Red Light Violation"

    def evaluate(self, obj: TrackedObject, traj: Trajectory, ctx: FrameContext) -> Optional[ViolationCandidate]:
        line = ctx.camera.get("stop_line")
        pair = traj.last_two
        if not line or pair is None or ctx.signal != SignalState.RED:
            return None
        a, b = tuple(line[0]), tuple(line[1])
        prev, cur = pair
        if not segments_intersect(prev, cur, a, b):
            return None
        direction = self.params.get("direction", "any")
        s_prev = side(prev, a, b)
        if direction == "pos_to_neg" and not s_prev > 0:
            return None
        if direction == "neg_to_pos" and not s_prev < 0:
            return None
        # Violation confidence = detection quality x signal reading quality x track maturity
        maturity = min(1.0, len(traj.points) / 10.0)
        vconf = obj.conf * max(ctx.signal_conf, 0.0) * (0.7 + 0.3 * maturity)
        return ViolationCandidate(self.name, obj.conf, round(vconf, 4), {"signal": ctx.signal.value})
