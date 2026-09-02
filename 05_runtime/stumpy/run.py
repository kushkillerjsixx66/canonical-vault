"""Bounded audit runner for the registered Stumpy rules."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .audit_matrix import CORE_AUDIT_MATRIX
from .manifest import AuditManifest
from .registry import StumpyAuditRegistry
from .report import StumpyAuditReport, build_report


@dataclass(frozen=True)
class Revision:
    value: str
    source: str


def resolve_repository_revision(repository_root: str) -> Revision:
    try:
        value = subprocess.check_output(
            ["git", "-C", repository_root, "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        if value:
            return Revision(value=value, source="git-rev-parse")
    except (OSError, subprocess.CalledProcessError):
        pass
    raise RuntimeError("unable to resolve repository revision; audit must not run against an unidentified revision")


def run_audit(repository_root: str, manifest: AuditManifest | None = None) -> StumpyAuditReport:
    """Execute the canonical matrix and derive coverage from executed findings.

    The audit matrix is the execution authority for the default Stumpy audit.
    Coverage must describe evidence acquisition that actually ran, not merely
    declarations present in a manifest or matrix.
    """
    selected_matrix = CORE_AUDIT_MATRIX
    if manifest is not None:
        manifest.validate()
        selected_rules = manifest.rules
        matrix_by_rule = {entry.rule.rule_id: entry.invariant for entry in selected_matrix}
    else:
        selected_rules = tuple(entry.rule for entry in selected_matrix)
        matrix_by_rule = {entry.rule.rule_id: entry.invariant for entry in selected_matrix}

    revision = resolve_repository_revision(repository_root)
    registry = StumpyAuditRegistry(repository_root, selected_rules)
    findings = registry.run()

    executed_rule_ids = {
        finding.finding_id.removeprefix("FIND-")
        for finding in findings
        if finding.finding_id.startswith("FIND-")
    }
    evaluated_invariants = tuple(
        entry.invariant
        for entry in selected_matrix
        if entry.rule.rule_id in executed_rule_ids
    )
    unevaluated_invariants = tuple(
        entry.invariant
        for entry in selected_matrix
        if entry.rule.rule_id not in executed_rule_ids
    )
    rules_not_evaluated = tuple(
        rule.rule_id for rule in selected_rules if rule.rule_id not in executed_rule_ids
    )

    return build_report(
        findings,
        repository_revision=revision.value,
        rules_evaluated=len(executed_rule_ids),
        rules_not_evaluated=rules_not_evaluated,
        evaluated_invariants=evaluated_invariants,
        unevaluated_invariants=unevaluated_invariants,
        evaluator_id="stumpy.audit_registry",
        evaluator_version="1.0.0",
    )


def run_default_audit(repository_root: str) -> StumpyAuditReport:
    return run_audit(repository_root)
