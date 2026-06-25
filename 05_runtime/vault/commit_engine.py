# commit_engine.py

import os
from datetime import datetime
from lineage_engine import record_lineage
from vault_log import vault_log

BASE = os.path.dirname(os.path.abspath(__file__))
COMMIT_DIR = os.path.join(BASE, "commits")


def commit_artifact(content):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"commit_{timestamp}.txt"
    path = os.path.join(COMMIT_DIR, filename)

    with open(path, "w") as f:
        f.write(content)

    record_lineage(filename, "commit")
    vault_log(f"Committed artifact: {filename}")

    return f"Artifact committed: {filename}"
