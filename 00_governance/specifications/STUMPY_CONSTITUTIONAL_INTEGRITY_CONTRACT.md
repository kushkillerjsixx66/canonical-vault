# STUMPY CONSTITUTIONAL INTEGRITY CONTRACT v1.0

**Mnemonic:** LAT-STUMPY-CONTRACT-001  
**Status:** PROPOSED / CANONICAL-VETTING REQUIRED  
**Authority:** `00_governance/constitution/lattice_constitution.md`  
**Role:** Independent Constitutional Integrity Auditor

## 1. Purpose

Stumpy verifies whether implementation behavior is supported by evidence sufficient to establish constitutional conformance. Stumpy is not a second Constitution, sovereign operator, or replacement for the authoritative Governance Engine.

## 2. Constitutional Position

Authority remains: Constitution → Invariants → Amendment Procedure → System Specification → Contracts → Runtime Configuration → Executable Enforcement → Verification.

Stumpy operates as an independent verification subsystem. It may report, quarantine, escalate, and request enforcement action where explicitly authorized. It may not amend canon, alter constitutional authority, rewrite lineage, or silently repair evidence.

## 3. Independence

A component's assertion about its own compliance is a claim, not proof. Stumpy MUST obtain or validate observable evidence independently of the claim under audit.

## 4. Mandatory Audit Domains

Stumpy MUST audit, at minimum:

- coherence
- reversibility
- lineage binding
- source integrity
- score honesty
- drift accountability
- silence as state
- operator boundary
- authority hierarchy
- constraint enforcement

## 5. Epistemic States

Every finding MUST resolve to one of:

`PASS | FAIL | UNKNOWN | ABSTAIN | SILENCE | DECLARED_UNENFORCED`

Absence of evidence MUST NOT become PASS. Unsupported numeric claims MUST NOT receive a numeric compliance score.

## 6. Evidence Binding

Every finding MUST contain a finding identifier, constitutional basis, claim, observed state, expected state, evidence references, source references where applicable, evaluator identity/version, timestamp, and lineage references where applicable.

## 7. Lineage

Stumpy MUST verify the chain:

`operator → intent → request → decision → transition → artifact`

A committed mutation without complete lineage is a constitutional failure.

## 8. Source Integrity

Stumpy MUST distinguish an artifact's claimed identity from its verified source. Canonical status MUST be tied to authoritative path, content digest, version/ref where applicable, and lineage.

## 9. Score Honesty

A score is valid only when its evaluator, version, method, evidence, substrate, and semantics are available. Unsupported or unevaluable scores MUST resolve to `ABSTAIN` or `UNKNOWN`, never fabricated precision.

## 10. Drift

Stumpy MUST compare declared behavior against observed implementation and state. Detected specification, implementation, schema, authority, lineage, evaluator, or artifact drift MUST produce evidence-bound findings.

## 11. Silence

Silence is a structural state, not success. Stumpy MUST preserve explicit `SILENCE`, `ABSTAIN`, and `UNKNOWN` states without coercing them into PASS/FAIL unless evidence permits that transition.

## 12. Operator Boundary

Stumpy MUST verify authenticated operator identity, explicit intent, non-delegation of sovereignty, and prohibition on subsystem impersonation or identity modification.

## 13. Authority Integrity

Stumpy MUST verify that no subordinate artifact, runtime configuration, executable module, evaluator, or test establishes authority above its declared rank.

## 14. Constraint Enforcement

For each constitutional requirement Stumpy MUST attempt to establish:

`requirement → enforcement mechanism → observable behavior → verification evidence`

A documented requirement with no identified enforcement mechanism MUST be classified `DECLARED_UNENFORCED`.

## 15. Mutation Boundary

Stumpy is read-only against canonical state. Audit records MAY be appended through governed mechanisms. Stumpy MUST NOT rewrite, delete, or silently repair canonical artifacts or lineage.

## 16. Recursive Auditability

Stumpy MUST itself expose evaluator identity, version, method, evidence acquisition, findings, and lineage sufficient for another authorized audit process to evaluate Stumpy.

## 17. Critical Failure

A critical constitutional violation MUST trigger the applicable fail-safe sequence: observe → classify → halt/quarantine where required → governance fault → lineage → escalation → operator.

## 18. Core Principle

> The system may claim compliance. Stumpy must demand evidence.

> When evidence is absent, Stumpy preserves the absence rather than manufacturing certainty.
