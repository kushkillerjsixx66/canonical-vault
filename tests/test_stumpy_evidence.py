from 05_runtime.stumpy.classifier import EpistemicState, classify_evidence
from 05_runtime.stumpy.claims import AuditClaim, AuditFinding
from 05_runtime.stumpy.evidence import EvidenceKind, EvidenceRecord


# NOTE: package path is intentionally mirrored by the repository runtime layout.
# Test runners that normalize package names may import this module through their
# configured runtime package alias.


def make_evidence(kind=EvidenceKind.TEST):
    return EvidenceRecord.create(
        evidence_id="EVID-001",
        claim_id="CLAIM-001",
        kind=kind,
        target="fixture",
        method="controlled-test",
        evaluator_id="stumpy",
        evaluator_version="0.1.0",
        payload={"result": "observed"},
    )


def test_assertion_only_cannot_pass():
    evidence = make_evidence(EvidenceKind.ASSERTION)
    assert classify_evidence([evidence], observed_conformance=True) is EpistemicState.UNKNOWN


def test_missing_evidence_is_unknown():
    assert classify_evidence([], observed_conformance=True) is EpistemicState.UNKNOWN


def test_observed_failure_is_fail():
    assert classify_evidence([make_evidence()], observed_conformance=False) is EpistemicState.FAIL


def test_observed_success_with_real_evidence_passes():
    assert classify_evidence([make_evidence()], observed_conformance=True) is EpistemicState.PASS


def test_explicit_unenforced_is_not_fail():
    assert classify_evidence([], observed_conformance=None, explicitly_unenforced=True) is EpistemicState.DECLARED_UNENFORCED


def test_silence_is_distinct_state():
    assert classify_evidence([], observed_conformance=None, explicit_silence=True) is EpistemicState.SILENCE


def test_finding_requires_evidence_for_pass_or_fail():
    claim = AuditClaim(
        claim_id="CLAIM-001",
        constitutional_basis="test",
        requirement="require evidence",
        target="fixture",
        expected_behavior="observed",
    )
    finding = AuditFinding(
        finding_id="FIND-001",
        claim=claim,
        state=EpistemicState.PASS,
        severity="HIGH",
        method="test",
    )
    try:
        finding.validate()
    except ValueError:
        return
    raise AssertionError("PASS finding without evidence must be rejected")
