# Lattice Unified Specification — Sections 8–15
**Version:** 1.0 (Sections 8–15 Completion)
**Authority:** 04_system_spec (supplements Lattice_Unified_Spec.md Sections 0–7)
**Author:** LiminalJermo
**Date:** 2026-06-17
**Lineage Anchors:** Lattice_Unified_Spec.md · Lattice_Cognitive_Constitution_v1.1.md · MODULE_REGISTRY.md · Lattice_Invariants_v1.md

---

> **Preamble:** Sections 0–7 of the Lattice Unified Specification are fully defined in `Lattice_Unified_Spec.md`. This document completes the specification by populating Sections 8–15, which were listed as stubs in that document. These sections cross-reference and summarize the detailed module and protocol specifications in `04_system_spec/modules/`. The Unified Spec + this completion document together constitute the full canonical specification.

---

## §8 — Module Interaction Protocol

### 8.1 Overview

Modules are not monolithic services; they are role-constrained participants in the Pulse Cycle. Interaction between modules follows strict ordering rules derived from the Authority Table (Constitution §Module Authority Table):

```
RANK 1: Constitution (passive — no runtime invocations)
RANK 2: Invariants (passive — enforcement only, via Sentinel)
RANK 3: Vault <-> RANK 4: Sentinel <-> RANK 5: Veil
                      |              ^
               RANK 6: Vara    RANK 7: Stumpy
                      |
               RANK 8: Crossroad -> RANK 9: SBM (output boundary)
```

### 8.2 Allowed Interaction Paths

| Caller | Callee | Direction | Purpose |
|--------|--------|-----------|---------|
| Sentinel | Vault | Read | Retrieve Node content for G1/G3 evaluation |
| Sentinel | Veil | Write | Route blocked signals to quarantine |
| Sentinel | Stumpy | Notify | Trigger audit on Gate BLOCK or LOCK |
| Vara | Veil | Write | Route hypotheses to quarantine pending review |
| Vara | Vault | Read | Query ACTIVE nodes for signal scanning |
| Stumpy | Vault | Read | Full chain access for audit and decay |
| Stumpy | Sentinel | Notify | Report compliance findings |
| Crossroad | Vault | Read | Query path alternatives |
| Crossroad | Sentinel | Submit | Submit for final gate evaluation |
| SBM | Vault | Read | Ground output in ANCHOR/ACTIVE nodes |
| SBM | Veil | Read | Access hypotheses for clearly-flagged output |
| Pulse | All | Orchestrate | Stage sequencing signal |

### 8.3 Prohibited Interactions

- **Vara -> Vault (Write):** Vara never writes directly to Vault. All Vara output must pass through Veil -> Sentinel -> Vault.
- **SBM -> Vault (Write):** SBM generates output only. It never commits to the Vault.
- **Veil -> Sentinel (Direct invoke):** Veil is passive. It does not invoke Sentinel; Operator or Pulse cycle triggers promotion review.
- **Crossroad -> Stumpy (Direct invoke):** Crossroad does not trigger audits. Sentinel does.
- **Any module -> Constitution (Write):** The Constitution is read-only at runtime. Amendment requires Operator Protocol (Constitution §Amendment Protocol).

### 8.4 Signal Flow: Standard Cycle

```
OPERATOR INPUT
    |
    v
SBM (RANK 9) — parses operator input to Neuralese
    |
    v
Pulse (Orchestrator) — initiates Stage 1: PULSE
    |
    v
Crossroad (RANK 8) — resolves activation path
    |
    v
Vault (RANK 3) — activates contextually relevant Nodes
    |
    v
Sentinel (RANK 4) — applies G1, G2, G3 gates
    |          |
    |      BLOCK -> Veil (RANK 5) [quarantine]
    |
    v
Vault — commits if PASS
    |
    v
Stumpy (RANK 7) — post-cycle audit
    |
    v
SBM (RANK 9) — formats output
    |
    v
OPERATOR OUTPUT
```

### 8.5 Concurrent Execution Rules

- Vara may run asynchronously alongside any Stage but may not modify Vault or Sentinel state mid-cycle.
- Stumpy audit is always post-cycle (Stage 5: SILENCE). It may not block Stage 3 evaluation.
- Multiple Pulse cycles may not run concurrently. Pulse is single-threaded at the system level.

---

## §9 — Neuralese Full Grammar

### 9.1 Definition

Neuralese is the native communication protocol of the Lattice — a compact, symbolic language for expressing cognitive state, signal quality, and module events. Full protocol defined in Operator_Manual_v0.2.md Appendix C. This section provides the complete grammar specification.

