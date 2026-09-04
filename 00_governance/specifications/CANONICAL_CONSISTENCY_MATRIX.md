# CANONICAL CONSISTENCY MATRIX
## Constitutional → Epistemic → Specification → Runtime → Verification

**Artifact ID:** `LAT-CCM-001`  
**Version:** `0.1-draft`  
**Status:** `DRAFT / PRE-CANONICAL`  
**Authority:** Lattice Constitution  
**Scope:** Canonical Vault and governed implementation surfaces  
**Primary Consumer:** Stumpy  
**Assessment Basis:** repository state at commit `15f02b2661c60625fa1c0276c30ff1d5f4dd0345`

> This artifact is a reconciliation instrument. It does not establish new constitutional authority.

---

# 1. Purpose

The Canonical Consistency Matrix establishes a traceable relationship between what the Lattice **claims**, what it **specifies**, what it **implements**, what it **tests**, and what it can **prove**.

A requirement appearing in a canonical document is not evidence that the implementation satisfies that requirement.

The matrix therefore traces each requirement through:

```text
CONSTITUTION
      ↓
INVARIANT
      ↓
EPISTEMIC BASIS
      ↓
SYSTEM SPECIFICATION
      ↓
CONTRACT
      ↓
IMPLEMENTATION
      ↓
TEST
      ↓
EVIDENCE
      ↓
STUMPY VERIFICATION
```

Authority flows downward. Evidence flows upward.

---

# 2. State Model

| State | Meaning |
|---|---|
| `DECLARED` | Requirement exists in an authoritative source. |
| `SPECIFIED` | Architectural realization is defined. |
| `CONTRACTED` | Executable/interface obligation exists. |
| `IMPLEMENTED` | Runtime mechanism exists. |
| `ENFORCED` | Runtime actively prevents or controls violation. |
| `TESTED` | Conformance test exists. |
| `EVIDENCED` | Observable evidence exists. |
| `VERIFIED` | Independent verification establishes conformance. |
| `UNKNOWN` | Evidence is insufficient. |
| `ABSTAIN` | Valid evaluation cannot be performed. |
| `DECLARED_UNENFORCED` | Requirement exists but no enforcement mechanism is established. |
| `DRIFTED` | Implementation or dependent artifact diverges from governing requirement. |
| `CONTRADICTED` | Normative artifacts make incompatible claims. |

These states MUST NOT be collapsed into a single numerical compliance score.

---

# 3. Authority Baseline

The current authority graph explicitly establishes:

```text
1  Constitution              SUPREME
2  Tier-1 Invariants        constitutionally subordinate / binding
3  Amendment Procedure      constitutional procedure
4  Unified System Spec      specification level
5  Contracts                operational contracts
6  Runtime Configuration    parameterization only / no override
7  Executable Runtime       enforcement plane
8  Tests                    verification only
```

Source: `00_governance/authority_graph.yaml`.

This is the baseline against which other artifacts SHALL be reconciled.

---

# 4. Populated Initial Matrix

## CCM-001 — Constitutional Authority

**Requirement:** The Constitution is the supreme authority governing the Lattice.

| Dimension | Current evidence | State |
|---|---|---|
| Authority | `00_governance/constitution/lattice_constitution.md` | `DECLARED` |
| Authority graph | `00_governance/authority_graph.yaml` rank 1 / SUPREME | `SPECIFIED` |
| Runtime | `05_runtime/governance/boundary.py` is designated enforcement plane | `IMPLEMENTED` |
| Tests | `tests/` is explicitly verification-only | `TESTED` |
| Independent verification | Stumpy v1 specification exists | `SPECIFIED` |

**Finding:** The authority hierarchy is explicitly modeled. The principal remaining question is whether every runtime path actually defers to the hierarchy.

