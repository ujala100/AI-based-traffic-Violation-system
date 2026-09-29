from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.models.entities import SignalState, TrackedObject, ViolationCandidate
from app.tracking.track_store import Trajectory


@dataclass
class FrameContext:
    ts: float
    frame: int
    signal: SignalState = SignalState.UNKNOWN
    signal_conf: float = 0.0
    camera: Dict[str, Any] = field(default_factory=dict)


class ViolationRule(ABC):
    """Add a new violation = subclass this + register it in engine.RULE_REGISTRY."""
    name: str = "base"

    def __init__(self, params: Dict[str, Any]) -> None:
        self.params = params
        self.enabled = bool(params.get("enabled", False))

    @abstractmethod
    def evaluate(self, obj: TrackedObject, traj: Trajectory, ctx: FrameContext) -> Optional[ViolationCandidate]:
        ...
