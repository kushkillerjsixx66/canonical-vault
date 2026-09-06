"""Deterministic behavioral probes for Stumpy invariant evidence."""
from __future__ import annotations
import ast
import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from queue import Queue
from typing import Callable


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_invariants_from_source(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if "INVARIANTS" in targets:
                value = ast.literal_eval(node.value)
                if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
                    raise ValueError("INVARIANTS must be a tuple of strings")
                return value
    raise ValueError("INVARIANTS not found in source")


def _read_canonical_invariants(graph: Path) -> tuple[str, ...]:
    text = graph.read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        start = lines.index("canonical_invariants:")
    except ValueError:
        raise ValueError("canonical_invariants section not found in authority graph")
    items: list[str] = []
    for line in lines[start + 1:]:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped and not stripped.startswith("#"):
            break
    return tuple(items)


def probe_coherence(
    matrix_path: Path,
    graph: Path,
) -> tuple[bool, str]:
    """Probe that runtime invariant matrix matches canonical authority graph."""
    try:
        runtime_invariants = _read_invariants_from_source(matrix_path)
    except (OSError, SyntaxError, ValueError) as exc:
        return False, f"runtime invariant declaration is malformed or unavailable: {exc}"

    try:
        canonical_invariants = _read_canonical_invariants(graph)
    except (OSError, ValueError) as exc:
        return False, f"canonical invariant declaration is malformed or unavailable: {exc}"

    if canonical_invariants == runtime_invariants:
        return True, "invariant sets match"
    if set(canonical_invariants) == set(runtime_invariants):
        return False, "invariant ordering differs"
    missing = set(canonical_invariants) - set(runtime_invariants)
    extra = set(runtime_invariants) - set(canonical_invariants)
    parts: list[str] = []
    if missing:
        parts.append(f"missing: {sorted(missing)}")
    if extra:
        parts.append(f"extra: {sorted(extra)}")
    return False, "; ".join(parts)


def probe_authority_hierarchy(
    graph: Path,
    expected_min_ranks: int = 1,
) -> tuple[bool, str]:
    """Probe that authority_graph.yaml contains a well-formed hierarchy."""
    try:
        text = graph.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"authority hierarchy declaration is unavailable: {exc}"

    ranks = [int(v) for v in re.findall(r"(?:^|\s)rank:\s*(\d+)", text, re.MULTILINE)]
    if not ranks:
        return False, "no rank entries found in authority graph"
    if len(ranks) < expected_min_ranks:
        return False, f"expected at least {expected_min_ranks} ranks, found {len(ranks)}"
    if sorted(ranks) != list(range(1, len(ranks) + 1)):
        return False, f"rank sequence is non-contiguous: {sorted(ranks)}"
    return True, f"authority hierarchy is well-formed with {len(ranks)} ranks"


def probe_gate_coverage(
    gates_path: Path,
    required_gates: tuple[str, ...],
) -> tuple[bool, str]:
    """Probe that all required governance gates are declared."""
    try:
        text = gates_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"gates declaration is unavailable: {exc}"
    missing = [g for g in required_gates if g not in text]
    if missing:
        return False, f"missing gates: {missing}"
    return True, "all required gates are declared"


def run_probes(
    probes: list[Callable[[], tuple[bool, str]]],
    result_queue: Queue | None = None,
) -> list[tuple[bool, str]]:
    """Run a list of probe callables and collect results."""
    results: list[tuple[bool, str]] = []
    for probe in probes:
        result = probe()
        results.append(result)
        if result_queue is not None:
            result_queue.put(result)
    return results