**Current status:** `SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-002 — Invariant Authority

**Requirement:** Invariants derive their authority from the Constitution and cannot override it.

| Dimension | Current evidence | State |
|---|---|---|
| Constitution | Article III defines seven absolute constraints | `DECLARED` |
| Invariant artifact | `00_governance/constitution/invariants.md` contains ten invariants | `DECLARED` |
| Authority graph | Rank 2 describes six canonical invariants | `CONTRADICTED` |
| Unified Spec | Section 1 defines five binding invariants | `CONTRADICTED` |
| Module Registry | Existing registry contains another operational invariant set | `DRIFTED / RECONCILIATION REQUIRED` |

**Critical finding:** The repository currently exposes multiple invariant ontologies without a demonstrated parent/derivation mapping.

**Current status:** `CONTRADICTED`

---

## CCM-003 — Invariant Ontology

**Requirement:** Different invariant sets must be explicitly scoped rather than presented as competing canonical authorities.

**Observed sets:**

```text
Constitution Article III       7
Invariants artifact            10
Authority graph description      6
Unified Spec Section 1           5
Operational/module sets         multiple
```

**Finding:** This is not automatically a contradiction if the sets represent different layers. The repository currently does not provide sufficient explicit parentage to establish that interpretation.

**Required remediation:** Establish:

```text
constitutional invariants
        ↓
epistemic / governance invariants
        ↓
operational invariants
        ↓
module invariants
```

**Current status:** `CONTRADICTION / HIGH PRIORITY RECONCILIATION`

---

## CCM-004 — Lineage Is Mandatory

**Requirement:** Every meaningful action, transformation, governance change, or mutation emits lineage.

**Constitutional sources:**
- Article I.4
- Article III.1
- Article VI.3
- `00_governance/constitution/invariants.md`

**Implementation surfaces:**
- governance runtime
- Vault runtime
- governance lineage
- snapshots / audit artifacts

**Finding:** Lineage is strongly declared and represented architecturally. Universal runtime coverage remains an implementation-verification question.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-005 — Canon Immutability

**Requirement:** Canonized artifacts cannot be edited or overwritten; replacement occurs through governed supersession/archive semantics.

**Constitutional sources:**
- Article III.2
- Article VI.3
- Invariants artifact #2

**Runtime target:** Vault implementation.

**Finding:** Canon immutability is clearly specified. The consistency matrix must verify every mutation path, not merely the primary Vault API.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-006 — Explicit Intent

**Requirement:** No governed action may occur without explicit intent attributable to an operator/process identity.

**Sources:**
- Constitution Article I.4
- Constitution Article VI.2
- Invariants artifact #3

**Runtime targets:** governance boundary, request/evaluation path, Vault writes.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-007 — Real Boundaries

**Requirement:** Modules may not cross declared domains except through governed interfaces, contracts, or protocols.

**Sources:**
- Constitution Article II.2–3
- Invariants artifact #4
- authority graph

**Runtime targets:** governance boundary and module interfaces.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-008 — Drift Accountability

**Requirement:** Drift must be detectable, measurable, logged, and recoverable when possible.

**Sources:**
- Constitution Article III.5
- Invariants artifact #5
- `00_governance/drift_domains.yaml`

**Runtime targets:** governance engine, audit path, Stumpy.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-009 — Reversibility

**Requirement:** Actions should be reversible where possible; irreversible actions require explicit handling and lineage.

**Sources:**
- Constitution Article III.6
- Invariants artifact #6
- Unified Spec G3

**Important semantic conflict:** The Constitution calls reversibility preferred and permits governed irreversible actions. The Unified Spec describes reversibility as non-negotiable and says all actions must be roll-backable, with no emergency suspension.

**Current status:** `SEMANTIC_CONFLICT / HIGH PRIORITY RECONCILIATION`

---

## CCM-010 — Governance Supersedes Runtime

**Requirement:** Runtime behavior must defer to governance; conflicts resolve in favor of governance.

**Sources:**
- Constitution Article III.7
- Invariants artifact #7
- authority graph runtime rank 6–7

**Current status:** `DECLARED / SPECIFIED / ENFORCEMENT VERIFICATION REQUIRED`

---

## CCM-011 — Operator Identity

**Requirement:** Operator identity is stable and cannot be modified or impersonated by runtime.

**Sources:**
- Constitution Article I
- Invariants artifact #8

**Runtime target:** operator authentication / governance boundary.

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-012 — Governed Visibility

**Requirement:** Visibility is controlled by declared governance rules; redaction must preserve underlying truth and lineage.

**Sources:**
- Invariants artifact #9
- Veil specifications

**Current status:** `DECLARED / SPECIFIED / ENFORCEMENT VERIFICATION REQUIRED`

---

## CCM-013 — Archive Is Not Deletion

**Requirement:** Archival does not erase truth, lineage, or responsibility.

**Sources:**
- Invariants artifact #10
- Vault/archive architecture

**Current status:** `DECLARED / SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-014 — Evidence Integrity

