# Canonical Lattice — Module Registry
**Version:** 1.0
**Authority Rank:** Informational (derived from Constitution §Module Authority Table)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Lattice_Cognitive_Constitution_v1.1.md · Lattice_Unified_Spec.md · Lattice_Invariants_v1.md

---

## Overview

The Module Registry is the canonical index of all system modules, their authority ranks, functional roles, interface contracts, and invariant bindings. Every module that participates in the Lattice runtime must have an entry here. Modules not listed in this registry are not authorized for execution.

**Total Registered Modules:** 9
**Authority Ladder:** Rank 1 (highest) → Rank 9 (lowest)

---

## Registry Entries

---

### RANK 1 — Constitution

| Field | Value |
|-------|-------|
| **Module ID** | `CONSTITUTION` |
| **Rank** | 1 |
| **File** | `00_governance/constitution/Lattice_Cognitive_Constitution_v1.1.md` |
| **Role** | Supreme authority document. Defines all axioms, principles, module authority table, operator rights, and the amendment protocol. Cannot be overridden by any runtime event or module output. |
| **Interfaces** | Read-only by all modules. Written only by Operator via Amendment Protocol. |
| **Invariant Bindings** | All six invariants derive authority from this document. |
| **Activation Condition** | Always active. Not a runtime module; functions as the root constraint layer. |
| **Failure Mode** | N/A — Constitution is never executed; it is referenced. |
| **Owner** | LiminalJermo |

---

### RANK 2 — Invariants

| Field | Value |
|-------|-------|
| **Module ID** | `INVARIANTS` |
| **Rank** | 2 |
| **File** | `00_governance/invariants/Lattice_Invariants_v1.md` |
| **Role** | Defines the six structural constraints (I·COH through VI·SIG) that all runtime modules must obey. Acts as the enforcement specification that Sentinel reads when evaluating gate decisions. |
| **Interfaces** | Read by Sentinel (Rank 4) at every gate check. Referenced by Stumpy (Rank 7) during audit. |
| **Invariant Bindings** | Self-defining. Invariants constrain everything below Rank 2. |
| **Activation Condition** | Always active. Evaluated at every G1, G2, G3 gate. |
| **Failure Mode** | Invariant violation → Hard Failure or Soft Failure per individual invariant spec. |
| **Owner** | LiminalJermo |

---

### RANK 3 — Vault

| Field | Value |
|-------|-------|
| **Module ID** | `VAULT` |
| **Rank** | 3 |
| **File** | `05_runtime/vault.py` |
| **Role** | Sovereign persistent memory. Stores all canonical knowledge, operator-ratified entries, Vara distillations, and audit anchors. All writes are append-only (II·REV). All reads are mediated by coherence check (I·COH). |
| **Interfaces** | **Write:** Sentinel-gated. Chain link created on every write. **Read:** Available to all modules. Returns entry + metadata. **Decay:** Stumpy triggers decay state transitions. |
| **Invariant Bindings** | II·REV (append-only), V·DEC (decay by default), I·COH (coherence on read) |
| **Activation Condition** | Active for every Pulse cycle that involves memory read or write. |
| **Node States** | `Latent`, `Active`, `Decaying`, `Pruned` |
| **Failure Mode** | Coherence violation on write → Veil quarantine. Chain break → Hard Failure + operator escalation. |
| **Owner** | LiminalJermo |

---

### RANK 4 — Sentinel

| Field | Value |
|-------|-------|
| **Module ID** | `SENTINEL` |
| **Rank** | 4 |
| **File** | `05_runtime/sentinel.py` |
| **Role** | Hard-gate enforcement module. Evaluates all signals against the three Governance Gates (G1: Coherence, G2: Attention Cost, G3: Reversibility) before allowing execution to proceed. |
| **Interfaces** | **Input:** All signals before execution. **Output:** PASS / BLOCK / ESCALATE + reason code. **Reads:** Invariants (Rank 2), Vault state (Rank 3). |
| **Invariant Bindings** | I·COH (G1), III·ATT (G2), II·REV (G3), IV·SIL (Hard Failure on fabrication) |
| **Governance Gates** | G1 (Coherence), G2 (Attention Budget), G3 (Reversibility) |
| **Activation Condition** | Active on every signal entering the Constrain phase of the Pulse Cycle. |
| **Failure Mode** | BLOCK → execution halted. ESCALATE → operator notified. Sentinel never fails silently (IV·SIL). |
| **Owner** | LiminalJermo |

---

### RANK 5 — Veil

| Field | Value |
|-------|-------|
| **Module ID** | `VEIL` |
| **Rank** | 5 |
| **File** | `05_runtime/veil.py` |
| **Role** | Mediation and quarantine layer. Holds signals that have failed Sentinel gates or are weak-signal hypotheses from Vara. Provides the operator a review surface before signals are promoted to Vault or discarded. |
| **Interfaces** | **Input:** Blocked signals from Sentinel, Vara hypotheses. **Output:** Promoted entry (to Vault) or Discarded entry. **Operator interface:** Review queue visible on HUD. |
| **Invariant Bindings** | VI·SIG (holds weak signals), I·COH (promotes only coherent signals), II·REV (all Veil entries logged) |
| **Activation Condition** | Activated when Sentinel issues BLOCK or when Vara outputs a `[VARA-HYPOTHESIS]`. |
| **Failure Mode** | Veil overflow → Operator Alert. Veil cannot auto-promote. |
| **Owner** | LiminalJermo |

