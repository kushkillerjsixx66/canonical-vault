"""Bounded audit runner for the registered Stumpy rules."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .manifest import AuditManifest, core_manifest
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
    selected = manifest or core_manifest()
    selected.validate()
    revision = resolve_repository_revision(repository_root)
    registry = StumpyAuditRegistry(repository_root, selected.rules)
    findings = registry.run()
    return build_report(
        findings,
        repository_revision=revision.value,
        rules_evaluated=len(selected.rules),
        evaluator_id="stumpy.audit_registry",
        evaluator_version="1.0.0",
    )


def run_default_audit(repository_root: str) -> StumpyAuditReport:
    return run_audit(repository_root, core_manifest())
