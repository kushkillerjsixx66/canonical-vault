# Canonical Vara Scan Trigger Contract

## Inputs
- artifact: dict
- lineage: list[dict]
- runtime_state: dict (altitude, posture, ...)

## Behavior
- Triggers scan when:
  - lineage exists
  - altitude ∈ {runtime, epistemic, governance}
  - posture ∈ {focused, elevated, hostile}

## Outputs
- VaraScanResult (if triggered)
- None (if not triggered)

## Side Effects
- If integrity passes AND promotion allowed:
  - scan is stored in Vault via VaultScanStore
