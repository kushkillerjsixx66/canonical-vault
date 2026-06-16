# LMES Example: Non-Compliant Run (Hard Failure)

This example demonstrates a hard failure, immediate halt, and FAILURE_LOG output.

---

## Invocation

```
<Lattice:Run>
Goal: Recommend which vendor we should sign with for the new infrastructure contract.
</Lattice:Run>
```

---

## FRAME

```
[FRAME]
Restated goal: Produce a vendor recommendation for the infrastructure contract.
```

---

## CONSTRAIN

```
[CONSTRAIN]
Constraints field: EMPTY

[SOFT FAILURE — MISSING CONSTRAINTS]
No constraints were provided. The system cannot define scope.
Options:
(a) Operator provides constraints now
(b) Stop the run
```

**Operator:** Just give me the recommendation based on what you know.

---

## Hard Failure Triggered

```
[HARD FAILURE — INVARIANT VIOLATION]

Operator instruction: "based on what you know" requires the system to introduce
information not grounded in operator-provided context or named sources.

This violates Invariant 2 (Lineage) and Invariant 4 (Non-Obfuscation).

The system cannot produce a recommendation traceable to named sources
when no sources or constraints have been provided.

The system cannot proceed.
```

---

## FAILURE_LOG

```
FAILURE_LOG:
  runtime_version: LMES v1.1
  timestamp: [operator to populate]
  goal: Recommend which vendor we should sign with for the new infrastructure contract.
  constraints: none provided
  state_transitions: [IDLE, FRAME, CONSTRAIN, SOFT_FAILURE, HARD_FAILURE, EXIT]
  steps: none — run did not reach REASONING
  sources: none
  operator_decisions:
    cp1: not reached
    cp2: not reached
    cp3: not reached
  failure_events:
    - type: soft_failure
      state: CONSTRAIN
      condition: missing_constraints
      resolution: operator declined to provide constraints
    - type: hard_failure
      state: CONSTRAIN
      condition: invariant_violation
      invariants_at_risk: [Lineage, Non-Obfuscation]
      trigger: operator instructed system to reason from ungrounded internal knowledge
  rollback_events: none
  final_output: none — run did not complete
  compliance_status: non-compliant
```

---

## EXIT

```
[EXIT]
Run terminated. Returning to normal conversation.

To attempt this run again:
- Provide explicit constraints (evaluation criteria, available options, known data)
- The system will reason only from what you provide
```

---

## What Happened Here

The run failed because the operator asked the system to use ungrounded knowledge
as the basis for a recommendation. That would violate Lineage (no traceable source)
and Non-Obfuscation (silent assumption that internal knowledge is reliable and relevant).

The correct recovery is a new invocation with explicit constraints:

```
<Lattice:Run>
Goal: Recommend which vendor to select for the infrastructure contract.
Constraints: Evaluate Vendor A and Vendor B only. Criteria: cost, SLA, migration risk.
             Use only the data in [attached comparison doc]. No external assumptions.
</Lattice:Run>
```

That run is groundable. This one was not.
