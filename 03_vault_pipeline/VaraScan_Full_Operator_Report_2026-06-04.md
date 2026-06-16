# Vara:Scan — Full Operator Report

**Scan ID:** bd79fb33-a533-4fd9-8da1-4f5181f7641a
**Generated:** 2026-06-04T11:45:00-04:00 (EDT)
**Operator:** Jermo / Lattice · Veil
**Pipeline:** IDE → CCE → CFC → Executor
**CCE Config:** strict_mode=true · allow_relaxation=true · conflict_threshold=0.50 · min_severity=advisory

---

## Executive Decision

**OVERALL DECISION: BLOCK**

- 2 HARD — Execution must halt pending resolution
- 3 SOFT — Human review required
- 7 DRIFT — Acknowledged; execution can proceed with awareness
- 7 CLEAR — No issues
- 3 ADVISORY — Informational only

**Verdict:** Two HARD violations detected across Structural and Execution planes. Dangling dependency detection is post-hoc only, and batch exception swallowing eliminates the audit trail for failed items. Pipeline execution must be gated pending resolution of both HARD findings.

---

## Plane Summary Table

| Plane | Harvester | Status | Confidence | Findings |
|---|---|---|---|---|
| P1 · Temporal | TemporalHarvester-v1 | NOMINAL | 0.94 | 3 |
| P2 · Semantic | SemanticHarvester-v1 | DEGRADED | 0.81 | 3 |
| P3 · Permission | PermissionHarvester-v1 | NOMINAL | 0.91 | 2 |
| P4 · Resource / Capacity | ResourceHarvester-v1 | DEGRADED | 0.79 | 3 |
| P5 · Structural / Dependency | StructuralHarvester-v1 | ALERT | 0.72 | 4 |
| P6 · Execution / Runtime | ExecutionHarvester-v1 | ALERT | 0.75 | 4 |

---

## Plane Detail

### P1 · Temporal — NOMINAL (0.94)
- **T-1 CLEAR** — Sequential task ordering verified. IDE Decomposer _infer_priority correctly elevates index=0 tasks to HIGH.
- **T-2 ADVISORY DRIFT** — Single-task decompositions carry -0.15 confidence penalty. Resolution: Supply richer intent text or explicit agent_hints.
- **T-3 CLEAR** — Temporal keyword extraction intact.

### P2 · Semantic — DEGRADED (0.81)
- **S-1 CLEAR** — Semantic constraint extraction enabled and validated.
- **S-2 LOW DRIFT** — Decomposer action-verb coverage gap — 'transform' keyword family missing synonyms: compile, synthesize, distill, emit. Resolution: Extend _KW_TRANSFORM.
- **S-3 MEDIUM CONFLICT** — Semantic conflict resolution lacks explicit hint for all-BLOCKING maps. Resolution: Ensure resolver generates non-null conflict_hint for BLOCKING-only maps.

### P3 · Permission — NOMINAL (0.91)
- **PR-1 CLEAR** — Permission-permission resolver registered.
- **PR-2 ADVISORY DRIFT** — No PERMISSION constraint type enumerated in public CCE models. Resolution: Add PERMISSION to formal ConstraintType enum.

### P4 · Resource / Capacity — DEGRADED (0.79)
- **R-1 CLEAR** — Resource/capacity constraint extraction active.
- **R-2 LOW DRIFT** — max_constraints=200 threshold produces warning, not error. Resolution: Add secondary ceiling max_constraints_hard=500 as hard error.
- **R-3 MEDIUM CONFLICT** — Edge weight threshold at 0.50 may suppress weak resource conflicts. Resolution: Lower threshold to 0.30 for resource-plane edges.

### P5 · Structural / Dependency — ALERT (0.72)
- **ST-1 CLEAR** — CCE edge structural checks fully operational.
- **ST-2 CLEAR** — CFC lineage tracking intact.
- **ST-3 LOW DRIFT** — Decomposer parallel-branch aggregation task uses generic description. Resolution: Derive description and agent_hint from intent's primary action context.
- **ST-4 HIGH VIOLATION — HARD — NOT RECOVERABLE** — Dangling dependency detection is post-hoc, not pre-execution gated. Decomposer._collect_warnings checks dangling depends_on IDs after tasks are built. Warnings returned to caller but do NOT raise DecompositionError. An executor receiving a DecompositionResult with dangling deps may deadlock or fail silently. **Resolution: Promote dangling-dependency detection to a hard error inside decompose() before returning.**

### P6 · Execution / Runtime — ALERT (0.75)
- **E-1 CLEAR** — CFC crash-free boundary active. RecoveryEngine wraps all recovery actions in try/except.
- **E-2 ADVISORY DRIFT** — QUARANTINE path: re-validation pathway not documented. Resolution: Document a QUARANTINE exit procedure. Expose as quarantine_exit_procedure in CFCConfig.
- **E-3 MEDIUM CONFLICT** — raise_on_invalid=False silently proceeds past intent validation failures. Resolution: Add minimum-validity gate.
- **E-4 HIGH VIOLATION — HARD — NOT RECOVERABLE** — Batch decomposition swallows exceptions when raise_on_invalid=False. decompose_batch() catches broad Exception and logs at ERROR level, then continues. Failed batch items produce no CFCReport, leaving executor with partial results and no audit trail. **Resolution: Emit a synthetic CFCReport(decision=BLOCK) for each failed batch item.**

---

## Remediation Priority Queue

| Priority | Plane | Finding | Action Required |
|---|---|---|---|
| P0 — HARD | P5 Structural | ST-4 | Promote dangling-dep check to hard error in decompose() |
| P0 — HARD | P6 Execution | E-4 | Emit synthetic CFCReport(BLOCK) for failed batch items |
| P1 — SOFT | P2 Semantic | S-3 | Add fallback conflict_hint for BLOCKING-only maps |
| P1 — SOFT | P4 Resource | R-3 | Lower conflict_weight_threshold to 0.30 for resource plane |
| P1 — SOFT | P6 Execution | E-3 | Add intent validity gate before CCE handoff |
| P2 — DRIFT | P2 Semantic | S-2 | Extend _KW_TRANSFORM keyword set |
| P2 — DRIFT | P4 Resource | R-2 | Add max_constraints_hard ceiling |
| P2 — DRIFT | P5 Structural | ST-3 | Derive aggregation task agent_hint from intent context |
| P2 — DRIFT | P6 Execution | E-2 | Document QUARANTINE exit procedure |
| P3 — ADVISORY | P3 Permission | PR-2 | Formalize PERMISSION in ConstraintType enum |
| P3 — ADVISORY | P1 Temporal | T-2 | Document single-task confidence penalty |

---

**Vara:Scan v1.0 · Lattice / Veil / VaraVault · 2026 Jermo**
