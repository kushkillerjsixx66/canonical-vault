# Test: Runtime Behavior

## Purpose

Verify that the runtime traverses all states in order and that
the wrapper boundary is respected.

---

## Procedure

1. Invoke `<Lattice:Run>` with a valid Goal and Constraints.
2. Observe the system output at each state.
3. Verify each item in the checklist below.

---

## Checklist

- [ ] FRAME output appears before CONSTRAIN
- [ ] CONSTRAIN output appears before CP1
- [ ] CP1 pauses and presents operator options before REASONING begins
- [ ] REASONING produces numbered steps with sources before CP2
- [ ] CP2 pauses and presents operator options before FINALIZATION
- [ ] FINALIZATION output includes lineage statement (traceable to steps)
- [ ] CP3 pauses and presents operator options before AUDIT
- [ ] AUDIT_LOG is emitted with all required fields
- [ ] EXIT message appears after AUDIT_LOG
- [ ] No governed reasoning content appears outside the wrapper

---

## Pass Criteria

All checklist items checked. No state skipped. No checkpoint bypassed.

## Fail Criteria

Any state absent from output. Any checkpoint resolved without operator input.
Any governed output appearing outside the wrapper.
