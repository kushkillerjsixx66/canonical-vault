# Vara – Canonical Epistemic Supervisor Contract

## Role

- Supervises Veil runtime state.
- Constructs epistemic context:
  - identity
  - runtime_state
  - lineage
- Emits `epistemic_state` events to Stumpy.

## Event Shape

- `type`: `epistemic_state`
- `source`: `vara`
- `payload`:
  - `identity`: operator identity (must include `operator_id`, `role`, `sovereignty`)
  - `runtime`: Veil runtime state (must include `altitude`)
  - `lineage`: list of entries:
    - `seq`
    - `operator_id`
    - `role`
    - `altitude`

## Invariants

- Every emitted payload MUST include `lineage`.
- `lineage` MUST be a list.
- Each lineage entry MUST include `seq`, `operator_id`, `role`, `altitude`.
- `runtime.altitude` MUST be one of:
  - `runtime`
  - `epistemic`
  - `governance`
  - `operator`
