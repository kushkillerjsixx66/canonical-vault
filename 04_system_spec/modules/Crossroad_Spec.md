# Crossroad — Module Specification
**Module ID:** `CROSSROAD`
**Authority Rank:** 8
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Lattice_Invariants_v1.md · Pulse_Cycle_Spec.md · `05_runtime/rift.py`

---

## Role

Crossroad is the **routing and transition management module** of the Canonical Lattice. It resolves ambiguity when the Pulse cycle produces multiple competing execution paths — selecting the canonical path according to the Invariants and passing it to Sentinel for gate evaluation.

Crossroad is structurally narrow in its mandate: it does not evaluate content, does not produce knowledge, and does not write to Vault. It makes exactly one decision per invocation: *which path forward*. That decision is recorded, reasoned, and passed downstream. Nothing more.

The name "Crossroad" reflects its function — it is the decision point at a fork, not the traveler moving through it.

---

## Authority & Rank

- **Rank 8** in the nine-rank Module Authority Table
- Superseded by all modules Rank 1-7
- Crossroad paths are evaluated by Sentinel (Rank 4) regardless of Crossroad's selection
- Crossroad recommendations are advisory to Sentinel, not binding

---

## Functional Responsibilities

### 1. Path Resolution (Primary Function)
Activated when Pulse Cycle Stage 2 (Activation) produces more than one candidate execution path. This occurs when:

- Multiple Vault Node clusters are relevant to the incoming signal and could serve as different context windows
- Vara has produced a hypothesis that, if included, would branch execution into a different inference path
- A Veil entry is eligible for re-evaluation and its inclusion would fork the path
- A previous Crossroad decision is being re-evaluated (operator issued `CROSSROAD RECONSIDER`)

### 2. Path Scoring
Crossroad scores each candidate path against two primary criteria (in priority order matching the Invariants):

1. **Coherence Score (I·COH):** Which path produces a higher coherence score across the active context window?
2. **Attention Cost (III·ATT):** If coherence scores are within epsilon of each other (default epsilon = 0.05), select the path with lower CCE attention cost

### 3. Tie-Breaking Protocol
If both criteria produce a tie within tolerance:

1. **Reversibility preference (II·REV):** Prefer the path that requires fewer or simpler Vault writes
2. **Recency preference:** Prefer the path that activates more recently referenced Nodes (lower decay state)
3. **Conservative default:** If all else ties, select the path with the fewest activated Nodes (minimum footprint)

Tie-breaking defaults are logged to Stumpy with a `CROSSROAD_TIE_DEFAULT` marker so the Operator can review and adjust if the conservative path is consistently suboptimal.

### 4. Rejected Path Preservation
All non-selected paths are preserved as `CROSSROAD_REJECTED` records in the Stumpy audit trail. They are not routed to Veil (they are not failures — they are unchosen alternatives). The Operator may review rejected paths via `CROSSROAD HISTORY`.

---

## Path Record Schema

```
CrossroadDecision {
    decision_id:          UUID
    cycle_id:             UUID
    timestamp:            ISO 8601
    candidate_count:      integer
    candidates: [
        {
            path_id:      UUID
            coherence:    float
            attention:    float
            write_count:  integer
            node_count:   integer
            status:       SELECTED | REJECTED
        }
    ]
    selected_path_id:     UUID
    selection_reason:     string
    tie_break_applied:    boolean
    tie_break_reason:     string | null
    operator_override:    boolean
    override_reason:      string | null
    stumpy_logged:        boolean
}
```

---

## Operator Commands

| Command | Effect |
|---------|--------|
| `CROSSROAD STATUS` | Return current pending path decisions, if any |
| `CROSSROAD HISTORY [N]` | Return last N Crossroad decisions with scoring |
| `CROSSROAD RECONSIDER [cycle_id]` | Re-evaluate path selection for a completed cycle (audit only) |
| `CROSSROAD OVERRIDE [decision_id] [path_id]` | Operator selects a rejected path; re-routes through Sentinel |
| `CROSSROAD TUNE epsilon [value]` | Adjust coherence-tie tolerance threshold |

---

## Operator Override Protocol

When the Operator issues `CROSSROAD OVERRIDE`:
1. The rejected path is retrieved from the Stumpy audit trail
2. It is re-submitted to Sentinel for G1 + G2 + G3 evaluation
3. If Sentinel PASSes, execution proceeds on the operator-selected path
4. The override is logged as an `OPERATOR_DIRECTIVE` Node in Vault
5. Stumpy records the override event with the original and override path IDs

This mechanism ensures that Crossroad's automated selection is always subject to operator review and correction, while maintaining the Sentinel gate as the non-bypassable enforcement layer.

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Candidate paths | IN | Pulse Cycle Stage 2 | Receives competing activation paths |
| CCE cost estimates | IN | CCE | Receives attention cost per path |
| Vault Node metadata | IN | Vault (Rank 3) | Reads Node decay state and reference recency |
| Selected path output | OUT | Sentinel (Rank 4) | Routes selected path for gate evaluation |
| Stumpy logging | OUT | Stumpy (Rank 7) | All decisions and rejected paths logged |
| Operator HUD | OUT | SBM (Rank 9) | Surfaces tie-break defaults and override options |

---

## Invariant Bindings

| Invariant | Binding |
|-----------|---------|
| I·COH | Primary selection criterion — maximize coherence |
| III·ATT | Secondary selection criterion — minimize attention cost |
| II·REV | Tie-breaking criterion — prefer fewer/simpler writes |
| IV·SIL | Crossroad never outputs noise; if no clear selection is possible, surfaces [CROSSROAD: NO_PATH] to operator |

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| All paths below coherence threshold | Hard | CROSSROAD: NO_PATH issued; operator required; cycle pauses at Stage 2 |
| Tie-break exhausted with no winner | Soft | Conservative default applied; logged with CROSSROAD_TIE_DEFAULT |
| Crossroad runtime error | Soft | Falls back to first-received path; logged as CROSSROAD_FALLBACK |
| Operator override fails Sentinel re-evaluation | Soft | Operator notified; original Crossroad selection used |

---

## Implementation Reference

**Source file:** `05_runtime/rift.py`

Key functions expected in implementation:
- `evaluate_paths(candidate_paths, vault_metadata, cce_costs) -> CrossroadDecision`
- `score_coherence(path) -> float`
- `score_attention(path) -> float`
- `apply_tiebreak(candidates) -> UUID`
- `override(decision_id, path_id, operator) -> bool`
- `get_history(n) -> list[CrossroadDecision]`

---

*Document Authority: MODULE_REGISTRY.md (Rank 8) · Lattice_Invariants_v1.md (I·COH, III·ATT, II·REV)*
*Operator: LiminalJermo | Generated: 2026-06-17*
