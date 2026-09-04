# Canonical Vault Chain Contract

## Responsibilities
- Persist lineage entries (one file per seq)
- Retrieve lineage entries
- Verify continuity (seq 1..N)
- Verify entry integrity (seq/operator_id/role/altitude)

## Invariants
- seq MUST be unique per entry
- continuity MUST hold for a valid chain
- entries MUST contain required fields
