# R-14 Active Constraint Register

**Source:** LGR-2026-09-002 §2.2 and §2.3
**Retention:** LONG

| ID | Type | Scope | Enforcement Layer | Status | Last Validated |
|---|---|---|---|---|---|
| SC-001 | Structural | Kernel Layer — Node Bindings | CEL-Structural / Static Analyzer | ACTIVE | 2026-09-01 22:14 EDT |
| SC-002 | Structural | Operator Dispatch — Tier 1 Primitives | CEL-Structural / Binding Registry | REMEDIATED | 2026-08-29 09:47 EDT |
| SC-003 | Referential | Lineage Propagation Chains — All Strata | CEL-Referential / Propagation Auditor | ACTIVE | 2026-09-01 22:14 EDT |
| SC-004 | Referential | Visibility Inheritance References | CEL-Referential / Visibility Registry | UNDER REVIEW | 2026-08-30 14:02 EDT |
| SC-005 | Temporal | KVSP Epoch Synchronization Events | CEL-Temporal / KVSP Sequencer | ACTIVE | 2026-09-01 22:14 EDT |
| SC-006 | Temporal | Governance Envelope — External Sync | CEL-Temporal / Envelope Controller | REMEDIATED | 2026-08-31 17:33 EDT |
| SC-007 | Compositional | Composite Operator Class Assemblies | CEL-Compositional / Composition Checker | ACTIVE | 2026-09-01 22:14 EDT |
| SC-008 | Compositional | Cross-Stratum Binding Assemblies | CEL-Compositional / Cross-Stratum Validator | REMEDIATED | 2026-08-28 11:58 EDT |

## R-14 canonical changes
- SC-002: Primitive dispatch is restricted to kernel/inner-stratum targets; envelope-stratum targets require a valid CSPG before activation.
- SC-006: External envelope synchronization must complete within its initiating epoch, or be suspended and resumed under a registered ESSA.
- SC-008: Cross-stratum assemblies with visibility differential of two or more levels require a registered VIS interposition before activation.

SC-004 remains UNDER REVIEW with its provisional boundary maintained. This is a current canonical status, not a resolved status.
