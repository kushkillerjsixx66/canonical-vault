# Snapshot Registry — Canonical Lattice
**Version:** 1.0
**Authority:** 04_system_spec (Vault state auditing)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Lattice_Invariants_v1.md (II·REV, V·DEC) · Stumpy (Rank 7) · Pulse_Cycle_Spec.md

---

## Overview

A **Snapshot** is a point-in-time capture of the Vault's full state — all active Nodes, their decay states, reference counts, chain links, and the Stumpy audit record associated with the capture event. Snapshots serve as recovery anchors, operator-review checkpoints, and the historical evidence base for the Lattice's epistemic lineage.

Snapshots do not replace the append-only Vault chain (II·REV). They are derived summaries — compressed representations of Vault state at a moment in time — stored as `AUDIT_RECORD` Nodes with decay exemption.

---

## Snapshot Classification

| Type | Trigger | Retention | Prunable |
|------|---------|-----------|---------|
| `AUTO_CYCLE` | Every Nth Pulse cycle (configurable; default N=50) | 90 days | Yes, after operator review |
| `OPERATOR_MANUAL` | Explicit operator command | Indefinite | Only with operator explicit prune |
| `PRE_AMENDMENT` | Automatically before any ANCHOR Node write or invariant amendment | Indefinite | No (Constitution-level anchor) |
| `VARA_PROMOTION` | Automatically when a Vara hypothesis is promoted from Veil to Vault | 180 days | Yes, after operator review |
| `SENTINEL_INCIDENT` | Automatically when a G1 Hard Failure occurs | 365 days | No |
| `DECAY_PURGE` | Automatically when an operator confirms a prune batch | 365 days | No |

---

## Snapshot Schema

```
Snapshot {
    snapshot_id:       UUID
    snapshot_type:     enum [ AUTO_CYCLE | OPERATOR_MANUAL | PRE_AMENDMENT | VARA_PROMOTION | SENTINEL_INCIDENT | DECAY_PURGE ]
    captured_at:       ISO 8601 timestamp
    pulse_cycle_id:    UUID (the cycle that triggered or coincided with the snapshot)
    vault_node_count:  integer (total Nodes at time of capture)
    state_summary: {
        LATENT:         integer
        ACTIVE:         integer
        DECAYING:       integer
        PRUNED:         integer
    }
    anchor_nodes:      list [ node_id ] (all ANCHOR-class Nodes at time of capture)
    compliance_status: COMPLIANT | FINDINGS_MINOR | FINDINGS_MAJOR
    stumpy_audit_id:   UUID (reference to the Stumpy audit record Node)
    operator_note:     string | null
    checksum:          SHA-256 (hash of full snapshot payload for integrity)
}
```

---

## Snapshot Index

*This section is updated by Stumpy after each snapshot is captured. Entries are listed in reverse chronological order.*

| Snapshot ID | Type | Captured At | Cycle ID | Nodes | Compliance | Note |
|-------------|------|-------------|----------|-------|------------|------|
| — | — | *No snapshots yet — vault initialized 2026-06-17* | — | — | — | Genesis state |

---

## Snapshot Procedures

### Creating a Manual Snapshot

The Operator issues:
```
OPERATOR_COMMAND: SNAPSHOT MANUAL [note: "reason for snapshot"]
```

Stumpy receives the command, compiles the Vault state, generates the Snapshot record, stores it as an `AUDIT_RECORD` Node (decay_rate = 0.0), and returns the `snapshot_id` to the operator.

### Restoring from a Snapshot

Snapshots are **not** restore points in the database-rollback sense — the Vault is append-only (II·REV) and cannot be rolled back. Instead, a snapshot serves as a **reference anchor**: the operator can use it to:
1. Identify which Nodes were active at the snapshot point
2. Re-activate `DECAYING` or `PRUNED` Nodes that were present at the snapshot (by creating new STANDARD Nodes with the same content, linked to the original chain)
3. Audit drift between current Vault state and the snapshot state

### Pre-Amendment Snapshots

The Operator Manual and Constitution require that a `PRE_AMENDMENT` snapshot be automatically captured before:
- Any write to an `ANCHOR`-class Node
- Any change to a Governance Gate threshold (G1 coherence minimum, G2 budget)
- Any Invariant amendment

Sentinel enforces this requirement. A write to an ANCHOR Node without a valid `PRE_AMENDMENT` snapshot in the audit trail within the last 5 minutes is blocked at G3.

---

## Snapshot Integrity

Every Snapshot carries a `checksum` (SHA-256 hash of the full payload). On retrieval, Stumpy recomputes the hash and compares. A mismatch indicates snapshot tampering — this is treated as a Hard Failure (I·COH + II·REV), surfaced immediately to the Operator with a `SENTINEL_INCIDENT` snapshot triggered automatically.

---

## Retention & Decay Policy

`AUTO_CYCLE` and `VARA_PROMOTION` snapshots are subject to decay after their retention period. Stumpy surfaces them as `PRUNE_CANDIDATE` after expiry. The Operator must confirm before they are moved to `PRUNED` state (II·REV — they are never deleted, only state-flagged).

`PRE_AMENDMENT`, `SENTINEL_INCIDENT`, and `DECAY_PURGE` snapshots are permanently retained (decay_rate = 0.0). Pruning these requires a constitutional-level amendment justification.

---

*Document Authority: Lattice_Invariants_v1.md (II·REV, V·DEC) · Pulse_Cycle_Spec.md §Stage 5*
*Operator: LiminalJermo | Generated: 2026-06-17*
