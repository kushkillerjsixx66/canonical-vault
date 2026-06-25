# lineage_engine.py

import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LINEAGE_DIR = os.path.join(BASE, "lineage")


def record_lineage(name, action):
    timestamp = datetime.utcnow().isoformat()
    entry = f"{timestamp} — {action}"

    path = os.path.join(LINEAGE_DIR, f"{name}.lineage")

    with open(path, "a") as f:
        f.write(entry + "\n")


def get_lineage(name):
    path = os.path.join(LINEAGE_DIR, f"{name}.lineage")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return f.read().splitlines()
