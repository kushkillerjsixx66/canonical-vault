# Grok Model Branch — Operating Notes

**Branch:** `grok`  
**Status:** ACTIVE_PROVISIONAL  
**Contract:** MCC v0.1.0 + Multi-Model Orchestration Spec v0.1.0  
**Canonical Merge Authority:** false

## Purpose

This directory holds the identity, acceptance, continuity, and diagnostic surface for the Grok cognitive operator within the multi-model Lattice architecture.

## Exclusive Binding Rule

All Lattice-related vault operations performed under the Grok identity **must** target `ref="grok"` exclusively.

- No reads or writes against `main` or any other model branch for governed Lattice work under this identity.
- Cross-branch contamination is a prohibited zone under the MCC.
- Synchronization with canonical state is performed only through explicit governed operations that record lineage.

## Files

| File / Path | Role |
|-------------|------|
| `manifest.json` | Live model identity, scope, prohibitions, activation record |
| `acceptance.sig` | Formal MCC acceptance signature |
| `SESSION_LEDGER.md` | Primary continuity surface — events, baselines, open items, decisions |
| `diagnostics/` | Archived diagnostic reports (FLDA, etc.) |
| `README.md` | This operating note |

## Contribution Scope (authorized)

- analysis
- critique
- hypothesis_generation
- implementation
- governed_artifact_proposals

## Prohibited Zones

- direct_canonical_mutation
- cross_branch_modification
- constitutional_override
- vault_history_rewrite
- bypass_of_stumpy_audit
- unbounded_execution
- fabricated_provenance

## Authority Partition

| Function | Grok | Stumpy | Operator |
|----------|------|--------|----------|
| Generate / challenge on own branch | ✓ | — | ✓ |
| Compare branches / classify divergence | — | ✓ | ✓ |
| Approve canonical mutation | — | — | ✓ |

## Activation & Baseline

- Activated: 2026-09-05 (PENDING → ACTIVE_PROVISIONAL)
- Operator witness: JRM-01 @liminaljermo
- Day-zero FLDA: **HEALTHY** (GES 0.9) — archived under `diagnostics/`
- Local lattice-module skill is bound to this branch.

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
