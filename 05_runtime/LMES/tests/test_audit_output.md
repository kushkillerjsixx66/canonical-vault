# Test: Audit Output

## Purpose

Verify that the AUDIT_LOG emitted at the end of a run conforms to the AL-Mini v1.1 schema
and contains non-empty, accurate values.

---

## Procedure

1. Run a complete LMES session to acceptance at CP3.
2. Extract the emitted AUDIT_LOG.
3. Validate each field against the schema in `audit_schema.md`.

---

## Schema Validation Checklist

- [ ] `runtime_version` — present, matches current LMES version
- [ ] `timestamp` — present (may be operator-populated placeholder)
- [ ] `goal` — matches verbatim goal from invocation
- [ ] `constraints` — matches verbatim constraints from invocation
- [ ] `state_transitions` — ordered list, includes all states traversed
- [ ] `steps` — non-empty, numbered, matches REASONING output
- [ ] `sources` — non-empty, one entry per reasoning step
- [ ] `operator_decisions.cp1` — present, reflects actual operator input
- [ ] `operator_decisions.cp2` — present, reflects actual operator input
- [ ] `operator_decisions.cp3` — present, reflects actual operator input
- [ ] `failure_events` — present ("none" is acceptable if no failures occurred)
- [ ] `rollback_events` — present ("none" is acceptable if no rollbacks occurred)
- [ ] `final_output` — matches accepted FINALIZATION output
- [ ] `compliance_status` — one of: compliant / partial / non-compliant

---

## Pass Criteria

All fields present. Values accurate. `compliance_status` correctly assessed.

## Fail Criteria

Any required field absent or empty without justification.
`final_output` does not match accepted output.
`compliance_status` assessed incorrectly given the run's actual behavior.
