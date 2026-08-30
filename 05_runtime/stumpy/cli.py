"""CLI entrypoint for bounded Stumpy audits."""

from __future__ import annotations

import argparse
import json

from .run import run_default_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Stumpy repository audit")
    parser.add_argument("repository_root")
    args = parser.parse_args()

    report = run_default_audit(args.repository_root)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
