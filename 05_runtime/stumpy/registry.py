"""Declarative requirement-to-evidence registry for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .audit import audit_behavioral_probe, audit_source_for_predicate
from .classifier import EpistemicState
from .finding import StumpyFinding, finding_from_behavioral_audit, finding_from_source_audit
from .score_honesty import audit_score_honesty, finding_from_score_honesty_audit


@dataclass(frozen=True)
class AuditRule:
    rule_id: str
    domain: str
    constitutional_basis: str
    requirement: str
    target: str
    expected_behavior: str
    predicate: str
    severity: str


class StumpyAuditRegistry:
    """Run explicitly registered audit rules without inferring missing rules."""

    def __init__(self, repository_root: str, rules: Iterable[AuditRule] = ()):
        self.repository_root = repository_root
        self.rules = tuple(rules)

    def run(self) -> list[StumpyFinding]:
        findings: list[StumpyFinding] = []
        for index, rule in enumerate(self.rules, start=1):
            evidence_id = f"EVID-{rule.rule_id}-{index:03d}"
            if rule.predicate == "behavioral_probe":
                result = audit_behavioral_probe(
                    repository_root=self.repository_root,
                    claim_id=rule.rule_id,
                    constitutional_basis=rule.constitutional_basis,
                    requirement=rule.requirement,
                    target=rule.target,
                    probe=rule.expected_behavior,
                    evidence_id=evidence_id,
                )
                findings.append(
                    finding_from_behavioral_audit(
                        result,
                        finding_id=f"FIND-{rule.rule_id}",
                        domain=rule.domain,
                        severity=rule.severity,
                    )
                )
                continue

            result = audit_source_for_predicate(
                repository_root=self.repository_root,
                claim_id=rule.rule_id,
                constitutional_basis=rule.constitutional_basis,
                requirement=rule.requirement,
                target=rule.target,
                expected_behavior=rule.expected_behavior,
                predicate=rule.predicate,
                evidence_id=evidence_id,
            )
            findings.append(
                finding_from_source_audit(
                    result,
                    finding_id=f"FIND-{rule.rule_id}",
                    domain=rule.domain,
                    severity=rule.severity,
                )
            )
        return findings


def default_repository_rules() -> tuple[AuditRule, ...]:
    return (
        AuditRule(
            rule_id="GOV-SCORE-001",
            domain="score_honesty",
            constitutional_basis="STUMPY_AUDIT_SCHEMA.yaml: score honesty",
            requirement="Evaluator scores must be grounded in an explicit method and evidence basis.",
            target="05_runtime/governance/engine.py",
            expected_behavior="score derived from declared evaluation method and evidence",
            predicate="contains_exact_text",
            severity="HIGH",
        ),
        AuditRule(
            rule_id="STUMPY-SOURCE-001",
            domain="source_integrity",
            constitutional_basis="STUMPY_EVIDENCE_ACQUISITION_SPEC.md",
            requirement="Stumpy source inspection must exist as an executable repository capability.",
            target="05_runtime/stumpy/source_inspector.py",
            expected_behavior="class RepositorySourceInspector(",
            predicate="contains_exact_text",
            severity="MEDIUM",
        ),
    )
