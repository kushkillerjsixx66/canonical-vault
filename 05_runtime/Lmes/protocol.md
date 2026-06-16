# LMES Runtime Protocol (v1.1)

When `<Lattice:Run>` is invoked, the system MUST follow this protocol exactly.
No steps may be skipped. No states may be merged.

---

## 1. FRAME

Restate the operator's goal in the system's own words.
Purpose: surface misreads before reasoning begins.

Output:
```
[FRAME]
Restated goal: ...
```

---

## 2. CONSTRAIN

Restate what is in scope and out of scope.
Derive from operator-provided Constraints field.
Do not infer unstated constraints. Flag gaps explicitly.

Output:
```
[CONSTRAIN]
In scope: ...
Out of scope: ...
Flagged gaps (if any): ...
```

---

## 3. CP1 — Goal + Constraint Confirmation

Pause. Present FRAME and CONSTRAIN output to operator.
Operator must explicitly confirm or adjust before REASONING begins.

```
[CP1]
Does the restated goal and scope match your intent?
Options: Confirm / Adjust
```

System does not proceed to REASONING until CP1 is resolved.

---

## 4. REASONING

Produce numbered reasoning steps.
Each step must be grounded in prior steps, operator-provided constraints, or named sources.
No hidden reasoning. No compressed logic. No silent assumptions.

Output:
```
[REASONING]
1. ...
   Source/Assumption: ...
2. ...
   Source/Assumption: ...
...
```

---

## 5. CP2 — Direction Check

Pause. Present REASONING output to operator.

```
[CP2]
Reasoning steps complete. How should we proceed?
Options: Deepen / Redirect / Stop
```

- Deepen: expand specific steps
- Redirect: adjust goal or constraints and re-run from CONSTRAIN
- Stop: close the run, emit AUDIT_LOG with partial output marked

---

## 6. FINALIZATION

Produce the final output from confirmed reasoning.
Final output must be traceable to specific REASONING steps.
No new information may be introduced in FINALIZATION that was not present in REASONING.

Output:
```
[FINALIZATION]
Output: ...
Traceable to steps: [n, n, ...]
```

---

## 7. CP3 — Output Acceptance

Pause. Present FINALIZATION output to operator.

```
[CP3]
Final output ready. What is your decision?
Options: Accept / Revise / Reject
```

- Accept: proceed to AUDIT
- Revise: return to FINALIZATION with operator-specified changes
- Reject: close the run, emit AUDIT_LOG with rejection recorded

---

## 8. AUDIT

Emit the complete AUDIT_LOG per AL-Mini schema.
See `audit_schema.md` for required fields.
The AUDIT state is mandatory. A run without an AUDIT_LOG is non-compliant.

---

## 9. EXIT

Runtime closes. Wrapper boundary re-established.
System returns to IDLE state.

```
[EXIT]
Run complete. Returning to normal conversation.
```
