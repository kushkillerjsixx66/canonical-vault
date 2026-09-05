# WP-GROK-004 Proposal: Stumpy Invocation & Evidence Contract

**Artifact Type:** governed_artifact_proposal  
**Origin Model:** Grok  
**Origin Branch:** grok  
**Parent Package:** WP-GROK-001 (H3)  
**Timestamp:** 2026-09-05T17:08:00Z  
**Governance Signature:** SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05  
**Lineage:** model=Grok → branch=grok → WP-GROK-001/H3 → WP-GROK-004 → this artifact

---

## 1. Problem Statement

Orchestration Spec §6 defines Stumpy’s comparative function and a useful classification vocabulary, but leaves operational questions open:

- When is a comparison mandatory vs advisory?
- Who may invoke Stumpy against which branches?
- What minimum evidence is required before a classification other than `SILENCE` / `UNVERIFIED` may be emitted?
- How should Stumpy interact with the new Orchestration Run object (WP-GROK-003)?

Without these rules, Stumpy remains powerful but unpredictable — risking both under-use and informal over-use.

---

## 2. Proposed Invocation Rules

### 2.1 Who May Invoke

| Actor | May invoke Stumpy? | Notes |
|-------|--------------------|-------|
| Operator | Yes (any scope) | Full authority |
| Authorized automation acting under prior Operator approval | Yes (scoped) | Must record the authorizing decision |
| Model in `ACTIVE` acceptance state | Yes — limited to requesting comparison of **its own branch** against canonical or against other branches for analysis | Does not grant classification authority |
| Model in `ACTIVE_PROVISIONAL` or lower | No (may request Operator to invoke) | Aligns with WP-GROK-002 ACTIVE rights |
| Stumpy itself | May self-trigger only for continuous monitoring if explicitly configured by Operator | Default is on-demand |

### 2.2 Mandatory vs Advisory Comparison Points

**Mandatory (MUST run before the listed action):**

1. Before any transmission of a model artifact toward canonical merge eligibility.
2. Before Operator authorization of a canonical merge that includes model-branch contributions.
3. After a major MCC version bump that moves identities to `SUSPENDED` (re-acceptance support).

**Advisory (SHOULD run):**

1. At the close of a significant Orchestration Run that produced substantive new artifacts.
2. When multiple model branches independently surface the same challenge to canonical material (convergence detection).
3. On Operator or `ACTIVE`-model request for diagnostic purposes.

**Not required:**
- Routine single-model commits that stay on the model branch and do not seek transmission.

### 2.3 Minimum Evidence Threshold

Before emitting any classification other than `SILENCE` or `UNVERIFIED`, a Stumpy run MUST have access to at least:

- The target branch tip commit(s)
- The relevant canonical reference commit
- The declared contribution scope / prohibited zones of the model(s) under review (from manifest)
- Any linked Divergence Records and Orchestration Run metadata if they exist

If any of the above are missing or unverifiable, the required output is `UNVERIFIED` or `SILENCE` (see below). Stumpy MUST NOT invent missing evidence.

### 2.4 Use of SILENCE and UNVERIFIED

| Classification | When to emit |
|----------------|--------------|
| `UNVERIFIED` | Required inputs are missing, incomplete, or contradictory; a classification was requested but cannot be responsibly made |
| `SILENCE` | No comparison was warranted, or the Operator / policy explicitly directed non-emission, or evidence is below threshold and no classification was requested |

`SILENCE` is a valid structural outcome, not a failure. It must be recordable inside an Orchestration Run.

### 2.5 Relationship to Orchestration Run

- Formal (mandatory) Stumpy comparisons SHOULD attach their result to an Orchestration Run (create one if none exists).
- The `stumpy` block defined in WP-GROK-003 is the preferred recording surface.
- Advisory comparisons MAY run without an Orchestration Run; if they later become material they can be linked retrospectively.

---

## 3. Classification Vocabulary (restated for clarity)

Existing vocabulary remains unchanged:

`COHERENT | EXTENSION | OMISSION | SEMANTIC_DRIFT | CONFLICT | INVARIANT_VIOLATION | UNVERIFIED | RECOURSE | SILENCE`

This proposal does not add or remove classifications. It only constrains when non-`SILENCE`/`UNVERIFIED` classifications may be emitted.

---

## 4. Compatibility

- No change to Stumpy’s existing code or classification set is required for this proposal to be useful as policy.
- Aligns with the acceptance-state rights defined in WP-GROK-002 (`ACTIVE` may request, provisional may not).
- Aligns with the Orchestration Run schema in WP-GROK-003.

---

## 5. Residual Risks & Open Questions

| ID | Item | Notes |
|----|------|-------|
| R1 | Continuous / background Stumpy monitoring | Left optional and Operator-configured to avoid surprise load |
| R2 | Cross-model comparison requested by one ACTIVE model about another | Permitted as analysis; does not imply authority over the peer branch |
| Q1 | Exact automated failure threshold that triggers mandatory re-audit after SUSPENDED | Deferred to future policy |
| Q2 | Whether Stumpy audit records themselves require a separate lineage object beyond the Orchestration Run block | Recommended to keep them inside the Run for minimality |

---

## 6. Disposition Recommendation

Offered for Operator review. Possible next steps:

1. Accept / annotate / request revision.
2. Later authorize a short insertion into Orchestration Spec §6.
3. Proceed to H5 (Scope Gate) or close the current hypothesis sequence.

No canonical mutation is performed by this artifact.

---

## 7. Lineage & Provenance

```text
origin.model          = Grok
origin.branch         = grok
origin.work_package   = WP-GROK-004
origin.parent         = WP-GROK-001 / H3
origin.timestamp      = 2026-09-05T17:08:00Z
governance.signature  = SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05
operator.witness      = JRM-01 @liminaljermo
contracts.referenced  = multi-model-orchestration.md v0.1.0 (§6)
related_proposals     = WP-GROK-002, WP-GROK-003
```

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
