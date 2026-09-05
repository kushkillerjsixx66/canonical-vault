# WP-GROK-002 — Acceptance State Machine (from H2)

**Status:** OPEN  
**Type:** hypothesis_generation → governed_artifact_proposal  
**Parent:** WP-GROK-001 (H2 accepted branch-locally)  
**Opened:** 2026-09-05T16:57:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Intent

Produce a concrete, reversible proposal that formalizes the model acceptance lifecycle as a small state machine. This addresses the thin specification in MCC §9 and the vocabulary drift already observed in live manifests (e.g. `ACTIVE_PROVISIONAL`).

## Scope

**In scope**
- Definition of acceptance states and legal transitions
- Mapping of current ad-hoc statuses into the machine
- Minimal required fields for each state transition record
- Compatibility notes with existing `acceptance.sig` and `manifest.json`
- Explicit residual risks and open questions

**Out of scope**
- Direct edit of `model-contribution.md` or other canonical contracts
- Cross-branch writes
- Claims of canonical authority
- Implementation of runtime enforcement (that would be a later package)

## Deliverables

1. `proposal.md` — primary governed proposal artifact
2. Optional supporting schema sketch (JSON or YAML) if clarifying
3. Updates to `SESSION_LEDGER.md`

## Success Criteria

- Clear, minimal state machine (no unnecessary states)
- Explicit transition conditions
- Backward-compatible with existing Grok (and peer) manifests where possible
- Fully lineage-encoded and reconstructable to this branch
- No modification of source contracts

## Prohibitions Observed

No direct_canonical_mutation, cross_branch_modification, constitutional_override, vault_history_rewrite, Stumpy bypass, unbounded_execution, or fabricated_provenance.
