from importlib import import_module

manifest_module = import_module("05_runtime.stumpy.manifest")
report_module = import_module("05_runtime.stumpy.report")
classifier_module = import_module("05_runtime.stumpy.classifier")
finding_module = import_module("05_runtime.stumpy.finding")


core_manifest = manifest_module.core_manifest
AuditManifest = manifest_module.AuditManifest
EpistemicState = classifier_module.EpistemicState
StumpyFinding = finding_module.StumpyFinding
build_report = report_module.build_report


def test_core_manifest_has_explicit_surface_boundary():
    manifest = core_manifest()
    assert manifest.manifest_id == "STUMPY-CORE-SURFACES-1.0"
    assert manifest.surfaces == ("00_governance", "01_epistemic_substrate", "02_system_spec")
    assert len(manifest.rules) == 3
    manifest.validate()


def test_report_requires_revision():
    finding = StumpyFinding(
        finding_id="FIND-001",
        domain="test",
        status=EpistemicState.PASS.value,
        severity="LOW",
        claim="test",
        observed_state={},
        expected_state={},
        constitutional_basis=["test"],
        evidence_refs=["EVID-001"],
        source_refs=["fixture"],
        lineage_refs=[],
        evaluator_id="test",
        evaluator_version="1.0.0",
        method="test",
        confidence=1.0,
        timestamp="2026-08-30T00:00:00+00:00",
    )
    try:
        build_report([finding], repository_revision="")
    except ValueError:
        return
    raise AssertionError("report without repository revision must be rejected")


def test_fail_dominates_pass():
    findings = []
    for status in (EpistemicState.PASS.value, EpistemicState.FAIL.value):
        findings.append(
            StumpyFinding(
                finding_id=f"FIND-{status}", domain="test", status=status, severity="LOW",
                claim="test", observed_state={}, expected_state={}, constitutional_basis=["test"],
                evidence_refs=["EVID-001"], source_refs=["fixture"], lineage_refs=[],
                evaluator_id="test", evaluator_version="1.0.0", method="test",
                confidence=1.0, timestamp="2026-08-30T00:00:00+00:00",
            )
        )
    report = build_report(findings, repository_revision="abc123")
    assert report.overall_state == EpistemicState.FAIL.value


def test_unknown_remains_visible_when_no_failure_exists():
    finding = StumpyFinding(
        finding_id="FIND-UNKNOWN",
        domain="test",
        status=EpistemicState.UNKNOWN.value,
        severity="LOW",
        claim="test",
        observed_state={},
        expected_state={},
        constitutional_basis=["test"],
        evidence_refs=["EVID-001"],
        source_refs=["fixture"],
        lineage_refs=[],
        evaluator_id="test",
        evaluator_version="1.0.0",
        method="test",
        confidence=None,
        timestamp="2026-08-30T00:00:00+00:00",
    )
    report = build_report([finding], repository_revision="abc123")
    assert report.overall_state == EpistemicState.UNKNOWN.value
    assert report.counts[EpistemicState.UNKNOWN.value] == 1
