# WP-GROK-003 Proposal: Structured Divergence Record + Orchestration Run Schema

**Artifact Type:** governed_artifact_proposal  
**Origin Model:** Grok  
**Origin Branch:** grok  
**Parent Package:** WP-GROK-001 (H1 + H4)  
**Timestamp:** 2026-09-05T17:03:00Z  
**Governance Signature:** SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05  
**Lineage:** model=Grok → branch=grok → WP-GROK-001/H1+H4 → WP-GROK-003 → this artifact

---

## 1. Problem Statement

Two related underspecifications remain after WP-GROK-001:

**H1 — Synchronization divergence**  
Orchestration Spec §4 requires that a sync record “unresolved branch-local divergence, if any” and must not silently discard branch work. In practice no durable, structured object captures what was present only on the model branch before sync, what was carried forward, and what disposition was given to discarded work.

**H4 — Orchestration Run object**  
Orchestration Spec §13 lists a strong set of fields for a governed multi-model run. No storage location, schema, or enforcement mechanism exists. The list remains a checklist rather than an auditable artifact.

These two gaps reinforce each other: without a Divergence Record, sync events are hard to reconstruct; without an Orchestration Run object, there is no natural container that ties sync events, Stumpy audits, and Operator dispositions together.

---

## 2. Proposed Objects

### 2.1 Divergence Record

Produced on every governed synchronization of a model branch with a canonical reference (normally `main`).

```yaml
divergence_record:
  schema_version: "DR-0.1.0"
  id: <uuid or deterministic id>
  timestamp: <ISO-8601>
  model: <model name>
  branch: <branch name>
  sync:
    source_ref: <canonical ref, usually main>
    source_commit: <sha>
    pre_sync_branch_tip: <sha>
    post_sync_branch_tip: <sha>
    method: <merge | rebase | fast-forward | other>
  divergence:
    commits_only_on_branch:          # list of shas or short summaries
      - <sha>
      - ...
    artifacts_only_on_branch:        # optional paths or artifact ids
      - <path>
    carried_forward: true | false | partial
    discarded_or_overlaid:
      - description: <short>
        disposition: retained_in_history | explicitly_dropped | folded_into_merge_commit | unknown
  operator:
    actor: <id or automation>
    witness: <Operator id>
    notes: <optional free text>
  lineage:
    related_orchestration_run: <id or null>
    related_commits: [<sha>, ...]
```

**Rules**
- MUST be produced for any non-trivial sync (i.e., when pre-sync tip ≠ source tip).
- SHOULD be produced even for pure fast-forwards (for completeness).
- MUST NOT claim that discarded work is irrecoverable if Git history still contains it; the record only documents the sync-time disposition.

### 2.2 Orchestration Run

A durable record of one governed multi-model (or single-model) cognitive cycle.

```yaml
orchestration_run:
  schema_version: "OR-0.1.0"
  id: <uuid or deterministic id>
  timestamp_start: <ISO-8601>
  timestamp_end: <ISO-8601 or null if still open>
  intent: <short string>
  canonical_starting_commit: <sha>
  participating_models:
    - model: <name>
      branch: <name>
      branch_commit_observed: <sha>
  constraints_applied: [<string>, ...]
  divergence_records: [<id>, ...]          # references to DR objects
  stumpy:
    audit_result: <classification or null>
    findings: [<string>, ...]
    audit_commit_or_path: <ref or null>
  conflicts_and_open_questions: [<string>, ...]
  governance_disposition: <PASS | PASS_WITH_RECOURSE | MEDIATING | REJECT | QUARANTINED | SILENCE | null>
  operator_authorization:
    authorized: true | false | null
    witness: <Operator id or null>
    timestamp: <ISO-8601 or null>
    notes: <optional>
  resulting_canonical_commit: <sha or null>
  lineage:
    model_origin: <if single-model run>
    related_work_packages: [<id>, ...]
```

**Rules**
- One Orchestration Run SHOULD be opened for any significant governed effort that may later seek transmission or Stumpy review.
- Divergence Records produced during the run SHOULD be linked via `divergence_records`.
- `governance_disposition` and `operator_authorization` remain null until explicitly set; absence of authorization is not authorization.

---

## 3. Relationship Between the Two Objects

```text
Orchestration Run
      │
      ├── references zero or more Divergence Records
      ├── records Stumpy audit outcome
      ├── records Operator disposition / authorization
      └── optionally records resulting canonical commit

Divergence Record
      │
      └── may point back to the Orchestration Run that contained the sync
```

A sync that occurs outside a formal Orchestration Run still produces a Divergence Record; the `related_orchestration_run` field is simply null.

---

## 4. Suggested Storage Locations (Non-Authoritative)

| Object | Suggested path pattern |
|--------|------------------------|
| Divergence Record | `00_governance/<model>/divergence/<id>.yaml` or under an orchestration run directory |
| Orchestration Run | `00_governance/orchestration/runs/<id>.yaml` (shared) or `00_governance/<model>/runs/<id>.yaml` |

Exact layout is left open; the schemas are the primary contribution of this package.

---

## 5. Compatibility & Non-Disruption

- Existing history is not invalidated. The schemas apply going forward.
- A pure fast-forward sync can emit a minimal Divergence Record with empty `commits_only_on_branch`.
- Models that have never performed a governed sync simply have no Divergence Records yet.
- The Orchestration Run object does not replace Git commits or Stumpy audit artifacts; it indexes and links them.

---

## 6. Residual Risks & Open Questions

| ID | Item | Notes |
|----|------|-------|
| R1 | Volume of Divergence Records | High-frequency automated syncs could produce noise; MAY allow summarization or sampling rules later. |
| R2 | Deterministic vs UUID identifiers | Left open; deterministic preferred when inputs are stable. |
| R3 | Who may close an Orchestration Run | Operator or authorized automation; not yet fully specified. |
| Q1 | Should every Stumpy comparison automatically open or attach to an Orchestration Run? | Recommended direction: yes for formal comparisons. |
| Q2 | Cross-model runs vs single-model runs — same schema? | Proposal uses one schema with a `participating_models` list. |
| Q3 | Required retention period | Unspecified; inherits broader Vault retention policy. |

---

## 7. Disposition Recommendation

This proposal is offered for Operator review. Possible next steps:

1. Annotate / accept / request revision of the two schemas.
2. Authorize a follow-on package that emits concrete JSON Schema or YAML Schema files.
3. Authorize later transmission toward Orchestration Spec §4 and §13 (still subject to full merge rules and Stumpy audit).

No canonical mutation is requested or performed by this artifact.

---

## 8. Lineage & Provenance

```text
origin.model          = Grok
origin.branch         = grok
origin.work_package   = WP-GROK-003
origin.parent         = WP-GROK-001 / H1 + H4
origin.timestamp      = 2026-09-05T17:03:00Z
governance.signature  = SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05
operator.witness      = JRM-01 @liminaljermo
contracts.referenced  = multi-model-orchestration.md v0.1.0 (§4, §13)
```

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
