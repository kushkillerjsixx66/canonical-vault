# WP-GROK-002 — Acceptance State Machine (from H2)

**Status:** OPEN — proposal revised (tightenings applied)  
**Type:** hypothesis_generation → governed_artifact_proposal  
**Parent:** WP-GROK-001 (H2 accepted branch-locally)  
**Opened:** 2026-09-05T16:57:00Z  
**Revised:** 2026-09-05T17:00:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Intent

Produce a concrete, reversible proposal that formalizes the model acceptance lifecycle as a small state machine. This addresses the thin specification in MCC §9 and the vocabulary drift already observed in live manifests (e.g. `ACTIVE_PROVISIONAL`).

## Scope

**In scope**
- Definition of acceptance states and legal transitions
- Mapping of current ad-hoc statuses into the machine
- Required fields for transition records
- Compatibility notes with existing `acceptance.sig` and `manifest.json`
- Explicit residual risks and open questions

**Out of scope**
- Direct edit of `model-contribution.md` or other canonical contracts
- Cross-branch writes
- Claims of canonical authority
- Implementation of runtime enforcement (that would be a later package)

## Deliverables

1. `proposal.md` — primary governed proposal artifact (revised) ✅
2. Updates to `SESSION_LEDGER.md` ✅

## Tightenings Applied (2026-09-05)

1. `ACTIVE` now has two concrete additional capabilities (cross-model comparison requests + eligibility for tier promotion review).
2. Transition records elevated to **MUST** for critical transitions (leaving PENDING, entering SUSPENDED/REVOKED, major MCC version bump).
3. Major MCC version bump → automatic `SUSPENDED` made normative.
4. Concrete example transition record added (Grok activation).

## Success Criteria

- Clear, minimal state machine ✅
- Explicit transition conditions ✅
- Backward-compatible with existing Grok manifests ✅
- Fully lineage-encoded ✅
- No modification of source contracts ✅

## Prohibitions Observed

No direct_canonical_mutation, cross_branch_modification, constitutional_override, vault_history_rewrite, Stumpy bypass, unbounded_execution, or fabricated_provenance.
