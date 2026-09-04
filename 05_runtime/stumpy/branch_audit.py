"""Read-only comparison of a model branch against canonical Git state.

This module deliberately treats Git history as evidence, not authority. It
never merges, rebases, resets, or writes repository state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import subprocess
from typing import Sequence


MODEL_BRANCHES = ("chatgpt", "claude", "gemini", "copilot", "grok")


class BranchAuditError(RuntimeError):
    """Raised when branch evidence cannot be established safely."""


@dataclass(frozen=True)
class FileChange:
    status: str
    path: str
    previous_path: str | None = None


@dataclass(frozen=True)
class BranchAuditReport:
    canonical_ref: str
    branch_ref: str
    canonical_commit: str
    branch_commit: str
    merge_base: str
    baseline_aligned: bool
    state: str
    changes: tuple[FileChange, ...]
    governance_sensitive_paths: tuple[str, ...]
    authority_boundary: str = "STUMPY_AUDIT_ONLY"

    @property
    def changed_paths(self) -> tuple[str, ...]:
        return tuple(change.path for change in self.changes)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "changes": [asdict(change) for change in self.changes],
            "changed_paths": list(self.changed_paths),
            "has_changes": self.has_changes,
        }


def _git(repository_root: str, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", repository_root, *args],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "output", "") or str(exc)
        raise BranchAuditError(f"git evidence acquisition failed: {detail.strip()}") from exc


def _commit(repository_root: str, ref: str) -> str:
    return _git(repository_root, "rev-parse", "--verify", f"{ref}^{{commit}}")


def _parse_name_status(output: str) -> tuple[FileChange, ...]:
    changes: list[FileChange] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        status = fields[0]
        if status.startswith(("R", "C")) and len(fields) >= 3:
            changes.append(FileChange(status=status, path=fields[2], previous_path=fields[1]))
        elif len(fields) >= 2:
            changes.append(FileChange(status=status, path=fields[1]))
        else:
            raise BranchAuditError(f"unparseable git name-status record: {line!r}")
    return tuple(changes)


def _is_governance_sensitive(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith((
        "00_governance/",
        "03_vault_pipeline/",
        "05_runtime/stumpy/",
    )) or normalized in {
        "05_runtime/stumpy.py",
        "05_runtime/lattice_core.py",
    }


def audit_branch(
    repository_root: str,
    branch_ref: str,
    *,
    canonical_ref: str = "main",
    allowed_branches: Sequence[str] = MODEL_BRANCHES,
) -> BranchAuditReport:
    """Compare ``branch_ref`` with canonical state without mutating Git.

    The canonical commit is resolved first and becomes the fixed comparison
    baseline. A branch based on an older/different canonical history is
    reported as ``BASELINE_MISMATCH`` rather than silently rebased or treated
    as comparable to the current baseline.
    """
    if branch_ref == canonical_ref:
        raise BranchAuditError("branch audit requires a model branch distinct from canonical")
    if allowed_branches and branch_ref not in set(allowed_branches):
        raise BranchAuditError(f"branch is outside governed model branch set: {branch_ref}")

    canonical_commit = _commit(repository_root, canonical_ref)
    branch_commit = _commit(repository_root, branch_ref)
    merge_base = _git(repository_root, "merge-base", canonical_ref, branch_ref)
    baseline_aligned = merge_base == canonical_commit

    raw = _git(
        repository_root,
        "diff",
        "--name-status",
        "--find-renames",
        f"{canonical_ref}...{branch_ref}",
    )
    changes = _parse_name_status(raw)
    sensitive = tuple(change.path for change in changes if _is_governance_sensitive(change.path))

    if not baseline_aligned:
        state = "BASELINE_MISMATCH"
    elif not changes:
        state = "COHERENT"
    elif sensitive:
        state = "SEMANTIC_DRIFT"
    elif any(change.status.startswith("D") for change in changes):
        state = "OMISSION"
    elif any(change.status.startswith("A") for change in changes):
        state = "EXTENSION"
    else:
        state = "CONFLICT"

    return BranchAuditReport(
        canonical_ref=canonical_ref,
        branch_ref=branch_ref,
        canonical_commit=canonical_commit,
        branch_commit=branch_commit,
        merge_base=merge_base,
        baseline_aligned=baseline_aligned,
        state=state,
        changes=changes,
        governance_sensitive_paths=sensitive,
    )
