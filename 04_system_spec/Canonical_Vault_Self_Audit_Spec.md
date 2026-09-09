# Canonical Vault Self-Audit Specification

**Version:** 0.1  
**Status:** Canonical specification candidate  
**Authority:** Derived from the Lattice Cognitive Constitution, Lattice Invariants, Vault Chain, Node Model, and Transmission Protocol  
**Purpose:** Define a repeatable mechanism for detecting divergence between repository state and declared canonical state without silently mutating canonical truth.

---

## 1. Principle

The Canonical Vault MUST be able to detect when its declared map of reality differs from repository reality.

The self-auditor is an observation and reconciliation mechanism. It MUST NOT promote its own observations to canonical truth without governed operator action.

Core rule:

> **Observe divergence; do not conceal divergence.**

---

## 2. Audit Loop

The self-audit follows the governed loop:

`OBSERVE → DISTILL → CONSTRAIN → REPORT → OPERATOR DECISION → RE-AUDIT`

The auditor MUST be deterministic for the same repository revision and audit configuration.

---

## 3. Audit Planes

### 3.1 Repository Plane

Enumerate tracked files and directories from the Git repository state.

### 3.2 Canonical Index Plane

Parse `VAULT_INDEX.md` and identify paths declared as canonical, existing, new, or otherwise indexed.

### 3.3 Specification Plane

Verify the presence and declared location of core specifications, including the Node Model and Transmission Protocol where applicable.

### 3.4 Runtime Plane

Compare specification-declared runtime paths with tracked implementation paths when explicit mappings exist.

### 3.5 Test Plane

Detect referenced test suites and distinguish presence from execution status. Presence MUST NOT be reported as passing execution.

### 3.6 Documentation Plane

Detect stale, broken, or contradictory paths in README and canonical index documents.

### 3.7 Hygiene Plane

Detect repository clutter, including tracked backup trees, duplicate artifacts, generated files, and suspicious secret-like material. Hygiene findings are observations, not automatic deletion instructions.

---

## 4. Divergence States

The auditor MUST classify observations using these states:

| State | Meaning |
|---|---|
| `CANONICAL` | Declared and present with no detected contradiction |
| `DISCOVERED` | Present in repository state but not represented by the canonical index |
| `MISSING` | Declared by the canonical index but absent from repository state |
| `RENAMED` | Likely replacement path detected for a missing declaration |
| `STALE` | Declaration exists but its metadata or architectural description is outdated |
| `CONFLICT` | Two authoritative or semi-authoritative sources disagree |
| `REQUIRES_OPERATOR` | Finding cannot be safely resolved automatically |
| `RESOLVED` | Previously observed divergence has a governed resolution record |
| `SILENCE` | Evidence is insufficient for a safe classification |

The auditor MUST NOT collapse `CONFLICT`, `REQUIRES_OPERATOR`, or `SILENCE` into success.

---

## 5. Finding Schema

Each finding SHOULD contain:

```text
finding_id
state
plane
path
related_paths
claim
observation
evidence
severity
recommended_action
requires_operator
repository_revision
```

`repository_revision` binds the observation to a specific Git commit or equivalent immutable repository state.

---

## 6. Severity

| Severity | Meaning |
|---|---|
| `INFO` | Informational divergence with no immediate governance consequence |
| `LOW` | Documentation or hygiene drift |
| `MEDIUM` | Structural synchronization problem |
| `HIGH` | Canonical/spec/runtime contradiction |
| `CRITICAL` | Integrity, lineage, governance, or security boundary is compromised |

Severity MUST describe observed impact, not implementation inconvenience.

---

## 7. Automatic Actions

The self-auditor MAY:

- enumerate repository state;
- compare declared paths against tracked paths;
- identify missing and undiscovered artifacts;
- detect obvious path inconsistencies;
- produce machine-readable and human-readable reports;
- bind findings to a repository revision.

The self-auditor MUST NOT automatically:

- rewrite canonical specifications;
- delete canonical artifacts;
- promote discovered artifacts into canonical status;
- resolve conflicts by guessing;
- report tests as passing unless execution evidence exists;
- suppress findings because they are inconvenient.

---

## 8. Canonical Synchronization Gate

A synchronization operation SHOULD require:

1. a completed self-audit;
2. explicit classification of findings;
3. operator approval for canonical mutations;
4. snapshot/lineage preservation where required;
5. a post-mutation self-audit.

A synchronization cycle is complete only when the post-mutation audit produces no unresolved HIGH or CRITICAL findings, or the operator explicitly records why such findings remain unresolved.

---

## 9. Report Contract

The canonical report SHOULD contain:

- repository revision;
- audit timestamp;
- auditor version;
- total tracked artifacts;
- indexed artifacts;
- undiscovered artifacts;
- missing declarations;
- stale/conflicting declarations;
- hygiene findings;
- unresolved operator actions;
- final synchronization state.

Suggested terminal states:

`SYNCHRONIZED` · `DIVERGENT` · `CONFLICTED` · `REQUIRES_OPERATOR` · `SILENCE`

---

## 10. Lineage

Every generated report is an audit record, not canonical truth.

The report MUST identify the repository revision it observed. A later repository revision invalidates assumptions about current repository state and therefore requires a new audit.

---

## 11. Initial Implementation Scope

Version 0.1 implements the repository/index comparison plane first. Subsequent versions MAY add specification/runtime/test cross-checks and governed remediation.

The initial implementation deliberately favors false-positive visibility over silent omission.

---

**Lineage anchors:** `VAULT_INDEX.md` · `04_system_spec/Lattice_Node_Model.md` · `00_governance/invariants/Lattice_Invariants_v1.md` · `03_vault_pipeline/Vault_Chain_Spec.md`  
**Design principle:** Coherence over elegance; evidence over assumption; reversibility over convenience.
