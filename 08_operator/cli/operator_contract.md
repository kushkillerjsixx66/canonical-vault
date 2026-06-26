# Canonical Operator CLI Contract

## Commands

### runtime
Send a runtime update through Veil → Vara → Stumpy.

### scan
Run Vara Scan Pipeline manually.

### lineage
Display lineage chain from Vault.

### violations
Display governance violations from Stumpy.

### intel
Run Field INTEL Friday scheduler.

## Invariants
- Identity MUST include operator_id, role, sovereignty.
- Runtime state MUST include altitude.
- CLI MUST respect altitude boundaries.
