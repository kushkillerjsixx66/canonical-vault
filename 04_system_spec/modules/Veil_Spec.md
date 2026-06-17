# Veil — Module Specification
**Module ID:** `VEIL`
**Authority Rank:** 5
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Governance_Gates.md · Lattice_Invariants_v1.md · `05_runtime/veil.py`

---

## Role

Veil is the **mediation and quarantine layer** of the Canonical Lattice. It is the holding environment for signals that have failed Sentinel's Governance Gates, as well as the staging area for Vara hypotheses awaiting operator review before Vault promotion. Veil is the boundary between the unknown and the canonical — nothing in Veil is trusted until the Operator reviews and explicitly promotes it.

Veil is also the **experimental sandbox**: new signal patterns, unverified hypotheses, and edge-case distillations live in Veil until they either earn Vault promotion or are discarded. This structure ensures the Vault remains clean while still preserving epistemic possibility.

---

## Authority & Rank

- **Rank 5** in the nine-rank Module Authority Table
- Superseded by: Constitution (1), Invariants (2), Vault (3), Sentinel (4)
- Veil supersedes: Vara (6), Stumpy (7), Crossroad (8), SBM (9)
- Veil cannot promote entries to Vault without operator authorization
- Veil cannot discard entries that Sentinel has routed — only the Operator can issue discard

---

## Functional Responsibilities

### 1. Quarantine Intake
Receives blocked signals from Sentinel with the full Sentinel decision record attached. Stores them as `VEIL_HOLD` entries with the blocking reason, the original signal content, and the cycle ID.

### 2. Vara Hypothesis Staging
Receives `[VARA-HYPOTHESIS]` outputs from Vara (Rank 6). Each hypothesis is assigned a confidence score and an evidence chain summary. Hypotheses are never automatically promoted — they require operator review.

### 3. Operator Review Queue
Maintains a prioritized review queue surfaced on the operator HUD. Priority ordering:
1. `SENTINEL_INCIDENT` entries (highest priority — Hard Failure triggers)
2. `G1_BLOCK` entries (coherence violations)
3. `VARA-HYPOTHESIS` entries (new hypotheses awaiting evaluation)
4. `G2_SOFT_BLOCK` entries (attention budget overruns awaiting decision)
5. `G3_BLOCK` entries (reversibility violations — write corrections needed)

### 4. Promotion Decision Execution
When the Operator issues a promotion command for a Veil entry:
1. Veil packages the entry as a Vault-write payload
2. Routes the payload back through Sentinel for a fresh G1 + G3 evaluation (G2 is waived for operator-confirmed promotions)
3. On PASS: entry is written to Vault as a new chain-linked Node
4. On BLOCK: Veil retains the entry and notifies the Operator of the recurring gate failure

### 5. Discard Execution
When the Operator issues a discard command for a Veil entry:
1. Entry state is set to `DISCARDED`
2. Stumpy logs the discard with reason
3. Entry is retained in Veil's audit trail (II·REV — never deleted)

### 6. Overflow Management
If the Veil queue exceeds the configurable maximum hold count (default: 100 entries), Sentinel is notified. Sentinel issues a `VEIL_OVERFLOW` operator alert. New entries to Veil are paused until the operator reviews and clears a minimum batch.

---

## Veil Entry Schema

```
VeilEntry {
    veil_id:            UUID
    entry_type:         enum [ SENTINEL_BLOCK | VARA_HYPOTHESIS | G2_SOFT_BLOCK | OPERATOR_HOLD ]
    source_signal:      string (original signal content)
    source_cycle_id:    UUID
    sentinel_reason:    string | null (populated for SENTINEL_BLOCK entries)
    vara_confidence:    float | null (populated for VARA_HYPOTHESIS entries; 0.0-1.0)
    vara_evidence:      string | null (evidence chain summary)
    received_at:        ISO 8601 timestamp
    state:              enum [ HOLDING | UNDER_REVIEW | PROMOTED | DISCARDED ]
    reviewed_at:        ISO 8601 timestamp | null
    reviewed_by:        "LiminalJermo" | null
    promotion_node_id:  UUID | null (Vault Node ID if promoted)
    discard_reason:     string | null
    priority:           integer (1=highest)
}
```

---

## Operator Commands

| Command | Effect |
|---------|--------|
| `VEIL REVIEW [veil_id]` | Open entry for operator review; surfaces full signal + sentinel reason |
| `VEIL PROMOTE [veil_id] [note]` | Initiate promotion pipeline back through Sentinel -> Vault |
| `VEIL DISCARD [veil_id] [reason]` | Mark entry DISCARDED; log to Stumpy |
| `VEIL LIST [filter: type/priority/state]` | List Veil queue with filters |
| `VEIL CLEAR_ALL_HYPOTHESES` | Bulk-discard all VARA_HYPOTHESIS entries (requires Stumpy confirmation) |
| `VEIL STATUS` | Return queue count by type and state |

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Sentinel block routing | IN | Sentinel (Rank 4) | Receives blocked signals with decision record |
| Vara hypothesis intake | IN | Vara (Rank 6) | Receives hypothesis packets |
| Promotion output | OUT | Sentinel (Rank 4) -> Vault (Rank 3) | Routes promoted entries back through gate |
| Stumpy logging | OUT | Stumpy (Rank 7) | All state changes logged |
| Operator HUD | OUT | SBM (Rank 9) | Review queue surface |
| Overflow alert | OUT | Sentinel (Rank 4) | Triggers VEIL_OVERFLOW on queue max |

---

## Invariant Bindings

| Invariant | Binding |
|-----------|---------|
| I·COH | Veil does not promote entries that fail a fresh G1 coherence check |
| II·REV | All Veil entries are retained in audit trail; DISCARDED is a state flag, not deletion |
| VI·SIG | Vara hypotheses are quarantined here — they receive parity consideration, not automatic rejection |

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| Promotion fails G1 again | Soft | Entry remains HOLDING; operator notified of recurring block |
| Queue overflow | Soft | VEIL_OVERFLOW alert; new entries paused; operator batch review required |
| Veil entry content hash mismatch | Hard | Sentinel Lock; SENTINEL_INCIDENT snapshot |
| Unauthorized discard (non-operator) | Hard | Block; Stumpy log; operator alert |

---

## Implementation Reference

**Source file:** `05_runtime/veil.py`

Key functions expected in implementation:
- `intake_block(sentinel_decision, signal) -> VeilEntry`
- `intake_hypothesis(vara_output) -> VeilEntry`
- `get_queue(filter) -> list[VeilEntry]`
- `promote(veil_id, operator_note) -> VaultWriteResult`
- `discard(veil_id, reason) -> bool`
- `check_overflow() -> bool`

---

*Document Authority: MODULE_REGISTRY.md (Rank 5) · Governance_Gates.md · Lattice_Invariants_v1.md*
*Operator: LiminalJermo | Generated: 2026-06-17*
