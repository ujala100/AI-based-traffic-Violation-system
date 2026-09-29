"""Traffic-signal state estimation.
A COCO-pretrained YOLO detects *that* a traffic light exists but NOT its colour.
We therefore read the colour inside a configured ROI using HSV thresholds (PARTIALLY IMPLEMENTED:
works for a fixed camera with a visible lamp; a custom-trained classifier is the upgrade path)."""
from __future__ import annotations
from typing import Sequence, Tuple

import cv2
import numpy as np

from app.models.entities import SignalState


def estimate_signal(frame: np.ndarray, roi: Sequence[int]) -> Tuple[SignalState, float]:
    x1, y1, x2, y2 = map(int, roi)
    crop = frame[max(0, y1):y2, max(0, x1):x2]
    if crop.size == 0:
        return SignalState.UNKNOWN, 0.0
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    bright = (hsv[..., 2] > 150) & (hsv[..., 1] > 100)
    h = hsv[..., 0]
    red = bright & ((h < 10) | (h > 170))
    yellow = bright & (h >= 15) & (h <= 35)
    green = bright & (h >= 40) & (h <= 90)
    counts = {SignalState.RED: int(red.sum()), SignalState.YELLOW: int(yellow.sum()), SignalState.GREEN: int(green.sum())}
    best = max(counts, key=counts.get)
    total = sum(counts.values())
    if counts[best] < 5:
        return SignalState.UNKNOWN, 0.0
    return best, round(counts[best] / total, 3)   # dominance of winning colour
