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
    raise ValueError("runtime audit matrix does not declare INVARIANTS")


def _read_canonical_invariants(graph: Path) -> tuple[str, ...]:
    """Read the machine-observable canonical invariant universe from authority graph."""
    text = graph.read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        start = lines.index("canonical_invariants:") + 1
    except ValueError as exc:
        raise ValueError("authority graph does not declare canonical_invariants") from exc

    values: list[str] = []
    for line in lines[start:]:
        if line.startswith("  - "):
            values.append(line[4:].strip())
            continue
        if line and not line.startswith(" "):
            break
    if not values:
        raise ValueError("authority graph canonical_invariants is empty")
    return tuple(values)


def probe_coherence(repository_root: str) -> tuple[bool, str]:
    matrix_path = Path(repository_root) / "05_runtime" / "stumpy" / "audit_matrix.py"
    graph = Path(repository_root) / "00_governance" / "authority_graph.yaml"

    try:
        runtime_invariants = _read_invariants_from_source(matrix_path)
    except (OSError, SyntaxError, ValueError) as exc:
        return False, f"runtime invariant declaration is malformed or unavailable: {exc}"

    try:
        canonical_invariants = _read_canonical_invariants(graph)
    except (OSError, ValueError) as exc:
        return False, f"canonical invariant declaration is malformed or unavailable: {exc}"

    if canonical_invariants != runtime_invariants:
        canonical_set = set(canonical_invariants)
        runtime_set = set(runtime_invariants)
        missing = sorted(canonical_set - runtime_set)
        extra = sorted(runtime_set - canonical_set)
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"extra={extra}")
        if not details:
            details.append("ordering differs")
        return False, "canonical invariant universe diverges across authority graph and runtime: " + "; ".join(details)

    return True, "canonical invariant universe is coherent across authority graph and runtime"


def probe_lineage_binding(repository_root: str) -> tuple[bool, str]:
    """Prove operator → intent → request → decision → transition → artifact binding."""
    root = str(Path(repository_root).resolve())
    if root not in sys.path:
        sys.path.insert(0, root)

    contracts = __import__("05_runtime.governance.contracts", fromlist=["*"])
    vault_module = __import__("05_runtime.vault", fromlist=["CanonicalVault"])
    operator = contracts.ValidatedOperatorContext(
        operator_id="stumpy-probe-operator",
        credential_id="stumpy-probe-credential",
        authenticated_at=contracts.iso_now(),
        session_id="stumpy-probe-session",
        signature="stumpy-probe-signature",
    )
    intent = contracts.ValidatedIntent(kind="audit", scope=("stumpy",), nonce="stumpy-probe-nonce", issued_at=contracts.iso_now())
    request = contracts.GovernedRequest(
        request_id="stumpy-probe-request",
        operator=operator,
        intent=intent,
        input_payload={"content": "lineage probe"},
        source_refs=("stumpy-probe",),
        requested_action="commit",
    )
    decision = contracts.GovernanceDecision.create("ALLOW", {}, ("STUMPY_PROBE",), (), {})
    artifact_hash = request.artifact_hash
    transition = contracts.StateTransition(
        transition_id="stumpy-probe-transition",
        prior_refs=(),
        operation="commit",
        payload_hash=request.payload_hash,
        decision_hash=decision.decision_hash,
        lineage_event_id="stumpy-probe-lineage",
        request_id=request.request_id,
        intent_id=request.intent.intent_id,
        artifact_hash=artifact_hash,
    )
    valid = contracts.LineageEvent(
        event_id="stumpy-probe-lineage",
        timestamp=contracts.iso_now(),
        operator_id=operator.operator_id,
        transition_id=transition.transition_id,
        decision_hash=decision.decision_hash,
        input_hash=request.payload_hash,
        payload_hash=request.payload_hash,
        evaluator_versions={},
        request_id=request.request_id,
        intent_id=request.intent.intent_id,
        artifact_hash=artifact_hash,
    )
    if not valid.is_constitutionally_bound_to(transition, request, decision):
        return False, "valid operator → intent → request → decision → transition → artifact chain failed to bind"

    vault = vault_module.CanonicalVault()
    receipt = vault.commit_transition(transition, decision, valid, request.input_payload, request=request)
    node = vault.nodes[0]
    if valid.artifact_hash != node["content_hash"] or receipt.node_id != node["node_id"]:
        return False, "lineage artifact identity did not resolve to the committed canonical artifact"

    tampered = contracts.LineageEvent(
        event_id=valid.event_id,
        timestamp=valid.timestamp,
        operator_id=valid.operator_id,
        transition_id=valid.transition_id,
        decision_hash=valid.decision_hash,
        input_hash=valid.input_hash,
        payload_hash=valid.payload_hash,
        evaluator_versions=valid.evaluator_versions,
        request_id=valid.request_id,
        intent_id=valid.intent_id,
        artifact_hash=contracts.sha256_digest("tampered artifact"),
    )
    if tampered.is_constitutionally_bound_to(transition, request, decision):
        return False, "tampered artifact identity was accepted by constitutional lineage binding"
    return True, "valid lineage bound to committed artifact and tampered artifact identity rejected"


def probe_drift_accountability(repository_root: str) -> tuple[bool, str]:
    path = Path(repository_root) / "00_governance" / "stumpy" / "stumpy_drift_detector.py"
    module = _load_module("stumpy_drift_detector", path)
    detector = module.DriftDetectorProcess(Queue(), Queue())
    altitude_findings = detector.inspect_event({"type": "runtime_state", "source": "stumpy-probe", "payload": {"altitude": "unauthorized"}})
    lineage_findings = detector.inspect_event({"type": "epistemic_state", "source": "stumpy-probe", "payload": {"state": "UNKNOWN"}})
    types = {finding.get("type") for finding in altitude_findings + lineage_findings}
    required = {"altitude_drift", "epistemic_drift"}
    if required <= types:
        return True, "altitude and epistemic drift conditions produced explicit findings"
    return False, f"drift detector missed expected finding types: {', '.join(sorted(required - types))}"


def probe_authority_hierarchy(repository_root: str) -> tuple[bool, str]:
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
    tampered = text + "\n  - rank: 99\n    authority: SUPREME\n    artifact: attacker\n"
    if len(re.findall(r"^    authority: SUPREME$", tampered, re.MULTILINE)) != 2:
        return False, "authority probe fixture did not create a duplicate supreme authority"
    return True, "authority hierarchy is ordered and duplicate supreme-root mutation is detectable"


def probe_reversibility(repository_root: str) -> tuple[bool, str]:
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
    try:
        fn = PROBES[probe]
    except KeyError:
        return False, f"unsupported behavioral probe: {probe}"
    return fn(repository_root)
