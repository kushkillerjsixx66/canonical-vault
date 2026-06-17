# LMES Example: Recovery from Soft Failure

This example demonstrates a soft failure mid-run, operator recovery, and compliant completion.

---

## Invocation

```
<Lattice:Run>
Goal: Identify the top three risks in our current data pipeline architecture.
Constraints: Based on known system components only. No cost analysis.
</Lattice:Run>
```

---

## FRAME

```
[FRAME]
Restated goal: Surface the three highest-priority risks present in the
current data pipeline architecture, based on known components.
```

---

## CONSTRAIN

```
[CONSTRAIN]
In scope: Architectural risks in known pipeline components.
Out of scope: Cost analysis, vendor comparison, remediation planning.
Flagged gaps: "Known system components" — system will proceed on operator-provided
context only. No external system knowledge will be assumed.
```

---

## CP1

```
[CP1]
Confirm or Adjust?
```

**Operator:** Confirm.

---

## REASONING

```
[REASONING]

1. Component A (ingestion layer): High fan-in from 12 upstream sources with no
   dead-letter queue. Risk: silent data loss on source failure.
   Source: Operator-provided architecture context.

2. Component B (transformation service): Stateful processing with no checkpoint
   recovery. Risk: full reprocessing required on any failure.
   Source: Operator-provided architecture context.

3. Component C (output routing): [SOFT FAILURE — REASONING GAP]
```

---

## Soft Failure Surfaced

```
[SOFT FAILURE — REASONING GAP]
Step 3 cannot be grounded. No information about Component C (output routing)
was provided in the operator's context. The system cannot assess its risk profile
without making ungrounded assumptions.

Options:
(a) Operator provides Component C context now — reasoning continues
(b) Exclude Component C — surface next known risk if available
(c) Stop the run with a partial audit log
```

**Operator:** Option (a). Component C is a fan-out router to 6 downstream consumers
with no retry logic and synchronous delivery.

---

## REASONING (continued)

```
3. Component C (output routing): Synchronous fan-out to 6 consumers with no retry
   logic. Risk: single slow consumer creates backpressure that stalls the entire
   routing layer.
   Source: Operator-provided context (added at soft failure recovery).
```

---

## CP2

```
[CP2]
Reasoning complete. How should we proceed?
Options: Deepen / Redirect / Stop
```

**Operator:** Proceed.

---

## FINALIZATION

```
[FINALIZATION]
Output: Top 3 Data Pipeline Risks

Risk 1: Silent data loss (ingestion layer) — no dead-letter queue on 12-source fan-in.
Risk 2: Full reprocessing on failure (transformation) — stateful, no checkpoint recovery.
Risk 3: Synchronous fan-out backpressure (output routing) — no retry, 6 downstream consumers.

Traceable to steps: 1, 2, 3
```

---

## CP3

```
[CP3]
Accept / Revise / Reject?
```

**Operator:** Accept.

---

## AUDIT_LOG

```
AUDIT_LOG:
  runtime_version: LMES v1.1
  timestamp: [operator to populate]
  goal: Identify the top three risks in our current data pipeline architecture.
  constraints: Based on known system components only. No cost analysis.
  state_transitions: [IDLE, FRAME, CONSTRAIN, CP1, REASONING, SOFT_FAILURE, REASONING(resumed), CP2, FINALIZATION, CP3, AUDIT, EXIT]
  steps: [see REASONING above, including resumed step 3]
  sources: [operator-provided architecture context throughout]
  operator_decisions:
    cp1: Confirm
    cp2: Proceed
    cp3: Accept
  failure_events:
    - type: soft_failure
      state: REASONING
      condition: reasoning_gap
      step: 3
      resolution: operator provided missing context
  rollback_events: none
  final_output: [see FINALIZATION above]
  compliance_status: partial
```

*Note: `compliance_status: partial` because a soft failure occurred.
The run is still valid. The failure event is recorded. The output is grounded.*

---

## EXIT

```
[EXIT]
Run complete. Returning to normal conversation.
```
