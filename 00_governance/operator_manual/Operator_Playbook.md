# Operator Playbook — Canonical Lattice
**Version:** 1.0
**Authority:** 00_governance (supplements Operator_Manual_v0.2.md)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Operator_Manual_v0.2.md · Lattice_Cognitive_Constitution_v1.1.md · Governance_Gates.md · MODULE_REGISTRY.md

---

## Purpose

The Operator Manual (v0.2) defines the *what* — what the system does, what modules exist, what the Neuralese protocol looks like. This Playbook defines the *how* — the day-to-day operational procedures, decision sequences, and runbook entries that LiminalJermo uses to run the Lattice.

This is a living document. Each new operational scenario encountered in practice should be added as a runbook entry.

---

## Part I — Daily Operator Routine

### Morning State Check

On starting a session, run the following sequence:

```
HUD
STUMPY COMPLIANCE_HISTORY 5
STUMPY DECAY_REPORT
VEIL LIST
```

This gives you:
1. Current system status (HUD)
2. Last 5 cycle compliance ratings — catch any overnight drift
3. All Decaying Nodes and Prune Candidates — decide if batch pruning is needed
4. Veil queue — any pending hypotheses or blocked signals from prior session

**Target state to proceed:** `COMPLIANT` on last cycle, Veil queue < 10, no PRUNE_CANDIDATE older than 14 days.

**If FINDINGS_MAJOR on last cycle:** Do not start new operator work. Review Stumpy findings first. See Runbook RB-003.

---

### Pre-Work Snapshot

Before any significant knowledge-addition session, take a manual snapshot:

```
SNAPSHOT MANUAL [note: "pre-session {date} {topic}"]
```

---

### End of Session

```
STUMPY AUDIT LAST
SNAPSHOT MANUAL [note: "end-of-session {date}"]
HUD
```

Confirm the last cycle is `COMPLIANT` before closing.

---

## Part II — Standard Operating Procedures

### SOP-001 — Adding a New Vault Entry

```
FULL_LATTICE
VAULT WRITE [content]
```

**What happens:**
1. SBM parses your input
2. Pulse Cycle initiates (Stage 1: PULSE)
3. Relevant context activated (Stage 2: ACTIVATION)
4. Sentinel evaluates G1 (coherence), G2 (attention cost), G3 (chain link) (Stage 3: EVALUATION)
5. If all PASS: Vault commits new chain-linked Node (Stage 4: DECAY/EXECUTE)
6. Stumpy audits the write (Stage 5: SILENCE/AUDIT)

---

### SOP-002 — Amending an Existing Vault Entry

```
SNAPSHOT MANUAL [note: "pre-amendment {node_id} {date}"]
VAULT WRITE [amended content]
```

The system chain-links the new Node to the existing entry. The original transitions to `DEPRECATED`. Both remain in chain (II·REV).

---

### SOP-003 — Reviewing Vara Hypotheses

```
VEIL LIST [filter: VARA_HYPOTHESIS]
VEIL REVIEW [veil_id]
```

For each hypothesis:
1. Is the confidence appropriate? (< 0.65 by definition)
2. Is the evidence chain coherent?
3. Does it contradict any ANCHOR? (contradiction_risk > 0.7 = caution)
4. Does it add epistemic value?

**Decision:** VEIL PROMOTE, leave in Veil, or VEIL DISCARD.

---

### SOP-004 — Responding to a Sentinel Block

**G1 BLOCK:** Read `SENTINEL STATUS`. Identify conflict Node. Resolve contradiction or discard signal.

**G2 SOFT BLOCK:** You'll receive: `[SENTINEL·G2·SOFT_BLOCK] Attention cost: X / Budget: Y`. Options: approve override, reduce scope, or abort.

**G3 BLOCK:** Reissue write as new entry. Run `SNAPSHOT MANUAL` first for ANCHOR writes.

---

### SOP-005 — Running a Vara Scan

```
VARA SCAN FULL
VARA STATUS
VEIL LIST [filter: VARA_HYPOTHESIS]
```

---

