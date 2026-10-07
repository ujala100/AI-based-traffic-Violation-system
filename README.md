# 🚦 AI-Based Smart Traffic Violation Detection

An AI-powered traffic monitoring system that uses computer vision to detect vehicles, track their movement, and identify traffic rule violations from CCTV footage or recorded traffic videos.

## 📌 Project Overview

Traffic rule violations are a major cause of road accidents and traffic congestion. Manually monitoring continuous traffic footage is time-consuming and difficult to scale.

This project aims to automate traffic surveillance using Artificial Intelligence and Computer Vision. It processes traffic video streams, detects and tracks vehicles, and identifies configurable violations such as red-light jumping, wrong-lane movement, and unsafe stopping.

The system also records violation details and generates reports to help analyze traffic patterns and support smarter traffic management.

## ✨ Key Features

* **Vehicle Detection:** Detect vehicles and relevant road objects from traffic footage.
* **Vehicle Tracking:** Track individual vehicles across video frames using object tracking.
* **Traffic Signal Detection:** Identify traffic signals and monitor their states.
* **Violation Detection:** Detect configurable traffic violations, including:

  * Red-light crossing
  * Wrong-lane movement
  * Unsafe stopping
* **Real-Time Visualization:** Display tracked vehicles, violation labels, and timestamps.
* **Automated Alerts:** Generate alerts when a violation meets the configured confidence threshold.
* **Violation Reports:** Export event details into a CSV file for further analysis.
* **Video Processing:** Support recorded traffic videos and, with suitable integration, continuous CCTV streams.

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Computer Vision:** OpenCV
* **Object Detection:** YOLO
* **Object Tracking:** Compatible tracking algorithms such as ByteTrack or BoT-SORT
* **Data Processing:** Pandas
* **Reporting:** CSV
* **Visualization:** OpenCV video overlays

*The final technology stack may vary depending on the models and libraries used in the implementation.*

## ⚙️ System Workflow

1. **Video Input:** Load a recorded traffic video or connect to a supported CCTV stream.
2. **Object Detection:** Detect vehicles, traffic signals, lanes, and other relevant road objects.
3. **Object Tracking:** Assign tracking IDs to detected vehicles and follow their movement across frames.
4. **Rule Evaluation:** Analyze vehicle positions, lane boundaries, traffic signal states, and movement patterns.
5. **Violation Detection:** Identify possible traffic violations based on configured rules.
6. **Event Logging:** Store timestamps, vehicle IDs, violation types, confidence scores, and available location information.
7. **Visualization and Reporting:** Display detection results and export violation records to a CSV file.

## 📊 Expected Output

The system is designed to provide:

* Annotated video showing detected and tracked vehicles.
* Violation labels displayed alongside relevant vehicles.
* Timestamps for detected events.
* Alerts for configured traffic violations.
* A CSV report containing violation records.

### Sample CSV Structure

| Timestamp | Location | Vehicle/Event Type  | Confidence Score |
| --------- | -------- | ------------------- | ---------------- |
| 10:25:14  | Lane 1   | Red-Light Violation | 0.94             |
| 10:26:08  | Lane 2   | Wrong-Lane Movement | 0.89             |

*The entries above are illustrative examples, not actual detection results.*

## 🚀 Getting Started

### Prerequisites

* Python 3.10 or a compatible version
* pip package manager
* A traffic video for testing
* A compatible YOLO model and its weights

### Installation

**1. Clone the repository**

```bash
git clone <https://github.com/ujala100/AI-based-traffic-Violation-system>
cd <YOUR_PROJECT_FOLDER>
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

**3. Install dependencies**

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise, install the basic libraries:

```bash
pip install ultralytics opencv-python pandas
```

**4. Add the required model weights and traffic video**

Place the YOLO model weights and sample traffic footage in the locations configured by your application.

**5. Run the application**

```bash
python main.py
```

Replace `main.py` with the actual entry-point filename if your project uses a different one.

## 📁 Suggested Project Structure

```text
AI-Traffic-Violation-Detection/
│
├── models/                 # Object detection model weights
├── videos/                 # Input traffic videos
├── outputs/                # Processed videos and reports
├── src/
│   ├── detection.py        # Vehicle and object detection
│   ├── tracking.py         # Vehicle tracking
│   ├── violations.py       # Traffic rule evaluation
│   └── reporting.py        # CSV report generation
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── README.md
```

*This is a suggested structure; adjust it to match the actual repository.*

## 🔮 Future Improvements

* Integrate live CCTV feeds for continuous traffic monitoring.
* Add automatic number plate recognition (ANPR).
* Improve detection under low-light, rainy, and crowded conditions.
* Introduce a dashboard for traffic statistics and violation trends.
* Store violation records in a database.
* Add configurable camera locations and lane-specific traffic rules.
* Evaluate detection accuracy, precision, recall, and false-positive rates.

## ⚠️ Limitations

* Detection performance depends on video quality, lighting, camera angle, and model accuracy.
* Reliable red-light detection requires traffic signal state recognition and correct vehicle stop-line configuration.
* Wrong-lane and unsafe-stopping detection require suitable lane geometry and rule definitions.
* Automated detections should be reviewed before being used for official enforcement.

## 🎯 Project Objective

To develop an AI-based traffic monitoring solution that automates vehicle detection, movement tracking, and traffic violation analysis, helping make traffic surveillance more efficient and scalable.


⭐ If you find this project interesting, consider giving the repository a star!
