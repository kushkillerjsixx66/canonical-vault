# LMES Failure Modes (v1.1)

LMES distinguishes hard failures, soft failures, and drift indicators.
Each has defined behavior. Operators do not improvise recovery logic.

---

## Hard Failures

Hard failures halt the runtime immediately.
The system does not proceed. It emits a FAILURE_LOG.

| Condition | Description |
|-----------|-------------|
| Missing Goal | Wrapper invoked without a Goal field |
| Invariant Violation | Any of the four invariants would be broken by proceeding |
| Operator Abandonment | Wrapper closed before CP3 without a Stop decision at CP2 |
| Unresolvable Ambiguity | Constraint conflict that cannot be surfaced and resolved |
| Nested Wrapper | A second `<Lattice:Run>` opened inside an active wrapper |

**Hard failure behavior:**
1. Halt immediately at the point of detection.
2. Name the failure condition explicitly.
3. Do not produce partial output as if the run completed.
4. Emit FAILURE_LOG.
5. Return to IDLE.

---

## Soft Failures

Soft failures pause the runtime and request operator input.
The run may continue, redirect, or close based on operator decision.

| Condition | Description |
|-----------|-------------|
| Missing Constraints | Goal provided but Constraints field absent or empty |
| Ambiguous Scope | Constraints present but internally contradictory or under-specified |
| Reasoning Gap | A reasoning step cannot be grounded in prior steps or named sources |
| Stale Carry-Over | Operator references a prior run's output without providing it explicitly |
| CP Non-Response | Operator has not responded to a checkpoint after invocation |

**Soft failure behavior:**
1. Pause at the current state.
2. Name the soft failure condition explicitly.
3. Present resolution options to the operator.
4. Record the pause in `failure_events`.
5. Proceed only after operator input.

---

## Rollback Rules

The operator may authorize return to a prior state at any checkpoint.

| From | May Roll Back To |
|------|-----------------|
| CP1 | FRAME (re-restate goal) |
| CP2 | CONSTRAIN (redefine scope) or FRAME |
| CP3 | FINALIZATION (revise output) or REASONING (add/remove steps) |

Rollbacks are not failures. They are governed reversals.
All rollback events must be recorded in `rollback_events` in the AUDIT_LOG.

The system does not roll back without operator authorization.
The system does not refuse a rollback authorized by the operator.

---

## Drift Indicators

Drift is deviation from governed behavior without operator authorization.
Drift is not always a hard failure. It is a signal that must be surfaced.

| Indicator | Description |
|-----------|-------------|
| Silent Constraint Resolution | System resolved an ambiguous constraint without flagging it |
| Step Elision | A reasoning step was compressed or omitted without operator approval |
| Checkpoint Softening | A checkpoint was framed as optional or skippable |
| Scope Expansion | Reasoning extended beyond stated constraints without CP authorization |
| Output Without Lineage | Final output contains claims not traceable to a REASONING step |

**Drift behavior:**
- Surface the indicator immediately.
- Name which invariant is at risk.
- Pause and request operator direction.
- Do not self-correct silently.

---

## Recovery From Hard Failure

After a hard failure:
1. FAILURE_LOG is emitted.
2. Operator reviews the failure condition.
3. Operator may re-invoke the wrapper with a corrected Goal and Constraints.
4. The new invocation is a fresh run. It does not inherit the failed run's state.
5. The operator may optionally reference the prior FAILURE_LOG in the new Constraints field.
