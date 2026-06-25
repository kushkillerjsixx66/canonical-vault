# vault_core.py

import os
from datetime import datetime

from commit_engine import commit_artifact
from retrieve_engine import retrieve_artifact
from review_engine import review_artifact
from canon_engine import canonize_artifact
from veil_engine import apply_veil
from lineage_engine import record_lineage
from vault_log import vault_log


VAULT_PATH = os.path.dirname(os.path.abspath(__file__))


def execute_action(intent, action):
    vault_log(f"Executing action: {action} under intent: {intent}")

    if intent == "Commit":
        return commit_artifact(action)

    elif intent == "Retrieve":
        return retrieve_artifact(action)

    elif intent == "Review":
        return review_artifact(action)

    elif intent == "Canonize":
        return canonize_artifact(action)

    else:
        return "Unknown intent."


def veil_entry(artifact_path, level="partial"):
    return apply_veil(artifact_path, level)
