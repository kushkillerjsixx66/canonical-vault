"""Coverage accounting for Stumpy's declared invariant audit matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .audit_matrix import INVARIANTS, CORE_AUDIT_MATRIX


@dataclass(frozen=True)
class CoverageReport:
    total_invariants: int
    evaluated_invariants: tuple[str, ...]
    unevaluated_invariants: tuple[str, ...]

    @property
    def evaluated_count(self) -> int:
        return len(self.evaluated_invariants)

    @property
    def coverage_ratio(self) -> float:
        return self.evaluated_count / self.total_invariants if self.total_invariants else 0.0

    def validate(self) -> None:
        if self.total_invariants != len(INVARIANTS):
            raise ValueError("coverage total must match canonical invariant vocabulary")
        if set(self.evaluated_invariants) & set(self.unevaluated_invariants):
            raise ValueError("an invariant cannot be both evaluated and unevaluated")
        if set(self.evaluated_invariants) | set(self.unevaluated_invariants) != set(INVARIANTS):
            raise ValueError("coverage must account for every canonical invariant")


def compute_core_coverage() -> CoverageReport:
    evaluated = tuple(dict.fromkeys(entry.invariant for entry in CORE_AUDIT_MATRIX))
    unevaluated = tuple(invariant for invariant in INVARIANTS if invariant not in evaluated)
    report = CoverageReport(
        total_invariants=len(INVARIANTS),
        evaluated_invariants=evaluated,
        unevaluated_invariants=unevaluated,
    )
    report.validate()
    return report
