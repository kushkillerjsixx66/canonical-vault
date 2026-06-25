
# vault_log.py

import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE, "logs", "vault.log")


def vault_log(message):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} — {message}\n")
