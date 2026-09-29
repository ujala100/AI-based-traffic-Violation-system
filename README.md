# AI-Based Smart Traffic Violation Detection System

Detects/tracks vehicles in CCTV video (YOLO + ByteTrack), applies a configurable rule engine
(red-light, wrong-way, unsafe stopping), stores events in SQLite, saves evidence snapshots,
raises alerts and exports CSV.

## Status
| Feature | Status |
|---|---|
| YOLO detection + ByteTrack/BoT-SORT IDs, trajectories | IMPLEMENTED (Phase 1) |
| Red-light, wrong-way, unsafe-stopping rules, config-driven | IMPLEMENTED (Phase 1, unit-tested) |
| Violation-confidence threshold, duplicate prevention | IMPLEMENTED |
| SQLite storage, snapshots, annotated video, CSV | IMPLEMENTED |
| Signal colour | PARTIAL - HSV reading inside a configured ROI (COCO YOLO cannot read light colour) |
| Lane detection | PARTIAL - lanes/zones are configured polygons, not auto-detected |
| FastAPI + WebSocket, React dashboard, Docker | Phase 2-3 |
| Speeding, helmet, seatbelt, phone | FUTURE (need calibration / custom models) |

## Detection vs violation confidence
Detection confidence = YOLO's belief that the box is a car. Violation confidence = detection conf x
evidence quality (signal-colour dominance, track length, motion angle/distance). Alerts use the latter.

## Run
```bash
cd backend
pip install -r requirements.txt
python -m pytest -q                       # run tests (no GPU/model needed)
python run_pipeline.py --video ../videos/input/traffic.mp4 --camera CAM_01
```
Edit `config/config.yaml`: set `stop_line`, `signal_roi`, zones, allowed direction for YOUR camera
(pixel coordinates). Output: `videos/output/annotated.mp4`, `violations/snapshots/`, `reports/violations.csv`.
