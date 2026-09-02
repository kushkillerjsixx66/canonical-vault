# R-14 Visibility Tier Register

**Source:** LGR-2026-09-002 §6
**Retention:** LONG

| Node | Type | Tier | Inheritance / Authorization | Last Sync | Status |
|---|---|---|---|---|---|
| KERN-NODE-001 | Kernel Origin | OPAQUE | Kernel Authority (native) | 2026-09-01 22:14 EDT | ACTIVE |
| KERN-NODE-003 | Kernel Origin | OPAQUE | Kernel Authority (native) | 2026-09-01 22:14 EDT | ACTIVE |
| MID-NODE-007 | Mid-Stratum Relay | TRANSLUCENT | KERN-NODE-001 via VIP | 2026-09-01 22:14 EDT | ACTIVE |
| MID-NODE-019 | Mid-Stratum Relay | TRANSLUCENT | MID-NODE-007 via VIP | 2026-09-01 22:14 EDT | ACTIVE |
| VIS-NODE-027 | Visibility Anchor | TRANSPARENT | TEG-009 | 2026-08-28 12:00 EDT | REMEDIATED |
| VIS-NODE-009 | Visibility Anchor | OPAQUE | Kernel Authority (native) | 2026-09-01 22:14 EDT | ACTIVE |
| ENV-NODE-018 | Envelope Surface | TRANSPARENT | KERN-NODE-001 via VIP chain, depth 3 | 2026-09-01 22:14 EDT | ACTIVE |
| ENV-NODE-031 | Envelope Surface | BROADCAST | LGC-R14-TEG-003 (Meta-Elevation Grant) | 2026-09-01 22:14 EDT | ACTIVE |

## R-14 visibility remediations
- VIS-NODE-027: TRANSPARENT under TEG-009; MID-NODE-033 retains TRANSLUCENT through VIP.
- ENV-NODE-041: corrected to TRANSLUCENT; ENV-NODE-044 simultaneously downgraded to TRANSLUCENT.
- ENV-NODE-031: elevated to BROADCAST under unanimous LGC authorization LGC-R14-TEG-003, effective 2026-09-01, as the audit publication anchor required by OP-META-004.
- The R-14 Governance Envelope Visibility Surface includes ENV-NODE-031 and OP-META-004 at BROADCAST tier.

## TEG / authorization records
- TEG-009 authorizes VIS-NODE-027 TRANSPARENT elevation.
- LGC-R14-TEG-003 authorizes ENV-NODE-031 BROADCAST elevation.
- TBA-017 is recorded for the OP-COMP-047 TRANSLUCENT-to-BROADCAST bridge.