**Requirement:** Empirical claims must be distinguishable from evidence and subject to qualification and lineage.

**Target surfaces:**
- epistemic substrate
- evidence classes
- signal qualification
- empirical doctrine
- Vara outputs
- Stumpy findings

**Current status:** `SPECIFICATION RECONCILIATION REQUIRED`

---

## CCM-015 — Score Honesty

**Requirement:** A score must expose sufficient evaluator, method, evidence, and semantic metadata to justify its interpretation.

**Required Stumpy behavior:** Unsupported precision MUST resolve to `UNKNOWN` or `ABSTAIN`, never fabricated compliance.

**Current status:** `SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-016 — Silence as State

**Requirement:** Silence, abstention, and unknown states must remain distinguishable from PASS.

**Sources:**
- Unified Spec silence invariant
- governance outcome model
- Stumpy specification

**Current status:** `SPECIFIED / IMPLEMENTATION VERIFICATION REQUIRED`

---

## CCM-017 — Constitutional Halt on Violation

**Requirement:** A subsystem violating the Constitution must halt execution, emit a governance fault, log lineage, and escalate.

**Constitutional source:** Article VIII.

**Conflicting artifact:** `00_governance/audit_policy.yaml` explicitly sets:

```yaml
invariant_enforcement:
  halt_on_breach: false
```

and specifies surface/log behavior rather than pipeline halt.

**Finding:** Direct enforcement contradiction.

**Current status:** `CRITICAL_CONTRADICTION`

---

## CCM-018 — Authority Scope of Unified Specification

**Requirement:** The Unified Specification is subordinate to constitutional authority.

**Authority graph:** explicitly places Unified Spec at rank 4 beneath Constitution and invariants.

**Unified Spec:** declares itself the "single authoritative reference" and says conflicts with prior artifacts are governed by the Unified Spec.

**Finding:** The two claims can coexist only if "authoritative" is explicitly scoped to integrated system specification and subordinate to the Constitution/Invariant hierarchy. Current wording is ambiguous and potentially contradictory.

**Current status:** `AUTHORITY_SCOPE_RECONCILIATION_REQUIRED`

---

## CCM-019 — Stumpy Role Boundary

**Requirement:** Stumpy must independently verify integrity without becoming a new constitutional sovereign.

**Current specification:**
- `00_governance/specifications/STUMPY_CONSTITUTIONAL_INTEGRITY_CONTRACT.md`
- `00_governance/specifications/STUMPY_V1_SPEC.md`
- `04_system_spec/modules/Stumpy_Spec.md`

**Observed issue:** Multiple Stumpy specifications exist and must be reconciled into one authority chain.

**Current status:** `SPECIFIED / CROSS-SPEC RECONCILIATION REQUIRED`

---

## CCM-020 — Stumpy Recursive Auditability

**Requirement:** Stumpy itself must expose enough metadata to be independently audited.

**Required fields:** evaluator identity/version, method, evidence sources, finding lineage, timestamp, decision.

**Current status:** `SPECIFIED / IMPLEMENTATION NOT YET VERIFIED`

---

# 5. Critical Contradiction Register

| ID | Domain | Source A | Source B | Finding | Severity | Resolution State |
|---|---|---|---|---|---|---|
| `CR-001` | Invariants | Constitution | Unified Spec / Invariants / Authority Graph | Multiple invariant sets lack explicit hierarchy | CRITICAL | OPEN |
| `CR-002` | Halt | Constitution Article VIII | `audit_policy.yaml` | Constitution requires halt; policy says `halt_on_breach: false` | CRITICAL | OPEN |
| `CR-003` | Reversibility | Constitution / Invariants | Unified Spec | Preferred/conditional reversibility vs non-negotiable rollback semantics | HIGH | OPEN |
| `CR-004` | Authority | Authority Graph | Unified Spec | Scoped specification authority is not expressed consistently | HIGH | OPEN |
| `CR-005` | Stumpy | Governance Stumpy specs | System Stumpy spec | Multiple normative descriptions require reconciliation | HIGH | OPEN |

---

# 6. Current Enforcement Coverage

This table is intentionally incomplete until runtime and test paths are exhaustively mapped.

| Requirement | Declared | Specified | Contracted | Implemented | Enforced | Tested | Evidence | Stumpy |
|---|---|---|---|---|---|---|---|---|
| Constitutional authority | ✓ | ✓ | ? | ? | ? | ✓ | ? | ? |
| Invariant authority | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Lineage | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Canon immutability | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Explicit intent | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Boundaries | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Drift | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Reversibility | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Governance supremacy | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Operator identity | ✓ | ✓ | ? | ✓* | ? | ? | ? | ? |
| Visibility | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Archive semantics | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Evidence integrity | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Score honesty | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Silence | ✓ | ✓ | ? | ? | ? | ? | ? | ? |
| Constitutional halt | ✓ | ✓ | ✓ | **CONFLICT** | **FAIL** | ? | ? | ? |

`*` indicates an implementation surface exists, not that universal enforcement has been proven.

`?` means not yet independently established by this matrix.

---

# 7. Required Reconciliation Order

The matrix identifies the following order as the minimum safe reconciliation sequence:

```text
1. Invariant ontology
        ↓
