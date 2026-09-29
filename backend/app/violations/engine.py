from __future__ import annotations
import logging
from typing import Any, Dict, List, Tuple, Type

from app.models.entities import TrackedObject, ViolationCandidate
from app.tracking.track_store import TrackStore
from app.violations.base import FrameContext, ViolationRule
from app.violations.red_light import RedLightRule
from app.violations.unsafe_stopping import UnsafeStoppingRule
from app.violations.wrong_way import WrongWayRule

log = logging.getLogger(__name__)

RULE_REGISTRY: Dict[str, Type[ViolationRule]] = {
    "red_light": RedLightRule,
    "wrong_way": WrongWayRule,
    "unsafe_stopping": UnsafeStoppingRule,
    # "speeding": SpeedingRule,   # FUTURE EXTENSION (needs camera calibration)
}


class ViolationEngine:
    """Runs enabled rules, applies violation-confidence threshold and de-duplication."""

    def __init__(self, cfg: Dict[str, Any]) -> None:
        rules_cfg = cfg["traffic_rules"]
        self.rules: List[ViolationRule] = [
            cls(rules_cfg[k]) for k, cls in RULE_REGISTRY.items() if k in rules_cfg and rules_cfg[k].get("enabled")
        ]
        v = cfg["violations"]
        self.threshold = float(v["violation_confidence_threshold"])
        self.cooldown = float(v.get("cooldown_seconds", 30))
        self._last_fired: Dict[Tuple[int, str], float] = {}
        self.vehicle_classes = set(cfg["detection"]["vehicle_classes"])

    def process(self, objs: List[TrackedObject], store: TrackStore, ctx: FrameContext
                ) -> List[Tuple[TrackedObject, ViolationCandidate]]:
        out = []
        for obj in objs:
            if obj.cls_name not in self.vehicle_classes:
                continue
            traj = store.get(obj.track_id)
            for rule in self.rules:
                cand = rule.evaluate(obj, traj, ctx)
                if cand is None:
                    continue
                if cand.violation_conf < self.threshold:
                    log.debug("below threshold %s id=%s %.2f", cand.violation_type, obj.track_id, cand.violation_conf)
                    continue
                key = (obj.track_id, cand.violation_type)
                last = self._last_fired.get(key)
                if last is not None and ctx.ts - last < self.cooldown:
                    continue                      # duplicate-event prevention
                self._last_fired[key] = ctx.ts
                out.append((obj, cand))
        return out
