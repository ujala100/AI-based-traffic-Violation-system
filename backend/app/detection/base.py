"""Detector interface: swap YOLO for any model by implementing `track()`."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

import numpy as np

from app.models.entities import TrackedObject


class Detector(ABC):
    @abstractmethod
    def track(self, frame: np.ndarray, frame_no: int, ts: float) -> List[TrackedObject]:
        """Detect + track objects in a frame; return objects with persistent track IDs."""
