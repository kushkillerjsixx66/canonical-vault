# R-14 Lineage Events and Resolved Anomalies

**Source:** LGR-2026-09-002 §3 and remediation lineage records
**Retention:** LONG

## Registered lineage events
| Event | Class | Origin | Terminal | Depth | Validated |
|---|---|---|---|---:|---|
| LEV-0814-001 | ORIGIN | KERN-NODE-001 | ENV-NODE-018 | N/A | 2026-08-14 08:01 EDT |
| LEV-0814-002 | PROPAGATION | KERN-NODE-001 | MID-NODE-007 | 1 | 2026-08-14 08:03 EDT |
| LEV-0819-007 | PROPAGATION | MID-NODE-007 | MID-NODE-019 | 2 | 2026-08-19 14:27 EDT |
| LEV-0822-003 | TERMINAL | MID-NODE-019 | ENV-NODE-018 | 3 | 2026-08-22 09:55 EDT |
| LEV-0825-011 | CYCLE-BREAK | MID-NODE-033 | MID-NODE-012 | anomaly depth 4 | 2026-08-25 17:43 EDT, remediated |
| LEV-0901-004 | TERMINAL | MID-NODE-044 | ENV-NODE-031 | 5 | 2026-09-01 11:18 EDT |

## Resolved anomalies
- ANOM-LV-007: unauthorized MID-NODE-033 → MID-NODE-012 back-edge removed; canonical chain re-registered as LEV-0825-012 through LEV-0825-015.
- ANOM-LV-009: corrected propagation event LEV-0826-008 restored SC-003 transfer; LEV-0826-007 marked SUPERSEDED.
- ANOM-LV-013: duplicate ORIGIN LEV-0831-002 suppressed; LEV-0831-001 remains canonical origin for GOV-OP-0831-04. Idempotent ORIGIN registration enforcement deployed.

## Additional R-14 refactor lineage
- LEV-0829-REF-001: OP-PRIM-017 v2.1 dispatch rebinding.
- LEV-0826-REF-002: OP-PRIM-031 v3.0 signature realignment.
- LEV-0829-REF-003: OP-COMP-023 v4.2 normalization.
- LEV-0830-REF-004: OP-COMP-047 v2.0 normalization.
- LEV-0826-REF-005: OP-COMP-061 v5.1 signature realignment.
- LEV-0827-REF-006: OP-META-004 promotion, authorized by LGC-R14-RES-006.

All resolved anomalies remain in historical lineage; the corrected registrations are the current canonical state.
