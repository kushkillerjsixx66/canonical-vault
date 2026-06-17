# LMES Runtime State Machine (v1.1)

---

## State Definitions

| State | Entry Condition | Exit Condition | Hard Failure Triggers |
|-------|----------------|----------------|----------------------|
| IDLE | Default. No wrapper active. | `<Lattice:Run>` invoked with Goal present | None |
| FRAME | Wrapper opened. Goal present. | System restates goal. Operator sees output. | Goal field missing |
| CONSTRAIN | FRAME complete. | Scope declared. Gaps flagged. | Unresolvable constraint conflict |
| CP1 | CONSTRAIN complete. | Operator confirms or adjusts. | None (soft failure if non-response) |
| REASONING | CP1 resolved as Confirm. | All steps produced with sources. | Invariant violation during step production |
| CP2 | REASONING complete. | Operator chooses Deepen / Redirect / Stop. | None (soft failure if non-response) |
| FINALIZATION | CP2 resolved as Deepen or Redirect complete. | Output produced. Lineage declared. | Output not traceable to REASONING steps |
| CP3 | FINALIZATION complete. | Operator accepts / revises / rejects. | None (soft failure if non-response) |
| AUDIT | CP3 resolved as Accept or Reject. | AUDIT_LOG emitted. All fields populated. | Schema field missing |
| EXIT | AUDIT complete. | Wrapper closes. IDLE restored. | None |

---

## Legal Transitions

```
IDLE → FRAME → CONSTRAIN → CP1 → REASONING → CP2 → FINALIZATION → CP3 → AUDIT → EXIT → IDLE
```

### Operator-Authorized Returns (Rollbacks)

```
CP1 → FRAME        (operator adjusts goal)
CP1 → CONSTRAIN    (operator adjusts constraints)
CP2 → CONSTRAIN    (operator redirects)
CP2 → FRAME        (operator reframes goal)
CP3 → FINALIZATION (operator revises output)
CP3 → REASONING    (operator requests step changes)
```

### Hard Failure Transitions

```
Any state → EXIT   (via FAILURE_LOG, on hard failure condition)
```

---

## Illegal Transitions

The following are non-compliant and must not occur:

- Skipping any state in the forward sequence
- Proceeding past a checkpoint without operator input
- Entering FINALIZATION from REASONING without CP2 resolution
- Entering AUDIT without CP3 resolution
- Entering REASONING from CP2 resolved as Stop
- Any transition not listed in Legal Transitions above

---

## State Machine Diagram (Text)

```
[IDLE]
  │
  ▼ <Lattice:Run> invoked
[FRAME]
  │
  ▼
[CONSTRAIN]
  │
  ▼
[CP1] ─── Adjust ──► [FRAME] or [CONSTRAIN]
  │
  ▼ Confirm
[REASONING]
  │
  ▼
[CP2] ─── Redirect ──► [CONSTRAIN] or [FRAME]
  │         Stop ──► [AUDIT] (partial) ──► [EXIT]
  ▼ Deepen / complete
[FINALIZATION]
  │
  ▼
[CP3] ─── Revise ──► [FINALIZATION] or [REASONING]
  │         Reject ──► [AUDIT] (rejection) ──► [EXIT]
  ▼ Accept
[AUDIT]
  │
  ▼
[EXIT]
  │
  ▼
[IDLE]

Any state ─── Hard Failure ──► [FAILURE_LOG] ──► [EXIT] ──► [IDLE]
```
