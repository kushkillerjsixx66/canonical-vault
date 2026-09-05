# WP-GROK-005 — Scope Gate as First-Class Constraint (H5)

**Status:** OPEN  
**Type:** governed_artifact_proposal  
**Parent:** WP-GROK-001 (H5 accepted branch-locally)  
**Opened:** 2026-09-05T17:13:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Intent

Produce a concrete, reversible proposal that elevates declared `contribution_scope` and `prohibited_zones` (from model manifests) into a first-class constraint checkable by ConstraintGate / CFC-style mechanisms before an artifact is proposed for Stumpy review or transmission. This closes the declaration-without-enforcement gap identified in WP-GROK-001.

## Scope

**In scope**
- Definition of a Scope Gate constraint
- Inputs (manifest scope / prohibited zones + candidate artifact metadata)
- Pass / Deny / Hold semantics
- Placement in the contribution cycle
- Relationship to existing Lattice ConstraintGate / CFC patterns
- Residual risks and open questions

**Out of scope**
- Direct edit of MCC, Orchestration Spec, or Lattice runtime code
- Cross-branch writes
- Claims of canonical authority
- Full runtime implementation (later package if authorized)

## Deliverables

1. `proposal.md` — primary governed proposal artifact
2. Updates to `SESSION_LEDGER.md`

## Success Criteria

- Clear, minimal gate definition
- Fail-closed posture on missing or mismatched scope data
- Compatible with existing contribution cycle and accepted proposals (WP-GROK-002–004)
- Fully lineage-encoded
- No modification of source contracts
