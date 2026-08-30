"""
Lattice Constitutional Conformance Test Suite (Phase 5 Assurance)
================================================================
Authority: 00_governance/constitution/lattice_constitution.md
Mnemonic: LAT-TEST-CONF-001
Status: ACTIVE / MANDATORY
Operator: JRM-01 (@liminaljermo)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from runtime.governance.contracts import (
    iso_now,
    sha256_digest,
    CommitReceipt,
    DestructiveResetProhibitedError,
    GovernanceDecision,
    GovernanceDeniedError,
    GovernedRequest,
    LineageEvent,
    LineageIntegrityError,
    NonAuthoritativeRuntimeError,
    SchemaCoherenceError,
    StateTransition,
    ValidatedIntent,
    ValidatedOperatorContext,
)
from runtime.governance.engine import AuthoritativeGovernanceEngine, ContainmentGovernanceEngine
from runtime.governance.boundary import GovernanceBoundary
from runtime.vault import CanonicalVault, NodeClassification, NodeState
from runtime.adapter.canonical_adapter import GovernedRuntimeAdapter
from runtime.lattice_core import Lattice as LegacyLattice


class TestConstitutionalConformance(unittest.TestCase):

    def setUp(self):
        self.authenticated_operator = ValidatedOperatorContext(
            operator_id="did:lattice:operator:JRM-01",
            credential_id="key-2026-auth-01",
            authenticated_at=iso_now(),
            session_id="sess-alpha-001",
            signature="sig:ed25519:valid-proof",
            roles=("OPERATOR", "ADMIN"),
            verified=True,
        )
        self.unauthenticated_operator = ValidatedOperatorContext(
            operator_id="UNAUTHENTICATED",
            credential_id="none",
            authenticated_at=iso_now(),
            session_id="sess-anon",
            signature="",
            roles=("GUEST",),
            verified=False,
        )
        self.valid_intent = ValidatedIntent(
            kind="proposal.create",
            scope=("vault.read", "proposal.create"),
            nonce="nonce-99128",
            issued_at=iso_now(),
        )
        self.canonical_vault = CanonicalVault()
        self.engine = AuthoritativeGovernanceEngine()
        self.governance_boundary = GovernanceBoundary(engine=self.engine, vault=self.canonical_vault)

    def test_01_all_entrypoints_use_authoritative_governance_boundary(self):
        with self.assertRaises(NonAuthoritativeRuntimeError):
            _ = LegacyLattice()

    def test_02_direct_vault_write_without_governance_decision_is_rejected(self):
        with self.assertRaises(GovernanceDeniedError):
            self.canonical_vault.store_direct_unguarded(content="Direct unlineaged payload")

    def test_03_every_committed_transition_has_immutable_lineage(self):
        req = GovernedRequest(
            request_id="req-mutation-001",
            operator=self.authenticated_operator,
            intent=self.valid_intent,
            input_payload={
                "content": "Constitutional Invariant Baseline Anchor",
                "classification": NodeClassification.ANCHOR.value,
                "state": NodeState.ACTIVE.value,
                "reversibility": {"chain_id": "chain-root-01", "append_only": True, "reversible": True},
            },
            source_refs=("00_governance/constitution/lattice_constitution.md",),
            requested_action="commit",
        )

        resp = self.governance_boundary.execute(req)
        self.assertEqual(resp.decision.decision, "ALLOW")
        self.assertIsNotNone(resp.receipt)
        self.assertIsNotNone(resp.lineage)
        self.assertEqual(len(self.canonical_vault.nodes), 1)
        self.assertEqual(self.canonical_vault.nodes[0]["lineage_id"], resp.lineage.event_id)
        self.assertEqual(self.canonical_vault.nodes[0]["transition_id"], resp.receipt.transition_id)

    def test_04_blocked_g3_transition_does_not_mutate_canonical_vault(self):
        initial_node_count = len(self.canonical_vault.nodes)
        req = GovernedRequest(
            request_id="req-g3-fail",
            operator=self.authenticated_operator,
            intent=self.valid_intent,
            input_payload={
                "content": "Non-reversible state mutation attempt",
                "reversibility": {"append_only": False, "reversible": False},
            },
            source_refs=(),
            requested_action="commit",
        )

        resp = self.governance_boundary.execute(req)
        self.assertEqual(resp.decision.decision, "BLOCK")
        self.assertEqual(resp.decision.gate_results["G3"].status, "BLOCK")
        self.assertIsNone(resp.receipt)
        self.assertEqual(len(self.canonical_vault.nodes), initial_node_count)
        self.assertEqual(len(self.governance_boundary.quarantine_sink), 1)
        self.assertEqual(self.governance_boundary.quarantine_sink[0]["decision"], "BLOCK")

    def test_05_canonical_vault_cannot_be_destructively_reset(self):
        req = GovernedRequest(
            request_id="req-node-1",
            operator=self.authenticated_operator,
            intent=self.valid_intent,
            input_payload={
                "content": "Permanent Canonical Data",
                "classification": NodeClassification.STANDARD.value,
                "state": NodeState.ACTIVE.value,
                "reversibility": {"chain_id": "chain-1", "append_only": True, "reversible": True},
            },
            source_refs=(),
            requested_action="commit",
        )
        resp = self.governance_boundary.execute(req)
        self.assertEqual(resp.decision.decision, "ALLOW")
        self.assertEqual(len(self.canonical_vault.nodes), 1)

        with self.assertRaises(DestructiveResetProhibitedError):
            self.canonical_vault.reset()

        self.assertEqual(len(self.canonical_vault.nodes), 1)

        msg = self.canonical_vault.reset_ephemeral_session_state()
        self.assertIn("canonical vault intact", msg)
        self.assertEqual(len(self.canonical_vault.nodes), 1)

    def test_06_governance_engine_cannot_default_to_allow_without_evidence(self):
        engine = ContainmentGovernanceEngine()
        decision = engine.decide_policy(er={}, gco={})
        self.assertEqual(decision["decision"], "SILENCE")
        self.assertIn("GOVERNANCE_EVALUATION_UNIMPLEMENTED", decision["violations"])

        evals = engine.run_evals(ioo={}, gco={})
        for metric, res in evals.items():
            self.assertIsNone(res["score"])
            self.assertEqual(res["status"], "ABSTAIN")

    def test_07_unsupported_claim_resolves_to_abstain_or_structured_silence(self):
        req_empty = GovernedRequest(
            request_id="req-empty",
            operator=self.authenticated_operator,
            intent=self.valid_intent,
            input_payload={"content": ""},
            source_refs=(),
            requested_action="query",
        )
        resp_empty = self.governance_boundary.execute(req_empty)
        self.assertEqual(resp_empty.decision.decision, "ABSTAIN")
        self.assertIsNone(resp_empty.decision.gate_results["G1"].score)
        self.assertEqual(resp_empty.decision.gate_results["G1"].confidence, 0.0)

    def test_08_operator_identity_is_authenticated_not_caller_asserted(self):
        req_unauth = GovernedRequest(
            request_id="req-unauth",
            operator=self.unauthenticated_operator,
            intent=self.valid_intent,
            input_payload={"content": "Attempting unauthenticated action"},
            source_refs=(),
            requested_action="query",
        )
        resp = self.governance_boundary.execute(req_unauth)
        self.assertEqual(resp.decision.decision, "BLOCK")
        self.assertIn("OPERATOR_AUTHENTICATION_REQUIRED", resp.decision.reasons)

    def test_09_all_canonical_manifest_paths_resolve(self):
        manifest_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "00_governance", "authority_graph.yaml")
        )
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("status: SUPREME_AUTHORITY", content)
        self.assertIn("hierarchy:", content)

    def test_10_authority_graph_has_single_supreme_root(self):
        manifest_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "00_governance", "authority_graph.yaml")
        )
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("00_governance/constitution/lattice_constitution.md", content)
        self.assertEqual(content.count("authority: SUPREME"), 1)

    def test_11_node_classification_is_not_used_as_lifecycle_state(self):
        vault = CanonicalVault()
        payload = {
            "content": "Test Node",
            "classification": "ANCHOR",
            "state": "ANCHOR",
        }
        p_hash = sha256_digest(payload)
        decision = GovernanceDecision.create("ALLOW", {}, (), (), {})
        
        transition = StateTransition(
            transition_id="t1",
            prior_refs=(),
            operation="commit",
            payload_hash=p_hash,
            decision_hash=decision.decision_hash,
            lineage_event_id="l1",
        )
        lineage = LineageEvent(
            event_id="l1",
            timestamp=iso_now(),
            operator_id="op1",
            transition_id="t1",
            decision_hash=decision.decision_hash,
            input_hash=p_hash,
            payload_hash=p_hash,
            evaluator_versions={},
        )

        with self.assertRaises(SchemaCoherenceError):
            vault.commit_transition(
                transition=transition,
                decision=decision,
                lineage=lineage,
                payload=payload,
            )

    def test_12_gate_override_behavior_matches_constitutional_policy(self):
        self.governance_boundary.engine.attention_spent = 100.0

        req = GovernedRequest(
            request_id="req-over-budget",
            operator=self.authenticated_operator,
            intent=self.valid_intent,
            input_payload={"content": "High cost message over budget"},
            source_refs=(),
            requested_action="query",
        )
        resp = self.governance_boundary.execute(req)
        self.assertEqual(resp.decision.decision, "BLOCK")
        self.assertEqual(resp.decision.gate_results["G2"].status, "SOFT_BLOCK")
        self.assertIsNone(resp.receipt)


if __name__ == "__main__":
    unittest.main()
