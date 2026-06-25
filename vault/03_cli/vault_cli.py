import argparse
import json
from pathlib import Path
from vault.02_runtime.core.vault_core import VaultCore

def main():
    parser = argparse.ArgumentParser(prog="vault")
    sub = parser.add_subparsers(dest="cmd")

    commit = sub.add_parser("commit")
    commit.add_argument("--role")
    commit.add_argument("--record-type")
    commit.add_argument("--payload")
    commit.add_argument("--metadata")

    args = parser.parse_args()
    vault = VaultCore(...)

    if args.cmd == "commit":
        payload = json.loads(Path(args.payload).read_text())
        metadata = json.loads(Path(args.metadata).read_text())
        print(vault.commit(args.role, args.record_type, payload, metadata))
