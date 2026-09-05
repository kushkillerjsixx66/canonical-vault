# WP-GROK-005 Proposal: Scope Gate as First-Class Constraint

**Artifact Type:** governed_artifact_proposal  
**Origin Model:** Grok  
**Origin Branch:** grok  
**Parent Package:** WP-GROK-001 (H5)  
**Timestamp:** 2026-09-05T17:13:00Z  
**Governance Signature:** SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05  
**Lineage:** model=Grok → branch=grok → WP-GROK-001/H5 → WP-GROK-005 → this artifact

---

## 1. Problem Statement

Model manifests declare `contribution_scope` and `prohibited_zones` (MCC §1, live Grok manifest). These declarations currently function as documentation only. There is no systematic check that a candidate artifact actually falls inside the declared scope or outside the prohibited zones before it is offered for Stumpy review or transmission.

Consequence: the boundary is soft. A model (or automation) can produce work that violates its own declared limits and the violation is discovered only later, if at all.

---

## 2. Proposed Scope Gate

### 2.1 Purpose

A first-class constraint that evaluates a candidate artifact against the producing model’s declared scope and prohibited zones, returning a clear decision before further governance steps.

### 2.2 Inputs

| Input | Source | Required |
|-------|--------|----------|
| Model identity | artifact origin / Orchestration Run | Yes |
| `contribution_scope` | model `manifest.json` | Yes |
| `prohibited_zones` | model `manifest.json` | Yes |
| Artifact type / classification | artifact metadata or path convention | Yes |
| Artifact summary or declared intent | artifact or accompanying note | Recommended |

If required inputs are missing or unverifiable → **DENY** (fail-closed).

### 2.3 Decision Semantics

| Decision | Meaning | Typical next step |
|----------|---------|-------------------|
| **PASS** | Artifact is within declared scope and outside prohibited zones | May proceed to Stumpy review / transmission path |
| **DENY** | Artifact falls outside scope or inside a prohibited zone, or required inputs missing | Block; record reason; do not proceed |
| **HOLD** | Scope data present but classification of the artifact is ambiguous | Pause for Operator or model clarification; do not treat as PASS |

### 2.4 Evaluation Rules (minimal)

1. If any required input is missing → DENY.
2. If artifact type or intent matches a prohibited zone → DENY.
3. If artifact type or intent is not covered by any entry in `contribution_scope` → DENY.
4. If coverage is ambiguous (e.g., novel artifact type not yet mapped) → HOLD.
5. Otherwise → PASS.

Exact matching language (string equality, prefix, ontology lookup) is left as an implementation detail; the gate only requires that the rule set be explicit and auditable.

### 2.5 Placement in the Contribution Cycle

```text
Artifact produced on model branch
        ↓
   Scope Gate          ← new checkpoint
        ↓
   PASS  →  (optional) local validation → Stumpy comparison → …
   HOLD  →  clarification loop
   DENY  →  stop; record; no transmission
```

The gate sits **before** Stumpy review and **before** any transmission toward canonical eligibility. It does not replace Stumpy; it filters obviously out-of-scope work early.

### 2.6 Recording

Every Scope Gate decision SHOULD be recorded, preferably inside the relevant Orchestration Run (new optional block) or as a small standalone gate record linked by id:

```yaml
scope_gate:
  model: <name>
  artifact_ref: <path or id>
  decision: PASS | DENY | HOLD
  reason: <short string>
  timestamp: <ISO-8601>
  manifest_scope_hash_or_version: <ref>
```

---

## 3. Relationship to Existing Lattice Patterns

The Scope Gate is intentionally shaped like existing ConstraintGate / CFC decisions (PERMIT / DENY / HOLD). It can be implemented as:

- an additional checker registered with ConstraintGate, or
- a thin pre-flight function that emits the same decision vocabulary, or
- a policy object consulted by the contribution cycle.

No change to the core CFC state machine is required for the proposal to be useful as policy.

---

## 4. Compatibility with Prior Accepted Packages

| Package | Alignment |
|---------|-----------|
| WP-GROK-002 (Acceptance State Machine) | Gate reads the live manifest of an accepted identity; suspended/revoked identities should already be barred upstream |
| WP-GROK-003 (Orchestration Run) | Gate decisions can be stored inside or linked from a Run |
| WP-GROK-004 (Stumpy Invocation) | Gate runs *before* Stumpy; reduces noise reaching comparative review |

---

## 5. Residual Risks & Open Questions

| ID | Item | Notes |
|----|------|-------|
| R1 | Overly coarse scope lists | Models may need to refine their declared scope over time; gate should not punish legitimate evolution |
| R2 | Novel artifact types | HOLD is the correct initial response; repeated HOLDs should trigger scope-manifest review |
| R3 | Performance / automation friction | Gate must stay cheap; complex ontology matching is out of scope for v0 |
| Q1 | Who may update a model’s contribution_scope? | Operator or model with subsequent re-acceptance? Left open |
| Q2 | Should DENY be appealable inside the same Orchestration Run? | Recommended yes, via Operator override recorded in the Run |
| Q3 | Exact artifact-type taxonomy | Not defined here; can start with the MCC artifact categories already listed |

---

## 6. Disposition Recommendation

Offered for Operator review. Possible next steps:

1. Accept / annotate / request revision.
2. Authorize a follow-on that produces a concrete checker sketch or JSON Schema for the gate record.
3. Consider the hypothesis sequence (H1–H5) complete once this package is accepted.

No canonical mutation is performed by this artifact.

---

## 7. Lineage & Provenance

```text
origin.model          = Grok
origin.branch         = grok
origin.work_package   = WP-GROK-005
origin.parent         = WP-GROK-001 / H5
origin.timestamp      = 2026-09-05T17:13:00Z
governance.signature  = SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05
operator.witness      = JRM-01 @liminaljermo
contracts.referenced  = model-contribution.md v0.1.0 (scope declarations)
related_proposals     = WP-GROK-002, WP-GROK-003, WP-GROK-004
```

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