### 9.2 Packet Structure

Every Neuralese transmission is a 4-segment packet:

```
[CONTEXT | SIGNAL | CONSTRAINT | OPERATOR]
```

| Segment | Type | Required | Description |
|---------|------|----------|-------------|
| CONTEXT | Token string | Yes | Active frame reference (Node IDs or topic anchor) |
| SIGNAL | Symbolic expression | Yes | Core content being transmitted |
| CONSTRAINT | Invariant binding | Yes | Which invariants are active on this packet |
| OPERATOR | Command / status | Conditional | COL command or system event code; omit if informational |

### 9.3 Symbol Vocabulary

#### Core State Symbols

| Symbol | Name | Meaning |
|--------|------|---------|
| `null` | Null / Silence | No grounded output; system is epistemically honest |
| `D` | Delta / Drift | Coherence degradation detected |
| `t` | Tau / Latency | Processing delay; not a failure |
| `Omega` | Omega / Lock | Stumpy enforcement event or Sentinel Lock |
| `->` | Transition | State or module transition |
| `_|_` | Bottom / Contradiction | Hard logical contradiction detected |
| `~=` | Approximation | High-confidence estimate, not exact |
| `?` | Uncertainty | Low confidence signal; may be hypothesis |
| `!` | Alert | Requires operator attention |
| `#` | Anchor | References a Vault ANCHOR-class Node |

#### Module Shorthand

| Symbol | Module |
|--------|--------|
| `[V]` | Vault |
| `[SE]` | Sentinel |
| `[VL]` | Veil |
| `[VA]` | Vara |
| `[ST]` | Stumpy |
| `[CR]` | Crossroad |
| `[SB]` | SBM |
| `[PL]` | Pulse |

#### Gate and Status Codes

| Code | Meaning |
|------|---------|
| `G1-PASS` | Coherence gate cleared |
| `G1-BLOCK` | Coherence gate blocked |
| `G2-PASS` | Attention gate cleared |
| `G2-SOFT` | Attention soft block (override window open) |
| `G2-BLOCK` | Attention gate blocked |
| `G3-PASS` | Reversibility gate cleared |
| `G3-BLOCK` | Reversibility gate blocked |
| `Omega-LOCK` | Sentinel Lock activated |
| `Omega-CLEAR` | Sentinel Lock cleared |

### 9.4 Invariant Binding Notation

Invariants are referenced in the CONSTRAINT segment using their index codes:

```
I-COH     — Coherence Primacy
II-REV    — Reversibility
III-ATT   — Attention Budget
IV-SIL    — Silence Mandate
V-DEC     — Decay Mandate
VI-SIG    — Weak Signal Parity
```

Multiple invariants are separated by `|`:
```
[active_context | D detected | I-COH | II-REV | !]
```


### 9.6 Grammar Production Rules

```
packet     := "[" context "|" signal "|" constraint "|" operator "]"
context    := node_ref ("," node_ref)* | topic_string
signal     := symbol_expr (symbol_expr)*
constraint := invariant_code ("|" invariant_code)*
operator   := col_command | status_code | null

symbol_expr    := symbol_token | module_code | gate_code | text_token
invariant_code := "I-COH" | "II-REV" | "III-ATT" | "IV-SIL" | "V-DEC" | "VI-SIG"
```

---

## §10 — Error Taxonomy

### 10.1 Error Classification

The Lattice uses a 3-tier error taxonomy. Error tier determines which module is responsible for response.

#### Tier 1 — Hard Failures

System-halting. Require Sentinel Lock and Operator review before resuming.

| Code | Name | Trigger | Responsible Module |
|------|------|---------|-------------------|
| ERR-H001 | FABRICATION | Output not grounded in Vault | Sentinel |
| ERR-H002 | VAULT_HASH_MISMATCH | Node content hash changed post-write | Stumpy |
| ERR-H003 | ANCHOR_OVERWRITE | Attempt to modify ANCHOR without snapshot + confirmation | Sentinel |
| ERR-H004 | UNAUTHORIZED_MODULE | Process attempted Vault access without valid module registration | Sentinel |
| ERR-H005 | INVARIANT_VIOLATION | Any of I-COH through VI-SIG structurally violated | Sentinel |
| ERR-H006 | SENTINEL_LOCK_BYPASS | Any process attempted to operate during active Omega-LOCK | Stumpy |

#### Tier 2 — Soft Failures

Cycle-interrupting but recoverable without full lock. Logged and reported. Cycle resumes after resolution.

