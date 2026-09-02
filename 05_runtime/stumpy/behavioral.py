"""Deterministic behavioral probes for Stumpy invariant evidence.

Probes run against isolated or repository state. They establish observable
properties without treating documentation or self-reported status as proof.
"""

from __future__ import annotations

import importlib.util
import re
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

    declared_count = 6 if "description: Six canonical invariants" in graph_text else None
    runtime_count = len(matrix.INVARIANTS)
    if declared_count is None:
        return False, "authority graph does not expose an observable canonical invariant count"
    if declared_count != runtime_count:
        return False, (
            "canonical invariant count diverges across authority graph and runtime: "
            f"authority graph={declared_count}, runtime={runtime_count}"
        )
    return True, "canonical invariant count is coherent across authority graph and runtime"


def probe_lineage_binding(repository_root: str) -> tuple[bool, str]:
    """Verify that a committed artifact carries the complete constitutional lineage chain."""
    path = Path(repository_root) / "05_runtime" / "vault.py"
    vault_module = _load_module("stumpy_canonical_vault", path)
    contracts = _load_module(
        "stumpy_governance_contracts",
        Path(repository_root) / "05_runtime" / "governance" / "contracts.py",
    )

    operator = contracts.ValidatedOperatorContext(
        operator_id="probe-operator",
        credential_id="probe-key",
        authenticated_at=contracts.iso_now(),
        session_id="probe-session",
        signature="probe-signature",
        roles=("OPERATOR",),
        verified=True,
    )
    intent = contracts.ValidatedIntent(
        kind="probe.commit",
        scope=("vault.write",),
        nonce="probe-nonce",
        issued_at=contracts.iso_now(),
    )
    request = contracts.GovernedRequest(
        request_id="probe-request",
        operator=operator,
        intent=intent,
        input_payload={"content": "lineage probe"},
        source_refs=("probe-source",),
        requested_action="commit",
    )
    engine = contracts
    # Build the same governed transition objects used by the active boundary.
    governance_engine = _load_module(
        "stumpy_governance_engine",
        Path(repository_root) / "05_runtime" / "governance" / "engine.py",
    ).AuthoritativeGovernanceEngine()
    decision = governance_engine.evaluate_request(request, [], [])
    if decision.decision != "ALLOW":
        return False, f"probe request could not reach commit path: {decision.decision}"

    transition = contracts.StateTransition(
        transition_id="probe-transition",
        prior_refs=request.source_refs,
        operation=request.requested_action,
        payload_hash=contracts.sha256_digest(request.input_payload),
        decision_hash=decision.decision_hash,
        lineage_event_id="probe-lineage",
        committed=False,
    )
    lineage = contracts.LineageEvent(
        event_id="probe-lineage",
        timestamp=contracts.iso_now(),
        operator_id=operator.operator_id,
        transition_id=transition.transition_id,
        decision_hash=decision.decision_hash,
        input_hash=transition.payload_hash,
        payload_hash=transition.payload_hash,
        evaluator_versions=decision.evaluator_versions,
    )

    vault = vault_module.CanonicalVault()
    receipt = vault.commit_transition(
        transition=transition,
        decision=decision,
        lineage=lineage,
        payload=request.input_payload,
    )
    node = vault.nodes[0]

    # The constitutional chain includes operator → intent → request → decision
    # → transition → artifact. The current persisted node must expose enough
    # binding to reconstruct every link, not merely transition/lineage IDs.
    present = set(node) | {"decision" if "decision_hash" in node else ""}
    missing = [
        field for field in ("operator_id", "intent_id", "request_id", "decision_hash", "transition_id", "lineage_id")
        if field not in present
    ]
    if missing:
        return False, "committed artifact cannot expose complete lineage binding: " + ", ".join(missing)
    if receipt.lineage_event_id != node["lineage_id"] or receipt.transition_id != node["transition_id"]:
        return False, "artifact lineage identifiers are not bound to the commit receipt"
    return True, "committed artifact exposes the complete constitutional lineage binding"


def probe_drift_accountability(repository_root: str) -> tuple[bool, str]:
    """Verify that observable drift conditions produce explicit findings."""
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


def probe_authority_hierarchy(repository_root: str) -> tuple[bool, str]:
    """Verify that the declared authority graph has one ordered supreme root."""
    path = Path(repository_root) / "00_governance" / "authority_graph.yaml"
    text = path.read_text(encoding="utf-8")
    ranks = [int(value) for value in re.findall(r"^  - rank: (\d+)$", text, re.MULTILINE)]
    supreme = re.findall(r"^    authority: SUPREME$", text, re.MULTILINE)
    root = "00_governance/constitution/lattice_constitution.md"
    if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
        return False, "authority graph ranks are not unique and ordered"
    if ranks and ranks[0] != 1:
        return False, "authority graph does not begin at rank 1"
    if len(supreme) != 1 or root not in text:
        return False, "authority graph does not expose exactly one supreme constitutional root"
    return True, "authority graph exposes one ordered supreme constitutional root"


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
    "authority_hierarchy": probe_authority_hierarchy,
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
