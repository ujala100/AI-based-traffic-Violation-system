📌 Overview

This system automatically detects and classifies traffic rule violations from continuous road-camera video streams. It identifies the vehicle involved, assigns a persistent tracking ID, records the timestamp and location, and generates a detailed CSV/JSON report — all in real time.

Built as an AI and Software Engineering project combining computer vision, object tracking, and rule-based violation logic.

✨ Features
Feature	Description
🎯 Vehicle Detection	Detects cars, trucks, buses, motorcycles using YOLOv8
🔁 Multi-Object Tracking	Persistent track IDs across frames using ByteTrack
🚨 Red-Light Violation	Detects vehicles crossing stop line while traffic light is red
⚠️ Wrong-Lane Movement	Velocity-based detection — catches vehicles moving against traffic flow
🛑 Unsafe/Illegal Stop	Detects isolated stationary vehicles (ignores traffic jams)
🏷️ Event Labels	Every violation annotated on video with type, ID, confidence, timestamp
📊 CSV Report	Full log with timestamp, location, vehicle type, and confidence score
🔔 Real-time Alerts	Console alerts with emoji indicators when violations are detected
🎬 Annotated Video	Output MP4 with bounding boxes, track trails, stop line, and violation banners
⚙️ Configurable	All thresholds, zones, and models controlled via config.yaml
🎬 Demo
Detection in Action
Frame 00279 | CAR ID:107 crosses stop line → 🚨 RED LIGHT VIOLATION (conf: 59.1%)
Frame 00090 | CAR ID:3   stationary 3s, isolated → 🛑 UNSAFE STOP (conf: 75.6%)
Frame 00241 | CAR ID:7   stationary 4s, isolated → 🛑 UNSAFE STOP (conf: 69.6%)
Sample Output Video Features
✅ Coloured bounding boxes per vehicle class
✅ Green motion trails showing vehicle path
✅ Dashed red stop line and yellow lane divider overlay
✅ Violation label directly on the offending vehicle's box
✅ Alert banner at the bottom of frame (max 2 visible at once)
✅ Live HUD — frame counter, FPS, total violation count
🗂️ Project Structure
traffic_violation_detection/
│
├── main.py                        ← Entry point — run this
├── config.yaml                    ← All settings (model, zones, thresholds)
├── requirements.txt               ← Python dependencies
├── README.md
│
├── src/
│   ├── detector.py                ← YOLOv8 + ByteTrack (detection & tracking)
│   ├── violation_detector.py      ← Smart violation logic (red-light, wrong-lane, unsafe-stop)
│   ├── visualizer.py              ← On-frame drawing (boxes, trails, banners, HUD)
│   ├── alert_system.py            ← Console alerts
│   ├── csv_reporter.py            ← CSV + JSON report writer
│   └── utils.py                   ← Shared helpers
│
├── demo/
│   └── generate_demo_video.py     ← Generates a synthetic test video
│
├── output/
│   ├── videos/                    ← Annotated output videos saved here
│   └── reports/                   ← CSV + JSON reports saved here
│
├── setup_and_run.bat              ← Windows: one-click install + run
├── setup_and_run.sh               ← Mac/Linux: one-click install + run
├── RUN_ON_MY_VIDEO.bat            ← Windows: drag-and-drop your video
└── RUN_WEBCAM.bat                 ← Windows: run on live webcam
⚙️ Installation
Prerequisites
Python 3.10 or higher
pip
Step 1 — Clone the repository
bash
git clone https://github.com/Aditya-acesun/traffic-violation-detection.git
cd traffic-violation-detection
Step 2 — Install dependencies
bash
pip install -r requirements.txt

✅ YOLOv8 weights (yolov8n.pt) are auto-downloaded on first run (~6 MB). No manual download needed.

🚀 Usage
Run on a video file
bash
python main.py --source your_video.mp4 --show
Run on live webcam
bash
python main.py --source 0 --show
Run on IP camera / RTSP stream
bash
python main.py --source "rtsp://admin:password@192.168.1.100:554/stream" --show
Run without live display (headless — just save output)
bash
python main.py --source your_video.mp4
Generate and run on demo video
bash
python demo/generate_demo_video.py
python main.py --source demo/sample_traffic.mp4 --show
Windows — one click

Double-click setup_and_run.bat for guided setup and run.

