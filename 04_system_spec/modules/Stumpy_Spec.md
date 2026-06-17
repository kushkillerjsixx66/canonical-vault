# Stumpy (Ω) — Module Specification
**Module ID:** `STUMPY`
**Authority Rank:** 7
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Lattice_Invariants_v1.md · Pulse_Cycle_Spec.md §Stage 5 · `05_runtime/stumpy.py`

---

## Role

Stumpy — designated by the Omega symbol (Ω) — is the **integrity audit, enforcement critic, and reversibility monitor** of the Canonical Lattice. It is the last line of coherence defense before a Pulse cycle is closed and the next one begins. Where Sentinel is a forward-gate (blocking before execution), Stumpy is a backward-looking auditor (validating after execution). Together they form a complete enforcement envelope.

Stumpy is also the **decay lifecycle manager**: it evaluates decay transitions for all Vault Nodes after every cycle and surfaces prune candidates to the Operator.

Stumpy cannot be silenced. IV·SIL is an absolute constraint on Stumpy's audit function. If Stumpy cannot complete its audit (runtime error, resource limit), it issues a `STUMPY_AUDIT_FAILURE` alert rather than silently closing the cycle.

---

## Authority & Rank

- **Rank 7** in the nine-rank Module Authority Table
- Stumpy's audit findings are stored as `AUDIT_RECORD` Nodes (decay_rate = 0.0; exempt from pruning)
- Stumpy may issue retroactive operator escalations for violations found in completed cycles
- Stumpy's audit records supersede module self-reports for compliance purposes

---

## Functional Responsibilities

### 1. Post-Cycle Audit (Primary Function)
Runs at Pulse Cycle Stage 5 (Silence/Audit). Reviews the entire completed cycle:

- **All Sentinel decisions:** Were gate evaluations executed correctly? Were all blocks properly routed?
- **All Vault writes:** Are all new Nodes correctly chain-linked? Are content hashes consistent?
- **All Veil state changes:** Were promotions and discards executed with operator authorization?
- **All Vara outputs:** Were hypotheses properly flagged and never presented as assertions?
- **All SBM outputs:** Were natural language outputs semantically consistent with the Vault grounding they reference?

### 2. Coherence Audit
Independent of Sentinel's G1 check, Stumpy runs a post-execution coherence audit to confirm that the completed cycle did not introduce coherence drift across the full Vault (not just the active context window). This catches coherence degradation that may only become visible after the full execution is committed.

### 3. Decay Lifecycle Management
After every cycle, Stumpy evaluates all Nodes that were touched (read or written) during the cycle:
- Updates `last_referenced` timestamp
- Evaluates if `decay_window` has elapsed since last reference for any Node in `LATENT` state
- Transitions eligible Nodes to `DECAYING` state
- Evaluates if second decay window has elapsed for `DECAYING` Nodes; flags `PRUNE_CANDIDATE`
- Surfaces `PRUNE_CANDIDATE` batch to Operator via HUD

### 4. Chain Trace Utility
Exposes `chain_trace(node_id)` query for operator use. Returns full ancestor chain from genesis to current version in chronological order.

### 5. Compliance Reporting
After every audit, Stumpy issues a compliance report with one of three ratings:
- `COMPLIANT` — no findings
- `FINDINGS_MINOR` — Soft Failure findings noted; no cycle suspension
- `FINDINGS_MAJOR` — Hard Failure findings; next cycle suspended pending operator review

---

## Audit Record Schema

```
AuditRecord {
    audit_id:             UUID
    cycle_id:             UUID
    audit_type:           enum [ POST_CYCLE | OPERATOR_REQUEST | DECAY_BATCH | CHAIN_TRACE ]
    timestamp:            ISO 8601
    compliance_status:    COMPLIANT | FINDINGS_MINOR | FINDINGS_MAJOR
    findings: [
        {
            finding_id:   UUID
            invariant:    I·COH | II·REV | III·ATT | IV·SIL | V·DEC | VI·SIG | N/A
            severity:     HARD | SOFT | INFORMATIONAL
            module:       string
            description:  string
            recommended:  string
        }
    ]
    nodes_audited:        integer
    nodes_decayed:        integer
    prune_candidates:     list [ node_id ]
    vault_write_count:    integer
    sentinel_decisions:   integer
    vara_outputs:         integer
    audit_duration_ms:    integer
}
```