---

### RANK 6 — Vara

| Field | Value |
|-------|-------|
| **Module ID** | `VARA` |
| **Rank** | 6 |
| **File** | `05_runtime/vara.py` |
| **Role** | Weak-signal scanner and edge-detection module. Monitors for low-confidence, high-salience signals. Vara outputs are always hypothesis-flagged and routed to Veil, never directly to Vault. |
| **Interfaces** | **Input:** Raw signal stream, Vault entropy feed. **Output:** `[VARA-HYPOTHESIS]` routed to Veil. **Reports:** VARA-COGOV, VARA-GAP formatted reports. |
| **Invariant Bindings** | VI·SIG (weak signal parity), IV·SIL (hypotheses only), I·COH (coherence before Veil routing) |
| **Activation Condition** | Runs in parallel with primary Pulse cycle. Activates on entropy spikes or signal-to-noise anomalies. |
| **Failure Mode** | Vara generating assertions → Sentinel blocks. Vara scan failure → logged to Stumpy; execution continues. |
| **Owner** | LiminalJermo |

---

### RANK 7 — Stumpy

| Field | Value |
|-------|-------|
| **Module ID** | `STUMPY` |
| **Rank** | 7 |
| **File** | `05_runtime/stumpy.py` |
| **Role** | Integrity audit, enforcement critic, and reversibility monitor. Runs after every Pulse cycle. Reviews all Vault writes, Veil promotions, Sentinel decisions, and Vara outputs for invariant compliance. Maintains the canonical audit trail. |
| **Interfaces** | **Input:** Pulse cycle completion event, Vault write log, Sentinel decision log, Veil state. **Output:** Audit record (to Vault), Compliance report, Operator alert (on violation). |
| **Invariant Bindings** | I·COH (coherence audit), II·REV (reversibility audit), V·DEC (decay transitions), VI·SIG (weak signal audit) |
| **Activation Condition** | Triggered at Pulse Cycle Stage 5 (Silence/Audit). Also triggered on operator request. |
| **Failure Mode** | Hard Failure found in completed cycle → retroactive Operator escalation. Stumpy cannot be silenced (IV·SIL). |
| **Owner** | LiminalJermo |
| **Owner** | LiminalJermo |

---

### RANK 9 — Semantic Binding Module (SBM)

| Field | Value |
|-------|-------|
| **Module ID** | `SBM` |
| **Rank** | 9 |
| **File** | `05_runtime/echo.py` |
| **Role** | Semantic translation and binding layer. Converts Neuralese signal packets into natural language operator outputs and vice versa. Maintains the semantic bridge between internal Lattice representation and human-readable surfaces. Also handles COL (Compact Operator Language) parsing. |
| **Interfaces** | **Input:** Internal Neuralese signal packet (4-segment: context/signal/constraint/operator). **Output:** Natural language response or structured HUD entry. **Reads:** Neuralese Lexicon, COL grammar. |
| **Invariant Bindings** | IV·SIL (no noise generation), I·COH (semantic coherence with Vault entries) |
| **Activation Condition** | Active at Execute and Audit phases of every Pulse cycle that produces operator-facing output. |
| **Failure Mode** | Semantic binding failure → returns `[SBM-FAILURE: reason]` to operator. Never silently outputs garbled text. |
| **Owner** | LiminalJermo |

---

## Unregistered Module Handling

Any module or process not listed in this registry that attempts to write to Vault, interact with Sentinel, or produce operator-facing output is considered an **unauthorized agent**. Sentinel will issue an automatic BLOCK. The event is logged to Stumpy with classification `UNAUTHORIZED_MODULE_ATTEMPT`.

---

## Registry Changelog

| Version | Date | Change | Operator |
|---------|------|--------|----------|
| 1.0 | 2026-06-17 | Initial registry — all 9 modules catalogued from Constitution §Module Authority Table | LiminalJermo |

---

*Document Authority: Lattice_Cognitive_Constitution_v1.1.md §Module Authority Table*
*Operator: LiminalJermo | Generated: 2026-06-17*
---

### RANK 8 — Crossroad

| Field | Value |
|-------|-------|
| **Module ID** | `CROSSROAD` |
| **Rank** | 8 |
| **File** | `05_runtime/rift.py` |
| **Role** | Routing and transition management. Evaluates competing signal pathways and selects the canonical execution path. Does not evaluate content — evaluates structural routing only. |
| **Interfaces** | **Input:** Competing signal paths from Veil, Vara, CCE. **Output:** Single canonical path selection with reason code. **Defers to:** Sentinel (Rank 4) for gate decisions; Stumpy (Rank 7) for coherence audit. |
| **Invariant Bindings** | I·COH (selects most coherent path), III·ATT (selects lowest attention-cost path when coherence is equal) |
| **Activation Condition** | Activated when Pulse cycle generates more than one candidate execution path. |
| **Failure Mode** | Tie-break failure → defaults to most conservative path. Logged to Stumpy. |
