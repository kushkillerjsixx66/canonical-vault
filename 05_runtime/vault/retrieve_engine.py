# retrieve_engine.py

import os

BASE = os.path.dirname(os.path.abspath(__file__))
COMMIT_DIR = os.path.join(BASE, "commits")
CANON_DIR = os.path.join(BASE, "canon")


def retrieve_artifact(query):
    # Search commits
    for root in [COMMIT_DIR, CANON_DIR]:
        for file in os.listdir(root):
            if query.lower() in file.lower():
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    return f.read()

    return "No matching artifact found."
