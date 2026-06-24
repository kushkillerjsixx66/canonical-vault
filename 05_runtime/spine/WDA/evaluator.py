from .types import EAT
from uuid import uuid4
from datetime import datetime


class AuditEvaluator:
    """
    Produces the Epistemic Audit Trail (EAT) record.
    """

    def evaluate(self, event) -> EAT:
        lineage = {
            "actor": event.actor,
            "context": event.context,
            "constraint_sources": event.decision.criteria_ref,
        }

        return EAT(
            eat_id=str(uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            capability=event.capability.name,
            decision=event.decision.label,
            output=event.output.output_type,
            verdict=event.capability.risk_level,
            lineage=lineage,
        )
