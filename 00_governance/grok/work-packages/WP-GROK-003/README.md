# WP-GROK-003 — Divergence Record + Orchestration Run Schema (H1 + H4)

**Status:** ACCEPTED (branch-local)  
**Type:** governed_artifact_proposal  
**Parent:** WP-GROK-001 (H1 and H4)  
**Opened:** 2026-09-05T17:02:00Z  
**Revised:** 2026-09-05T17:06:00Z  
**Accepted:** 2026-09-05T17:07:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Final Disposition

Proposal accepted as branch-local working design after review improvements.  
No source contracts modified.

## Key Design Points (accepted)

- Divergence Record required on non-trivial syncs; recommended on fast-forwards
- `carried_forward: partial` requires notes
- Orchestration Run includes explicit `status` field (open | closed | abandoned)
- Recommended storage: `00_governance/<model>/divergence/` and `00_governance/orchestration/runs/`
- Concrete examples included for both objects

## Artifacts

- `proposal.md` (improved + accepted)
- This README
