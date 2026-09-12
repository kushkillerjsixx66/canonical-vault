# WP-GROK-004 — Stumpy Invocation & Evidence Contract (H3)

**Status:** ACCEPTED (branch-local)  
**Type:** governed_artifact_proposal  
**Parent:** WP-GROK-001 (H3)  
**Opened:** 2026-09-05T17:07:00Z  
**Revised:** 2026-09-05T17:11:00Z  
**Accepted:** 2026-09-05T17:13:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Final Disposition

Proposal accepted as branch-local working design under Operator direction.  
No source contracts modified. Elevation toward Orchestration Spec §6 remains Operator-authorized only.

## Key Design Points (accepted)

- Invocation rights tied to acceptance state (`ACTIVE` may request; provisional may not)
- Mandatory comparison points: pre-transmission, pre-merge authorization, post-major MCC bump
- Minimum evidence threshold; missing inputs force `UNVERIFIED` / `SILENCE`
- Automation authorization must be referenceable
- Continuous mode still bound by evidence threshold and Run recording
- Aligns with WP-GROK-002 and WP-GROK-003

## Artifacts

- `proposal.md` (revised + accepted)
- This README
