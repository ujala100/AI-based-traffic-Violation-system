import copy
import numpy as np
from app.config.settings import load_config
from app.models.entities import SignalState, TrackedObject
from app.tracking.track_store import TrackStore
from app.violations.base import FrameContext
from app.violations.engine import ViolationEngine
from app.utils.geometry import segments_intersect, point_in_polygon

CFG = load_config()
CAM = CFG["cameras"]["CAM_01"]


def obj(tid, x, y, ts, conf=0.9, cls="car"):
    return TrackedObject(tid, cls, conf, (x - 20, y - 40, x + 20, y), int(ts * 25), ts)


def run(engine, store, frames, signal=SignalState.RED, sconf=0.95):
    hits = []
    for ts, objs in frames:
        store.update(objs)
        hits += engine.process(objs, store, FrameContext(ts, int(ts * 25), signal, sconf, CAM))
    return hits


def test_geometry():
    assert segments_intersect((0, 0), (10, 10), (0, 10), (10, 0))
    assert point_in_polygon((5, 5), [(0, 0), (10, 0), (10, 10), (0, 10)])
    assert not point_in_polygon((15, 5), [(0, 0), (10, 0), (10, 10), (0, 10)])


def test_red_light_crossing_fires_once():
    e, s = ViolationEngine(CFG), TrackStore()
    frames = [(i / 25, [obj(1, 300, 380 + i * 4, i / 25)]) for i in range(30)]  # crosses y=400
    hits = run(e, s, frames)
    assert [h[1].violation_type for h in hits] == ["Red Light Violation"]      # dedupe: exactly one


def test_no_violation_on_green():
    e, s = ViolationEngine(CFG), TrackStore()
    frames = [(i / 25, [obj(1, 300, 380 + i * 4, i / 25)]) for i in range(30)]
    assert run(e, s, frames, signal=SignalState.GREEN) == []


def test_confidence_threshold_blocks_low_conf():
    e, s = ViolationEngine(CFG), TrackStore()
    frames = [(i / 25, [obj(1, 300, 380 + i * 4, i / 25, conf=0.9)]) for i in range(30)]
    assert run(e, s, frames, sconf=0.3) == []      # weak signal reading -> low violation confidence


def test_wrong_way():
    e, s = ViolationEngine(CFG), TrackStore()
    frames = [(i / 25, [obj(2, 500 - i * 6, 200, i / 25)]) for i in range(40)]  # right -> left
    hits = run(e, s, frames, signal=SignalState.GREEN)
    assert any(h[1].violation_type == "Wrong-Way Movement" for h in hits)


def test_correct_direction_ok():
    e, s = ViolationEngine(CFG), TrackStore()
    frames = [(i / 25, [obj(2, 100 + i * 6, 200, i / 25)]) for i in range(40)]
    assert run(e, s, frames, signal=SignalState.GREEN) == []


def test_unsafe_stopping():
    cfg = copy.deepcopy(CFG)
    e, s = ViolationEngine(cfg), TrackStore()
    frames = [(i / 5, [obj(3, 300, 420, i / 5)]) for i in range(80)]           # 16 s stationary in zone
    hits = run(e, s, frames, signal=SignalState.GREEN)
    assert [h[1].violation_type for h in hits] == ["Unsafe Stopping"]
    assert hits[0][0].track_id == 3


def test_rule_can_be_disabled():
    cfg = copy.deepcopy(CFG)
    cfg["traffic_rules"]["red_light"]["enabled"] = False
    e, s = ViolationEngine(cfg), TrackStore()
    frames = [(i / 25, [obj(1, 300, 380 + i * 4, i / 25)]) for i in range(30)]
    assert run(e, s, frames) == []


def test_track_id_history_persistent():
    s = TrackStore()
    for i in range(5):
        s.update([obj(7, 10 + i, 10, i / 25)])
    assert len(s.get(7).points) == 5
