# Vara Scan Pipeline Manifest
Version: 1.0
Altitude: epistemic → governance

## Responsibilities
- Run Vara Scan
- Validate integrity
- Promote to Vault
- Emit governance events

## Inputs
- artifact
- lineage
- runtime_state

## Outputs
- vault_promotion
- epistemic_violation

## Invariants
- Must validate scan integrity
- Must validate lineage before promotion
