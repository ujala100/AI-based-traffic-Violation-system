"""CLI:  python run_pipeline.py --video ../videos/input/traffic.mp4 --camera CAM_01"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.config.settings import PROJECT_ROOT, load_config
from app.database.db import Database
from app.detection.yolo_detector import YoloTracker
from app.services.pipeline import TrafficPipeline
from app.services.report import violations_to_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True, help="file path, RTSP url, or 0 for webcam")
ap.add_argument("--camera", default="CAM_01")
ap.add_argument("--config", default=None)
a = ap.parse_args()

cfg = load_config(a.config)
db = Database(str(PROJECT_ROOT / "traffic.db"))
src = int(a.video) if a.video.isdigit() else a.video
pipe = TrafficPipeline(cfg, YoloTracker(cfg["detection"]), db, a.camera,
                       snapshot_dir=str(PROJECT_ROOT / "violations" / "snapshots"),
                       on_event=lambda e: print(f"ALERT {e.violation_type} vehicle#{e.track_id} {e.confidence:.0%}"))
out = PROJECT_ROOT / "videos" / "output" / "annotated.mp4"
events = pipe.run(src, str(out))
csv = violations_to_csv(db.list_violations(10000), str(PROJECT_ROOT / "reports" / "violations.csv"))
print(f"{len(events)} violations | video: {out} | csv: {csv}")
