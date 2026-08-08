"""
PARADOX_ENGINE_1.0 — Command-Line Interface
Canon Layer: INTERFACE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

Usage
-----
  python -m paradox_engine run "This statement is false."
  python -m paradox_engine run --label liar --altitude 5 "This statement is false."
  python -m paradox_engine library
  python -m paradox_engine library --run liar
  python -m paradox_engine vault list
  python -m paradox_engine vault replay <vault-key>
  python -m paradox_engine status
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from typing import List, Optional

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG
from paradox_engine.core.engine import ParadoxEngine
from paradox_engine.core.paradox import Paradox, ParadoxLibrary
from paradox_engine.core.simulation import SimulationState


# ── Formatting Helpers ─────────────────────────────────────────────────────────

BOLD  = "\033[1m"
DIM   = "\033[2m"
GREEN = "\033[32m"
YELLOW= "\033[33m"
RED   = "\033[31m"
CYAN  = "\033[36m"
RESET = "\033[0m"


def _h(text: str) -> str:
    return f"{BOLD}{CYAN}{text}{RESET}"


def _ok(text: str) -> str:
    return f"{GREEN}✓{RESET} {text}"


def _warn(text: str) -> str:
    return f"{YELLOW}⚠{RESET} {text}"


def _err(text: str) -> str:
    return f"{RED}✗{RESET} {text}"


def _print_result(sim, verbose: bool = False) -> None:
    """Pretty-print simulation outcome to stdout."""
    result = sim.result
    state  = sim.state.name

    colour = GREEN if state == "COMPLETED" else (YELLOW if state == "BOUNDED" else RED)
    print(f"\n{_h('═' * 60)}")
    print(f"  {BOLD}Simulation{RESET}  {DIM}{sim.simulation_id[:16]}…{RESET}")
    print(f"  {BOLD}Paradox{RESET}     {sim.paradox.label!r}")
    print(f"  {BOLD}State{RESET}       {colour}{state}{RESET}")
    print(f"  {BOLD}Altitude{RESET}    {sim.altitude}")
    if sim.containment_signature:
        print(f"  {BOLD}ContainSig{RESET}  {DIM}{sim.containment_signature[:32]}…{RESET}")
    if sim.vault_key:
        print(f"  {BOLD}Vault Key{RESET}   {DIM}{sim.vault_key}{RESET}")

    if result:
        s = result.summary()
        print(f"\n{_h('  Resolution Summary')}")
        print(f"    halt_reason     : {s['halt_reason']}")
        print(f"    contained       : {s['contained']}")
        print(f"    total_nodes     : {s['total_nodes']}")
        print(f"    cycles          : {s['cycle_count']}")
        print(f"    max_depth       : {s['max_depth']}")
        print(f"    unique_props    : {s['unique_props']}")
        print(f"    drift_score     : {s['drift_score']:.4f}")
        print(f"    inflation_ratio : {s['inflation_ratio']:.4f}")
        print(f"    elapsed_sec     : {s['elapsed_seconds']:.6f}")
        print(f"    iterations      : {s['iterations']}")

        if verbose:
            print(f"\n{_h('  Branch Trace (first 20 entries)')}")
            for depth, fp, polarity in result.branch_trace[:20]:
                print(f"    depth={depth:02d}  polarity={polarity:<14s}  fp={fp}")
            if len(result.branch_trace) > 20:
                remaining = len(result.branch_trace) - 20
                print(f"    … {remaining} more entries (use --verbose for full trace)")

    print(f"{_h('═' * 60)}\n")


# ── Sub-commands ───────────────────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace, engine: ParadoxEngine) -> int:
    """Run a single paradox through the full spin_up → run → decay cycle."""
    seed = " ".join(args.seed)
    if not seed.strip():
        print(_err("No seed text provided."), file=sys.stderr)
        return 1

    print(f"\n{_ok(f'Spinning up paradox: {seed[:80]!r}')}")

    try:
        sim = engine.run_full(
            paradox  = seed,
            label    = args.label or "",
            altitude = args.altitude,
        )
    except Exception as exc:
        print(_err(f"Engine error: {exc}"), file=sys.stderr)
        return 2

    _print_result(sim, verbose=getattr(args, "verbose", False))
    return 0


def cmd_library(args: argparse.Namespace, engine: ParadoxEngine) -> int:
    """List or run built-in paradoxes from ParadoxLibrary."""
    if args.run:
        try:
            paradox = ParadoxLibrary.get(args.run)
        except KeyError as exc:
            print(_err(str(exc)), file=sys.stderr)
            return 1

        print(f"\n{_ok(f'Running library paradox: {paradox.label!r}')}")
        print(f"    seed: {paradox.seed_text[:100]}")

        sim = engine.run_full(paradox, altitude=args.altitude)
        _print_result(sim, verbose=getattr(args, "verbose", False))
        return 0

    # List mode
    print(f"\n{_h('Built-in Paradox Library')}\n")
    for p in ParadoxLibrary.all():
        wrapped = textwrap.fill(p.seed_text, width=70, subsequent_indent="             ")
        print(f"  {BOLD}{p.label:<16}{RESET}{wrapped}")
    print()
    return 0


def cmd_vault(args: argparse.Namespace, engine: ParadoxEngine) -> int:
    """Vault sub-commands: list or replay."""
    if args.vault_cmd == "list":
        records = engine.vault.list_records()
        if not records:
            print(_warn("Vault is empty."))
            return 0
        print(f"\n{_h('Vault Records')}\n")
        for rec in records:
            expired = f"  {RED}[EXPIRED]{RESET}" if rec.is_expired else ""
            print(f"  {DIM}{rec.vault_key[:20]}…{RESET}  {rec.paradox_label!r}{expired}")
        print()
        return 0

    elif args.vault_cmd == "replay":
        data = engine.vault.replay(args.key)
        if data is None:
            print(_err(f"No replayable record found for key: {args.key}"))
            return 1
        print(json.dumps(data, indent=2, default=str))
        return 0

    print(_err(f"Unknown vault sub-command: {args.vault_cmd}"), file=sys.stderr)
    return 1


def cmd_status(args: argparse.Namespace, engine: ParadoxEngine) -> int:
    """Print engine status snapshot."""
    st = engine.status()
    print(f"\n{_h('ParadoxEngine Status')}\n")
    for k, v in st.items():
        if isinstance(v, dict):
            print(f"  {BOLD}{k}{RESET}:")
            for sk, sv in v.items():
                print(f"      {sk}: {sv}")
        else:
            print(f"  {BOLD}{k:<22}{RESET}{v}")
    print()
    return 0


# ── Argument Parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paradox_engine",
        description="PARADOX_ENGINE_1.0 — Recursive paradox exploration and containment.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python -m paradox_engine run "This statement is false."
          python -m paradox_engine library
          python -m paradox_engine library --run liar
          python -m paradox_engine vault list
          python -m paradox_engine status
        """),
    )
    parser.add_argument(
        "--max-depth",     type=int,   default=64,    metavar="N",
        help="Maximum recursion depth (default: 64)"
    )
    parser.add_argument(
        "--max-iterations",type=int,   default=1024,  metavar="N",
        help="Maximum resolver iterations (default: 1024)"
    )
    parser.add_argument(
        "--max-runtime",   type=float, default=30.0,  metavar="SEC",
        help="Maximum wall-clock seconds per simulation (default: 30)"
    )
    parser.add_argument(
        "--no-archive",    action="store_true",
        help="Destroy simulations instead of archiving them to the vault"
    )
    parser.add_argument(
        "--altitude",      type=int,   default=None,  metavar="N",
        help="Starting cognitive altitude 1–7 (default: 4)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print full branch trace after resolution"
    )

    subs = parser.add_subparsers(dest="command", required=True)

    # run
    run_p = subs.add_parser("run", help="Run a paradox from seed text.")
    run_p.add_argument("seed", nargs="+", help="Seed text for the paradox.")
    run_p.add_argument("--label", default="", help="Optional label.")

    # library
    lib_p = subs.add_parser("library", help="List or run built-in paradoxes.")
    lib_p.add_argument("--run", metavar="LABEL",
                       help="Run a named paradox from the library.")

    # vault
    vault_p = subs.add_parser("vault", help="Inspect the vault.")
    vault_subs = vault_p.add_subparsers(dest="vault_cmd", required=True)
    vault_subs.add_parser("list", help="List vault records.")
    replay_p = vault_subs.add_parser("replay", help="Replay a vaulted simulation.")
    replay_p.add_argument("key", help="Vault key to replay.")

    # status
    subs.add_parser("status", help="Print engine status.")

    return parser


# ── Entry Point ───────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args   = parser.parse_args(argv)

    # Build config from CLI flags
    from paradox_engine.config import (
        EngineConfig, ExplorationBounds, DecayPolicy,
        DriftPolicy, NarrativeInflationPolicy, AltitudeDiscipline, GovernancePolicy
    )
    config = EngineConfig(
        exploration=ExplorationBounds(
            max_depth           = args.max_depth,
            max_iterations      = args.max_iterations,
            max_runtime_seconds = args.max_runtime,
        ),
        decay=DecayPolicy(
            auto_archive=not args.no_archive,
        ),
    )

    engine = ParadoxEngine(config=config)

    try:
        if args.command == "run":
            return cmd_run(args, engine)
        elif args.command == "library":
            return cmd_library(args, engine)
        elif args.command == "vault":
            return cmd_vault(args, engine)
        elif args.command == "status":
            return cmd_status(args, engine)
        else:
            parser.print_help()
            return 1
    finally:
        engine.shutdown()


if __name__ == "__main__":
    sys.exit(main())
