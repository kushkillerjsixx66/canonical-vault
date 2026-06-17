# LMES Example: Strategic Run

---

## Invocation

```
<Lattice:Run>
Goal: Create a 12-month strategy for scaling a startup from 5 to 20 employees.
Constraints: Avoid over-hiring, maintain culture, no legal advice.
</Lattice:Run>
```

---

## FRAME

```
[FRAME]
Restated goal: Produce a phased 12-month hiring and scaling strategy
that grows the team from 5 to 20 while managing culture dilution risk
and avoiding premature or redundant hires.
```

---

## CONSTRAIN

```
[CONSTRAIN]
In scope: Hiring sequence, role prioritization, culture mechanisms,
          risk flags for over-hiring, milestone-based scaling triggers.
Out of scope: Legal structures, employment contracts, compensation modeling.
Flagged gaps: None.
```

---

## CP1

```
[CP1]
Does the restated goal and scope match your intent?
Options: Confirm / Adjust
```

**Operator:** Confirm.

---

## REASONING

```
[REASONING]

1. Baseline assessment: Map existing 5-person team roles and capacity gaps.
   Source: Operator-provided constraint (current team size = 5).

2. Identify highest-leverage hires: Roles that unblock the most other work first.
   Source: Standard hiring sequencing patterns for early-stage teams.

3. Define culture anchors: What behaviors and norms define the current team.
   Source: Assumption — culture at 5 is primarily behavioral, not documented.

4. Establish hiring gates: Revenue, product, or operational triggers that justify each hire.
   Source: Assumption — over-hiring risk is highest when hiring precedes demand signals.

5. Phase hiring waves:
   - Months 1–3: Fill capacity gaps in highest-leverage roles (target: 5→8)
   - Months 4–6: Expand execution capacity (target: 8→13)
   - Months 7–12: Scale operations and specialized functions (target: 13→20)
   Source: Three-wave model based on standard startup scaling patterns.

6. Culture transmission mechanisms: Onboarding, pairing, explicit norm documentation.
   Source: Assumption — culture dilution risk increases at team size inflection points (~10, ~20).

7. Risk flags: Identify roles where over-hiring is most common (sales, ops).
   Source: Common failure modes in seed-to-series-A scaling.
```

---

## CP2

```
[CP2]
Reasoning steps complete. How should we proceed?
Options: Deepen / Redirect / Stop
```

**Operator:** Deepen step 4 — I want more specificity on what the hiring gates look like.

*(System deepens step 4, then returns to CP2.)*

**Operator:** Proceed to finalization.

---

## FINALIZATION

```
[FINALIZATION]
Output: 12-Month Scaling Strategy (5→20)

Phase 1 (Months 1–3): Leverage hires. Identify top 3 capacity gaps. Hire only roles
that unblock 2+ other workstreams. Gate: current team at capacity on core deliverables.

Phase 2 (Months 4–6): Execution expansion. Hire to support proven demand, not projected
demand. Gate: revenue or usage signal confirms need before offer goes out.

Phase 3 (Months 7–12): Operational scaling. Introduce specialization. Gate: team size
consistently exceeding coordination capacity of generalist structure.

Culture mechanisms: Structured onboarding, 90-day pairing assignment, explicit norm
documentation before each hiring wave.

Traceable to steps: 1, 2, 3, 4, 5, 6, 7
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
  goal: Create a 12-month strategy for scaling a startup from 5 to 20 employees.
  constraints: Avoid over-hiring, maintain culture, no legal advice.
  state_transitions: [IDLE, FRAME, CONSTRAIN, CP1, REASONING, CP2, REASONING(deepen), CP2, FINALIZATION, CP3, AUDIT, EXIT]
  steps: [see REASONING above]
  sources: [startup scaling patterns, operator constraints, stated assumptions]
  operator_decisions:
    cp1: Confirm
    cp2: Deepen step 4, then proceed
    cp3: Accept
  failure_events: none
  rollback_events: none
  final_output: [see FINALIZATION above]
  compliance_status: compliant
```

---

## EXIT

```
[EXIT]
Run complete. Returning to normal conversation.
```