🎛️ CLI Arguments
Argument	Default	Description
--source	""	Video path, 0 for webcam, or RTSP URL
--config	config.yaml	Path to config file
--show	False	Open live display window
--no-save	False	Do not save annotated output video
--location	from config	Camera location tag written into CSV
--stop-line	auto	Override stop-line Y pixel manually
--divider-x	auto	Override lane-divider X pixel manually
🧠 How It Works
┌─────────────────────────────────────────────────────────────┐
│                        Video Frame                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   YOLOv8 Detection    │  ← Detects vehicles + traffic lights
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  ByteTrack Tracking   │  ← Assigns persistent track IDs
              └───────────┬───────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
  ┌──────────────┐ ┌────────────┐ ┌─────────────┐
  │  Red-Light   │ │ Wrong Lane │ │ Unsafe Stop │
  │  Checker     │ │  Checker   │ │  Checker    │
  └──────┬───────┘ └─────┬──────┘ └──────┬──────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │    Violation Events   │
             └──────┬────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
  Console Alert  CSV/JSON    Annotated
                 Report       Video
Violation Logic (Smart & Low False-Positive)
🚨 Red-Light Crossing
Traffic light must be detected and confirmed RED for 8+ consecutive frames
Vehicle must transition: was behind stop line → crosses stop line while red
One event per vehicle — no repeated alerts
⚠️ Wrong-Lane Movement
Computes consensus direction of all vehicles (median velocity dy across frame)
Flags a vehicle only if its velocity is consistently opposite to consensus for 10+ frames
Works for any road layout — no hard-coded lane positions
🛑 Unsafe / Illegal Stop
Vehicle must be stationary for 3+ seconds (90 frames at 30 fps)
Isolation check: if 2+ nearby vehicles are also stopped → it's a traffic jam, skip
Only flags truly isolated, illegally stopped vehicles
📊 Output
Annotated Video

Saved to output/videos/<input_name>_violations_<timestamp>.mp4

Every frame contains:

Bounding boxes colour-coded by vehicle type
Track ID + class + confidence label
Motion trail (last 30 positions)
Stop line and lane divider overlay
Violation label on the offending vehicle box
Alert banner at bottom (max 2 at once — never covers the road)
HUD panel (top-left): frame, FPS, total violations
CSV Report

Saved to output/reports/violation_report.csv

event_id, wall_time, video_timestamp, frame_idx, location,
violation_type, vehicle_type, track_id, confidence,
box_x1, box_y1, box_x2, box_y2, extra
JSON Summary

Saved to output/reports/violation_report.json

json
{
  "total_violations": 9,
  "by_type": {
    "unsafe_stop": 8,
    "red_light": 1
  },
  "events": [ ... ]
}
⚙️ Configuration (config.yaml)
Switch model size (speed vs accuracy trade-off)
Model	Size	Speed	Accuracy
yolov8n.pt	6 MB	⚡⚡⚡ Fastest	Good
yolov8s.pt	22 MB	⚡⚡ Fast	Better
yolov8m.pt	49 MB	⚡ Medium	Very Good
yolov8l.pt	83 MB	Slower	Excellent
yaml
model:
  weights: "yolov8s.pt"   # change here
Tune violation sensitivity
yaml
violations:
  red_light:
    min_frames_in_red: 8        # increase → fewer false positives
    confidence_threshold: 0.55

  wrong_lane:
    lane_cross_frames: 10       # velocity window in frames

  unsafe_stop:
    stationary_frames: 90       # 3 seconds @ 30fps
Set camera zones manually
yaml
zones:
  stop_line:      [[0, 400], [1280, 400]]      # Y pixel of stop line
  lane_divider:   [[640, 0],  [640, 720]]       # X pixel of lane centre
  restricted_area: [[100,500],[600,500],[600,700],[100,700]]  # polygon
🗂️ Dataset

This system works out-of-the-box with no custom dataset — it uses YOLOv8 pre-trained on COCO which already detects:

Cars, trucks, buses, motorcycles
Traffic lights, stop signs

For fine-tuning on custom traffic data:

Dataset	Classes	Link
Roboflow Traffic Violation	23 classes	Link
BDD100K	10 classes	Link
Kaggle Traffic Dataset	23 classes	Link
❓ Troubleshooting
Problem	Fix
No module named 'ultralytics'	Run pip install -r requirements.txt
Slow FPS on CPU	Use yolov8n.pt, set img_size: 320 in config
No display window	Add --show flag to the command
Too many false positives	Raise confidence_threshold and min_frames_in_red in config
No violations detected	Lower thresholds or check stop-line Y position in config
GPU acceleration	Set device: "cuda" in config (requires NVIDIA GPU + CUDA)
🛠️ Tech Stack
Component	Technology
Object Detection	YOLOv8 (Ultralytics)
Multi-Object Tracking	ByteTrack
Video Processing	OpenCV
Data & Reports	Pandas, CSV, JSON
Configuration	PyYAML
Language	Python 3.10+
📚 References
Redmon et al. — You Only Look Once: Unified, Real-Time Object Detection (CVPR 2016)
Zhang et al. — ByteTrack: Multi-Object Tracking by Associating Every Detection Box (ECCV 2022)
Yu et al. — BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning (CVPR 2020)
Ultralytics — YOLOv8 Documentation (2023)
