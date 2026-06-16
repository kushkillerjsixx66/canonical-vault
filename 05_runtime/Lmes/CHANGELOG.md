# LMES Changelog

---

## v1.1 — Current

### Added
- `specification.md` — canonical reference for terminology, states, semantics, compliance
- `lmes_runtime/failure_modes.md` — hard/soft failure conditions, rollback rules, drift indicators
- `lmes_runtime/runtime_states.md` — formal state machine definition
- `lmes_runtime/compliance_rules.md` — compliance checklist and violation taxonomy
- `operators/governance_examples.md` — extended governance scenarios
- `examples/recovery_example.md` — governed recovery from a soft failure
- `examples/failed_run_example.md` — non-compliant run with FAILURE_LOG output
- `tests/test_failure_recovery.md` — failure and recovery test procedure
- `tests/test_checkpoint_integrity.md` — checkpoint completeness test procedure
- `CHANGELOG.md` — this file

### Changed
- `README.md` — updated framing: "runtime governance shell for bounded reasoning execution"
- `README.md` — added Non-Goals section
- `lmes_runtime/audit_schema.md` — added fields: `runtime_version`, `timestamp`, `failure_events`, `rollback_events`, `state_transitions`

### Invariants
No invariants were changed. Reversibility, Lineage, Operator Primacy, Non-Obfuscation remain the complete set.

---

## v1.0 — Initial Release

### Added
- `README.md`
- `lmes_runtime/wrapper.md`
- `lmes_runtime/protocol.md`
- `lmes_runtime/invariants.md`
- `lmes_runtime/audit_schema.md`
- `operators/onboarding.md`
- `operators/quickstart.md`
- `examples/strategic_example.md`
- `examples/operational_example.md`
- `tests/test_runtime_behavior.md`
- `tests/test_audit_output.md`
- `diagrams/lmes_architecture.png` (placeholder)
- `diagrams/runtime_flow.png` (placeholder)
