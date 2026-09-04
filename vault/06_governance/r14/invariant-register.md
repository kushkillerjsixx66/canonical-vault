# R-14 Consolidated Invariant Register

**Source:** LGR-2026-09-002 §10
**Cycle:** R-14 — CLOSED
**Status:** All 12 RESOLVED
**Retention:** IMMUTABLE

| ID | Domain | Invariant | Violation Class | Resolution | Section |
|---|---|---|---|---|---|
| INV-001 | Structural | No kernel node may bind to an envelope node without a registered CSPG | STRUCTURAL_VIOLATION | Dispatch rebinding + CSPG registration | 2.3 / 4.3 REF-OC-001 |
| INV-002 | Referential | All operator references must resolve to currently registered, non-deprecated targets | REFERENTIAL_FAULT | Operator re-registration + reference re-resolution | 3.3 ANOM-LV-009 |
| INV-003 | Temporal | No propagation chain may span epoch boundaries without a registered ESSA | TEMPORAL_ORDER_VIOLATION | ESSA retroactive registration + protocol update | 2.3 REM-SC-019 / 8.3 REM-KV-003 |
| INV-004 | Structural | No Primitive Operator binding shall reference an envelope-stratum node without a CSPG | STRUCTURAL_VIOLATION | Dispatch rebinding + SC-002 remediation | 2.3 REM-SC-014 |
| INV-005 | Compositional | Cross-stratum assemblies spanning two or more visibility tier levels require a VIS interposition | COMPOSITIONAL_CONFLICT | VIS registration + SC-008 remediation | 2.3 REM-SC-022 / 4.3 REF-OC-003 |
| INV-006 | Lineage | No lineage propagation graph may contain an unauthorized back-edge cycle | CYCLE_BREAK | Back-edge removal + propagation chain re-registration | 3.3 ANOM-LV-007 |
| INV-007 | Temporal | All external governance authority sync events must complete within a single epoch or under ESSA | TEMPORAL_ORDER_VIOLATION | ESSA retroactive registration + SC-006 remediation | 2.3 REM-SC-019 |
| INV-008 | Lineage | No duplicate ORIGIN registrations may coexist for the same governed operation scope | ORIGIN_AMBIGUITY | Duplicate suppression + idempotency enforcement | 3.3 ANOM-LV-013 |
| INV-009 | Visibility | No node may operate at a visibility tier higher than its registry-recorded tier without a TEG | VISIBILITY_INHERITANCE_FAULT | TEG retroactive registration + registry correction | 6.3 REM-VG-011 / REM-VG-014 |
| INV-010 | Transmission | All DEFERRED channel transmissions must include a validated GovernanceStateVector | TRANSMISSION_INTEGRITY_FAULT | TC-003 contract update + payload re-queue | 7.3 REM-TG-008 |
| INV-011 | Compositional | A TRANSPARENT-to-OPAQUE co-binding within any assembly requires a VIS interposition | COMPOSITIONAL_CONFLICT | VIS interposition + SC-008 remediation | 2.3 REM-SC-022 |
| INV-012 | Kernel | KVSP CONVERGENCE_FAILURE escalation must trigger KVO notification within 3 minutes | ESCALATION_TIMEOUT | KVSP escalation protocol update + KVO acknowledgment | 8.3 REM-KV-003 |

All entries are the master post-R-14 invariant list and supersede prior current-state representations while prior versions remain in Git history.