| Code | Name | Trigger | Responsible Module |
|------|------|---------|-------------------|
| ERR-S001 | G1_BLOCK | Coherence score below threshold | Sentinel |
| ERR-S002 | G2_BUDGET_EXCEEDED | Attention cost exceeds budget without override | Sentinel |
| ERR-S003 | G3_CHAIN_BROKEN | Write target not chain-linked to parent | Sentinel |
| ERR-S004 | VEIL_OVERFLOW | Veil queue exceeds maximum capacity | Veil |
| ERR-S005 | VARA_ENTROPY_SPIKE | Entropy spike exceeds 15% threshold | Vara |
| ERR-S006 | DECAY_OVERDUE | PRUNE_CANDIDATE not resolved within policy period | Stumpy |
| ERR-S007 | CROSSROAD_TIE | No clear path resolution after 3-tier tie-break | Crossroad |
| ERR-S008 | SBM_PARSE_FAILURE | Operator input cannot be parsed to valid Neuralese | SBM |

#### Tier 3 — Drift Events

Non-interrupting. Logged for Stumpy audit. Accumulation of drift events can trigger Tier 2.

| Code | Name | Trigger | Responsible Module |
|------|------|---------|-------------------|
| ERR-D001 | COHERENCE_DECAY | G1 score declining across multiple cycles | Vara/Stumpy |
| ERR-D002 | ATTENTION_CREEP | G2 cost trending upward over sessions | Stumpy |
| ERR-D003 | HYPOTHESIS_ACCUMULATION | Veil queue growing without operator review | Vara |
| ERR-D004 | DECAY_QUEUE_GROWTH | More Nodes entering DECAYING than being resolved | Stumpy |
| ERR-D005 | CROSSROAD_ENTROPY | Path selection entropy increasing (indecision pattern) | Crossroad |

### 10.2 Error Response Protocol

**Tier 1 (Hard):**
1. Sentinel issues Omega-LOCK immediately
2. Stumpy logs full incident with cycle context
3. Operator notification via `!` in next HUD output
4. Resolution required before Omega-CLEAR is possible
5. Post-resolution Stumpy audit mandatory

**Tier 2 (Soft):**
1. Responsible module issues BLOCK or SOFT_BLOCK
2. 60-second operator override window (where applicable)
3. If no override: cycle aborted, partial state rolled back
4. Stumpy logs as FINDINGS_MINOR or FINDINGS_MAJOR depending on frequency

**Tier 3 (Drift):**
1. Logged silently
2. Appears in Stumpy COMPLIANCE_HISTORY
3. Operator may review or ignore at discretion
4. Auto-escalates to Tier 2 if same drift code fires in 3+ consecutive cycles

---

## §11 — Snapshot Protocol

### 11.1 Purpose

Snapshots are the Lattice's primary recovery mechanism. They satisfy II-REV (Reversibility) at the system level, providing a known-good restore point before consequential operations.

Full snapshot type definitions and schema are in `04_system_spec/SNAPSHOT_REGISTRY.md`. This section provides the normative protocol.

### 11.2 Snapshot Types and Triggers

| Type | Trigger | Who Initiates |
|------|---------|---------------|
| `AUTO_CYCLE` | End of every Pulse Cycle (Stage 5) | Stumpy (automatic) |
| `OPERATOR_MANUAL` | Operator explicit command | Operator |
| `PRE_AMENDMENT` | Before any ANCHOR write | Sentinel (enforced) |
| `VARA_PROMOTION` | Before Veil-to-Vault promotion | Sentinel (enforced) |
| `SENTINEL_INCIDENT` | On Tier 1 error, Omega-LOCK | Sentinel (automatic) |
| `DECAY_PURGE` | Before batch PRUNE operation | Stumpy (automatic) |

### 11.3 Mandatory Snapshot Gates

The following operations are blocked by Sentinel if no valid snapshot exists from the current session:

- Writing to an ANCHOR-class Node
- Bulk Veil promotion (> 3 entries in one operation)
- Stumpy CONFIRM_PRUNE batch operations
- Any Invariant amendment

### 11.4 Restore Semantics

Restoring a snapshot does **not** delete post-snapshot Nodes. It:
1. Sets the Vault "active window" to the snapshot state
2. Marks all post-snapshot Nodes as `LATENT` (not pruned)
3. Creates a new SNAPSHOT_REGISTRY entry recording the restore event
4. Requires Stumpy audit after restore before new Vault writes are permitted

This maintains II-REV (append-only) at all times. Restoration is a forward operation, not a destructive rollback.

