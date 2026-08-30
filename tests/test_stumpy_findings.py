from importlib import import_module

from  pathlib import Path

stumpy_audit = import_module("05_runtime.stumpy.audit")
stumpy_finding = import_module("05_runtime.stumpy.finding")

ROOT = Path(__file__).resolve().parents[1]


def test_source_audit_becomes_schema_aligned_finding():
    result = stumpy_audit.audit_source_for_predicate(
        repository_root=str(ROOT),
        claim_id="CLAIM-GOV-001",
        constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
        requirement="governance engine exposes expected class",
        target="05_runtime/governance/engine.py",
        expected_behavior="AuthoritativeGovernanceEngine",
        predicate="contains_class",
        evidence_id="EVID-GOV-001",
    )
    finding = stumpy_finding.finding_from_source_audit(
        result,
        finding_id="FIND-GOV-001",
        domain="SOURCE_INTEGRITY",
        severity="INFO",
    )
    data = finding.to_dict()
    assert data["status"] == "PASS"
    assert data["evidence_refs"] == ["EVID-GOV-001"]
    assert data["source_refs"] == ["05_runtime/governance/engine.py"]


def test_pass_without_evidence_is_rejected():
    finding = stumpy_finding.StumpyFinding(
        finding_id="FIND-INVALID",
        domain="SOURCE_INTEGRITY",
        status="PASS",
        severity="HIGH",
        claim="invalid",
        observed_state={},
        expected_state={},
        constitutional_basis=["test"],
        evidence_refs=[],
        source_refs=[],
        lineage_refs=[],
        evaluator_id="test",
        evaluator_version="1.0",
        method="test",
        confidence=1.0,
        timestamp="2026-08-30T00:00:00+00:00",
    )
    try:
        finding.validate()
    except ValueError:
        return
    raise AssertionError("evidence-free PASS must be rejected")
