# Field INTEL Friday Scheduler — Canonical Contract

## Responsibilities
- Load lineage from Vault Chain
- Run Vara Scan Pipeline across all artifacts
- Collect scan results
- Generate weekly intelligence report
- Store report in Vault

## Inputs
- artifacts: list of dicts
- runtime_state: dict (altitude, posture, etc.)

## Outputs
- path to stored Field INTEL Friday report

## Invariants
- lineage MUST be preserved
- scan pipeline MUST run deterministically
- report MUST include weak signals, anomalies, trends
