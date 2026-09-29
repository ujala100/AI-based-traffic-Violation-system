"""Loads config/config.yaml. Rules read their parameters from here - nothing is hard-coded."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_config(path=None) -> Dict[str, Any]:
    p = Path(path or os.getenv("TVDS_CONFIG", PROJECT_ROOT / "config" / "config.yaml"))
    with open(p, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key in ("detection", "violations", "traffic_rules", "cameras"):
        if key not in cfg:
            raise ValueError(f"config missing section: {key}")
    return cfg


def resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p
