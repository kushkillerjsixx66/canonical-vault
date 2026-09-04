# R-14 Governance Envelope State Register

**Source:** LGR-2026-09-002 §9
**Retention:** LONG

| Envelope ID | Surface | Boundary Specification | Last Synchronized | Authority | Status |
|---|---|---|---|---|---|
| GE-CS-001 | Constraint | SC-001 through SC-008 as remediated in R-14 | 2026-09-01 22:00 EDT | GEA-01 Primary | SYNCHRONIZED |
| GE-CS-002 | Constraint | Drift Domain boundaries as expanded in R-14 | 2026-09-01 22:00 EDT | GEA-02 Secondary | SYNCHRONIZED |
| GE-TS-001 | Transmission | TC-001 through TC-006 as remediated in R-14 | 2026-09-01 20:30 EDT | GEA-01 Primary | SYNCHRONIZED |
| GE-TS-002 | Transmission | External channel TC-006 (GEA-03 DEFERRED) | 2026-08-31 18:30 EDT | GEA-03 External Partner | SYNCHRONIZED |
| GE-VS-001 | Visibility | BROADCAST-tier nodes ENV-NODE-031, OP-META-004 | 2026-09-01 22:14 EDT | GEA-01 Primary | SYNCHRONIZED |
| GE-VS-002 | Visibility | TRANSPARENT-tier envelope nodes ENV-NODE-018, ENV-NODE-022, ENV-NODE-029 | 2026-09-01 22:14 EDT | GEA-02 Secondary | SYNCHRONIZED |

## Canonical surface state
- Constraint Surface: SC-001 unchanged; SC-002 v2.1 CSPG requirement; SC-003 unchanged; SC-004 under review/provisional boundary; SC-005 unchanged; SC-006 ESSA requirement; SC-007 unchanged; SC-008 VIS interposition requirement.
- Transmission Surface: TC-001 through TC-006 as remediated; TC-006 uses ESSA and two-stage handshake for epoch-spanning DEFERRED transmission.
- Visibility Surface: ENV-NODE-031 and OP-META-004 are BROADCAST under LGC-R14-TEG-003; transparent envelope nodes remain registered as listed above.

## Synchronization remediations
- GE-CS-001 synchronized after pre-R-14 SC-002/SC-008 and missing SC-006 ESSA discrepancies were detected and corrected.
- GE-TS-002 synchronized after TC-006 handshake and ESSA deficiencies were corrected; ESSA-042 registered for the E-211/E-212 span.
- GE-VS-001 synchronized after ENV-NODE-031 and OP-META-004 were elevated to BROADCAST; GEA-01 confirmed the audit-ledger subscription and TEG authorization.
