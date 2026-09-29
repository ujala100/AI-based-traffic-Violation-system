from __future__ import annotations
from typing import Iterable

import pandas as pd

COLUMNS = ["timestamp", "location", "vehicle_id", "vehicle_type", "event_type",
           "confidence_score", "frame_number", "snapshot_path"]


def violations_to_csv(rows: Iterable[dict], out_path: str) -> str:
    df = pd.DataFrame([{
        "timestamp": r["timestamp"], "location": r["location"], "vehicle_id": f"Vehicle_{r['tracking_id']}",
        "vehicle_type": r["vehicle_type"], "event_type": r["violation_type"],
        "confidence_score": round(r["confidence"], 2), "frame_number": r["frame_number"],
        "snapshot_path": r["snapshot_path"] or ""} for r in rows], columns=COLUMNS)
    df.to_csv(out_path, index=False)
    return out_path
