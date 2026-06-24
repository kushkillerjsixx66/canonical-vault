from typing import List
from .types import RawIntent, Constraint, MechanismPlan
from .selector import MechanismSelector
from .planner import MechanismPlanner


class MTMRuntime:
    """
    Mechanism Translation Module runtime.
    """

    def __init__(self):
        self.selector = MechanismSelector()
        self.planner = MechanismPlanner()

    def run(
        self,
        intent: RawIntent,
        pam_constraints: List[Constraint],
        cce_constraints: List[Constraint],
        cfc_constraints: List[Constraint],
    ) -> MechanismPlan:

        all_constraints = pam_constraints + cce_constraints + cfc_constraints

        pam_verdict = next(
            (c.value for c in pam_constraints if c.name == "principle_verdict"),
            "CLEAR"
        )

        mechanism = self.selector.select(intent.text, pam_verdict)

        plan = self.planner.build_plan(
            mechanism=mechanism,
            constraints=all_constraints,
            intent_text=intent.text,
        )

        return plan
