"""
Lattice Constitutional Control Plane: GovernanceBoundary
=========================================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-GOV-BND-001
Status: ACTIVE / AUTHORITATIVE
Operator: JRM-01 (@liminaljermo)
"""

import uuid
from typing import Any, Dict, List, Optional
from .contracts import (
    iso_now,
    CommitReceipt,
    GovernanceDecision,
    GovernedRequest,
    GovernedResponse,
    LineageEvent,
    NonAuthoritativeRuntimeError,
    StateTransition,
)
from .engine import AuthoritativeGovernanceEngine


class GovernanceBoundary:
    def __init__(self, engine: Optional[AuthoritativeGovernanceEngine] = None, vault: Optional[Any] = None):
        self.engine = engine or AuthoritativeGovernanceEngine()
        self.vault = vault
        self.lineage_sink: List[LineageEvent] = []
        self.quarantine_sink: List[Dict[str, Any]] = []

    def execute(self, request: GovernedRequest) -> GovernedResponse:
        active_nodes = self.vault.get_active_nodes() if self.vault else []
        anchor_nodes = self.vault.get_anchor_nodes() if self.vault else []

        decision = self.engine.evaluate_request(request, active_nodes, anchor_nodes)

        transition_id = f"trans-{uuid.uuid4()}"
        lineage_id = f"lineage-{uuid.uuid4()}"
        artifact_hash = request.artifact_hash

        transition = StateTransition(
            transition_id=transition_id,
            prior_refs=request.source_refs,
            operation=request.requested_action,
            payload_hash=request.payload_hash,
            decision_hash=decision.decision_hash,
            lineage_event_id=lineage_id,
            committed=False,
            request_id=request.request_id,
            intent_id=request.intent.intent_id,
            artifact_hash=artifact_hash,
        )

        lineage_event = LineageEvent(
            event_id=lineage_id,
            timestamp=iso_now(),
            operator_id=request.operator.operator_id,
            transition_id=transition_id,
            decision_hash=decision.decision_hash,
            input_hash=request.payload_hash,
            payload_hash=request.payload_hash,
            evaluator_versions=decision.evaluator_versions,
            request_id=request.request_id,
            intent_id=request.intent.intent_id,
            artifact_hash=artifact_hash,
        )

        if decision.decision != "ALLOW":
            quarantine_record = {
                "quarantine_id": f"quarantine-{uuid.uuid4()}",
                "timestamp": iso_now(),
                "request_id": request.request_id,
                "operator_id": request.operator.operator_id,
                "intent_id": request.intent.intent_id,
                "decision": decision.decision,
                "reasons": decision.reasons,
                "gate_results": {g: res.status for g, res in decision.gate_results.items()},
                "payload_hash": request.payload_hash,
            }
            self.quarantine_sink.append(quarantine_record)
            self.lineage_sink.append(lineage_event)

            silenced = decision.decision == "SILENCE"
            return GovernedResponse(
                decision=decision,
                lineage=lineage_event,
                receipt=None,
                output=None if silenced else {"status": decision.decision, "reasons": decision.reasons},
                silenced=silenced,
            )

        receipt = None
        if request.requested_action in ("store", "mutate", "commit", "update") and self.vault:
            receipt = self.vault.commit_transition(
                transition=transition,
                decision=decision,
                lineage=lineage_event,
                payload=request.input_payload,
                request=request,
            )

        self.lineage_sink.append(lineage_event)

        return GovernedResponse(
            decision=decision,
            lineage=lineage_event,
            receipt=receipt,
            output={"status": "SUCCESS", "action": request.requested_action, "receipt": receipt},
            silenced=False,
        )
