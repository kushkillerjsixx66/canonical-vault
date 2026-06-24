from typing import List, Dict, Any
from .types import Mechanism, Constraint, MechanismPlan


class MechanismPlanner:
    """
    Converts a mechanism + constraints into an executable plan.
    """

    def build_plan(
        self,
        mechanism: Mechanism,
        constraints: List[Constraint],
        intent_text: str
    ) -> MechanismPlan:

        steps = [
            {"step": "parse_intent", "intent": intent_text},
            {"step": "apply_mechanism", "mechanism": mechanism.name},
            {"step": "enforce_constraints", "count": len(constraints)},
            {"step": "produce_output"},
        ]

        constraint_map: Dict[str, Any] = {
            c.name: {"rule": c.rule, "value": c.value, "source": c.source}
            for c in constraints
        }

        lineage = {
            "mechanism": mechanism.name,
            "constraint_sources": list({c.source for c in constraints}),
        }

        return MechanismPlan(
            mechanism=mechanism,
            steps=steps,
            constraints=constraint_map,
            lineage=lineage,
        )
