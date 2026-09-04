from pathlib import Path

from importlib import import_module

stumpy_audit = import_module("05_runtime.stumpy.audit")
EpistemicState = import_module("05_runtime.stumpy.classifier").EpistemicState


ROOT = Path(__file__).resolve().parents[1]


def audit(**kwargs):
    defaults = dict(
        repository_root=str(ROOT),
        constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
        target="05_runtime/stumpy/source_inspector.py",
        evidence_id="EVID-SOURCE-TEST",
    )
    defaults.update(kwargs)
    return stumpy_audit.audit_source_for_predicate(**defaults)


def test_source_audit_detects_exact_source_property():
    result = audit(
        claim_id="CLAIM-SOURCE-001",
        requirement="source property is observable",
        expected_behavior="RepositorySourceInspector",
        predicate="contains_class",
    )
    assert result.state is EpistemicState.PASS
    assert result.claim.evidence.verify_digest()


def test_source_audit_detects_missing_property():
    result = audit(
        claim_id="CLAIM-SOURCE-002",
        requirement="missing property must be detected",
        expected_behavior="DefinitelyNotPresentInSource",
        predicate="contains_exact_text",
    )
    assert result.state is EpistemicState.FAIL
    assert result.claim.evidence.verify_digest()


def test_source_audit_does_not_infer_unknown_predicate():
    result = audit(
        claim_id="CLAIM-SOURCE-003",
        requirement="unsupported test predicate",
        expected_behavior="anything",
        predicate="semantic_magic",
    )
    assert result.state is EpistemicState.UNKNOWN


def test_source_audit_can_verify_a_real_governance_symbol():
    result = audit(
        claim_id="CLAIM-GOV-001",
        requirement="governance engine exposes expected class",
        target="05_runtime/governance/engine.py",
        expected_behavior="AuthoritativeGovernanceEngine",
        predicate="contains_class",
        evidence_id="EVID-GOV-001",
    )
    assert result.state is EpistemicState.PASS
    assert result.claim.evidence.verify_digest()
