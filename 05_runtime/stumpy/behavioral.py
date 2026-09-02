"""Deterministic behavioral probes for Stumpy invariant evidence.

Probes run against isolated temporary state. They establish observable runtime
properties without treating source text or documentation as behavioral proof.
"""

from __future__ import annotations

import importlib.util
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


def probe_coherence(repository_root: str) -> tuple[bool, str]:
    """Verify that canonical invariant declarations agree across layers."""
    matrix = _load_module(
        "stumpy_audit_matrix",
        Path(repository_root) / "05_runtime" / "stumpy" / "audit_matrix.py",
    )
    graph = Path(repository_root) / "00_governance" / "authority_graph.yaml"
    graph_text = graph.read_text(encoding="utf-8")

    declared_count = None
    marker = "description: Six canonical invariants"
    if marker in graph_text:
        declared_count = 6

    runtime_count = len(matrix.INVARIANTS)
    if declared_count is None:
        return False, "authority graph does not expose a machine-observable canonical invariant count"
    if declared_count != runtime_count:
        return False, (
            "canonical invariant count diverges across authority graph and runtime: "
            f"authority graph={declared_count}, runtime={runtime_count}"
        )
    return True, "canonical invariant count is coherent across authority graph and runtime"


def probe_lineage_binding(repository_root: str) -> tuple[bool, str]:
    """Verify that persisted lineage contains the complete constitutional chain."""
    path = Path(repository_root) / "03_vault_pipeline" / "vault_chain" / "vault_chain.py"
    VaultChain = _load_module("stumpy_vault_chain_lineage", path).VaultChain
    required = ("operator", "intent", "request", "decision", "transition", "artifact")

    with tempfile.TemporaryDirectory() as root:
        chain = VaultChain(root=root)
        entry = {
            "seq": 1,
            "operator": "probe-operator",
            "intent": "probe-intent",
            "request": "probe-request",
            "decision": "probe-decision",
            "transition": "probe-transition",
            "artifact": "probe-artifact",
        }
        chain.append(entry)
        persisted = chain.load(1)
        if persisted is None:
            return False, "lineage entry could not be reloaded"
        missing = tuple(field for field in required if field not in persisted)
        if missing:
            return False, f"persisted lineage is missing required fields: {', '.join(missing)}"
        return True, "persisted lineage contains operator → intent → request → decision → transition → artifact"


def probe_drift_accountability(repository_root: str) -> tuple[bool, str]:
    """Verify that observable drift conditions produce evidence-bound findings."""
    path = Path(repository_root) / "00_governance" / "stumpy" / "stumpy_drift_detector.py"
    module = _load_module("stumpy_drift_detector", path)
    detector = module.DriftDetectorProcess(Queue(), Queue())

    altitude_findings = detector.inspect_event({
        "type": "runtime_state",
        "source": "stumpy-probe",
        "payload": {"altitude": "unauthorized"},
    })
    lineage_findings = detector.inspect_event({
        "type": "epistemic_state",
        "source": "stumpy-probe",
        "payload": {"state": "UNKNOWN"},
    })

    types = {finding.get("type") for finding in altitude_findings + lineage_findings}
    required = {"altitude_drift", "epistemic_drift"}
    if required <= types:
        return True, "altitude and epistemic drift conditions produced explicit findings"
    return False, f"drift detector missed expected finding types: {', '.join(sorted(required - types))}"


def probe_reversibility(repository_root: str) -> tuple[bool, str]:
    """Verify that an existing lineage sequence cannot be overwritten."""
    path = Path(repository_root) / "03_vault_pipeline" / "vault_chain" / "vault_chain.py"
    VaultChain = _load_module("stumpy_vault_chain", path).VaultChain
    with tempfile.TemporaryDirectory() as root:
        chain = VaultChain(root=root)
        entry = {"seq": 1, "operator_id": "probe", "role": "test", "altitude": "runtime"}
        chain.append(entry)
        try:
            chain.append({**entry, "operator_id": "attacker"})
        except FileExistsError:
            preserved = chain.load(1)
            if preserved == entry:
                return True, "duplicate sequence rejected and original lineage preserved"
            return False, "duplicate sequence rejected but original lineage changed"
        return False, "duplicate sequence was accepted"


def probe_constraint_enforcement(repository_root: str) -> tuple[bool, str]:
    """Verify that an unsafe runtime event produces an enforcement finding."""
    path = Path(repository_root) / "00_governance" / "stumpy" / "stumpy_enforcement_pipelines.py"
    module = _load_module("stumpy_enforcement", path)
    violations = Queue()
    process = module.EnforcementProcess(Queue(), violations)
    findings = process.route_event({"type": "runtime_state", "payload": {"unsafe": True}})
    if any(f.get("type") == "runtime_enforcement_triggered" for f in findings):
        return True, "unsafe runtime state produced an enforcement finding"
    return False, "unsafe runtime state produced no enforcement finding"


PROBES: dict[str, Callable[[str], tuple[bool, str]]] = {
    "coherence": probe_coherence,
    "lineage_binding": probe_lineage_binding,
    "drift_accountability": probe_drift_accountability,
    "reversibility": probe_reversibility,
    "constraint_enforcement": probe_constraint_enforcement,
}


def run_behavioral_probe(repository_root: str, probe: str) -> tuple[bool, str]:
    """Run one explicitly registered behavioral probe."""
    try:
        fn = PROBES[probe]
    except KeyError:
        return False, f"unsupported behavioral probe: {probe}"
    return fn(repository_root)
