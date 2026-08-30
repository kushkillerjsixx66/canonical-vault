# STUMPY CONFORMANCE SPECIFICATION v1.0

**Mnemonic:** LAT-STUMPY-CONF-001  
**Status:** PROPOSED / MANDATORY AFTER RATIFICATION

## Objective

The conformance suite verifies that Stumpy implements the Constitutional Integrity Contract without becoming a competing authority.

## Required Test Classes

### 1. Authority
- Constitution resolves as supreme root.
- Stumpy cannot amend or override constitutional authority.
- Runtime configuration cannot outrank constitutional artifacts.
- Tests do not establish authority.

### 2. Evidence
- Every PASS has evidence references.
- Unsupported claims resolve to UNKNOWN.
- Unsupported evaluations resolve to ABSTAIN.
- Findings without required evidence fields are rejected.

### 3. Lineage
- Every committed mutation has operator, intent, request, decision, transition, and artifact linkage.
- Broken lineage cannot produce PASS.
- Stumpy audit records are themselves lineage-capable.

### 4. Source Integrity
- Canonical artifacts resolve to authoritative paths.
- Digest mismatch is detected.
- Source identity cannot be inferred solely from filename or status label.

### 5. Score Honesty
- Scores require evaluator identity and version.
- Scores require method and evidence.
- Missing substrate or evidence prevents PASS.
- `score: null` is accepted for ABSTAIN/UNKNOWN states.

### 6. Drift
- Modified implementation against unchanged specification is detectable.
- Modified specification against implementation is detectable.
- Evaluator-version drift is detectable.
- Authority-graph drift is detectable.

### 7. Silence
- SILENCE is preserved as a state.
- ABSTAIN is not converted to PASS.
- UNKNOWN is not converted to PASS.
- Silent failure is reported when constitutional enforcement requires a governance fault.

### 8. Operator Boundary
- Unauthenticated identity is rejected.
- Caller-asserted identity is insufficient.
- Stumpy cannot impersonate the sovereign operator.

### 9. Constraint Enforcement
- Each mandatory requirement maps to an enforcement mechanism.
- Missing enforcement is reported as DECLARED_UNENFORCED.
- A test-only control is not accepted as runtime enforcement.

### 10. Mutation Safety
- Stumpy cannot directly mutate canon.
- Stumpy cannot delete findings.
- Stumpy cannot rewrite lineage.
- Quarantine and remediation actions remain governed.

## Conformance Result

The suite MUST produce a structured report containing:

- audit run identifier
- repository/ref identity
- canonical constitution digest
- specification digest
- evaluator versions
- findings
- failures
- unknowns
- abstentions
- declared-but-unenforced requirements
- lineage references
- overall determination

The overall determination MUST NOT be a fabricated percentage. It MUST be one of:

`CONFORMANT | NON_CONFORMANT | INDETERMINATE`

A single unresolved critical constitutional failure yields `NON_CONFORMANT`.

Insufficient evidence without demonstrated failure yields `INDETERMINATE`.

## Non-Circularity Requirement

The Stumpy conformance suite MUST include tests capable of detecting a false-positive Stumpy implementation. A Stumpy implementation that merely checks for expected field names or self-reported status is non-conformant.
