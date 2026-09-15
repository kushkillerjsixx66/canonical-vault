# Canonical Lattice — Module Registry
**Version:** 2.0
**Status:** CANONICAL PROPOSED UPDATE
**Operator:** JRM-01 | LiminalJermo
**Updated:** 2026-09-15
**Authority:** Derived registry; constitutional authority remains external to this index
**Primary Canonical Source:** `CANON:LATTICE:CGS:1.0` — Unified Canonical Reference, September 1, 2026

---

## 1. Purpose

This registry indexes the current Lattice module architecture, its execution spine, module lineage, handoff position, and governance relationship.

The previous registry (v1.0, 2026-06-17) reflected an earlier architecture and listed SBM as the only execution-spine module. It is superseded by this registry for current module topology.

The current canonical execution spine is a **seven-module pipeline**:

**IDE → CCE → CFC → SBM → IDE-2 → PAM → MTM → Runtime/WDA/Executor**

Canonical pipeline position (`M1–M7`) is authoritative for cross-module references. Internal specification identifiers such as `MOD-IDE-01` are implementation-layer identifiers and must not replace M1–M7 in governance documents, handoff contracts, or CVSI routing.

---

## 2. Execution Spine Registry

### M1 — Intent Decomposition Engine (IDE)

| Field | Value |
|---|---|
| **Module ID** | `IDE` |
| **Pipeline Position** | M1 |
| **Namespace** | `core.intent_decomposition_engine` / `lattice.core.intent_decomposition_engine` |
| **Version** | v0.4.0 |
| **Lineage Anchor** | `CANON:LATTICE:IDE:0.4.0` |
| **Upstream** | Raw Intent Payload (RIP) + optional Context Frame Zero (CF-0) |
| **Downstream** | Governed Intent Graph (IG-G) / DecompositionResult → CCE (M2) |
| **Processing** | INGEST → NORMALIZE → ATOMIZE → STRUCTURE → DRIFT-PRECHECK → HASH → EMIT |
| **Primary Function** | Decompose operator intent into governed, ordered task structures while preserving operator intent and structural integrity. |
| **Canonical Source** | CGS-v1.0 §2.1 |

### M2 — Constraint Cartography Engine (CCE)

| Field | Value |
|---|---|
| **Module ID** | `CCE` |
| **Pipeline Position** | M2 |
| **Namespace** | `core.constraint_cartography_engine` / `lattice.core.constraint_cartography_engine` |
| **Version** | v0.4.0 |
| **Lineage Anchor** | `CANON:LATTICE:CCE:0.4.0` |
| **Upstream** | DecompositionResult from IDE (M1) |
| **Downstream** | ConstraintResolutionResult + CCEValidationReport → CFC (M3) |
| **Primary Function** | Extract, classify, map, and resolve intent-level and task-level constraints, including conflict and scope analysis. |
| **Canonical Source** | CGS-v1.0 §2.2 |

### M3 — Crash-Free Constraint Engine (CFC)

| Field | Value |
|---|---|
| **Module ID** | `CFC` |
| **Pipeline Position** | M3 |
| **Version** | v2.0.0 |
| **Lineage Anchor** | `CANON:LATTICE:CFC:2.0.0` |
| **Upstream** | ConstraintResolutionResult + CCEValidationReport from CCE (M2) |
| **Downstream** | Constraint Package (CP) + CFCReport → SBM (M4) |
| **Processing** | INGEST → NORMALIZE → VALIDATE → VOCABULARY → DRIFT → INTEGRITY → VERDICT → EMIT |
| **Primary Function** | Structural constraint validation, Ω-1 vocabulary enforcement, drift detection, lineage integrity, and governed verdict generation. |
| **Canonical Source** | CGS-v1.0 §2.3 |

### M4 — Semantic Binding Module (SBM)

