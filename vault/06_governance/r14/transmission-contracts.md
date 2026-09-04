# R-14 Transmission Contract Register

**Source:** LGR-2026-09-002 §7
**Retention:** LONG

| ID | Class | Source | Target | Integrity Constraint | Priority | Status |
|---|---|---|---|---|---|---|
| TC-001 | SYNCHRONOUS | KERN-NODE-001 | KERN-NODE-003 | Full payload integrity + epoch validation | CRITICAL | ACTIVE |
| TC-002 | ASYNCHRONOUS | MID-NODE-007 | MID-NODE-019 | Checksum + constraint-binding transfer validation | HIGH | ACTIVE |
| TC-003 | DEFERRED | MID-NODE-044 | ENV-NODE-029 | State vector match + epoch-boundary alignment | STANDARD | REMEDIATED |
| TC-004 | INTERRUPT-DRIVEN | KERN-NODE-008 | ENV-NODE-031 | Integrity pre-check + BROADCAST-tier authorization | CRITICAL | ACTIVE |
| TC-005 | ASYNCHRONOUS | ENV-NODE-018 | ENV-NODE-022 | Payload type restriction + visibility tier match | HIGH | ACTIVE |
| TC-006 | DEFERRED | ENV-NODE-022 | GEA-03 (External) | ESSA validation + external authority handshake | STANDARD | REMEDIATED |

## Canonical remediation bindings
- TC-003 now requires a validated GovernanceStateVector at queue time and re-validation before delivery if kernel state changes; maximum deferred queue latency is 2 epoch periods. Source state vector: OP-COMP-061-v5.1.
- TC-006 requires ESSA for epoch-spanning delivery and a two-stage external handshake: initiation acknowledgment in E-N and completion in E-N or E-N+1 under valid ESSA.
- TC-004 requires a BROADCAST authorization check against LGC-R14-TEG-003 before interrupt dispatch to ENV-NODE-031; maximum pre-check budget is 50ms.
