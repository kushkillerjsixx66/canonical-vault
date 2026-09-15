# Semantic Binding Module (SBM) — Canonical Specification

**Module ID:** `M4`
**Module Name:** Semantic Binding Module (SBM)
**Pipeline Position:** M4
**Canonical Version:** v1.0 (CGS-v1.0 consolidation reference)
**Lineage Anchor:** `CANON:LATTICE:CGS:1.0` / SBM module card
**Status:** ACTIVE — canonical execution-spine specification

> **Authority note:** This specification supersedes the June 17, 2026 Rank-9 SBM model. The M1–M7 pipeline position is authoritative for cross-document references. Legacy authority-rank language is historical and must not be used as the active module hierarchy.

## Role

SBM is the fourth execution-spine module. It receives the **Constraint Package (CP)** from CFC (M3), performs governed semantic binding, and emits a **Semantic Binding Package (SBP)** plus **SemanticBindingReport** to IDE-2 (M5).

SBM is a processing module in the execution spine. It is not the sole natural-language output authority, and it does not occupy Rank 9 in an active nine-rank module hierarchy.

## Pipeline Handoff

```text
M3 CFC
  ↓ Constraint Package (CP)
M4 SBM
  ↓ Semantic Binding Package (SBP) + SemanticBindingReport
M5 IDE-2
```

### Upstream Input

**Constraint Package (CP)** from CFC (M3), carrying governed constraints, CFC verdict information, and lineage integrity.

### Downstream Output

**Semantic Binding Package (SBP)** + **SemanticBindingReport** → IDE-2 (M5).

The SBP is a governed handoff artifact. It carries binding evidence, not merely a list of bound terms.

## Processing Phases

```text
BIND → VALIDATE → DRIFT_PRECHECK → HASH → VERDICT → COMPLIANCE_AUGMENT → EMIT
```

## Core Capabilities

1. **Vocabulary binding** using n-gram token extraction with the canonical cascade:
   `exact → synonym → deprecated → unbound`.
2. **Ω-0 / Ω-1 invariant enforcement**, with five invariant checks per Intent Atom.
3. **Ω-4 drift prechecks** covering:
   - `vocabulary_drift`
   - `semantic_drift`
   - `binding_decay`
4. **Triple-hash integrity** using lineage, binding, and full-integrity hashes.
5. **Compliance marker augmentation** for the canonical compliance surfaces identified by the CGS reference, including EU AI Act Art. 11 and ISO 42001 6.1.2.
6. **CVSI translation** of the module-native verdict into the canonical downstream verdict interface.

## Verdict Model

SBM retains its domain-native binding tiers for diagnostic precision:

| SBM Native Tier | Binding Coverage | CVSI Canonical Tier |
|---|---:|---|
| BOUND | ≥ 90% | PASS |
| PARTIAL | ≥ 60% | CONDITIONAL |
| DEGRADED | ≥ 30% | DEGRADED |
| REJECTED | < 30% | HALT |

Downstream consumers use **CVSI** rather than relying on module-native verdict vocabulary.

## M4 → M5 Contract

The canonical handoff is **SBM → IDE-2**, not SBM → PAM.

Required handoff semantics:

- `binding_coverage`
- `drift_flags[]`
- `verdict_SBM`
- `lineage_hash`

The handoff boundary is **post-binding**. Vocabulary invariants and the binding floor apply at this boundary.

The canonical artifact name is **Semantic Binding Package (SBP)**. A `SemanticBindingReport` accompanies the package as the reporting surface for the M4 decision.

## Relationship to IDE-2

IDE-2 (M5) re-grounds SBM's semantic output against the original M1 Governed Intent Graph. SBM therefore must preserve sufficient binding evidence and lineage for IDE-2 to measure semantic displacement rather than receiving an opaque semantic transformation.

SBM does not perform the M5 coherence comparison itself. That comparison belongs to IDE-2.

## Invariant and Governance Bindings

SBM operates within the canonical governance regime and must preserve:

- vocabulary integrity;
- semantic binding coherence;
- drift visibility;
- lineage integrity;
- reversibility and auditability requirements inherited from upstream governance;
- CVSI-compatible verdict propagation.

The six governance invariants G1–G6 are the primary binding gate at PAM. SBM's role is to provide a semantically grounded, auditable artifact for the downstream bridge and principle-alignment stages.

## Failure Conditions

At minimum, the following conditions are governed and must remain observable downstream:

- insufficient binding coverage;
- vocabulary drift;
- semantic drift;
- binding decay;
- lineage/hash integrity failure;
- compliance-marker loss;
- downstream handoff schema mismatch.

A failure must not be silently converted into an apparently valid SBP.

## Historical Compatibility

The former June 17, 2026 SBM specification described SBM as Rank 9 in a nine-rank authority table, placed it after Crossroad, and made it the exclusive natural-language operator output boundary. Those references belong to the pre-consolidation architecture.

They are superseded by **CGS-v1.0, dated September 1, 2026**, which defines SBM as **M4** and places **IDE-2 as M5 between SBM and PAM**.

Historical documents may remain preserved for lineage, but active governance documents and cross-module contracts must use the M1–M7 model.

## Canonical References

- `04_system_spec/MODULE_REGISTRY.md`
- `contracts/sbm_ide2.json`
- `contracts/ide2_pam.json`
- `contracts/sbm_pam.json` — retained as a deprecated compatibility record only
- `CANON:LATTICE:CGS:1.0`

*Reconciled against the Unified Canonical Reference — September 1, 2026.*