| Field | Value |
|---|---|
| **Module ID** | `SBM` |
| **Pipeline Position** | M4 |
| **Upstream** | Constraint Package (CP) from CFC (M3) |
| **Downstream** | Semantic Binding Package (SBP) + SemanticBindingReport → IDE-2 (M5) |
| **Processing** | BIND → VALIDATE → DRIFT_PRECHECK → HASH → VERDICT → COMPLIANCE_AUGMENT → EMIT |
| **Primary Function** | Bind governed semantic outputs to canonical vocabulary and produce auditable semantic-binding evidence. |
| **Canonical Source** | CGS-v1.0 §2.4 |

### M5 — Intent Signal Bridge (IDE-2)

| Field | Value |
|---|---|
| **Module ID** | `IDE-2` |
| **Pipeline Position** | M5 |
| **Upstream** | SemanticBindingReport from SBM (M4) |
| **Downstream** | Governed Semantic-Intent Bridge Packet → PAM (M6) |
| **Primary Function** | Re-ground SBM output against the original M1 intent graph, measure semantic displacement, and emit governed drift information before principle alignment. |
| **Architectural Exception** | IDE-2 is the only pipeline module with a read-only backward reference to M1 output. This is an intentional governed exception to the non-adjacent-coupling rule. |
| **Canonical Source** | CGS-v1.0 §2.5 |

### M6 — Principle Alignment Module (PAM)

| Field | Value |
|---|---|
| **Module ID** | `PAM` |
| **Pipeline Position** | M6 |
| **Namespace** | `lattice.core.principle_alignment` |
| **Version** | v0.4.0 |
| **Lineage Anchor** | `CANON:LATTICE:PAM:0.4.0` |
| **Upstream** | Governed Semantic-Intent Bridge Packet from IDE-2 (M5) |
| **Downstream** | Principle-Anchored Intent Graph (PA-IG) + PrincipleAlignmentReport → MTM (M7) |
| **Processing** | INGEST → BIND → VALIDATE → DRIFT → EVIDENCE → EMIT |
| **Primary Function** | Anchor governed intent to the canonical principle hierarchy, validate alignment, detect drift, and emit evidence-bearing principle alignment results. |
| **Primary Gate Set** | G1 Coherence; G2 Reversibility; G3 Epistemic Humility; G4 Permission Boundaries; G5 Auditability; G6 Containment |
| **WDA Output** | 12 WDA Evidence Records per PA-IG in standard operation |
| **Canonical Source** | CGS-v1.0 §2.6 |

### M7 — Mechanism Translation Module (MTM)

| Field | Value |
|---|---|
| **Module ID** | `MTM` |
| **Pipeline Position** | M7 |
| **Upstream** | Principle-Anchored Intent Graph (PA-IG) + PrincipleAlignmentReport from PAM (M6) |
| **Downstream** | Mechanism Execution Contract (MEC) → Runtime/WDA/Executor |
| **Primary Function** | Translate principle-aligned intent into an executable, governed mechanism contract while preserving lineage, compliance, and reversibility information. |
| **Canonical Source** | CGS-v1.0 §2.7 |

---

## 3. Canonical Handoff Chain

| From | Artifact | To |
|---|---|---|
| IDE (M1) | Governed Intent Graph / DecompositionResult | CCE (M2) |
| CCE (M2) | ConstraintResolutionResult + CCEValidationReport | CFC (M3) |
| CFC (M3) | Constraint Package + CFCReport | SBM (M4) |
| SBM (M4) | Semantic Binding Package + SemanticBindingReport | IDE-2 (M5) |
| IDE-2 (M5) | Governed Semantic-Intent Bridge Packet | PAM (M6) |
| PAM (M6) | Principle-Anchored Intent Graph + PrincipleAlignmentReport | MTM (M7) |
| MTM (M7) | Mechanism Execution Contract | Runtime / WDA / Executor |

