# STUMPY Evidence Acquisition Specification

**Status:** DRAFT / IMPLEMENTATION-BINDING
**Version:** 1.0
**Authority:** Stumpy Constitutional Integrity Contract
**Scope:** Evidence acquisition for independent constitutional audit

## 1. Purpose

This specification defines how Stumpy acquires, preserves, evaluates, and binds evidence before producing an audit finding.

Stumpy SHALL distinguish claims from evidence. A component's assertion about its own compliance is not evidence of compliance.

## 2. Governing Principle

> No finding may be stronger than the evidence supporting it.

Evidence SHALL be independently attributable to a source, observation, execution, or verified state transition. Unsupported assertions SHALL NOT be promoted into evidence.

## 3. Evidence Classes

Stumpy SHALL recognize at least these evidence classes:

- `SOURCE`: immutable repository or canonical artifact content identified by path and digest.
- `SPECIFICATION`: declared requirement, invariant, contract, or expected behavior.
- `RUNTIME`: observed behavior of an executable component under controlled conditions.
- `TEST`: result of a reproducible conformance or adversarial test.
- `STATE`: observed canonical Vault state or transition state.
- `LINEAGE`: cryptographic or structural relationship connecting request, decision, transition, and artifact.
- `RECEIPT`: durable record of an observation or execution.
- `ASSERTION`: statement supplied by a component or operator that has not independently been verified.

`ASSERTION` SHALL NEVER be treated as sufficient evidence for `PASS`.

## 4. Acquisition Pipeline

Every evidence-bearing audit SHALL follow this logical sequence:

```text
RESOLVE
  -> IDENTIFY
  -> HASH
  -> OBSERVE
  -> EXECUTE (when applicable)
  -> CAPTURE
  -> BIND
  -> CLASSIFY
```

### 4.1 RESOLVE

Resolve the authoritative requirement and its source artifact before evaluating implementation behavior.

The resolver SHALL record:

- requirement identifier;
- authority source;
- artifact path or canonical identifier;
- version when available;
- authority status.

### 4.2 IDENTIFY

Identify the exact implementation, test, state, or artifact being evaluated.

Ambiguous targets SHALL produce `UNKNOWN` rather than an inferred target.

### 4.3 HASH

Source artifacts used as evidence SHOULD be content-addressed. Where a digest is unavailable, the evidence SHALL record the strongest available immutable identifier and downgrade certainty as appropriate.

### 4.4 OBSERVE

Capture behavior or state without modifying canonical state.

Observation SHALL record the method used and the target observed.

### 4.5 EXECUTE

When a requirement concerns runtime enforcement, Stumpy SHOULD execute a controlled probe or invoke an existing conformance test rather than relying solely on source inspection.

Mutating probes SHALL use isolated or explicitly reversible fixtures unless the constitutional contract explicitly authorizes mutation.

### 4.6 CAPTURE

The raw observation, test result, or state required to substantiate the finding SHALL be captured as evidence.

A summary without a recoverable basis is not sufficient evidence.

### 4.7 BIND

Each evidence item SHALL be bound to:

- claim ID;
- target;
- evaluator identity and version;
- acquisition method;
- timestamp;
- source or execution reference;
- lineage reference where applicable.

### 4.8 CLASSIFY

Evidence SHALL be converted into an epistemic state only after acquisition and comparison.

Permitted states are:

- `PASS`
- `FAIL`
- `UNKNOWN`
- `ABSTAIN`
- `SILENCE`
- `DECLARED_UNENFORCED`

## 5. Source Evidence

Source evidence SHALL identify the exact file or canonical artifact used for the conclusion.

A source reference SHOULD contain:

```yaml
path: <repository path>
digest: <content digest when available>
revision: <commit/ref when available>
locator: <line/function/section when available>
```

A specification that declares an enforcement mechanism but has no corresponding implementation source SHALL NOT be classified as implemented merely because the specification exists.

## 6. Runtime Evidence

Runtime evidence SHALL distinguish:

1. source-level capability;
2. instantiated capability;
3. exercised behavior;
4. observed result.

The presence of a function, class, route, or configuration entry is not proof that the corresponding behavior is enforced.

## 7. Test Evidence

A passing test SHALL be attributed to:

- exact test identifier;
- test implementation;
- target revision;
- observed result;
- evaluator version.

Tests SHALL NOT be treated as comprehensive proof outside the behavior they actually exercise.

