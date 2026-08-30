# STUMPY v1.0 SPECIFICATION

**ID:** LAT-STUMPY-001  
**Status:** PROPOSED  
**Layer:** Governance / Verification  
**Mutation Authority:** NONE

## 1. System Role

Stumpy is the Lattice Constitutional Integrity Auditor. It independently evaluates whether declared constitutional properties are supported by observable evidence.

Stumpy is not a sovereign authority, general governance engine, canonical writer, or autonomous constitutional editor.

## 2. Inputs

Stumpy accepts governed audit targets including:

- Constitution and amendments
- invariant definitions
- authority graph
- contracts and specifications
- runtime source/configuration
- Vault state
- lineage and transition records
- governance decisions and receipts
- evaluator definitions
- test evidence
- MCP-facing governance surfaces

## 3. Pipeline

`RESOLVE → CLAIMS → EVIDENCE → COMPARE → VERIFY → CLASSIFY → REPORT → ESCALATE`

### RESOLVE
Resolve authoritative versions, paths, refs, and digests.

### CLAIMS
Extract normative and operational claims from authoritative artifacts.

### EVIDENCE
Collect implementation and runtime evidence relevant to each claim.

### COMPARE
Compare declared requirements against observed behavior.

### VERIFY
Test evidence sufficiency, lineage, source identity, enforcement, and authority.

### CLASSIFY
Assign an explicit epistemic state and severity.

### REPORT
Produce immutable, evidence-bound findings.

### ESCALATE
Apply constitutional escalation requirements for critical violations.

## 4. Audit Matrix

| Domain | Required Question |
|---|---|
| Coherence | Does observed behavior contradict governing context? |
| Reversibility | Can state transitions be traced and reversed/canonized as required? |
| Lineage | Is the full action chain bound to evidence? |
| Source Integrity | Is claimed canonical content actually authoritative and digest-consistent? |
| Score Honesty | Does every score have defensible provenance and method? |
| Drift | Does implementation remain aligned with declared specification? |
| Silence | Are silence, abstention, and uncertainty preserved explicitly? |
| Operator Boundary | Is sovereign authority authenticated and protected? |
| Authority | Does actual authority match the declared hierarchy? |
| Constraint Enforcement | Is every mandatory constraint actually enforced rather than merely documented? |

## 5. Decision Semantics

Stumpy MUST NOT collapse audit results into an unsupported percentage.

Primary result:

`CONFORMANT | NON_CONFORMANT | INDETERMINATE`

Finding states:

`PASS | FAIL | UNKNOWN | ABSTAIN | SILENCE | DECLARED_UNENFORCED`

## 6. Critical Rules

1. No evidence, no PASS.
2. No lineage on required mutation, FAIL.
3. No evaluator provenance for a score, ABSTAIN.
4. Documentation without enforcement, DECLARED_UNENFORCED.
5. Silence is not success.
6. A subordinate component cannot establish its own constitutional authority.
7. Stumpy cannot alter the evidence it audits.
8. Stumpy findings cannot silently disappear.

## 7. Outputs

A Stumpy audit MUST produce:

- audit_id
- target identity
- repository/ref
- canonical constitution digest
- specification digest
- evaluator versions
- findings
- evidence references
- lineage references
- escalation state
- overall determination

## 8. Security and Integrity Boundary

Stumpy is read-only against canon. Any quarantine, fault, escalation, or remediation request MUST pass through the existing governed execution boundary.

## 9. Recursive Verification

Stumpy MUST expose enough provenance to permit independent verification of its own findings. Its implementation MUST NOT rely on a self-reported compliance flag as its primary evidence.

## 10. Implementation Direction

The existing lightweight `05_runtime/stumpy.py` implementation is insufficient for this specification. It should be treated as a legacy primitive until replaced or wrapped by a contract-compliant implementation.
