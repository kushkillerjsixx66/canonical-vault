# Canonical Vault Integration Contract for Vara Scan

## Responsibilities

### VaultScanStore
- Persist VaraScanResult to Vault.
- Use lineage seq as filename.
- Store JSON with:
  - weak_signals
  - trends
  - anomalies
  - unspecified
  - lineage

### VaultScanPromoter
- Promote scan if:
  - lineage exists
  - AND (weak signals OR anomalies exist)

### VaultScanIntegrity
- Validate:
  - lineage entries contain seq/operator_id/role/altitude
  - weak signals contain key/description/evidence
  - anomalies contain field/value/reason

## Invariants
- Vault MUST NOT accept invalid scans.
- Promotion MUST be deterministic.
- Lineage MUST be preserved exactly.
