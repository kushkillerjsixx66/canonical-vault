"""
cli.py — Unified CLI Entry Point
PATCH v1.1: FIX v1.0 used 'signal <text>' / 'vault_export' syntax —
incompatible with lattice_runtime.py REPL. Now unified via LatticeREPL.dispatch().
All commands added: Vault:Retrieve, Echo:Trace, Stumpy:Audit, ∮, ‰, hud.
"""
from __future__ import annotations
import argparse, sys, os
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
from lattice_runtime import LatticeREPL, CommandParser

def main() -> None:
    p = argparse.ArgumentParser(prog="lattice",
        description="Canonical Lattice CLI — governance-first cognitive OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""One-shot examples:
  lattice --signal "What is coherence?"
  lattice --hud
  lattice --vault-export""")
    p.add_argument("--signal",         metavar="TEXT")
    p.add_argument("--vault-export",   action="store_true")
    p.add_argument("--vault-retrieve", metavar="KEY")
    p.add_argument("--echo-trace",     metavar="KEY")
    p.add_argument("--hud",            action="store_true")
    p.add_argument("--one-shot",       metavar="COMMAND")
    args = p.parse_args()
    repl = LatticeREPL(); cp = CommandParser()
    if args.signal:         print(repl.dispatch("<Signal:Send>", args.signal));          return
    if args.vault_export:   print(repl.dispatch("<Vault:Export>", ""));                  return
    if args.vault_retrieve: print(repl.dispatch("<Vault:Retrieve>", args.vault_retrieve)); return
    if args.echo_trace:     print(repl.dispatch("<Echo:Trace>", args.echo_trace));       return
    if args.hud:            print(repl.dispatch("hud", ""));                             return
    if args.one_shot:
        cmd, arg = cp.parse(args.one_shot); print(repl.dispatch(cmd, arg)); return
    repl.run()

if __name__ == "__main__":
    main()
