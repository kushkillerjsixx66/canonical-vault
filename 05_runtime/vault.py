"""
Lattice Hardened Canonical Vault
================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-VAULT-001
Status: ACTIVE / AUTHORITATIVE
Operator: JRM-01 (@liminaljermo)
"""

import hashlib
import json
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from .governance.contracts import (
    iso_now,
    sha256_digest,
    CommitReceipt,
    DestructiveResetProhibitedError,
    GovernanceDecision,
    GovernanceDeniedError,
    GovernedRequest,
    LineageEvent,
    LineageIntegrityError,
    SchemaCoherenceError,
    StateTransition,
)


class NodeClassification(str, Enum):
    ANCHOR = "ANCHOR"
    STANDARD = "STANDARD"
    VARA_PROMOTED = "VARA_PROMOTED"
    OPERATOR_DIRECTIVE = "OPERATOR_DIRECTIVE"
    AUDIT_RECORD = "AUDIT_RECORD"


class NodeState(str, Enum):
    LATENT = "LATENT"
    ACTIVE = "ACTIVE"
    DECAYING = "DECAYING"
    PRUNED = "PRUNED"
    QUARANTINED = "VEIL_QUARANTINE"
    TOMBSTONED = "TOMBSTONED"


class CanonicalVault:
    DEFAULT_INVARIANT_TAGS = ["I·COH", "II·REV", "III·ATT", "IV·SIL", "V·DEC", "VI·SIG"]

    def __init__(self):
        self._nodes: List[Dict[str, Any]] = []
        self._transitions: List[StateTransition] = []
        self._lineage_sink: List[LineageEvent] = []
        self._ephemeral_session_cache: Dict[str, Any] = {}

    @property
    def nodes(self) -> List[Dict[str, Any]]:
        return list(self._nodes)

    def commit_transition(
        self,
        transition: StateTransition,
        decision: GovernanceDecision,
        lineage: LineageEvent,
        payload: Dict[str, Any],
        request: Optional[GovernedRequest] = None,
    ) -> CommitReceipt:
        if decision.decision != "ALLOW":
            raise GovernanceDeniedError(decision)

        # Validate the artifact schema before lineage binding so malformed
        # state is rejected for the reason that is constitutionally primary.
        classification = payload.get("classification", NodeClassification.STANDARD.value)
        state = payload.get("state", NodeState.ACTIVE.value)

        if classification not in [c.value for c in NodeClassification]:
            raise SchemaCoherenceError(f"Invalid classification: {classification}")
        if state not in [s.value for s in NodeState]:
            raise SchemaCoherenceError(f"Invalid state: {state}")

        if request is None or not lineage.is_constitutionally_bound_to(transition, request, decision):
            raise LineageIntegrityError(
                "Lineage event is not bound to operator, intent, request, decision, and transition."
            )

        content = payload.get("content") or payload.get("signal") or ""

        node = self._build_canonical_node(
            content=content,
            classification=classification,
            state=state,
            chain_id=payload.get("chain_id"),
            invariant_tags=payload.get("invariant_tags"),
            operator_note=payload.get("operator_note"),
            transition_id=transition.transition_id,
            lineage_id=lineage.event_id,
            operator_id=request.operator.operator_id,
            intent_id=request.intent.intent_id,
            request_id=request.request_id,
            decision_hash=decision.decision_hash,
        )

        # The committed artifact must be the exact artifact represented by
        # the constitutional lineage binding, not merely a related payload.
        if node["content_hash"] != request.artifact_hash:
            raise LineageIntegrityError("Committed artifact does not match constitutional artifact identity.")

        self._nodes.append(node)
        self._transitions.append(transition)
        self._lineage_sink.append(lineage)

        commit_id = f"commit-{uuid.uuid4()}"
        root_hash = sha256_digest([n["content_hash"] for n in self._nodes])

        return CommitReceipt(
            commit_id=commit_id,
            transition_id=transition.transition_id,
            lineage_event_id=lineage.event_id,
            timestamp=iso_now(),
            vault_root_hash=root_hash,
            node_id=node["node_id"],
        )

    def store_direct_unguarded(self, *args, **kwargs):
        raise GovernanceDeniedError(
            GovernanceDecision.create(
                decision="BLOCK",
                gate_results={},
                reasons=("DIRECT_VAULT_MUTATION_FORBIDDEN",),
                evidence_refs=(),
                evaluator_versions={},
            )
        )

    def reset(self):
        raise DestructiveResetProhibitedError(
            "Canonical Vault cannot be destructively reset. State is append-only and cryptographically bound."
        )

    def reset_ephemeral_session_state(self) -> str:
        self._ephemeral_session_cache.clear()
        return "Ephemeral session state cleared; canonical vault intact."

    def get_active_nodes(self) -> List[Dict[str, Any]]:
        return [n for n in self._nodes if n["state"] == NodeState.ACTIVE.value]

    def get_anchor_nodes(self) -> List[Dict[str, Any]]:
        return [n for n in self._nodes if n["classification"] == NodeClassification.ANCHOR.value]

    def retrieve(self, include_pruned: bool = False) -> List[Dict[str, Any]]:
        if include_pruned:
            return list(self._nodes)
        return [n for n in self._nodes if n["state"] != NodeState.PRUNED.value]

    def _build_canonical_node(
        self,
        content: Any,
        classification: str,
        state: str,
        chain_id: Optional[str],
        invariant_tags: Optional[List[str]],
        operator_note: Optional[str],
        transition_id: str,
        lineage_id: str,
        operator_id: str,
        intent_id: str,
        request_id: str,
        decision_hash: str,
    ) -> Dict[str, Any]:
        content_text = content if isinstance(content, str) else json.dumps(content, sort_keys=True)
        now = iso_now()
        node_id = str(uuid.uuid4())
        return {
            "node_id": node_id,
            "chain_id": chain_id or f"chain-{node_id}",
            "operator_id": operator_id,
            "intent_id": intent_id,
            "request_id": request_id,
            "decision_hash": decision_hash,
            "transition_id": transition_id,
            "lineage_id": lineage_id,
            "content": content_text,
            "content_hash": sha256_digest(content_text),
            "classification": classification,
            "state": state,
            "created_at": now,
            "last_referenced": now,
            "reference_count": 0,
            "invariant_tags": invariant_tags or list(self.DEFAULT_INVARIANT_TAGS),
            "operator_note": operator_note,
            "reversibility": {
                "chain_id": chain_id or f"chain-{node_id}",
                "append_only": True,
                "reversible": True,
            },
        }