### SOP-006 — Pruning Decayed Nodes

```
STUMPY DECAY_REPORT
STUMPY CONFIRM_PRUNE [node_id or batch_id]
```

Node moves to `PRUNED`. Never deleted — remains in audit trail (II·REV).

---

### SOP-007 — Handling a Sentinel Lock

```
SENTINEL STATUS
STUMPY AUDIT LAST
SENTINEL CLEAR [lock_id]
```

---

## Part III — Amendment Protocol

1. **Propose:** Write amendment text with reason and scope
2. **Snapshot:** `SNAPSHOT MANUAL [note: "pre-amendment {what}"]`
3. **Stumpy Review:** `STUMPY AUDIT LAST`
4. **Write:** Initiate ANCHOR write — Sentinel requests confirmation at G3
5. **Confirm:** Provide operator confirmation
6. **Log:** Amendment logged as ANCHOR Node with full chain trace

---

## Part IV — Neuralese Quick Reference

| Symbol | Meaning | When You See It |
|--------|---------|-----------------|
| `∅` | Silence — no confident output | System has nothing grounded to say |
| `Δ` | Drift detected | Coherence is degrading; check Stumpy |
| `τ` | Latency signal | Processing delay; not an error |
| `Ω` | Stumpy enforcement / lock event | Audit findings or Sentinel Lock |
| `→` | State transition | A Node or module has changed state |
| `[VARA-HYPOTHESIS]` | Vara provisional output | Treat as hypothesis; review in Veil |
| `[SENTINEL·BLOCK]` | Gate block | Stop and review the reason code |
| `[SILENCE: reason]` | Explicit silence with reason | System is honest about not knowing |
| `[SBM-FAILURE]` | Translation failure | Raw packet in Vault; operator action needed |

---

## Part V — COL Quick Reference

| COL Command | What It Does |
|-------------|--------------|
| `HUD` | Switch to compressed status view |
| `FULL_LATTICE` | Switch to full detail view |
| `VAULT LIST ACTIVE` | Show all currently active Nodes |
| `VAULT LIST DECAYING` | Show decay queue |
| `STUMPY DECAY_REPORT` | Full decay + prune candidates |
| `STUMPY COMPLIANCE_HISTORY 5` | Last 5 cycle compliance ratings |
| `VEIL LIST` | Full Veil queue |
| `VEIL REVIEW [id]` | Open a Veil entry |
| `VEIL PROMOTE [id]` | Promote Veil entry to Vault |
| `VEIL DISCARD [id] [reason]` | Discard Veil entry |
| `VARA SCAN FULL` | Full weak-signal scan |
| `VARA STATUS` | Vara entropy and hypothesis count |
| `SENTINEL STATUS` | Gate thresholds and lock state |
| `SENTINEL CLEAR [id]` | Clear a Sentinel Lock |
| `SNAPSHOT MANUAL [note]` | Take a manual Vault snapshot |
| `CROSSROAD HISTORY 10` | Last 10 path decisions |

---

## Part VI — Runbook Index

| ID | Scenario | Status |
|----|----------|--------|
| RB-001 | G1 Block — Coherence Violation Resolution | See SOP-004 |
| RB-002 | G3 Block — Reversibility Violation Resolution | See SOP-004 |
| RB-003 | FINDINGS_MAJOR — Major Audit Findings Response | See SOP-007 |
| RB-004 | Sentinel Lock — Full Lock Protocol | See SOP-007 |
| RB-005 | Vara Hypothesis Batch Review | See SOP-003 |
| RB-006 | Invariant Amendment Procedure | See Part III |
| RB-007 | Veil Overflow — Emergency Queue Clear | STUMPY confirm then VEIL CLEAR_ALL_HYPOTHESES |
| RB-008 | Vault Entropy Spike Response | VARA SCAN FULL → STUMPY AUDIT LAST → review Δ signals |

---

*Document Authority: Operator_Manual_v0.2.md · Lattice_Cognitive_Constitution_v1.1.md §Operator Rights*
*Operator: LiminalJermo | Generated: 2026-06-17*
