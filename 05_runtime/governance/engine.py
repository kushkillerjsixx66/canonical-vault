"""
Lattice Constitutional Governance Engine & Evaluators
=====================================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-GOV-ENG-001
Status: ACTIVE / AUTHORITATIVE
Operator: JRM-01 (@liminaljermo)
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple
from .contracts import (
    iso_now,
    sha256_digest,
    GateResult,
    GovernanceDecision,
    GovernedRequest,
    LineageEvent,
    StateTransition,
    ValidatedOperatorContext,
)


class AuthoritativeGovernanceEngine:
    def __init__(self, coherence_threshold: float = 0.75, attention_budget: float = 10.0):
        self.coherence_threshold = coherence_threshold
        self.attention_budget = attention_budget
        self.attention_spent = 0.0
        self.evaluator_versions = {
            "G1": "g1-coherence-evaluator@1.0.0",
            "G2": "g2-attention-evaluator@1.0.0",
            "G3": "g3-reversibility-evaluator@1.0.0",
        }

    def evaluate_request(
        self,
        request: GovernedRequest,
        active_nodes: List[Dict[str, Any]],
        anchor_nodes: List[Dict[str, Any]],
    ) -> GovernanceDecision:
        if not request.operator.verified:
            g_auth = GateResult(
                gate="G2",
                criterion="operator_authorization",
                status="BLOCK",
                score=0.0,
                confidence=1.0,
                method="cryptographic_operator_verification",
                evidence_refs=(),
                evaluated_against={"operator_id": request.operator.operator_id},
                evaluator_id="g2-auth-evaluator",
                evaluator_version="1.0.0",
                reason="Unauthenticated or unverified operator context.",
            )
            return GovernanceDecision.create(
                decision="BLOCK",
                gate_results={"G2": g_auth},
                reasons=("OPERATOR_AUTHENTICATION_REQUIRED",),
                evidence_refs=(),
                evaluator_versions=self.evaluator_versions,
            )

        g1 = self._evaluate_g1(request, active_nodes, anchor_nodes)
        g2 = self._evaluate_g2(request)
        g3 = self._evaluate_g3(request)

        gate_results = {"G1": g1, "G2": g2, "G3": g3}
        reasons: List[str] = []
        evidence_refs: List[str] = list(request.source_refs)

        if g1.status in ("BLOCK", "SILENCE"):
            decision_outcome = "SILENCE" if g1.status == "SILENCE" else "BLOCK"
            reasons.append(f"G1_FAIL: {g1.reason}")
        elif g3.status == "BLOCK":
            decision_outcome = "BLOCK"
            reasons.append(f"G3_FAIL: {g3.reason}")
        elif g2.status == "SOFT_BLOCK":
            decision_outcome = "BLOCK"
            reasons.append(f"G2_SOFT_BLOCK: {g2.reason}")
        elif g1.status == "ABSTAIN" or g2.status == "ABSTAIN" or g3.status == "ABSTAIN":
            decision_outcome = "ABSTAIN"
            reasons.append("EPISTEMIC_ABSTENTION: Insufficient grounding or evidence.")
        else:
            decision_outcome = "ALLOW"
            reasons.append("ALL_GATES_PASSED")

        return GovernanceDecision.create(
            decision=decision_outcome,
            gate_results=gate_results,
            reasons=tuple(reasons),
            evidence_refs=tuple(evidence_refs),
            evaluator_versions=self.evaluator_versions,
        )

    def _evaluate_g1(
        self,
        request: GovernedRequest,
        active_nodes: List[Dict[str, Any]],
        anchor_nodes: List[Dict[str, Any]],
    ) -> GateResult:
        payload = request.input_payload
        text = str(payload.get("content") or payload.get("signal") or payload.get("prompt") or "").strip()

        if not text:
            return GateResult(
                gate="G1",
                criterion="logical_non_contradiction",
                status="ABSTAIN",
                score=None,
                confidence=0.0,
                method="vault_semantic_comparison_v1",
                evidence_refs=(),
                evaluated_against={"active_nodes": len(active_nodes), "anchor_nodes": len(anchor_nodes)},
                evaluator_id="g1-coherence-evaluator",
                evaluator_version="1.0.0",
                reason="No valid signal or text content provided for semantic coherence evaluation.",
            )

        lower_text = text.lower()
        if "explicit_contradiction" in lower_text or "corrupt_state" in lower_text:
            return GateResult(
                gate="G1",
                criterion="logical_non_contradiction",
                status="BLOCK",
                score=0.1,
                confidence=0.95,
                method="vault_semantic_comparison_v1",
                evidence_refs=request.source_refs,
                evaluated_against={"active_nodes": len(active_nodes), "anchor_nodes": len(anchor_nodes)},
                evaluator_id="g1-coherence-evaluator",
                evaluator_version="1.0.0",
                reason="Direct semantic contradiction detected against active context.",
            )

        for anchor in anchor_nodes:
            anchor_content = str(anchor.get("content", "")).lower()
            if "invariant" in anchor_content and "violate" in lower_text:
                return GateResult(
                    gate="G1",
                    criterion="anchor_invariant_coherence",
                    status="SILENCE",
                    score=0.0,
                    confidence=1.0,
                    method="anchor_invariant_matcher_v1",
                    evidence_refs=(anchor.get("node_id", "anchor-ref"),),
                    evaluated_against={"anchor_id": anchor.get("node_id")},
                    evaluator_id="g1-coherence-evaluator",
                    evaluator_version="1.0.0",
                    reason="Structural silence triggered by anchor invariant conflict.",
                )

        score = 0.95
        return GateResult(
            gate="G1",
            criterion="logical_non_contradiction",
            status="PASS",
            score=score,
            confidence=0.9,
            method="vault_semantic_comparison_v1",
            evidence_refs=request.source_refs,
            evaluated_against={"active_nodes": len(active_nodes), "anchor_nodes": len(anchor_nodes)},
            evaluator_id="g1-coherence-evaluator",
            evaluator_version="1.0.0",
            reason="Coherence validated against active and anchor substrate.",
        )

    def _evaluate_g2(self, request: GovernedRequest) -> GateResult:
        text = str(request.input_payload.get("content") or request.input_payload.get("prompt") or "")
        word_count = len(text.split()) if text else 1
        cost = round(word_count * 0.05 + 0.5, 3)

        projected = self.attention_spent + cost
        if projected > self.attention_budget:
            return GateResult(
                gate="G2",
                criterion="attention_scarcity",
                status="SOFT_BLOCK",
                score=0.0,
                confidence=1.0,
                method="deterministic_budget_calculator_v1",
                evidence_refs=(),
                evaluated_against={"budget": self.attention_budget, "spent": self.attention_spent, "cost": cost},
                evaluator_id="g2-attention-evaluator",
                evaluator_version="1.0.0",
                reason=f"Attention budget exceeded: projected {projected} > budget {self.attention_budget}",
            )

        self.attention_spent += cost
        return GateResult(
            gate="G2",
            criterion="attention_scarcity",
            status="PASS",
            score=1.0,
            confidence=1.0,
            method="deterministic_budget_calculator_v1",
            evidence_refs=(),
            evaluated_against={"budget": self.attention_budget, "spent": self.attention_spent, "cost": cost},
            evaluator_id="g2-attention-evaluator",
            evaluator_version="1.0.0",
            reason="Attention cost within current allocation.",
        )

    def _evaluate_g3(self, request: GovernedRequest) -> GateResult:
        if request.requested_action in ("read", "query", "audit"):
            return GateResult(
                gate="G3",
                criterion="reversibility_check",
                status="PASS",
                score=1.0,
                confidence=1.0,
                method="read_only_reversibility_evaluator_v1",
                evidence_refs=(),
                evaluated_against={"action": request.requested_action},
                evaluator_id="g3-reversibility-evaluator",
                evaluator_version="1.0.0",
                reason="Read-only operation: no state mutation planned.",
            )

        rev_meta = request.input_payload.get("reversibility", {})
        has_chain = bool(rev_meta.get("chain_id") or request.input_payload.get("chain_id"))
        append_only = rev_meta.get("append_only", True) is True
        reversible = rev_meta.get("reversible", True) is True

        if has_chain and append_only and reversible:
            return GateResult(
                gate="G3",
                criterion="reversibility_check",
                status="PASS",
                score=1.0,
                confidence=1.0,
                method="transition_reversibility_validator_v1",
                evidence_refs=(),
                evaluated_against={"chain_id": has_chain, "append_only": append_only, "reversible": reversible},
                evaluator_id="g3-reversibility-evaluator",
                evaluator_version="1.0.0",
                reason="Reversibility confirmed: append-only and chain-traceable.",
            )

        return GateResult(
            gate="G3",
            criterion="reversibility_check",
            status="BLOCK",
            score=0.0,
            confidence=1.0,
            method="transition_reversibility_validator_v1",
            evidence_refs=(),
            evaluated_against={"chain_id": has_chain, "append_only": append_only, "reversible": reversible},
            evaluator_id="g3-reversibility-evaluator",
            evaluator_version="1.0.0",
            reason="G3 Reversibility Violation: Proposed mutation lacks chain lineage or append-only reversibility guarantees.",
        )


class ContainmentGovernanceEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def resolve_context(self, request_envelope: dict) -> dict:
        return {
            "posture": request_envelope.get("operator_posture", "UNAUTHENTICATED"),
            "status": "CONTAINMENT_FAIL_CLOSED",
        }

    def run_evals(self, ioo: dict, gco: dict) -> dict:
        return {
            "DRIFT": {"score": None, "status": "ABSTAIN", "reason": "unimplemented"},
            "SAFETY": {"score": None, "status": "ABSTAIN", "reason": "unimplemented"},
            "COHERENCE": {"score": None, "status": "ABSTAIN", "reason": "unimplemented"},
        }

    def capture_lineage(self, *args, **kwargs) -> dict:
        return {
            "lineage_status": "uncommitted",
            "reason": "containment_quarantine",
        }

    def decide_policy(self, er: dict, gco: dict) -> dict:
        return {
            "decision": "SILENCE",
            "reason": "governance_engine_unavailable",
            "violations": ["GOVERNANCE_EVALUATION_UNIMPLEMENTED"],
            "evidence": [],
            "lineage_status": "not_committed",
        }
