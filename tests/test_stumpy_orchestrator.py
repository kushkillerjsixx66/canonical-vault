from importlib import import_module
from pathlib import Path

import pytest

orchestrator = import_module("05_runtime.stumpy.orchestrator")

ROOT = Path(__file__).resolve().parents[1]


def test_orchestrator_requires_unique_participants():
    with pytest.raises(ValueError):
        orchestrator.orchestrate(str(ROOT), branches=("chatgpt", "chatgpt"))


def test_orchestrator_requires_a_participant():
    with pytest.raises(ValueError):
        orchestrator.orchestrate(str(ROOT), branches=())


def test_orchestrator_uses_one_canonical_commit_for_all_observations():
    report = orchestrator.orchestrate(str(ROOT), branches=("chatgpt", "claude"))

    assert report.authority_boundary == "STUMPY_AUDIT_ONLY"
    assert report.canonical_commit
    assert report.participating_branches == ("chatgpt", "claude")
    assert len(report.observations) == 2
    assert all(observation.commit for observation in report.observations)
    assert all(observation.state for observation in report.observations)
    assert isinstance(report.to_dict(), dict)


def test_orchestrator_marks_non_coherent_branches_for_review(monkeypatch):
    class FakeReport:
        canonical_ref = "main"
        canonical_commit = "c" * 40
        branch_ref = "chatgpt"
        branch_commit = "b" * 40
        baseline_aligned = True
        state = "EXTENSION"
        governance_sensitive_paths = ()
        changed_paths = ("proposal.md",)

    monkeypatch.setattr(orchestrator, "audit_branch", lambda *args, **kwargs: FakeReport())
    monkeypatch.setattr(orchestrator, "_new_run_id", lambda commit: "TEST-RUN")
    monkeypatch.setattr(orchestrator, "_commit", lambda *args: "c" * 40)

    report = orchestrator.orchestrate(str(ROOT), branches=("chatgpt",))

    assert report.run_id == "TEST-RUN"
    assert report.requires_review is True
    assert report.divergence == ("chatgpt",)
