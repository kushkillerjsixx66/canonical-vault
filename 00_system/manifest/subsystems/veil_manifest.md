# Veil Subsystem Manifest
Version: 1.0
Altitude: runtime

## Responsibilities
- Accept operator identity
- Accept runtime altitude/posture
- Emit runtime_update events

## Inputs
- identity
- runtime_state

## Outputs
- runtime_update → Vara

## Invariants
- Must not emit epistemic or governance events
- Must validate identity structure
- Must validate altitude/posture format

## Boundaries
- Veil is the ONLY entrypoint for runtime updates
