# review_engine.py

import os
from lineage_engine import get_lineage


def review_artifact(name):
    lineage = get_lineage(name)
    if not lineage:
        return "No lineage found."

    output = [f"Lineage for {name}:"]
    for entry in lineage:
        output.append(f"- {entry}")

    return "\n".join(output)