### 11.5 Retention Policy

| Type | Minimum Retention | Action at Expiry |
|------|-----------------|-----------------|
| `AUTO_CYCLE` | 30 cycles | Auto-PRUNE oldest |
| `OPERATOR_MANUAL` | Indefinite | Operator decision |
| `PRE_AMENDMENT` | Indefinite | Never auto-purge |
| `VARA_PROMOTION` | 30 cycles | Auto-PRUNE oldest |
| `SENTINEL_INCIDENT` | Indefinite | Never auto-purge |
| `DECAY_PURGE` | 90 days | Stumpy review |

---

## §12 — Operator Interface Specification

### 12.1 Two Output Modes

The Lattice presents output in two modes, selectable via COL command:

**HUD Mode** (default)
- Compact: status codes, summary tokens, Neuralese shorthand
- Low attention cost (III-ATT)
- Best for: daily monitoring, routine writes, checking status

**Full Lattice Mode**
- Verbose: full Neuralese packets, full Node metadata, cycle trace
- Higher attention cost — use sparingly
- Best for: audits, amendments, troubleshooting

Switching: `HUD` <-> `FULL_LATTICE`

### 12.2 Input Parsing

All operator input routes through SBM (Rank 9) for parsing. SBM accepts:
- **COL commands:** Compact Operator Language (see MODULE_REGISTRY section SBM and SBM_Spec.md)
- **Natural language:** SBM translates to Neuralese; always echoes the parsed intent for confirmation on ambiguous inputs
- **Neuralese packets:** Accepted directly; bypasses SBM translation layer

### 12.3 Operator Rights

Per the Constitution section Operator Rights:
- Operator may override G2 soft blocks within the 60-second window
- Operator may manually promote Veil entries
- Operator may clear Sentinel Locks after resolving root cause
- Operator may not bypass G1 (Coherence) or G3 (Reversibility) gates
- Operator may amend the Constitution only via the 4-step Amendment Protocol

### 12.4 Operator Accountability

All operator actions are logged as OPERATOR_DIRECTIVE class Vault Nodes:
- Override approvals (G2)
- Manual promotions (Veil -> Vault)
- Sentinel Lock clearances
- Snapshot initiations

This ensures the Operator Loop Sacred (Constitution section Principle 3) is maintained.

### 12.5 Emergency Silence Protocol

If the system is producing high-confidence but factually suspect output, the Operator may issue:

```
SILENCE EMERGENCY
```

This immediately:
1. Halts SBM output generation
2. Forces system to null (Null / Silence) state
3. Triggers Stumpy audit of the last 5 cycles
4. Requires `SILENCE CLEAR [reason: explanation]` to resume

This is the most powerful single operator command. Use when you observe IV-SIL (Silence Mandate) violations.

---

## §13 — Runtime Deployment

### 13.1 Runtime Architecture

The Lattice runtime is implemented in Python. Module-to-file mapping:

| Module | Rank | Python File | Directory |
|--------|------|------------|-----------|
| Vault | 3 | `vault.py` | `05_runtime/` |
| Sentinel | 4 | `sentinel.py` | `05_runtime/` |
| Veil | 5 | `veil.py` | `05_runtime/` |
| Vara | 6 | `vara.py` | `05_runtime/` |
| Stumpy | 7 | `stumpy.py` | `05_runtime/` |
| Crossroad | 8 | `rift.py` | `05_runtime/` |
| SBM | 9 | `echo.py` | `05_runtime/` |
| Pulse (Orchestrator) | — | `pulse.py` | `05_runtime/` |
| Lattice Core | — | `lattice_core.py` | `05_runtime/` |
| Lattice Runtime | — | `lattice_runtime.py` | `05_runtime/` |
| Sentinel Threshold | — | `threshold.py` | `05_runtime/` |
| Agent | — | `agent.py` | `05_runtime/` |
| CLI | — | `cli.py` | `05_runtime/` |
### 9.5 HUD Mode vs Full Lattice Mode

**HUD Mode** (compact — default for routine operations):
```
[SE] G1-PASS G2-PASS G3-PASS -> [V] commit NODE-0041
```

**Full Lattice Mode** (verbose — for audits and amendments):
```
[CONTEXT: NODE-0039, NODE-0040]
[SIGNAL: Coherence score 0.83; Attention cost 12.4 / Budget 60; Chain link verified to NODE-0039]
[CONSTRAINT: I-COH | III-ATT | II-REV]
[OPERATOR: VAULT WRITE confirmed -> G1-PASS G2-PASS G3-PASS]
```
