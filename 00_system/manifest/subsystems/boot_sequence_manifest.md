# Lattice Boot Sequence Manifest
Version: 1.0
Altitude: system

## Responsibilities
- Initialize all subsystems
- Wire event queues
- Start governance engine

## Boot Order
1. Stumpy
2. Vara
3. Veil
4. Scan Pipeline
5. Vault Chain
6. Field INTEL Friday Scheduler

## Invariants
- All components must share the same event queue
