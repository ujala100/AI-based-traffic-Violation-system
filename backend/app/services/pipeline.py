"""End-to-end pipeline: video -> detect/track -> rules -> events -> DB/snapshot/annotated video."""
from __future__ import annotations
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import cv2

from app.database.db import Database
from app.detection.base import Detector
from app.detection.signal import estimate_signal
from app.models.entities import SignalState, ViolationEvent
from app.tracking.track_store import TrackStore
from app.violations.base import FrameContext
from app.violations.engine import ViolationEngine

log = logging.getLogger(__name__)
RED, GREEN, YEL = (0, 0, 255), (0, 200, 0), (0, 220, 255)


class TrafficPipeline:
    def __init__(self, cfg: Dict[str, Any], detector: Detector, db: Database, camera_id: str = "CAM_01",
                 snapshot_dir: str = "violations/snapshots",
                 on_event: Optional[Callable[[ViolationEvent], None]] = None) -> None:
        self.cfg, self.detector, self.db = cfg, detector, db
        self.camera_id = camera_id
        self.camera = cfg["cameras"][camera_id]
        self.engine = ViolationEngine(cfg)
        self.store = TrackStore()
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.on_event = on_event          # e.g. WebSocket broadcaster (Phase 2)
        self.fps_now = 0.0
        self.active: Dict[int, str] = {}

    def _signal(self, frame) -> tuple:
        rule = self.cfg["traffic_rules"].get("red_light", {})
        if rule.get("signal_mode", "hsv") == "fixed":
            return SignalState(rule.get("fixed_state", "RED")), 1.0
        roi = self.camera.get("signal_roi")
        return estimate_signal(frame, roi) if roi else (SignalState.UNKNOWN, 0.0)

    def run(self, video_path: str, output_path: Optional[str] = None, start_time: Optional[datetime] = None,
            max_frames: Optional[int] = None) -> List[ViolationEvent]:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise IOError(f"Cannot open video source: {video_path}")
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        target = self.cfg["detection"].get("process_fps", 0)
        step = max(1, round(src_fps / target)) if target else 1
        w, h = int(cap.get(3)), int(cap.get(4))
        writer = None
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), src_fps / step, (w, h))
        start_time = start_time or datetime.now()
        events: List[ViolationEvent] = []
        n = processed = 0
        t0 = time.time()
        try:
            while True:
                ok, frame = cap.read()
                if not ok or (max_frames and n >= max_frames):
                    break
                n += 1
                if (n - 1) % step:
                    continue
                ts = (n - 1) / src_fps
                events += self._process_frame(frame, n, ts, start_time)
                if writer:
                    writer.write(frame)
                processed += 1
                self.fps_now = processed / max(time.time() - t0, 1e-6)
        finally:
            cap.release()
            if writer:
                writer.release()
        log.info("done: %d frames, %.1f FPS, %d violations", processed, self.fps_now, len(events))
        return events

    def _process_frame(self, frame, frame_no: int, ts: float, start: datetime) -> List[ViolationEvent]:
        objs = self.detector.track(frame, frame_no, ts)
        self.store.update(objs)
        sig, sig_conf = self._signal(frame)
        ctx = FrameContext(ts, frame_no, sig, sig_conf, self.camera)
        hits = self.engine.process(objs, self.store, ctx)
        wall = start + timedelta(seconds=ts)
        events = []
        for obj, cand in hits:
            ev = ViolationEvent(wall, self.camera_id, self.camera["name"], obj.track_id, obj.cls_name,
                                cand.violation_type, cand.violation_conf, frame_no, details=cand.details)
            self.active[obj.track_id] = cand.violation_type
            snap = self._annotate(frame.copy(), objs, sig, ev, obj)
            path = self.snapshot_dir / f"vehicle_{obj.track_id}_{frame_no}.jpg"
            cv2.imwrite(str(path), snap)
            ev.snapshot_path = str(path)
            ev.id = self.db.add_violation(ev)
            events.append(ev)
            if self.on_event:
                self.on_event(ev)
        for o in objs:
            self.db.upsert_vehicle(self.camera_id, o.track_id, o.cls_name,
                                   (start + timedelta(seconds=self.store.get(o.track_id).first_seen)).isoformat(" ", "seconds"),
                                   wall.isoformat(" ", "seconds")) if o.cls_name in self.engine.vehicle_classes and frame_no % 30 == 0 else None
        self._annotate(frame, objs, sig, None, None)
        return events

    def _annotate(self, frame, objs, sig, ev, focus):
        line = self.camera.get("stop_line")
        if line:
            cv2.line(frame, tuple(map(int, line[0])), tuple(map(int, line[1])), YEL, 2)
        for o in objs:
            x1, y1, x2, y2 = map(int, o.bbox)
            bad = o.track_id in self.active
            col = RED if bad else GREEN
            cv2.rectangle(frame, (x1, y1), (x2, y2), col, 2)
            cv2.putText(frame, f"{o.cls_name} #{o.track_id} {o.conf:.2f}", (x1, max(12, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
        cv2.putText(frame, f"Signal: {sig.value}  FPS: {self.fps_now:.1f}", (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        if ev is not None:
            lines = [f"VIOLATION: {ev.violation_type.upper()}", f"Vehicle ID: {ev.track_id}",
                     f"Confidence: {ev.confidence:.0%}", f"Time: {ev.timestamp:%H:%M:%S}", f"Camera: {ev.camera_id}"]
            for i, t in enumerate(lines):
                cv2.putText(frame, t, (10, 50 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2)
        return frame
