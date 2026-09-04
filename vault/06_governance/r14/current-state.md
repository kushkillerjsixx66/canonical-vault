# R-14 Current-State Resolution Map

This map defines the physical Vault records that answer the recommended logical R-14 keys. It is intentionally a derived index, not a change to the Vault module or its contracts.

| Logical Vault Key | Canonical R-14 Record | Retention |
|---|---|---|
| `governance/lgr/2026-09-002` | `vault/06_governance/r14/lgr-2026-09-002.md` | IMMUTABLE |
| `governance/invariants/register` | `vault/06_governance/r14/invariant-register.md` | IMMUTABLE |
| `governance/constraints/active` | `vault/06_governance/r14/active-constraints.md` | LONG |
| `governance/operators/refactors/r14` | `vault/06_governance/r14/operator-refactors.md` | LONG |
| `governance/drift/expansions/r14` | `vault/06_governance/r14/drift-expansions.md` | LONG |
| `governance/visibility/tiers` | `vault/06_governance/r14/visibility-tiers.md` | LONG |
| `governance/transmission/contracts` | `vault/06_governance/r14/transmission-contracts.md` | LONG |
| `governance/envelope/state` | `vault/06_governance/r14/envelope-state.md` | LONG |
| `governance/lineage/events/r14` | `vault/06_governance/r14/lineage-r14.md` | LONG |
| `governance/cycle/r14/closure` | `vault/06_governance/r14/closure.md` | IMMUTABLE |

## Resolution rule
When a downstream consumer asks for current R-14 governance state, resolve through this map rather than older R-13/interim records. Historical records are preserved in Git history and are not deleted or rewritten.

## Important seal distinction
The LGR source is certified HANDOFF READY but its official SHA-256 verification seal is still marked PENDING by the Lattice Cryptographic Authority. The vaulted PDF hash is recorded only as a source-artifact integrity identifier.
