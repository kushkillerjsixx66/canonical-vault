"""
Lattice Constitutional Runtime Contracts
========================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-CONTRACT-001
Status: ACTIVE / AUTHORITATIVE
Operator: JRM-01 (@liminaljermo)
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional, Tuple


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_digest(data: Any) -> str:
    if isinstance(data, str):
        content = data.encode("utf-8")
    elif isinstance(data, bytes):
        content = data
    else:
        content = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


class GovernanceError(Exception):
    pass


class NonAuthoritativeRuntimeError(GovernanceError):
    pass


class GovernanceDeniedError(GovernanceError):
    def __init__(self, decision: "GovernanceDecision"):
        self.decision = decision
        super().__init__(f"Governance check denied execution: {decision.decision}. Reasons: {decision.reasons}")


class LineageIntegrityError(GovernanceError):
    pass


class DestructiveResetProhibitedError(GovernanceError):
    pass


class SchemaCoherenceError(GovernanceError):
    pass


@dataclass(frozen=True)
class ValidatedOperatorContext:
    operator_id: str
    credential_id: str
    authenticated_at: str
    session_id: str
    signature: str
    roles: Tuple[str, ...] = ("OPERATOR",)
    verified: bool = True

    def has_scope(self, required_scope: str) -> bool:
        return self.verified and ("ADMIN" in self.roles or "OPERATOR" in self.roles)


@dataclass(frozen=True)
class ValidatedIntent:
    kind: str
    scope: Tuple[str, ...]
    nonce: str
    issued_at: str

    @property
    def intent_id(self) -> str:
        """Stable identity derived from the immutable validated intent fields."""
        return sha256_digest({
            "kind": self.kind,
            "scope": list(self.scope),
            "nonce": self.nonce,
            "issued_at": self.issued_at,
        })


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
        """Content identity used to bind a resulting canonical artifact."""
        content = self.input_payload.get("content")
        if content is None:
            content = self.input_payload.get("signal")
        if content is None:
            content = ""
        return sha256_digest(content if isinstance(content, (str, bytes)) else json.dumps(content, sort_keys=True))


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
        dec_hash = sha256_digest(summary)
        return cls(
            decision=decision,
            gate_results=gate_results,
            reasons=reasons,
            evidence_refs=evidence_refs,
            evaluator_versions=evaluator_versions,
            decision_hash=dec_hash,
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

    @property
    def artifact_hash(self) -> str:
        """Canonical artifact identity derived from the transition payload."""
        return self.payload_hash


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

    @property
    def artifact_hash(self) -> str:
        """Canonical artifact identity carried through the lineage event."""
        return self.payload_hash

    def is_bound_to(self, transition: StateTransition, decision: GovernanceDecision) -> bool:
        return (
            self.transition_id == transition.transition_id
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


@dataclass(frozen=True)
class GovernedResponse:
    decision: GovernanceDecision
    lineage: LineageEvent
    receipt: Optional[CommitReceipt]
    output: Optional[Dict[str, Any]]
    silenced: bool
