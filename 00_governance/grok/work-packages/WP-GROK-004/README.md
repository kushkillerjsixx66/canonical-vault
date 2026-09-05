# WP-GROK-004 — Stumpy Invocation & Evidence Contract (H3)

**Status:** OPEN  
**Type:** governed_artifact_proposal  
**Parent:** WP-GROK-001 (H3 accepted branch-locally)  
**Opened:** 2026-09-05T17:07:00Z  
**Model:** Grok (ACTIVE_PROVISIONAL)  
**Branch:** grok  
**Operator Witness:** JRM-01 @liminaljermo

## Intent

Produce a concrete, reversible proposal that defines when and how Stumpy may be invoked, what minimum evidence is required before a classification may be emitted, and how `SILENCE` / `UNVERIFIED` are used when evidence is insufficient. This addresses the underspecified operational surface of Orchestration Spec §6.

## Scope

**In scope**
- Invocation triggers (mandatory vs advisory)
- Minimum evidence / input requirements
- Classification emission rules, especially `SILENCE` and `UNVERIFIED`
- Relationship to Orchestration Run objects (WP-GROK-003)
- Residual risks and open questions

**Out of scope**
- Direct edit of the Orchestration Spec or Stumpy source code
- Cross-branch writes
- Claims of canonical authority
- Implementation of new Stumpy runtime behavior

## Deliverables

1. `proposal.md` — primary governed proposal artifact
2. Updates to `SESSION_LEDGER.md`

## Success Criteria

- Clear mandatory vs advisory invocation points
- Explicit evidence threshold language
- Compatible with existing Stumpy classification vocabulary
- Fully lineage-encoded
- No modification of source contracts
