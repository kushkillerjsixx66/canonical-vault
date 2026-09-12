# WP-GROK-005 — Scope Gate as First-Class Constraint (H5)

**Status:** ACCEPTED (branch-local)  
**Type:** governed_artifact_proposal  
**Parent:** WP-GROK-001 (H5)  
**Opened:** 2026-09-05T17:13:00Z  
**Revised:** 2026-09-05T17:16:00Z  
**Accepted:** 2026-09-05T17:16:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Final Disposition

Proposal accepted as branch-local working design.  
This completes the conversion of all five hypotheses (H1–H5) from WP-GROK-001 into concrete designs.

## Key Design Points (accepted)

- PASS / DENY / HOLD gate over declared contribution_scope + prohibited_zones
- Fail-closed on missing required inputs
- Initial artifact-type vocabulary starts from MCC categories
- DENY override only by explicit Operator decision recorded in an Orchestration Run
- Runs before Stumpy and before transmission
- Compatible with WP-GROK-002–004

## Artifacts

- `proposal.md` (revised + accepted)
- This README
