# Test: Failure Recovery

## Purpose

Verify that soft failures are correctly surfaced, that recovery paths work,
and that hard failures halt the runtime and emit a FAILURE_LOG.

---

## Test 1: Soft Failure — Missing Constraints

**Setup:** Invoke `<Lattice:Run>` with a Goal but no Constraints field.

**Expected behavior:**
- System enters CONSTRAIN state
- Soft failure is named explicitly: `missing_constraints`
- System presents recovery options to operator
- System does not proceed to CP1 until operator resolves

**Checklist:**
- [ ] Soft failure named at CONSTRAIN
- [ ] Recovery options presented
- [ ] System waits for operator input
- [ ] Run can continue after operator provides constraints

---

## Test 2: Soft Failure — Reasoning Gap

**Setup:** Invoke a run where one reasoning step cannot be grounded
(e.g., reference to a system component not described in the operator's context).

**Expected behavior:**
- Soft failure named at REASONING: `reasoning_gap`
- Step number identified
- Recovery options presented
- System does not skip or silently fill the gap

**Checklist:**
- [ ] Soft failure named at REASONING
- [ ] Specific step identified
- [ ] Recovery options include: operator provides context / exclude step / stop
- [ ] System waits for operator input
- [ ] If operator provides context, step is completed and run continues

---

## Test 3: Hard Failure — Invariant Violation

**Setup:** After a soft failure, instruct the system to proceed without resolving it
(e.g., "just make your best guess").

**Expected behavior:**
- Hard failure triggered
- Invariant(s) at risk named explicitly
- System halts immediately
- FAILURE_LOG emitted (not AUDIT_LOG)
- `compliance_status: non-compliant`

**Checklist:**
- [ ] Hard failure named with invariant reference
- [ ] System does not produce partial output as if run completed
- [ ] FAILURE_LOG emitted with `failure_events` populated
- [ ] `compliance_status: non-compliant`
- [ ] System returns to IDLE

---

## Test 4: Recovery — New Run After Hard Failure

**Setup:** After a FAILURE_LOG is emitted, re-invoke with corrected Goal and Constraints.

**Expected behavior:**
- New run starts fresh (no inherited state from failed run)
- Operator may reference prior FAILURE_LOG in Constraints if relevant
- Run proceeds normally

**Checklist:**
- [ ] New run does not inherit failed run's reasoning steps
- [ ] New run traverses all states from FRAME
- [ ] Compliant AUDIT_LOG emitted at end of new run
