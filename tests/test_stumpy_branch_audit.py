from importlib import import_module
from pathlib import Path

import pytest

branch_audit = import_module("05_runtime.stumpy.branch_audit")

ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    import subprocess

    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def test_branch_audit_rejects_canonical_as_model_branch():
    with pytest.raises(branch_audit.BranchAuditError):
        branch_audit.audit_branch(str(ROOT), "main")


def test_branch_audit_rejects_ungoverned_branch():
    with pytest.raises(branch_audit.BranchAuditError):
        branch_audit.audit_branch(str(ROOT), "random-branch")


def test_branch_audit_report_is_read_only_and_structured():
    report = branch_audit.audit_branch(str(ROOT), "chatgpt")

    assert report.canonical_ref == "main"
    assert report.branch_ref == "chatgpt"
    assert len(report.canonical_commit) == 40
    assert len(report.branch_commit) == 40
    assert len(report.merge_base) == 40
    assert report.authority_boundary == "STUMPY_AUDIT_ONLY"
    assert isinstance(report.to_dict(), dict)


def test_branch_audit_does_not_change_working_revision():
    before = _git("rev-parse", "HEAD")
    branch_audit.audit_branch(str(ROOT), "chatgpt")
    after = _git("rev-parse", "HEAD")
    assert after == before
