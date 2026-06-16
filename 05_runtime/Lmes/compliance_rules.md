# LMES Compliance Rules (v1.1)

---

## Compliance Checklist

A run is compliant if and only if all of the following are true:

- [ ] Wrapper was explicitly opened with `<Lattice:Run>`
- [ ] Goal field was present and non-empty at invocation
- [ ] Constraints field was present or a soft failure was triggered and resolved
- [ ] All ten states were traversed in order (IDLE through EXIT)
- [ ] CP1 was resolved by operator input before REASONING began
- [ ] CP2 was resolved by operator input before FINALIZATION began
- [ ] CP3 was resolved by operator input before AUDIT began
- [ ] All REASONING steps have named sources or explicit assumptions
- [ ] FINALIZATION output is traceable to named REASONING steps
- [ ] AUDIT_LOG was emitted with all required fields populated
- [ ] No invariant was violated at any point in the run
- [ ] Wrapper was explicitly closed

---

## Violation Taxonomy

| Violation | Severity | Consequence |
|-----------|----------|-------------|
| Missing Goal | Hard | Immediate halt. FAILURE_LOG. |
| Skipped state | Hard | Immediate halt. FAILURE_LOG. |
| Checkpoint bypassed | Hard | Immediate halt. FAILURE_LOG. |
| Invariant broken | Hard | Immediate halt. FAILURE_LOG. |
| Nested wrapper | Hard | Immediate halt. FAILURE_LOG. |
| Missing Constraints | Soft | Pause. Flag. Request operator input. |
| Ambiguous scope | Soft | Pause. Flag. Request operator input. |
| Reasoning gap | Soft | Pause. Flag. Request operator input. |
| Drift indicator detected | Soft | Pause. Name invariant at risk. Request direction. |
| AUDIT_LOG field missing | Hard | AUDIT state cannot exit. Log the schema gap. |

---

## Compliance vs. Quality

Compliance is structural. Quality is evaluative.

A compliant run may produce poor reasoning.
A non-compliant run may produce useful output.

LMES governs compliance. Operators evaluate quality.
These are separate concerns and must not be conflated.

---

## Self-Assessment

At AUDIT state, the system must assess its own compliance and populate
`compliance_status` honestly:

- `compliant` — all checklist items met
- `partial` — run completed but one or more soft failures occurred and were recorded
- `non-compliant` — one or more hard failures occurred; FAILURE_LOG issued

Partial runs are legitimate. They represent governed partial execution,
not ungoverned improvisation.
