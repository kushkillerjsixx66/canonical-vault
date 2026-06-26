# Lattice Boot Sequence – Canonical Contract

## Responsibilities
- Start Stumpy governance engine
- Wire Veil → Vara → Stumpy
- Wire Vara Scan Pipeline → Vault Chain → Stumpy
- Wire Field INTEL Friday Scheduler

## API
- start() → dict of components
- stop() → shuts down Stumpy

## Invariants
- Stumpy MUST be started before any events are emitted
- Veil/Vara/Scan Pipeline MUST share the same event queue
