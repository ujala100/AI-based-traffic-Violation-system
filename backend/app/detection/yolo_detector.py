from __future__ import annotations
import logging
from typing import Any, Dict, List

import numpy as np

from app.config.settings import resolve
from app.detection.base import Detector
from app.models.entities import TrackedObject

log = logging.getLogger(__name__)


def pick_device(pref: str = "auto") -> str:
    if pref != "auto":
        return pref
    try:
        import torch
        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


class YoloTracker(Detector):
    """Ultralytics YOLO with built-in ByteTrack/BoT-SORT (persist=True keeps IDs across frames)."""

    def __init__(self, det_cfg: Dict[str, Any]) -> None:
        from ultralytics import YOLO  # lazy import: tests don't need torch
        model_path = resolve(det_cfg["model_path"])
        self.model = YOLO(str(model_path) if model_path.exists() else model_path.name)
        self.device = pick_device(det_cfg.get("device", "auto"))
        self.conf = det_cfg["detection_confidence"]
        self.tracker = det_cfg.get("tracker", "bytetrack.yaml")
        self.imgsz = det_cfg.get("imgsz", 640)
        self.keep = set(det_cfg["vehicle_classes"]) | {"person", "traffic light"}
        log.info("YOLO loaded on %s", self.device)

    def track(self, frame: np.ndarray, frame_no: int, ts: float) -> List[TrackedObject]:
        res = self.model.track(frame, persist=True, tracker=self.tracker, conf=self.conf,
                               imgsz=self.imgsz, device=self.device, verbose=False)[0]
        out: List[TrackedObject] = []
        if res.boxes is None or res.boxes.id is None:
            return out
        for box, tid, cls, cf in zip(res.boxes.xyxy.cpu().numpy(), res.boxes.id.int().cpu().tolist(),
                                     res.boxes.cls.int().cpu().tolist(), res.boxes.conf.cpu().tolist()):
            name = res.names[cls]
            if name in self.keep:
                out.append(TrackedObject(tid, name, float(cf), tuple(map(float, box)), frame_no, ts))
        return out
