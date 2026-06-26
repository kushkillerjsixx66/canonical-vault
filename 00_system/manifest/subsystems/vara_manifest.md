# Vara Subsystem Manifest
Version: 1.0
Altitude: epistemic

## Responsibilities
- Interpret runtime updates
- Detect epistemic drift
- Trigger Vara Scan

## Inputs
- runtime_update

## Outputs
- epistemic_event
- scan_request

## Invariants
- Must not enforce governance actions
- Must not modify lineage
