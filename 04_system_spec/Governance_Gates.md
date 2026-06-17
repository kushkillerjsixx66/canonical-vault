# Governance Gates — Canonical Specification
**Version:** 1.0
**Authority:** 04_system_spec (derived from Lattice_Unified_Spec.md §Governance Gates)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Lattice_Unified_Spec.md · Lattice_Invariants_v1.md · MODULE_REGISTRY.md (Sentinel, Rank 4)

---

## Overview

The three Governance Gates are the runtime enforcement checkpoints of the Canonical Lattice. They are evaluated sequentially by Sentinel (Rank 4) during **Stage 3 (Evaluation/Constrain)** of every Pulse Cycle. No execution may proceed until all three gates have issued a PASS.

Gates are not filters — they are hard structural constraints. A gate BLOCK is not a warning. It is a halt.

---

## Gate Architecture

Gates are evaluated in strict order: **G1 → G2 → G3**. A BLOCK at G1 terminates evaluation; G2 and G3 are not reached. This sequencing reflects the constitutional priority: coherence first, attention second, reversibility third.

```
Signal from Stage 2 (Activation)
          |
          v
    +-------------+
    |     G1      |---- BLOCK ---> Veil quarantine + Operator alert
    |  Coherence  |
    +------+------+
           | PASS
           v
    +-------------+
    |     G2      |---- SOFT BLOCK ---> Operator notification (may override)
    |  Attention  |
    +------+------+
           | PASS (or Operator override)
           v
    +-------------+
    |     G3      |---- BLOCK ---> Write rejected + Operator alert
    |Reversibility|
    +------+------+
           | PASS
           v
    Stage 4 (Execute)
```

---

## G1 — Coherence Gate

**Invariant Binding:** I·COH (Coherence Supremacy)
**Failure Class:** Hard Failure
**Module Enforcer:** Sentinel (Rank 4), with Stumpy (Rank 7) audit

### Evaluation Criteria

G1 passes when the proposed execution path is internally consistent with the existing Vault state. G1 checks:

1. **Logical Non-Contradiction:** The proposed signal does not introduce a contradiction with any `ACTIVE` or `ANCHOR` Node in the current context window.
2. **Semantic Coherence:** The signal is semantically interpretable within the Neuralese framework. Ambiguous or malformed packets do not pass G1.
3. **Vault Anchor Alignment:** The signal does not conflict with any `ANCHOR`-class Node.
4. **Chain Integrity:** If the signal involves a Vault write, the proposed chain link is valid and traceable to a genesis node.

### Scoring

Coherence is evaluated on a 0.0–1.0 scale. The configurable minimum threshold defaults to **0.75**. Scores below threshold trigger BLOCK. Scores ≥ 0.85 PASS with no comment.

### BLOCK Behavior

- Signal is routed to **Veil** with reason code `G1_COHERENCE_VIOLATION`
- Operator receives alert: `[SENTINEL·G1·BLOCK] Reason: {coherence_violation_summary}`
- Stumpy logs the BLOCK with full context window snapshot
- Cycle terminates at Stage 3; Stage 4 does not execute
- No Vault write occurs

### PASS Behavior

- G1 reason code `G1_PASS` logged to Stumpy
- Evaluation proceeds to G2

---

## G2 — Attention Cost Gate

**Invariant Binding:** III·ATT (Attention Is a Scarce Resource)
**Failure Class:** Soft Failure (operator override permitted)
**Module Enforcer:** Sentinel (Rank 4), with CCE providing cost estimate

### Evaluation Criteria

G2 passes when the total cognitive attention cost of the proposed execution path fits within the configured attention budget for the current session.

CCE computes:
```
attention_cost = (context_size x context_weight)
               + (inference_depth x depth_weight)
               + (vault_writes x write_weight)
               + (vara_hypotheses_to_evaluate x vara_weight)
```

Default weights:

| Component | Default Weight |
|-----------|----------------|
| context_size (Nodes) | 0.1 per active Node |
| inference_depth | 0.3 per recursive inference step |
| vault_writes | 0.5 per write operation |
| vara_hypotheses | 0.2 per hypothesis evaluated |

