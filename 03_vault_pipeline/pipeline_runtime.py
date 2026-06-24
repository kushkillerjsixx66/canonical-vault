"""
Lattice Pipeline Orchestration Runtime
-------------------------------------

Executes the full governed pipeline:

IDE → CCE → CFC → SBM → PAM → MTM → WDA
"""

from dataclasses import dataclass
from typing import Dict, Any, List

# Kernel imports
from runtime.kernel.ide import IDERuntime
from runtime.kernel.cce import CCERuntime
from runtime.kernel.cfc import CFCRuntime

# Spine imports
from runtime.spine.sbm import SBMRuntime, RawInput
from runtime.spine.pam import PAMRuntime, Principle
from runtime.spine.mtm import MTMRuntime, RawIntent, Constraint
from runtime.spine.wda import (
    WDARuntime,
    Capability,
    Decision,
    Output,
    DriftSignal,
    Event,
)


@dataclass
class PipelineResult:
    ide: Any
    cce: Any
    cfc: Any
    sbm: Any
    pam: Any
    mtm: Any
    wda: Any
    lineage: Dict[str, Any]


class PipelineRuntime:
    """
    Full Lattice pipeline orchestrator.
    """

    def __init__(self, principles: List[Principle], persist_eat_fn=None):
        # Kernel
        self.ide = IDERuntime()
        self.cce = CCERuntime()
        self.cfc = CFCRuntime()

        # Spine
        self.sbm = SBMRuntime()
        self.pam = PAMRuntime(principles)
        self.mtm = MTMRuntime()
        self.wda = WDARuntime(persist_fn=persist_eat_fn)

    def run(self, text: str, metadata: Dict[str, Any] | None = None) -> PipelineResult:
        metadata = metadata or {}

        # -------------------------
        # 1. IDE — Intent Decomposition
        # -------------------------
        ide_out = self.ide.run(text, metadata)

        # -------------------------
        # 2. CCE — Constraint Cartography
        # -------------------------
        cce_out = self.cce.run(ide_out)

        # -------------------------
        # 3. CFC — Crash-Free Constraints
        # -------------------------
        cfc_out = self.cfc.run(ide_out, cce_out)

        # -------------------------
        # 4. SBM — Semantic Breakdown
        # -------------------------
        sbm_raw = RawInput(text=text, metadata=metadata)
        sbm_out = self.sbm.run(sbm_raw)

        # -------------------------
        # 5. PAM — Principle Anchoring
        # -------------------------
        atoms = [a.text for a in sbm_out.atoms]
        pam_out = self.pam.run(atoms)

        # -------------------------
        # 6. MTM — Mechanism Translation
        # -------------------------
        raw_intent = RawIntent(text=text, metadata=metadata)

        pam_constraints = [
            Constraint(
                name="principle_verdict",
                rule="pam_verdict",
                value=pam_out.verdict,
                source="pam",
            )
        ]

        cce_constraints = [
            Constraint(
                name=s.name,
                rule="keyword",
                value=s.value,
                source="cce",
            )
            for s in cce_out.signals
        ]

        cfc_constraints = [
            Constraint(
                name="execution_posture",
                rule="posture",
                value=cfc_out.posture,
                source="cfc",
            )
        ]

        mtm_out = self.mtm.run(
            intent=raw_intent,
            pam_constraints=pam_constraints,
            cce_constraints=cce_constraints,
            cfc_constraints=cfc_constraints,
        )

        # -------------------------
        # 7. WDA — Walking Data Audit
        # -------------------------
        event = Event(
            capability=Capability(
                name="pipeline_execution",
                risk_level="HIGH" if cfc_out.posture == "blocked" else "LOW",
                requires_policy=True,
            ),
            decision=Decision(
                decision_type="mechanism_plan",
                label=mtm_out.mechanism.name,
                confidence=1.0,
                requires_policy=True,
                criteria_ref=list(mtm_out.constraints.keys()),
            ),
            output=Output(
                output_id="final",
                output_type="mechanism_plan",
                ref="mtm",
                visibility="INTERNAL",
                downstream_targets=[],
            ),
            drift=DriftSignal(
                score=0.0,
                threshold=1.0,
                drift_type=None,
                explanation=None,
            ),
            modifies_or_depends_on_artifact=False,
            is_reversible=True,
            context={"posture": cfc_out.posture},
            actor={"type": "system"},
            raw_input_ref="input",
            normalized_features_ref=None,
            sensitivity_label="low",
            governance_requires_audit=True,
        )

        wda_out = self.wda.run(event)

        # -------------------------
        # Final lineage
        # -------------------------
        lineage = {
            "ide": ide_out.metadata,
            "cce": cce_out.metadata,
            "cfc": cfc_out.metadata,
            "pam": pam_out.lineage,
            "mtm": mtm_out.lineage,
            "wda": wda_out.lineage,
        }

        return PipelineResult(
            ide=ide_out,
            cce=cce_out,
            cfc=cfc_out,
            sbm=sbm_out,
            pam=pam_out,
            mtm=mtm_out,
            wda=wda_out,
            lineage=lineage,
        )
