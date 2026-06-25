# lineage_engine.py

import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LINEAGE_DIR = os.path.join(BASE, "lineage")

# Operator signature (canonical)
OPERATOR_SIGNATURE = "SIG: JRM-01 @liminaljermo"


def record_lineage(name, action, context=None):
    """
    Writes a lineage entry for an artifact.
    Each entry includes:
    - timestamp (UTC ISO)
    - action performed
    - operator signature
    - optional context (e.g., commit message, canon reason)
    """

    timestamp = datetime.utcnow().isoformat()

    entry = f"{timestamp} — {action} — {OPERATOR_SIGNATURE}"
    if context:
        entry += f" — {context}"

    path = os.path.join(LINEAGE_DIR, f"{name}.lineage")

    with open(path, "a") as f:
        f.write(entry + "\n")


def get_lineage(name):
    """
    Returns the lineage chain for an artifact as a list of entries.
    """
    path = os.path.join(LINEAGE_DIR, f"{name}.lineage")

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return f.read().splitlines()
