"""Explicit bounded audit manifest for the Vault's core specification surfaces.

The manifest records what Stumpy is authorized to inspect. It does not imply
that unlisted material is compliant or even evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass

from .registry import AuditRule, StumpyAuditRegistry


CORE_SURFACES = (
    "00_governance",
    "01_epistemic_substrate",
    "02_system_spec",
)


@dataclass(frozen=True)
class AuditManifest:
    manifest_id: str
    surfaces: tuple[str, ...]
    rules: tuple[AuditRule, ...]

    def validate(self) -> None:
        if not self.manifest_id:
            raise ValueError("manifest_id is required")
        if not self.surfaces:
            raise ValueError("manifest must name at least one surface")
        if any(not rule.target for rule in self.rules):
            raise ValueError("every rule must identify a target")


def core_manifest() -> AuditManifest:
    manifest = AuditManifest(
        manifest_id="STUMPY-CORE-SURFACES-1.0",
        surfaces=CORE_SURFACES,
        rules=(
            AuditRule(
                rule_id="GOV-SCORE-001",
                domain="score_honesty",
                constitutional_basis="STUMPY_AUDIT_SCHEMA.yaml: score honesty",
                requirement="Evaluator scores must be grounded in an explicit method and evidence basis.",
                target="05_runtime/governance/engine.py",
                expected_behavior="score = 0.95",
                predicate="contains_exact_text",
                severity="HIGH",
            ),
            AuditRule(
                rule_id="EPISTEMIC-SILENCE-001",
                domain="epistemic_substrate",
                constitutional_basis="STUMPY_AUDIT_SCHEMA.yaml: epistemic state integrity",
                requirement="Epistemic classification must explicitly represent UNKNOWN rather than silently infer PASS.",
                target="05_runtime/stumpy/classifier.py",
                expected_behavior="EpistemicState.UNKNOWN",
                predicate="contains_exact_text",
                severity="HIGH",
            ),
            AuditRule(
                rule_id="SYSTEM-SPEC-001",
                domain="system_spec",
                constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
                requirement="Evidence acquisition must be explicitly documented as a canonical specification.",
                target="00_governance/specifications/STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
                expected_behavior="Evidence Acquisition",
                predicate="contains_exact_text",
                severity="MEDIUM",
            ),
        ),
    )
    manifest.validate()
    return manifest


def registry_for_core_surfaces(repository_root: str) -> StumpyAuditRegistry:
    manifest = core_manifest()
    return StumpyAuditRegistry(repository_root, manifest.rules)