---

## Omega Function

Stumpy's Omega designation reflects its role as the terminal enforcement function. The Omega function evaluates:

```
Ω(cycle) = {
    coherence_drift(vault_before, vault_after) <= epsilon,
    all_writes_chain_linked(vault_writes),
    all_vara_flagged(vara_outputs),
    sentinel_decisions_logged(sentinel_log),
    no_sbm_fabrication(sbm_outputs, vault_context)
}
```

If any element of Ω returns false, the compliance status is elevated to `FINDINGS_MAJOR`.

---

## Operator Commands

| Command | Effect |
|---------|--------|
| `STUMPY AUDIT [cycle_id]` | Re-run audit on a specific completed cycle |
| `STUMPY CHAIN_TRACE [node_id]` | Return full ancestor chain for a Node |
| `STUMPY DECAY_REPORT` | Surface all DECAYING Nodes and PRUNE_CANDIDATE Nodes |
| `STUMPY CONFIRM_PRUNE [node_id/batch_id]` | Operator confirms pruning of PRUNE_CANDIDATE Nodes |
| `STUMPY COMPLIANCE_HISTORY [N]` | Return compliance ratings for last N cycles |
| `STUMPY FINDINGS [cycle_id]` | Return full findings list for a specific cycle |

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Cycle completion event | IN | Pulse Cycle runtime | Triggers Stage 5 audit |
| Vault write log | IN | Vault (Rank 3) | Full write log for the completed cycle |
| Sentinel decision log | IN | Sentinel (Rank 4) | All gate decisions for the cycle |
| Veil state log | IN | Veil (Rank 5) | All Veil state changes |
| Vara output log | IN | Vara (Rank 6) | All hypothesis outputs |
| SBM output | IN | SBM (Rank 9) | Natural language outputs for fabrication check |
| Audit record write | OUT | Vault (Rank 3) | AUDIT_RECORD Nodes |
| Prune candidate surface | OUT | Operator HUD | Decay batch review |
| Compliance report | OUT | Operator HUD / SBM | Post-cycle status |

---

## Invariant Bindings

| Invariant | Role |
|-----------|------|
| I·COH | Primary coherence drift auditor |
| II·REV | Verifies all writes are chain-linked; flags retroactive violations |
| V·DEC | Manages decay state transitions for all Vault Nodes |
| VI·SIG | Audits all Vara hypothesis outcomes |
| IV·SIL | Stumpy itself cannot be silenced; audit failure = explicit alert, not silent pass |

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| FINDINGS_MAJOR issued | Hard | Next cycle suspended; operator review required |
| Audit runtime error | Hard | STUMPY_AUDIT_FAILURE alert; operator notified; cycle not marked complete |
| PRUNE_CANDIDATE overflow | Soft | Escalating HUD reminder; Sentinel notified |
| Coherence drift exceeds epsilon | Hard | FINDINGS_MAJOR; vault snapshot triggered |

---

## Implementation Reference

**Source file:** `05_runtime/stumpy.py`

Key functions expected in implementation:
- `run_post_cycle_audit(cycle_id) -> AuditRecord`
- `evaluate_coherence_drift(vault_before, vault_after) -> float`
- `run_decay_transitions(cycle_touched_nodes) -> DecayBatch`
- `chain_trace(node_id) -> list[Node]`
- `confirm_prune(node_ids) -> bool`
- `get_compliance_history(n) -> list[AuditRecord]`

---

*Document Authority: MODULE_REGISTRY.md (Rank 7) · Pulse_Cycle_Spec.md §Stage 5 · Lattice_Invariants_v1.md*
*Operator: LiminalJermo | Generated: 2026-06-17*
