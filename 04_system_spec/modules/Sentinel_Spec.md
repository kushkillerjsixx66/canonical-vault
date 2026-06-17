# Sentinel — Module Specification
**Module ID:** `SENTINEL`
**Authority Rank:** 4
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Governance_Gates.md · Lattice_Invariants_v1.md · `05_runtime/sentinel.py`

---

## Role

Sentinel is the **hard-gate enforcement module** of the Canonical Lattice. It is the primary runtime firewall between signal ingestion and execution. No signal, write, or operator directive proceeds to Stage 4 (Execute) without Sentinel's explicit PASS decision.

Sentinel does not evaluate content — it evaluates structural compliance against the six Invariants and the three Governance Gates. It is intentionally narrow in scope: fast, deterministic, and binary in its core decisions.

Sentinel is incorruptible by design. No module, operator shortcut, or runtime state may bypass Sentinel's gate evaluation. The only mechanism for modifying Sentinel's evaluation thresholds is the Operator-authorized amendment process, and changes are logged as ANCHOR Nodes.

---

## Authority & Rank

- **Rank 4** in the nine-rank Module Authority Table
- Superseded only by: Constitution (1), Invariants (2), Vault (3)
- Sentinel supersedes: Veil (5), Vara (6), Stumpy (7), Crossroad (8), SBM (9)
- Sentinel may BLOCK outputs from any lower-rank module without operator override

---

## Functional Responsibilities

### 1. Governance Gate Evaluation (Primary Function)
Sentinel evaluates all three Governance Gates in sequence during Pulse Cycle Stage 3:

- **G1 — Coherence Gate** (I·COH): Validates that the signal is internally coherent with the active Vault state
- **G2 — Attention Cost Gate** (III·ATT): Validates that execution cost is within session budget
- **G3 — Reversibility Gate** (II·REV): Validates that any planned Vault write is append-only

Full evaluation logic is specified in `Governance_Gates.md`.

### 2. Invariant Violation Detection
Sentinel monitors for runtime violations of any of the six Invariants across all Pulse Cycle stages, not just Stage 3. It may issue a retroactive BLOCK if a violation is detected after Stage 3 has passed but before Stage 4 commits.

### 3. Unauthorized Module Rejection
Any process not registered in `MODULE_REGISTRY.md` that attempts to interact with Vault, Veil, or Vara is automatically blocked by Sentinel with reason code `UNAUTHORIZED_MODULE_ATTEMPT`.

### 4. Fabrication Detection (IV·SIL)
Sentinel monitors SBM (Rank 9) output for hallucination signatures — outputs generated without coherent Vault grounding. Detection triggers a Hard Failure with Sentinel Lock.

### 5. Sentinel Lock
In cases of critical Hard Failure (IV·SIL fabrication, chain tampering, unauthorized agent), Sentinel issues a **Sentinel Lock**: all new Pulse Cycles are suspended until the Operator reviews and explicitly clears the lock.

---

## Decision Output Format

Every Sentinel decision is a structured record:

```
SentinelDecision {
    decision_id:        UUID
    cycle_id:           UUID
    timestamp:          ISO 8601
    gate:               G1 | G2 | G3 | INVARIANT | MODULE_AUTH
    decision:           PASS | BLOCK | SOFT_BLOCK | ESCALATE | LOCK
    reason_code:        string (see Decision Codes below)
    reason_detail:      string (human-readable explanation)
    offending_signal:   string | null
    veil_routed:        boolean
    operator_notified:  boolean
    stumpy_logged:      boolean
}
```

---

## Decision Codes

