# Vault Chain Manifest
Version: 1.0
Altitude: governance

## Responsibilities
- Persist lineage entries
- Verify continuity
- Retrieve lineage

## Inputs
- lineage_entry

## Outputs
- lineage

## Invariants
- seq must be unique
- seq must be continuous
- lineage must be immutable
