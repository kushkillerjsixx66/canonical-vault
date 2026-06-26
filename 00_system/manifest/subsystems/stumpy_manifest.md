# Stumpy Governance Engine Manifest
Version: 1.0
Altitude: governance

## Responsibilities
- Enforce invariants
- Detect violations
- Maintain violation log
- Process governance hooks

## Inputs
- epistemic_violation
- vault_promotion

## Outputs
- governance_violation

## Invariants
- Must validate lineage continuity
- Must validate promotion integrity
- Must persist all violations