| Code | Gate | Severity | Meaning |
|------|------|----------|---------|
| `G1_PASS` | G1 | — | Coherence validated |
| `G1_BLOCK_CONTRADICTION` | G1 | Hard | Signal contradicts ANCHOR or ACTIVE Node |
| `G1_BLOCK_SEMANTIC_MALFORM` | G1 | Hard | Neuralese packet unparseable |
| `G1_BLOCK_HASH_MISMATCH` | G1 | Hard | Vault Node content hash mismatch |
| `G2_PASS` | G2 | — | Within attention budget |
| `G2_SOFT_BLOCK_OVER_BUDGET` | G2 | Soft | Exceeds session attention budget |
| `G2_OVERRIDE_OPERATOR` | G2 | Soft/Override | Operator approved over-budget |
| `G2_ABORT_TIMEOUT` | G2 | Soft/Abort | Operator did not respond within 60s |
| `G3_PASS` | G3 | — | Reversibility confirmed |
| `G3_AUTO_PASS` | G3 | — | No write planned |
| `G3_BLOCK_OVERWRITE` | G3 | Hard | Attempted in-place overwrite |
| `G3_BLOCK_CHAIN_MISSING` | G3 | Hard | Write lacks chain_id |
| `G3_BLOCK_ANCHOR_UNCONFIRMED` | G3 | Hard | ANCHOR write without pre-amendment snapshot |
| `INV_VIOLATION_SIL` | Invariant | Hard | Fabrication detected (IV·SIL) |
| `INV_VIOLATION_REV` | Invariant | Hard | Attempted silent delete (II·REV) |
| `UNAUTHORIZED_MODULE_ATTEMPT` | Module Auth | Hard | Unregistered module interaction |
| `SENTINEL_LOCK` | System | Critical | Full system suspension; operator required |

---

## Sentinel Lock Protocol

**Trigger Conditions:**
- IV·SIL fabrication detected in SBM output
- Content hash mismatch on Vault Node read
- Unregistered module attempts write to Vault
- G3 ANCHOR write without pre-amendment snapshot

**Lock Behavior:**
1. All in-progress Pulse Cycles are halted
2. Partial Stage 4 writes are rolled back
3. Current Vault state is snapshot-captured (`SENTINEL_INCIDENT` type)
4. Operator receives `[SENTINEL·LOCK]` alert with full incident report
5. No new cycles begin until Operator issues `SENTINEL_CLEAR` command

**Lock Clearance:**
- Operator reviews incident report
- Operator issues `SENTINEL_CLEAR [lock_id]` command
- Stumpy logs clearance event
- System resumes normal Pulse cycle processing

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Gate evaluation input | IN | Pulse Cycle Stage 2 | Receives assembled context + signal |
| CCE cost estimate | IN | CCE | Receives attention cost for G2 |
| Vault state | IN | Vault (Rank 3) | Reads active Nodes for G1 coherence check |
| Invariants | IN | Invariants (Rank 2) | Reads enforcement rules |
| Veil routing | OUT | Veil (Rank 5) | Routes blocked signals to quarantine |
| Stumpy logging | OUT | Stumpy (Rank 7) | All decisions logged immediately |
| Operator alert | OUT | HUD / SBM | Hard Failures and Locks surfaced to operator |
| Crossroad override | OUT | Crossroad (Rank 8) | May issue path-redirect on G2 Soft Block |

---

## Implementation Reference

**Source file:** `05_runtime/sentinel.py`

Key functions expected in implementation:
- `evaluate_g1(context_window, signal_packet) -> SentinelDecision`
- `evaluate_g2(attention_cost, session_budget) -> SentinelDecision`
- `evaluate_g3(write_payload, vault_chain) -> SentinelDecision`
- `detect_fabrication(sbm_output, vault_context) -> bool`
- `issue_lock(reason_code) -> LockRecord`
- `clear_lock(operator_command) -> bool`
- `check_module_registry(module_id) -> bool`

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| G1 coherence violation | Hard | Signal quarantined to Veil; operator alert |
| G2 over-budget | Soft | Operator notification; 60s window |
| G3 reversibility violation | Hard | Write rejected; operator alert |
| IV·SIL fabrication | Hard | Sentinel Lock; operator clearance required |
| Chain hash mismatch | Hard | Sentinel Lock; operator clearance required |
| Unauthorized module | Hard | Block; Stumpy log; operator alert |

---

*Document Authority: MODULE_REGISTRY.md (Rank 4) · Governance_Gates.md · Lattice_Invariants_v1.md*
*Operator: LiminalJermo | Generated: 2026-06-17*
