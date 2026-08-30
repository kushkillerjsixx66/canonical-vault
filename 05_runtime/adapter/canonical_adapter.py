"""
Lattice Governed Canonical Runtime Adapter
==========================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-ADP-001
Status: ACTIVE / AUTHORITATIVE
Operator: JRM-01 (@liminaljermo)
"""

import uuid
from typing import Any, Dict, Optional
from ..governance.contracts import (
    iso_now,
    GovernedRequest,
    GovernedResponse,
    ValidatedIntent,
    ValidatedOperatorContext,
)
from ..governance.boundary import GovernanceBoundary


class GovernedRuntimeAdapter:
    def __init__(self, boundary: Optional[GovernanceBoundary] = None):
        self.boundary = boundary or GovernanceBoundary()

    def run(self, request_envelope: Dict[str, Any]) -> Dict[str, Any]:
        op_data = request_envelope.get("operator", {})
        operator = ValidatedOperatorContext(
            operator_id=op_data.get("operator_id", "UNAUTHENTICATED"),
            credential_id=op_data.get("credential_id", "none"),
            authenticated_at=op_data.get("authenticated_at", iso_now()),
            session_id=op_data.get("session_id", f"session-{uuid.uuid4()}"),
            signature=op_data.get("signature", ""),
            roles=tuple(op_data.get("roles", ["GUEST"])),
            verified=bool(op_data.get("verified", False)),
        )

        intent_data = request_envelope.get("intent", {})
        intent = ValidatedIntent(
            kind=intent_data.get("kind", "query"),
            scope=tuple(intent_data.get("scope", ["read"])),
            nonce=intent_data.get("nonce", str(uuid.uuid4())),
            issued_at=intent_data.get("issued_at", iso_now()),
        )

        governed_req = GovernedRequest(
            request_id=request_envelope.get("request_id", f"req-{uuid.uuid4()}"),
            operator=operator,
            intent=intent,
            input_payload=request_envelope.get("payload", {}),
            source_refs=tuple(request_envelope.get("source_refs", ())),
            requested_action=request_envelope.get("action", "query"),
        )

        response: GovernedResponse = self.boundary.execute(governed_req)

        if response.silenced:
            return {
                "decision": "SILENCE",
                "output": None,
                "reasons": response.decision.reasons,
                "lineage_status": "quarantined",
            }

        return {
            "decision": response.decision.decision,
            "gate_results": {g: res.status for g, res in response.decision.gate_results.items()},
            "eval_scores": {
                g: {"score": res.score, "confidence": res.confidence, "status": res.status}
                for g, res in response.decision.gate_results.items()
            },
            "lineage": {
                "event_id": response.lineage.event_id,
                "decision_hash": response.lineage.decision_hash,
                "payload_hash": response.lineage.payload_hash,
            },
            "receipt": response.receipt.__dict__ if response.receipt else None,
            "output": response.output,
        }
