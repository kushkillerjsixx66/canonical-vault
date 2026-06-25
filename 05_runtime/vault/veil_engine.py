# veil_engine.py

import os
from datetime import datetime
from lineage_engine import record_lineage

OPERATOR_SIGNATURE = "SIG: JRM-01 @liminaljermo"


def apply_veil(path, level="partial"):
    """
    Applies a Veil layer to an artifact.
    Levels:
        - clear   : no redaction
        - partial : reveal first 80 chars
        - full    : total redaction
    """

    with open(path, "r") as f:
        content = f.read()

    if level == "clear":
        record_lineage(os.path.basename(path), "veil-clear", context=OPERATOR_SIGNATURE)
        return content

    if level == "partial":
        preview = content[:80]
        output = preview + "\n...[VEILED — PARTIAL]..."
        record_lineage(os.path.basename(path), "veil-partial", context=OPERATOR_SIGNATURE)
        return output

    if level == "full":
        record_lineage(os.path.basename(path), "veil-full", context=OPERATOR_SIGNATURE)
        return "[REDACTED — VEIL‑2]"

    # fallback
    record_lineage(os.path.basename(path), "veil-unknown", context=OPERATOR_SIGNATURE)
    return "[VEIL ERROR]"
