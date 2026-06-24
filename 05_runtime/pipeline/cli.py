#!/usr/bin/env python3

"""
Lattice Pipeline CLI
--------------------

Usage:
    python cli.py run "your text here"
"""

import argparse
import json
import yaml
import os

from pipeline_runtime import PipelineRuntime
from runtime.spine.pam import Principle


def load_principles(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Principles file not found: {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    principles = []
    for p in data.get("principles", []):
        principles.append(
            Principle(
                id=p["id"],
                description=p.get("description", ""),
                tags=p.get("tags", []),
            )
        )

    return principles


def pretty(obj):
    return json.dumps(obj, indent=2, default=lambda o: o.__dict__)


def run_pipeline(text: str):
    principles_path = "00_governance/principles.yaml"
    principles = load_principles(principles_path)

    pipeline = PipelineRuntime(principles)
    result = pipeline.run(text)

    print("\n=== IDE ===")
    print(pretty(result.ide))

    print("\n=== CCE ===")
    print(pretty(result.cce))

    print("\n=== CFC ===")
    print(pretty(result.cfc))

    print("\n=== SBM ===")
    print(pretty(result.sbm))

    print("\n=== PAM ===")
    print(pretty(result.pam))

    print("\n=== MTM ===")
    print(pretty(result.mtm))

    print("\n=== WDA ===")
    print(pretty(result.wda))

    print("\n=== LINEAGE ===")
    print(pretty(result.lineage))


def main():
    parser = argparse.ArgumentParser(description="Lattice Pipeline CLI")
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Run pipeline on input text")
    run_cmd.add_argument("text", type=str, help="Input text")

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(args.text)
    else:
        print("No command provided. Use: python cli.py run \"text\"")


if __name__ == "__main__":
    main()
