# Lattice Minimal Executable System (LMES v1.1)

LMES is the smallest deployable version of the Lattice architecture.
It preserves the essential governance invariants while remaining simple
enough to instantiate in any text-based environment.

LMES is a runtime governance shell for bounded reasoning execution.
Governance is the mechanism. Runtime is the environment. Reasoning is the payload.

## What LMES Provides

- A hard boundary between normal conversation and governed reasoning
- A runtime protocol that enforces structure
- A lineage system that makes reasoning auditable
- A checkpoint system that preserves operator primacy
- A minimal invariant set that prevents drift
- Explicit failure semantics and rollback behavior
- A formal runtime state machine

## Non-Goals

LMES is NOT:
- a general AI alignment framework
- a replacement for human judgment
- an autonomous decision-making system
- a truth engine
- a moral authority structure

LMES exists to improve:
- reasoning visibility
- reversibility
- operator control
- auditability

## Quick Start

Wrap any governed reasoning inside:

```
<Lattice:Run>
Goal: ...
Constraints: ...
</Lattice:Run>
```

The system will:
1. Enter FRAME state — restate the goal
2. Enter CONSTRAIN state — define scope
3. Pause at CP1 — operator confirms
4. Enter REASONING state — produce steps + sources
5. Pause at CP2 — operator directs
6. Enter FINALIZATION state — produce output
7. Pause at CP3 — operator accepts/revises/rejects
8. Enter AUDIT state — emit Audit Log
9. EXIT

## Model-Agnostic

LMES requires no infrastructure beyond text.
All governance is structural, not platform-dependent.

## Version

LMES v1.1

## License

Open use permitted as long as invariants remain intact.