## 8. Negative and Adversarial Evidence

Stumpy SHALL support deliberately invalid fixtures for testing whether an evaluator produces false positives.

Required adversarial classes include:

- fabricated PASS;
- missing evidence;
- invalid digest;
- broken lineage;
- false authority;
- unsupported score;
- silent failure;
- documentation-only enforcement.

A Stumpy implementation that accepts a deliberately dishonest fixture as compliant SHALL fail its own conformance test.

## 9. Evidence Sufficiency Rules

### PASS

`PASS` requires sufficient evidence demonstrating that the observed behavior satisfies the stated requirement.

### FAIL

`FAIL` requires evidence of a contradiction, missing required enforcement, invalid integrity, or observed prohibited behavior.

### UNKNOWN

Use `UNKNOWN` when relevant evidence is unavailable, ambiguous, stale, or insufficient to determine the claim.

### ABSTAIN

Use `ABSTAIN` when the evaluator cannot validly produce the requested judgment under its declared method or evidence policy.

### SILENCE

Use `SILENCE` only when the audited system explicitly enters a defined silence state. Silence SHALL NOT be interpreted as success.

### DECLARED_UNENFORCED

Use `DECLARED_UNENFORCED` when a requirement is explicitly declared but no executable enforcement mechanism is identified.

## 10. Score Honesty

A numeric score SHALL NOT be emitted unless the evaluator records:

- score definition;
- calculation method;
- evidence basis;
- evaluator identity/version;
- target of evaluation.

A default or hard-coded score without evidentiary calculation SHALL be classified as an unsupported score and SHALL NOT substantiate `PASS`.

## 11. Independence

Stumpy SHALL maintain a distinction between:

```text
subject assertion -> claim
Stumpy observation -> evidence
comparison -> judgment
```

A subject component SHALL NOT be the sole authority for a finding concerning its own compliance.

## 12. Canonical Safety

Evidence acquisition SHALL be read-only with respect to canonical state unless an explicitly authorized, isolated, and reversible test requires mutation.

Stumpy SHALL NOT directly modify canonical Constitution, Invariants, or Vault artifacts as part of ordinary auditing.

## 13. Finding Construction

Every finding SHALL reference the evidence records that support it and SHALL be representable using `STUMPY_AUDIT_SCHEMA.yaml`.

A finding without evidence references SHALL be invalid.

The minimum causal chain is:

```text
constitutional requirement
    -> implementation target
    -> expected behavior
    -> observed behavior
    -> evidence
    -> epistemic classification
    -> finding
```

## 14. Reproducibility

Evidence acquisition SHOULD be reproducible from the recorded source revision, target identifier, method, and test fixture.

If reproducibility is impossible, the finding SHALL disclose that limitation and SHALL NOT imply stronger certainty than the evidence warrants.

## 15. Minimum Conformance Tests

A conforming Stumpy evidence layer SHALL demonstrate that it can:

1. bind a source observation to a claim;
2. distinguish source presence from runtime enforcement;
3. reject unsupported PASS claims;
4. classify missing evidence as `UNKNOWN` or `ABSTAIN` as appropriate;
5. identify documentation-only enforcement as `DECLARED_UNENFORCED`;
6. detect invalid lineage;
7. detect fabricated or mismatched source digests;
8. preserve evaluator identity and method;
9. avoid mutating canonical state during ordinary audit;
10. reject a deliberately dishonest evaluator fixture.

## 16. Relationship to Existing Canonical Artifacts

This specification operationalizes the evidence requirements established by:

- `STUMPY_V1_SPEC.md`;
- `STUMPY_CONSTITUTIONAL_INTEGRITY_CONTRACT.md`;
- `STUMPY_CONFORMANCE_SPEC.md`;
- `STUMPY_AUDIT_SCHEMA.yaml`;
- `CANONICAL_CONSISTENCY_MATRIX.md`.

Where these artifacts conflict, the canonical authority hierarchy and constitutional integrity rules govern resolution. Stumpy SHALL report unresolved contradiction rather than silently selecting a convenient interpretation.

## 17. Implementation Boundary

This specification defines the evidence contract, not the complete Stumpy implementation.

The implementation SHALL preserve the separation between:

```text
Evidence acquisition
        !=
Evidence interpretation
        !=
Finding classification
        !=
Canonical mutation
```

That separation is mandatory for audit independence and drift accountability.
