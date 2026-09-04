"""Runtime governance contracts and constitutional lineage primitives."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional, Tuple


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_digest(value: Any) -> str:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ValidatedOperatorContext:
    operator_id: str
    credential_id: str
    authenticated_at: str
    session_id: str
    signature: str
    roles: Tuple[str, ...] = ()
    verified: bool = True


@dataclass(frozen=True)
class ValidatedIntent:
    kind: str
    scope: Tuple[str, ...]
    nonce: str
    issued_at: str
    intent_id: str = field(default_factory=lambda: f"intent-{uuid.uuid4()}")


@dataclass(frozen=True)
class GovernedRequest:
    request_id: str
    operator: ValidatedOperatorContext
    intent: ValidatedIntent
    input_payload: Dict[str, Any]
    source_refs: Tuple[str, ...]
    requested_action: str
    runtime_version: str = "1.0.0"
    policy_version: str = "1.0.0"

    @property
    def payload_hash(self) -> str:
        return sha256_digest(self.input_payload)

    @property
    def artifact_hash(self) -> str:
        """Identity of the content that a canonical artifact would contain."""
        content = self.input_payload.get("content")
        if content is None:
            content = self.input_payload.get("signal")
        if content is None:
            content = ""
        return sha256_digest(
            content if isinstance(content, (str, bytes)) else json.dumps(content, sort_keys=True)
        )


@dataclass(frozen=True)
class GateResult:
    gate: Literal["G1", "G2", "G3"]
    criterion: str
    status: Literal["PASS", "BLOCK", "SOFT_BLOCK", "ABSTAIN", "SILENCE", "QUARANTINE"]
    score: Optional[float]
    confidence: float
    method: str
    evidence_refs: Tuple[str, ...]
    evaluated_against: Dict[str, Any]
    evaluator_id: str
    evaluator_version: str
    reason: str


@dataclass(frozen=True)
class GovernanceDecision:
    decision: Literal["ALLOW", "BLOCK", "SILENCE", "ABSTAIN", "QUARANTINE"]
    gate_results: Dict[str, GateResult]
    reasons: Tuple[str, ...]
    evidence_refs: Tuple[str, ...]
    evaluator_versions: Dict[str, str]
    decision_hash: str
    timestamp: str = field(default_factory=iso_now)

    @classmethod
    def create(
        cls,
        decision: Literal["ALLOW", "BLOCK", "SILENCE", "ABSTAIN", "QUARANTINE"],
        gate_results: Dict[str, GateResult],
        reasons: Tuple[str, ...],
        evidence_refs: Tuple[str, ...],
        evaluator_versions: Dict[str, str],
    ) -> "GovernanceDecision":
        summary = {
            "decision": decision,
            "reasons": list(reasons),
            "evidence_refs": list(evidence_refs),
            "evaluator_versions": evaluator_versions,
            "gate_statuses": {g: res.status for g, res in gate_results.items()},
        }
        return cls(
            decision=decision,
            gate_results=gate_results,
            reasons=reasons,
            evidence_refs=evidence_refs,
            evaluator_versions=evaluator_versions,
            decision_hash=sha256_digest(summary),
        )


@dataclass(frozen=True)
class StateTransition:
    transition_id: str
    prior_refs: Tuple[str, ...]
    operation: str
    payload_hash: str
    decision_hash: str
    lineage_event_id: str
    committed: bool = False
    request_id: str = ""
    intent_id: str = ""
    artifact_hash: str = ""


@dataclass(frozen=True)
class LineageEvent:
    event_id: str
    timestamp: str
    operator_id: str
    transition_id: str
    decision_hash: str
    input_hash: str
    payload_hash: str
    evaluator_versions: Dict[str, str]
    request_id: str = ""
    intent_id: str = ""
    artifact_hash: str = ""

    def is_bound_to(self, transition: StateTransition, decision: GovernanceDecision) -> bool:
        return (
            bool(self.artifact_hash)
            and bool(transition.artifact_hash)
            and self.transition_id == transition.transition_id
            and self.decision_hash == decision.decision_hash
            and self.decision_hash == transition.decision_hash
            and self.payload_hash == transition.payload_hash
            and self.artifact_hash == transition.artifact_hash
        )

    def is_constitutionally_bound_to(
        self,
        transition: StateTransition,
        request: GovernedRequest,
        decision: GovernanceDecision,
    ) -> bool:
        """Require operator → intent → request → decision → transition → artifact binding."""
        return (
            self.is_bound_to(transition, decision)
            and self.operator_id == request.operator.operator_id
            and self.intent_id == request.intent.intent_id
            and self.request_id == request.request_id
            and transition.intent_id == request.intent.intent_id
            and transition.request_id == request.request_id
            and self.artifact_hash == request.artifact_hash
        )


@dataclass(frozen=True)
class CommitReceipt:
    commit_id: str
    transition_id: str
    lineage_event_id: str
    timestamp: str
    vault_root_hash: str
    node_id: str


class GovernanceDeniedError(RuntimeError):
    def __init__(self, decision: GovernanceDecision):
        super().__init__(f"Governance denied: {decision.decision}")
        self.decision = decision


class LineageIntegrityError(RuntimeError):
    pass


class DestructiveResetProhibitedError(RuntimeError):
    pass


class SchemaCoherenceError(ValueError):
    pass


class NonAuthoritativeRuntimeError(RuntimeError):
    pass


class GovernedResponse:
    def __init__(self, decision, lineage, receipt, output, silenced=False):
        self.decision = decision
        self.lineage = lineage
        self.receipt = receipt
        self.output = output
        self.silenced = silenced
