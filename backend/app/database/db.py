from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from typing import Iterator, List

from app.models.entities import ViolationEvent

SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicles(
  id INTEGER PRIMARY KEY AUTOINCREMENT, camera_id TEXT, tracking_id INTEGER, vehicle_type TEXT,
  first_seen TEXT, last_seen TEXT, UNIQUE(camera_id, tracking_id, first_seen));
CREATE TABLE IF NOT EXISTS violations(
  id INTEGER PRIMARY KEY AUTOINCREMENT, tracking_id INTEGER, vehicle_type TEXT, violation_type TEXT,
  timestamp TEXT, confidence REAL, camera_id TEXT, location TEXT, frame_number INTEGER,
  snapshot_path TEXT, status TEXT DEFAULT 'new', details TEXT);
CREATE INDEX IF NOT EXISTS idx_v_time ON violations(timestamp);
CREATE TABLE IF NOT EXISTS traffic_events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, timestamp TEXT, metadata TEXT);
"""


class Database:
    def __init__(self, path: str = "traffic.db") -> None:
        self.path = path
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()

    def add_violation(self, e: ViolationEvent) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO violations(tracking_id,vehicle_type,violation_type,timestamp,confidence,camera_id,"
                "location,frame_number,snapshot_path,details) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (e.track_id, e.vehicle_type, e.violation_type, e.timestamp.isoformat(sep=" ", timespec="seconds"),
                 e.confidence, e.camera_id, e.location, e.frame_number, e.snapshot_path, json.dumps(e.details)))
            return int(cur.lastrowid)

    def upsert_vehicle(self, camera_id: str, tid: int, vtype: str, first: str, last: str) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO vehicles(camera_id,tracking_id,vehicle_type,first_seen,last_seen) VALUES(?,?,?,?,?) "
                      "ON CONFLICT(camera_id,tracking_id,first_seen) DO UPDATE SET last_seen=excluded.last_seen",
                      (camera_id, tid, vtype, first, last))

    def list_violations(self, limit: int = 100, offset: int = 0) -> List[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM violations ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
            return [dict(r) for r in rows]

    def stats(self) -> dict:
        with self._conn() as c:
            by = {r[0]: r[1] for r in c.execute("SELECT violation_type, COUNT(*) FROM violations GROUP BY 1")}
            veh = c.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        return {"total_violations": sum(by.values()), "by_type": by, "total_vehicles": veh}