2. Authority terminology and scope
        ↓
3. Halt / enforcement semantics
        ↓
4. Reversibility semantics
        ↓
5. Stumpy role and specification consolidation
        ↓
6. Runtime enforcement mapping
        ↓
7. Conformance test mapping
        ↓
8. Evidence mapping
        ↓
9. Stumpy independent verification
```

Do not canonicalize downstream artifacts while upstream authority or semantics remain unresolved.

---

# 8. Evidence Rules

### E1 — Documentation is not evidence of execution

A document establishes what the system says. It does not establish what the runtime did.

### E2 — Test scope is bounded

A passing test establishes only the behavior actually exercised.

### E3 — Observation is contextual

Runtime evidence establishes observed behavior within the scope of the observation.

### E4 — Stumpy is evidence-producing, not authority-producing

A Stumpy finding is an independently evaluated result. It does not amend constitutional authority.

### E5 — Missing evidence remains missing

`UNKNOWN` MUST NOT silently become `PASS`.

### E6 — Numeric scores require provenance

No score may imply more precision than its evaluator, evidence, and methodology support.

---

# 9. Canonical Consistency States

The completed matrix SHALL classify requirements using composite states where appropriate:

- `CANONICALLY_ALIGNED`
- `CANONICALLY_DECLARED`
- `IMPLEMENTATION_DRIFT`
- `ENFORCEMENT_GAP`
- `EVIDENCE_GAP`
- `AUTHORITY_CONFLICT`
- `SEMANTIC_CONFLICT`
- `LINEAGE_GAP`
- `VERIFICATION_GAP`
- `CRITICAL_CONSTITUTIONAL_FAILURE`

These states are descriptive, not authority-bearing.

---

# 10. Completion Criteria

The matrix is not complete merely because every row has a file reference.

Completion requires:

1. every constitutional requirement identified;
2. every subordinate invariant mapped;
3. every requirement mapped to specification;
4. implementation mapped where applicable;
5. enforcement mechanism identified;
6. conformance tests identified;
7. evidence requirements identified;
8. contradictions resolved or explicitly registered;
9. lineage requirements mapped;
10. Stumpy verification paths established.

---

# 11. Non-Canonical Status

This document remains `DRAFT / PRE-CANONICAL` until:

- repository-wide mapping is complete;
- contradictions are dispositioned;
- authority relationships are ratified;
- implementation and test mappings are independently verified.

It MUST NOT be used to override existing canonical artifacts while reconciliation remains open.

---

# 12. Governing Principle

> **The Vault preserves canonical knowledge. The Consistency Matrix preserves the relationship between canonical claims and observable implementation. Stumpy verifies that relationship.**

The objective is not to force every artifact to agree by deleting inconvenient differences.

The objective is to determine which differences represent legitimate specialization and which represent architectural drift, contradiction, or unenforced intent.
