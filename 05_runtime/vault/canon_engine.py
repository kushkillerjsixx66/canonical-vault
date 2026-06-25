# canon_engine.py

import os
import shutil
from lineage_engine import record_lineage
from vault_log import vault_log

BASE = os.path.dirname(os.path.abspath(__file__))
COMMIT_DIR = os.path.join(BASE, "commits")
CANON_DIR = os.path.join(BASE, "canon")


def canonize_artifact(name):
    source = os.path.join(COMMIT_DIR, name)
    if not os.path.exists(source):
        return "Artifact not found in commits."

    dest = os.path.join(CANON_DIR, name)
    shutil.copy(source, dest)

    record_lineage(name, "canonized")
    vault_log(f"Canonized artifact: {name}")

    return f"Artifact canonized: {name}"
