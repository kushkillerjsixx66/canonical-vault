# Lattice Node Model — Canonical Specification
**Version:** 1.0
**Authority:** 04_system_spec (derived from Lattice_Unified_Spec.md §Node Model)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Lattice_Unified_Spec.md · Lattice_Invariants_v1.md (V·DEC) · MODULE_REGISTRY.md

---

## Overview

A **Node** is the atomic unit of knowledge in the Lattice Vault. Every piece of information — a signal distillation, an operator directive, a Vara hypothesis that passed Veil review, or a Stumpy audit record — is stored as a Node. Nodes are not static records; they are living objects with state, decay rates, chain links, and reference counts.

This document defines the complete Node model: its data schema, four lifecycle states, transition rules, and invariant bindings.

---

## 1. Node Schema

```
Node {
    node_id:          UUID (immutable, assigned at creation)
    chain_id:         UUID (links to previous version; null for genesis nodes)
    content:          string
    content_hash:     SHA-256
    classification:   enum [ ANCHOR | STANDARD | VARA_PROMOTED | OPERATOR_DIRECTIVE | AUDIT_RECORD ]
    state:            enum [ LATENT | ACTIVE | DECAYING | PRUNED ]
    created_at:       ISO 8601 timestamp
    last_referenced:  ISO 8601 timestamp
    decay_rate:       float (0.0 = exempt; 1.0 = maximum)
    decay_window:     integer (days before first state transition)
    reference_count:  integer
    invariant_tags:   list [ I·COH | II·REV | III·ATT | IV·SIL | V·DEC | VI·SIG ]
    operator_note:    string | null
    pruned_at:        ISO 8601 timestamp | null
    prune_reason:     string | null
}
```

### Field Notes
- **`chain_id`**: Implements II·REV. Every write creates a new Node; the old Node becomes the ancestor. Full chain is always traversable.
- **`classification`**: ANCHOR nodes have `decay_rate = 0.0` and are never eligible for pruning without explicit operator action.
- **`content_hash`**: Hash mismatch on read is a Hard Failure (I·COH + II·REV violation).
- **`decay_rate`**: Set by the writing module. Only the Operator may set `decay_rate = 0.0`.

---

## 2. Node States

### 2.1 LATENT

The Node exists in the Vault but is not currently participating in active context.

**Entry:** All newly created Nodes begin in LATENT state.

**Exit:**
- Referenced by any module or operator → transitions to ACTIVE
- Unreferenced for `decay_window` days → transitions to DECAYING

**Invariant Bindings:** V·DEC (decay clock begins), II·REV (entry exists in chain)

**Vault Behavior:** Searchable and readable. Not surfaced proactively on HUD.

---

### 2.2 ACTIVE

The Node is currently referenced within the active context window. Contributes to coherence evaluation (I·COH) and attention budgeting (III·ATT).

**Entry:** Node in LATENT state is referenced by any module or operator read.

**Exit:**
- Reference window ends → transitions back to LATENT
- Superseded by a new version (chain write) → transitions to LATENT (as superseded ancestor)

**Invariant Bindings:** I·COH (participates in coherence check), III·ATT (contributes to attention budget)

**Vault Behavior:** Included in active context. Visible on HUD if operator requests context summary.

---

### 2.3 DECAYING

The Node has not been referenced for at least one full `decay_window` period. Approaching pruning eligibility.

**Entry:**
- Node in LATENT state unreferenced for `decay_window` days
- Operator may manually transition a LATENT node to DECAYING

**Exit:**
- Referenced before second decay window → transitions back to ACTIVE
- Unreferenced for a second `decay_window` period → Stumpy flags as PRUNE_CANDIDATE
- Operator confirms pruning → transitions to PRUNED

**Invariant Bindings:** V·DEC (decay mechanism), II·REV (DECAYING is a state flag, not deletion)

**Vault Behavior:** Still readable. Surfaced in Stumpy decay reports.

---

### 2.4 PRUNED

Confirmed for pruning by the operator. No longer active in Vault context. Record is retained with `state = PRUNED`, `pruned_at`, and `prune_reason` — never deleted (II·REV).

**Entry:**
- Operator confirms prune for a DECAYING / PRUNE_CANDIDATE Node
- Operator explicitly prunes an ANCHOR or STANDARD Node (requires amendment-level authorization)

**Exit:** PRUNED is a terminal state. Nodes cannot be un-pruned.

**Invariant Bindings:** II·REV (record preserved), V·DEC (decay completed)

**Vault Behavior:** Not readable by standard module queries. Accessible only via Stumpy audit queries.

---

## 3. State Transition Diagram

```
         CREATE
           |
      +---------+    REFERENCED    +---------+
      | LATENT  |----------------->| ACTIVE  |
      |         |<-----------------+         |
      +---------+    REF ENDS     +---------+
           |
    decay_window elapsed
           |
      +---------+
      | DECAYING|--- referenced before 2nd window ---> ACTIVE
      +---------+
           |
    2nd decay_window + operator confirm
           |
      +---------+
      |  PRUNED | (terminal)
      +---------+
```

---

## 4. Node Classification Rules

| Classification | Decay Rate | Prune-Eligible | Who Can Create |
|----------------|------------|----------------|----------------|
| `ANCHOR` | 0.0 (exempt) | No (Constitution-level action required) | Operator only |
| `STANDARD` | Configurable | Yes (after decay windows) | Any gate-passing module |
| `VARA_PROMOTED` | 0.5 (default) | Yes | Veil (after operator review) |
| `OPERATOR_DIRECTIVE` | 0.1 (slow decay) | Yes (operator must re-confirm) | Operator only |
| `AUDIT_RECORD` | 0.0 (exempt) | No | Stumpy only |

---

## 5. Coherence Evaluation on Read

When any module reads a Node, the following coherence check is performed (I·COH):

1. Retrieve Node content
2. Recompute content hash — compare to stored `content_hash`. Mismatch → Hard Failure
3. Check for logical contradiction with all ACTIVE Nodes in current context window
4. If contradiction detected → route conflicting Node to Veil for operator review; do not surface to execution
5. If coherent → return Node content + metadata to requesting module

---

## 6. Chain Traversal

Every Vault write that modifies an existing entry creates a new Node linked by `chain_id`. The full lineage of any entry is traversable by following `chain_id` links backward to the genesis node (where `chain_id = null`).

Stumpy exposes a `chain_trace(node_id)` query that returns the full ancestor chain in chronological order.

---

*Document Authority: Lattice_Unified_Spec.md §Node Model · Lattice_Invariants_v1.md (II·REV, V·DEC)*
*Operator: LiminalJermo | Generated: 2026-06-17*