Every stage produces a governed handoff artifact. Inter-module communication is adjacent by default and transits the governed Bus; direct non-adjacent coupling is forbidden except for the explicitly governed, read-only IDE-2 → M1 reference.

---

## 4. Meta-Module / Governance Layer

The execution spine above is distinct from the Lattice's governance and meta-module layer. These systems should not be conflated with M1–M7.

| Component | Function | Architectural Layer |
|---|---|---|
| **Constitution** | Supreme constitutional boundary and authority source | Constitutional |
| **Vault** | Persistent lineage-anchored memory substrate | Persistence |
| **Veil** | Liminal boundary regulator / containment surface | Runtime / Governance |
| **Vara** | Disconfirmation and weak-signal scanning | Epistemic |
| **Stumpy** | Enforcement, audit, and survival-side governance | Governance |
| **Sentinel** | Gate / enforcement surface where applicable | Governance |
| **WDA** | Walking Data Audit and evidence production | Audit / Evidence |
| **Operator Layer** | Operator interface, posture, authority, and manual | Operator |

These components may participate in or govern the execution spine but are not substitutes for M1–M7.

---

## 5. Canonical Artifacts and Verdict Interface

The execution spine's principal governed artifacts are:

- IDE → Governed Intent Graph (IG-G)
- CCE → ConstraintResolutionResult + CCEValidationReport
- CFC → Constraint Package (CP) + CFCReport
- SBM → Semantic Binding Package (SBP) + SemanticBindingReport
- IDE-2 → Governed Semantic-Intent Bridge Packet
- PAM → Principle-Anchored Intent Graph (PA-IG) + PrincipleAlignmentReport
- MTM → Mechanism Execution Contract (MEC)

The **Canonical Verdict Severity Interface (CVSI)** provides the unified downstream verdict vocabulary:

**PASS / CONDITIONAL / DEGRADED / HALT**

Native module verdicts must translate to CVSI before downstream consumption.

---

## 6. Registry Governance Rules

1. M1–M7 are the authoritative canonical pipeline positions.
2. A module entry must identify its lineage anchor or canonical source.
3. Module specifications may be detailed in separate source documents; this registry indexes them and does not replace their full specifications.
4. The September 1, 2026 CGS-v1.0 consolidation pass supersedes conflicting earlier pipeline references.
5. The registry must not silently collapse IDE-2 into IDE, PAM, or SBM. They are distinct governed stages.
6. Governance/meta-modules must not be represented as execution-spine replacements merely because they existed earlier in the Vault.
7. Changes to this registry require the normal governed proposal / review / merge process.

---

## 7. Drift Resolution

### DR-MOD-001 — Stale Module Registry
**Observed:** Registry v1.0, generated 2026-06-17, listed only SBM as the execution-spine module and reported nine total registered modules.

**Resolution:** Replace the obsolete single-SBM execution representation with the current seven-module canonical execution spine M1–M7 and explicitly separate the execution spine from governance/meta-modules.

### DR-MOD-002 — Pipeline Position Collision
**Observed:** Drive specifications use internal identifiers `MOD-IDE-01` through `MOD-MTM-06` that do not correspond to canonical pipeline position.

**Resolution:** M1–M7 are authoritative for governance and cross-module references. Internal specification identifiers remain implementation-layer metadata only.

### DR-MOD-003 — IDE-2 / PAM Omission
**Observed:** Earlier registry material did not register the post-SBM intent bridge or principle-alignment stage.

**Resolution:** Register IDE-2 as M5 and PAM as M6, preserving their distinct contracts and lineage.

---

## 8. Registry Status

**Current state:** Updated on `chatgpt` branch for governed review.

**Proposed change:** Registry v1.0 → v2.0.

**Required review:** Operator approval before merge to `main`.

**Canonical source authority:** `CANON:LATTICE:CGS:1.0` and its integrated module specifications.

---

*This registry is an index and routing reference. Full module behavior remains governed by the individual module specifications and the Cognitive Governance Substrate.*
