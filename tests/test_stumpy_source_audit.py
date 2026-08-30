from pathlib import Path

from importlib import import_module

stumpy_audit = import_module("05_runtime.stumpy.audit")
EpistemicState = import_module("05_runtime.stumpy.classifier").EpistemicState


def test_source_audit_detects_exact_source_property():
    root = Path(__file__).resolve().parents[1]
    result = stumpy_audit.audit_source_for_predicate(
        repository_root=str(root),
        claim_id="CLAIM-SOURCE-001",
        constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
        requirement="source property is observable",
        target="05_runtime/stumpy/source_inspector.py",
        expected_behavior="RepositorySourceInspector",
        predicate="contains_class",
        evidence_id="EVID-SOURCE-001",
    )
    assert result.state is EpistemicState.PASS
    assert result.claim.evidence.verify_digest()


def test_source_audit_does_not_infer_unknown_predicate():
    root = Path(__file__).resolve().parents[1]
    result = stumpy_audit.audit_source_for_predicate(
        repository_root=str(root),
        claim_id="CLAIM-SOURCE-002",
        constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
        requirement="unsupported test predicate",
        target="05_runtime/stumpy/source_inspector.py",
        expected_behavior="anything",
        predicate="semantic_magic",
        evidence_id="EVID-SOURCE-002",
    )
    assert result.state is EpistemicState.UNKNOWN
