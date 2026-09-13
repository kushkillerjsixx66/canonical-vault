"""Governed multi-model branch orchestration for Stumpy.

This module coordinates read-only branch audits against one fixed canonical
snapshot. It does not merge, mutate canonical state, or resolve conflicts.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Sequence

from .branch_audit import BranchAuditReport, MODEL_BRANCHES, audit_branch


@dataclass(frozen=True)
class ModelObservation:
    branch: str
    commit: str
    baseline_aligned: bool
    state: str
    changed_paths: tuple[str, ...]
    governance_sensitive_paths: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationReport:
    run_id: str
    canonical_ref: str
    canonical_commit: str
    participating_branches: tuple[str, ...]
    observations: tuple[ModelObservation, ...]
    convergence: tuple[str, ...]
    divergence: tuple[str, ...]
    authority_boundary: str = "STUMPY_AUDIT_ONLY"

    @property
    def requires_review(self) -> bool:
        return bool(self.divergence) or any(
            not observation.baseline_aligned or observation.governance_sensitive_paths
            for observation in self.observations
        )

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "observations": [asdict(observation) for observation in self.observations],
            "convergence": list(self.convergence),
            "divergence": list(self.divergence),
            "requires_review": self.requires_review,
        }


def _new_run_id(canonical_commit: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"MMO-{timestamp}-{canonical_commit[:12]}"


def orchestrate(
    repository_root: str,
    *,
    canonical_ref: str = "main",
    branches: Sequence[str] = MODEL_BRANCHES,
    run_id: str | None = None,
) -> OrchestrationReport:
    """Audit multiple model branches against one immutable canonical baseline."""
    selected = tuple(branches)
    if not selected:
        raise ValueError("at least one governed model branch is required")
    if len(set(selected)) != len(selected):
        raise ValueError("participating branches must be unique")

    # Resolve the canonical commit once. Each branch audit then compares
    # against the same ref, preventing the baseline from moving mid-run.
    from .branch_audit import _commit

    canonical_commit = _commit(repository_root, canonical_ref)
    reports: list[BranchAuditReport] = []
    for branch in selected:
        reports.append(
            audit_branch(
                repository_root,
                branch,
                canonical_ref=canonical_ref,
                allowed_branches=MODEL_BRANCHES,
            )
        )

    observations = tuple(
        ModelObservation(
            branch=report.branch_ref,
            commit=report.branch_commit,
            baseline_aligned=report.baseline_aligned,
            state=report.state,
            changed_paths=report.changed_paths,
            governance_sensitive_paths=report.governance_sensitive_paths,
        )
        for report in reports
    )

    states = {observation.state for observation in observations}
    convergence = tuple(
        sorted(
            observation.branch
            for observation in observations
            if observation.state == "COHERENT"
        )
    )
    divergence = tuple(
        sorted(
            observation.branch
            for observation in observations
            if observation.state != "COHERENT"
        )
    )

    # Multiple branches reporting the same non-coherent state is convergence
    # of observation, not proof of truth or authorization.
    if len(states) == 1 and states != {"COHERENT"}:
        divergence = tuple(sorted(observation.branch for observation in observations))

    return OrchestrationReport(
        run_id=run_id or _new_run_id(canonical_commit),
        canonical_ref=canonical_ref,
        canonical_commit=canonical_commit,
        participating_branches=selected,
        observations=observations,
        convergence=convergence,
        divergence=divergence,
    )
