# WP-GROK-002 — Acceptance State Machine (from H2)

**Status:** ACCEPTED (branch-local)  
**Type:** hypothesis_generation → governed_artifact_proposal  
**Parent:** WP-GROK-001 (H2 accepted branch-locally)  
**Opened:** 2026-09-05T16:57:00Z  
**Revised:** 2026-09-05T17:00:00Z  
**Accepted:** 2026-09-05T17:02:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Intent

Produce a concrete, reversible proposal that formalizes the model acceptance lifecycle as a small state machine. This addresses the thin specification in MCC §9 and the vocabulary drift already observed in live manifests (e.g. `ACTIVE_PROVISIONAL`).

## Final Disposition

Proposal **accepted** as branch-local working design under Operator direction “Accept proposal of H2”.  
No source contracts modified. Elevation to MCC §9 remains an Operator-authorized transmission action only.

## Key Design Points (accepted)

- Five states: `PENDING` → `ACTIVE_PROVISIONAL` → `ACTIVE` ↔ `SUSPENDED` → `REVOKED`
- `ACTIVE` confers two concrete additional capabilities (cross-model comparison requests + tier-promotion eligibility)
- Critical transitions MUST produce a transition record
- Major MCC version bump → automatic `SUSPENDED` (normative)
- Fully backward-compatible with existing Grok artifacts

## Artifacts

- `proposal.md` (revised with tightenings)
- This README

## Prohibitions Observed

No direct_canonical_mutation, cross_branch_modification, constitutional_override, vault_history_rewrite, Stumpy bypass, unbounded_execution, or fabricated_provenance.
