from importlib import import_module


audit_matrix = import_module("05_runtime.stumpy.audit_matrix")
run_module = import_module("05_runtime.stumpy.run")


def test_canonical_invariant_universe_is_fully_mapped_to_audit_rules():
    evaluated = tuple(entry.invariant for entry in audit_matrix.CORE_AUDIT_MATRIX)

    assert set(evaluated) == set(audit_matrix.INVARIANTS)
    assert len(evaluated) == len(set(evaluated))
    assert tuple(invariant for invariant in audit_matrix.INVARIANTS if invariant not in evaluated) == ()


def test_run_audit_accounts_for_invariants_without_executed_findings(monkeypatch):
    monkeypatch.setattr(
        run_module,
        "resolve_repository_revision",
        lambda _: run_module.Revision("test-revision", "test"),
    )

    class FakeRegistry:
        def __init__(self, repository_root, rules):
            self.rules = tuple(rules)

        def run(self):
            return []

    monkeypatch.setattr(run_module, "StumpyAuditRegistry", FakeRegistry)

    report = run_module.run_default_audit(".")

    assert set(report.evaluated_invariants) == set()
    assert set(report.unevaluated_invariants) == set(audit_matrix.INVARIANTS)
    assert report.coverage_ratio == 0.0
    report.validate()