Session attention budget defaults to **10.0 units**. Operator may expand per-session.

### SOFT BLOCK Behavior

- Signal is not immediately rejected
- Operator receives notification: `[SENTINEL·G2·SOFT_BLOCK] Attention cost: {cost} / Budget: {budget}. Options: (1) Approve override, (2) Reduce scope, (3) Abort`
- Operator has **60 seconds** to respond before cycle auto-aborts
- If Operator approves override: cycle proceeds to G3 with override logged to Stumpy
- If no response within 60 seconds: cycle aborts

### PASS Behavior

- G2 reason code `G2_PASS` with cost figure logged to Stumpy
- Attention cost committed to session budget
- Evaluation proceeds to G3

---

## G3 — Reversibility Gate

**Invariant Binding:** II·REV (Reversibility by Default)
**Failure Class:** Hard Failure
**Module Enforcer:** Sentinel (Rank 4), with Vault chain validation

### Evaluation Criteria

G3 applies only when Stage 4 will include a **Vault write operation**. If no write is planned, G3 auto-PASSES.

When a write is planned, G3 checks:
1. **Chain Link Present:** The proposed write includes a valid `chain_id`.
2. **Overwrite Prohibition:** The write does not modify or delete an existing Node in place.
3. **ANCHOR Protection:** Writes to `ANCHOR`-class Nodes require operator explicit confirmation.
4. **Deprecation Compliance:** Entries being superseded must have their state set to `DEPRECATED`, not deleted.

### BLOCK Behavior

- Write operation is rejected
- Operator receives alert: `[SENTINEL·G3·BLOCK] Reason: {reversibility_violation_detail}`
- Execution proceeds to Stage 4 **without the write** if the response is otherwise valid
- Stumpy logs the BLOCK and the rejected write payload

### PASS Behavior

- G3 reason code `G3_PASS` logged to Stumpy
- Write payload cleared for commit in Stage 4

---

## Gate Decision Matrix

| Scenario | G1 | G2 | G3 | Outcome |
|----------|----|----|----|--------|
| Clean signal, low cost, append write | PASS | PASS | PASS | Execute |
| Coherence violation | BLOCK | — | — | Veil; operator alert |
| Over-budget, approved by operator | PASS | OVERRIDE | PASS | Execute with override logged |
| Over-budget, no operator response | PASS | SOFT_BLOCK → ABORT | — | Cycle aborted |
| Silent overwrite attempted | PASS | PASS | BLOCK | Response surfaced; write rejected |
| Vara hypothesis (read-only, no write) | PASS | PASS | PASS (auto) | Execute (no write) |
| ANCHOR write (operator-confirmed) | PASS | PASS | PASS (with confirmation) | Execute with anchor amendment log |

---

## Sentinel Decision Codes

| Code | Gate | Meaning |
|------|------|--------|
| `G1_PASS` | G1 | Coherence validated |
| `G1_BLOCK` | G1 | Coherence violation; signal quarantined |
| `G2_PASS` | G2 | Within attention budget |
| `G2_SOFT_BLOCK` | G2 | Over budget; awaiting operator |
| `G2_OVERRIDE` | G2 | Operator approved over-budget execution |
| `G2_ABORT` | G2 | Soft block expired; cycle aborted |
| `G3_PASS` | G3 | Reversibility confirmed |
| `G3_AUTO_PASS` | G3 | No write planned; gate trivially passed |
| `G3_BLOCK` | G3 | Reversibility violation; write rejected |
| `G3_ANCHOR_CONFIRM` | G3 | ANCHOR write confirmed by operator |

---

## Amendment

The threshold values for G1 (coherence minimum) and G2 (attention budget) are configurable by the Operator. Changes are stored as `OPERATOR_DIRECTIVE` Nodes and logged to the Governance log. Gate logic itself may only be amended through the full Constitutional Amendment Protocol.

---

*Document Authority: Lattice_Unified_Spec.md §Governance Gates · Lattice_Invariants_v1.md (I·COH, II·REV, III·ATT)*
*Operator: LiminalJermo | Generated: 2026-06-17*
