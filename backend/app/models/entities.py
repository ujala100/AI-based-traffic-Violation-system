from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class SignalState(str, Enum):
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    UNKNOWN = "UNKNOWN"


@dataclass
class TrackedObject:
    track_id: int
    cls_name: str
    conf: float                                   # DETECTION confidence
    bbox: Tuple[float, float, float, float]       # x1,y1,x2,y2
    frame: int
    ts: float                                     # seconds since video start

    @property
    def ground_point(self) -> Tuple[float, float]:
        """Bottom-centre of the box ~ where the vehicle touches the road."""
        return ((self.bbox[0] + self.bbox[2]) / 2, self.bbox[3])


@dataclass
class ViolationCandidate:
    violation_type: str
    detection_conf: float
    violation_conf: float                          # confidence the RULE was really broken
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ViolationEvent:
    timestamp: datetime
    camera_id: str
    location: str
    track_id: int
    vehicle_type: str
    violation_type: str
    confidence: float
    frame_number: int
    snapshot_path: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
