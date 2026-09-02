# R-14 Operator-Class Refactor Registry

**Source:** LGR-2026-09-002 §4
**Retention:** LONG

| ID | Operator | Tier | Refactor | Affected Bindings | Status | Canonical Contract |
|---|---|---:|---|---|---|---|
| REF-OC-001 | OP-PRIM-017 | 1 | DISPATCH REBINDING | SC-002, CSPG-Registry | RESOLVED | OP-PRIM-017-v2.1 |
| REF-OC-002 | OP-PRIM-031 | 1 | SIGNATURE REALIGNMENT | SC-001, LEV-Registry | RESOLVED | OP-PRIM-031-v3.0 |
| REF-OC-003 | OP-COMP-023 | 2 | CONTRACT NORMALIZATION | SC-002, SC-008, COMP-ASSM-019 | RESOLVED | OP-COMP-023-v4.2 |
| REF-OC-004 | OP-COMP-047 | 2 | CONTRACT NORMALIZATION | SC-007, VIS-Registry | RESOLVED | OP-COMP-047-v2.0 |
| REF-OC-005 | OP-COMP-061 | 2 | SIGNATURE REALIGNMENT | SC-003, SC-007, LEV-0826 | RESOLVED | OP-COMP-061-v5.1 |
| REF-OC-006 | OP-META-004 | 3 | META-PROMOTION | SC-001 through SC-008, Full Envelope | RATIFIED | OP-META-004-v1.0 |

## Canonical contract notes
- OP-PRIM-017-v2.1 restricts dispatch to inner-stratum namespaces; envelope targets require CSPG validation.
- OP-PRIM-031-v3.0 requires explicit `state_vector: GovernanceStateVector` and `epoch: EpochToken`.
- OP-COMP-023-v4.2 requires `VIS-ID` for assemblies with visibility-tier differential of two or more levels.
- OP-COMP-047-v2.0 requires `TBA-ID` for the TRANSLUCENT-to-BROADCAST bridge.
- OP-COMP-061-v5.1 explicitly propagates `state_vector` through the composite wrapper.
- OP-META-004-v1.0 is the R-14 META-PROMOTION of OP-COMP-071, operates at BROADCAST visibility, is bound to SC-001 through SC-008, and may initiate Tier 1/2 refactors only upon Governance Council authorization.

REF-OC-006 was authorized by unanimous Lattice Governance Council resolution LGC-R14-RES-006 on 2026-08-27.
