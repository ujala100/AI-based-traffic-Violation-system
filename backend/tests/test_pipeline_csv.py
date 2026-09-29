import cv2, numpy as np, csv, copy
from app.config.settings import load_config
from app.database.db import Database
from app.detection.base import Detector
from app.models.entities import TrackedObject
from app.services.pipeline import TrafficPipeline
from app.services.report import violations_to_csv, COLUMNS


class FakeDetector(Detector):
    """Simulates a car driving down through the stop line (y=400)."""
    def track(self, frame, frame_no, ts):
        y = 300 + frame_no * 4
        return [TrackedObject(23, "car", 0.91, (280, y - 40, 320, y), frame_no, ts)]


def test_end_to_end_and_csv(tmp_path):
    vid = str(tmp_path / "in.mp4")
    w = cv2.VideoWriter(vid, cv2.VideoWriter_fourcc(*"mp4v"), 25, (640, 480))
    for _ in range(60):
        w.write(np.zeros((480, 640, 3), np.uint8))
    w.release()
    cfg = copy.deepcopy(load_config())
    cfg["traffic_rules"]["red_light"]["signal_mode"] = "fixed"
    cfg["traffic_rules"]["wrong_way"]["enabled"] = False
    cfg["traffic_rules"]["unsafe_stopping"]["enabled"] = False
    db = Database(str(tmp_path / "t.db"))
    got = []
    p = TrafficPipeline(cfg, FakeDetector(), db, "CAM_01", str(tmp_path / "snaps"), on_event=got.append)
    events = p.run(vid, str(tmp_path / "out.mp4"))
    assert len(events) == 1 and len(got) == 1                     # alert callback + no duplicates
    assert events[0].violation_type == "Red Light Violation"
    rows = db.list_violations()
    assert len(rows) == 1 and rows[0]["snapshot_path"]
    out = violations_to_csv(rows, str(tmp_path / "r.csv"))
    r = list(csv.DictReader(open(out)))
    assert list(r[0].keys()) == COLUMNS and r[0]["vehicle_id"] == "Vehicle_23"
    assert (tmp_path / "out.mp4").exists()
