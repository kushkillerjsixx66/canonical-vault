# Canonical Vara Scan Contract

## Inputs
- artifact: dict
- lineage: list of lineage entries

## Outputs
- VaraScanResult:
  - weak_signals
  - trends
  - anomalies
  - unspecified
  - lineage

## Invariants
- lineage MUST be preserved
- weak signals MUST be extracted deterministically
- anomalies MUST reflect structural gaps
- trends MUST be derived from weak signals
