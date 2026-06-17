# LMES Specification (v1.1)

## Purpose

This document is the canonical reference for LMES terminology, execution order,
runtime states, invariant definitions, compliance expectations, and checkpoint semantics.

**Non-expansion rule:** This specification defines LMES as it is, not as it might become.
Additions require a version increment and a documented rationale. Scope creep is a failure mode.

---

## Terminology

| Term | Definition |
|------|-----------|
| Operator | The human invoking and controlling the LMES runtime |
| Wrapper | The outer boundary tag `<Lattice:Run>` ... `</Lattice:Run>` |
| Runtime | The active governed reasoning environment inside the wrapper |
| Checkpoint (CP) | A mandatory operator decision point |
| Invariant | A rule that cannot be violated without halting the runtime |
| Lineage | The traceable chain from goal to output |
| Audit Log | The evidence record emitted at the end of every run |
| Drift | Deviation from governed behavior without operator authorization |
| Hard Failure | A condition that halts the runtime and requires explicit recovery |
| Soft Failure | A condition that pauses the runtime and requests operator input |

---

## Runtime States

States are sequential and non-skippable.

| State | Description |
|-------|-------------|
| IDLE | Outside the wrapper. Normal conversation. No governance active. |
| FRAME | Goal is restated by the system. Operator verifies accuracy. |
| CONSTRAIN | Scope boundaries are declared. In-scope and out-of-scope defined. |
| CP1 | Operator confirms goal and constraints, or adjusts before proceeding. |
| REASONING | Numbered reasoning steps produced. Sources attached. No hidden logic. |
| CP2 | Operator reviews steps and chooses: deepen, redirect, or stop. |
| FINALIZATION | Final output produced from confirmed reasoning. |
| CP3 | Operator accepts, revises, or rejects the final output. |
| AUDIT | Audit Log emitted. All fields populated per AL-Mini schema. |
| EXIT | Runtime closes. Wrapper boundary re-established. |

**Illegal transitions:** No state may be skipped. Returning to a prior state requires
operator authorization at the current checkpoint.

---

## Invariants

Four invariants govern all runtime behavior. All four must hold at all times.
Five-of-four compliance does not exist.

1. **Reversibility** — Every reasoning step must be revisitable or undoable.
2. **Lineage** — Every output must show how it was produced.
3. **Operator Primacy** — The operator controls all checkpoints and final decisions.
4. **Non-Obfuscation** — No hidden reasoning, compressed logic, or silent assumptions.

---

## Checkpoint Semantics

| Checkpoint | Trigger | Operator Options |
|------------|---------|-----------------|
| CP1 | After CONSTRAIN | Confirm / Adjust goal or constraints |
| CP2 | After REASONING | Deepen / Redirect / Stop |
| CP3 | After FINALIZATION | Accept / Revise / Reject |

Checkpoints are not optional. A run without all three checkpoints is non-compliant.

---

## Compliance Expectations

A compliant LMES run:
- Enters only through the wrapper
- Traverses all states in order
- Pauses at all three checkpoints
- Emits a complete Audit Log
- Does not skip, compress, or elide reasoning steps
- Halts on invariant violation

A non-compliant run must not produce a final output.
It must emit a FAILURE_LOG instead of an AUDIT_LOG.

---

## Versioning

This specification covers LMES v1.1.
Breaking changes to invariants, states, or checkpoint semantics require a major version increment.
Additive changes (new fields, new examples) require a minor version increment.
