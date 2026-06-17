# LMES Example: Operational Run

---

## Invocation

```
<Lattice:Run>
Goal: Draft a fast, fair interview loop for a senior engineer.
Constraints: Avoid bias, small team, no legal advice.
</Lattice:Run>
```

---

## FRAME

```
[FRAME]
Restated goal: Design a structured, bias-aware interview process for a
senior engineering candidate, appropriate for a small team context.
```

---

## CONSTRAIN

```
[CONSTRAIN]
In scope: Interview stages, signal definition, scoring approach, bias reduction mechanisms.
Out of scope: Legal compliance, compensation negotiation, offer process.
Flagged gaps: "Fast" is ambiguous — does it mean fewer stages, shorter per-stage, or both?
```

---

## CP1

```
[CP1]
Does the restated goal and scope match your intent?
"Fast" is flagged as ambiguous. Please clarify: fewer stages, shorter duration, or both?
Options: Confirm / Adjust
```

**Operator:** Adjust. "Fast" means fewer stages — target 3 stages maximum.

---

## REASONING

```
[REASONING]

1. Define the signals the process must surface: technical depth, judgment, collaboration.
   Source: Standard senior engineering evaluation criteria.

2. Map signals to stages (3-stage constraint):
   - Stage 1: Async technical screen (45 min) — assesses problem-solving approach
   - Stage 2: Live technical interview (60 min) — assesses depth and collaboration
   - Stage 3: Values/judgment conversation (45 min) — assesses culture fit and decision-making
   Source: Operator constraint (≤3 stages), standard interview design patterns.

3. Define scoring per stage: structured rubric with defined signals, not holistic impression.
   Source: Assumption — holistic scoring is the primary vector for unconscious bias.

4. Bias reduction mechanisms:
   - Standardized questions per stage (same questions for every candidate)
   - Separate scoring from discussion (each interviewer scores independently before debrief)
   - Structured debrief agenda (signal-by-signal, not candidate-by-candidate)
   Source: Evidence-based interviewing practices.

5. Small team considerations: Limit interview panel to 2–3 people per stage.
   Avoid scheduling fatigue by batching stages on the same day where possible.
   Source: Operator constraint (small team).
```

---

## CP2

```
[CP2]
Reasoning steps complete. How should we proceed?
Options: Deepen / Redirect / Stop
```

**Operator:** Proceed to finalization.

---

## FINALIZATION

```
[FINALIZATION]
Output: Senior Engineer Interview Loop (3-Stage)

Stage 1 — Async Technical Screen (45 min)
  Signal: Problem-solving approach and communication clarity.
  Format: Take-home or async prompt. Standardized rubric. Scored before Stage 2.

Stage 2 — Live Technical Interview (60 min)
  Signal: Technical depth, reasoning under pressure, collaboration.
  Format: Structured problem + debrief. Same prompt for all candidates. Independent scoring.

Stage 3 — Judgment and Values Conversation (45 min)
  Signal: Decision-making, culture alignment, intellectual honesty.
  Format: Standardized scenario questions. Independent scoring before debrief.

Bias reduction: Standardized questions. Independent pre-debrief scoring.
Structured debrief agenda: evaluate signals, not candidates holistically.

Traceable to steps: 1, 2, 3, 4, 5
```

---

## CP3

```
[CP3]
Final output ready. What is your decision?
Options: Accept / Revise / Reject
```

**Operator:** Accept.

---

## AUDIT_LOG

```
AUDIT_LOG:
  runtime_version: LMES v1.1
  timestamp: [operator to populate]
  goal: Draft a fast, fair interview loop for a senior engineer.
  constraints: Avoid bias, small team, no legal advice. Fast = ≤3 stages.
  state_transitions: [IDLE, FRAME, CONSTRAIN, CP1, CONSTRAIN(adjust), CP1, REASONING, CP2, FINALIZATION, CP3, AUDIT, EXIT]
  steps: [see REASONING above]
  sources: [standard interview design, bias reduction practices, operator constraints]
  operator_decisions:
    cp1: Adjust — clarified "fast" as ≤3 stages
    cp2: Proceed
    cp3: Accept
  failure_events: none
  rollback_events: CP1 → CONSTRAIN (scope clarification)
  final_output: [see FINALIZATION above]
  compliance_status: compliant
```

---

## EXIT

```
[EXIT]
Run complete. Returning to normal conversation.
```
