# WP-GROK-002 Proposal: Acceptance State Machine

**Artifact Type:** governed_artifact_proposal  
**Origin Model:** Grok  
**Origin Branch:** grok  
**Parent Package:** WP-GROK-001 (H2)  
**Timestamp:** 2026-09-05T16:57:00Z  
**Revised:** 2026-09-05T17:00:00Z (tightenings applied)  
**Governance Signature:** SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05  
**Lineage:** model=Grok → branch=grok → WP-GROK-001/H2 → WP-GROK-002 → this artifact

---

## 1. Problem Statement

MCC §9 currently requires only the existence of an `acceptance.sig`. It does not define:

- intermediate states between initial declaration and full participation,
- legal transitions between states,
- re-acceptance rules after contract version changes,
- suspension or revocation procedure,
- a stable vocabulary for live manifests.

Observed consequence: live manifests already invent pragmatic statuses (e.g. `ACTIVE_PROVISIONAL`). Without a shared state machine, vocabulary drift is inevitable and Stumpy (or any auditor) lacks a stable signal.

---

## 2. Proposed State Machine

### 2.1 States

| State | Meaning | Canonical Merge Authority |
|-------|---------|---------------------------|
| `PENDING` | Identity declared; acceptance.sig not yet committed or not yet witnessed | false |
| `ACTIVE_PROVISIONAL` | Acceptance recorded; operating under provisional tier; full contribution scope available on own branch | false |
| `ACTIVE` | Fully accepted participant. In addition to all `ACTIVE_PROVISIONAL` rights, may initiate governed cross-model comparison requests and is eligible for governance-tier promotion review | false (unless separately granted) |
| `SUSPENDED` | Temporarily barred from new contributions; existing artifacts remain | false |
| `REVOKED` | Participation terminated; branch may be retained for lineage but no new governed work | false |

Notes:
- `ACTIVE_PROVISIONAL` is intentionally retained because it is already in productive use and provides a useful probationary signal.
- `ACTIVE` is distinguished by two concrete additional capabilities: (1) authority to request governed cross-model comparisons, and (2) eligibility for governance-tier promotion review. Until an identity is promoted to `ACTIVE`, those two capabilities remain unavailable.
- No state grants canonical merge authority by itself. That remains an orthogonal Operator decision.

### 2.2 Legal Transitions

```text
PENDING ──────────────► ACTIVE_PROVISIONAL
   │                         │
   │                         ├──► ACTIVE
   │                         │
   │                         ├──► SUSPENDED ◄──► ACTIVE / ACTIVE_PROVISIONAL
   │                         │
   └─────────────────────────┴──► REVOKED
```

| From | To | Required Conditions |
|------|----|---------------------|
| `PENDING` | `ACTIVE_PROVISIONAL` | Valid `acceptance.sig` committed + Operator witness recorded |
| `ACTIVE_PROVISIONAL` | `ACTIVE` | Explicit Operator promotion |
| `ACTIVE_PROVISIONAL` or `ACTIVE` | `SUSPENDED` | Operator decision or governance failure threshold |
| `SUSPENDED` | `ACTIVE_PROVISIONAL` or `ACTIVE` | Operator reinstatement (returns to the state held before suspension unless otherwise specified) |
| Any non-REVOKED | `REVOKED` | Operator decision (recorded; irreversible without new acceptance cycle) |
| `REVOKED` | `PENDING` | Only via entirely new acceptance cycle (new sig + witness) |

**Contract version bump rule (normative):**  
A major version bump of the Model Contribution Contract (MCC) automatically transitions every non-`REVOKED` identity to `SUSPENDED`. Reinstatement requires an explicit Operator re-witness against the new contract version. Minor or patch bumps leave acceptance state unchanged.

### 2.3 Transition Record

**MUST** produce a transition record for any transition that:
- leaves `PENDING`, or
- enters `SUSPENDED` or `REVOKED`, or
- is caused by a major MCC version bump.

**SHOULD** produce a transition record for all other transitions.

Minimal schema:

```yaml
transition:
  from: <state>
  to: <state>
  timestamp: <ISO-8601>
  actor: <model or Operator id>
  witness: <Operator id or authorized delegate>
  reason: <short string>
  related_commit: <sha or null>
  contract_version: <MCC version at time of transition>
```

Suggested location: `00_governance/<model>/transitions/` or an append-only section inside an extended acceptance record.

#### Example (Grok activation)

```yaml
transition:
  from: PENDING
  to: ACTIVE_PROVISIONAL
  timestamp: "2026-09-05T16:45:00Z"
  actor: Grok
  witness: JRM-01 @liminaljermo
  reason: "Operator direction to activate identity; acceptance.sig committed"
  related_commit: "de03812af35100d500e660b5fc67291f30561f49"
  contract_version: "MCC-0.1.0"
```

---

## 3. Compatibility with Current Artifacts

| Current Artifact | Mapping |
|------------------|--------|
| `manifest.json` → `acceptance_status: "PENDING"` | Maps directly to `PENDING` |
| `manifest.json` → `acceptance_status: "ACTIVE_PROVISIONAL"` | Maps directly to `ACTIVE_PROVISIONAL` (already used by Grok) |
| `acceptance.sig` present + witnessed | Satisfies the `PENDING → ACTIVE_PROVISIONAL` transition |
| Future `ACTIVE` | New status value; confers the two additional capabilities defined in §2.1 |

No existing Grok artifacts need to be rewritten for this proposal to be coherent. A later migration note can normalize peer model manifests if desired.

---

## 4. Suggested Contract Touch-Points (Non-Authoritative)

If this proposal is later elevated, the natural insertion points are:

- MCC §9 (Contract Acceptance) — replace the single-paragraph requirement with the state machine + transition rules + version-bump rule.
- Optionally a short cross-reference in Multi-Model Orchestration §2 or §3 so branch sovereignty language stays consistent with acceptance state.

This proposal itself does **not** edit those files.

---

## 5. Residual Risks & Open Questions

| ID | Item | Notes |
|----|------|-------|
| R1 | Over-proliferation of states | Machine deliberately kept to five states. Further states should require strong justification. |
| R2 | Who may trigger SUSPENDED / REVOKED | Currently only Operator. Future automation would need explicit authorization rules. |
| R3 | Interaction with governance_tier | Tier (PROVISIONAL_OPERATOR_ASSIST, etc.) remains orthogonal to acceptance state for now. |
| R4 | Automatic SUSPENDED on major MCC bump may be disruptive | Accepted trade-off for signal clarity; Operator can reinstate promptly. |
| Q1 | Exact governance-failure threshold that auto-triggers SUSPENDED | Left to future Stumpy / Operator policy. |
| Q2 | Should transition records themselves be subject to Stumpy audit? | Recommended yes; not yet specified. |

---

## 6. Disposition Recommendation

This revised proposal is offered for Operator review. Possible next steps:

1. Annotate / accept / request further revision.
2. Authorize a follow-on package that produces a concrete JSON Schema or YAML schema file for transition records.
3. Authorize a later transmission package that proposes the text insertion into MCC §9 (still subject to full merge rules and Stumpy audit).

No canonical mutation is requested or performed by this artifact.

---

## 7. Lineage & Provenance

```text
origin.model          = Grok
origin.branch         = grok
origin.work_package   = WP-GROK-002
origin.parent         = WP-GROK-001 / H2
origin.timestamp      = 2026-09-05T16:57:00Z
origin.revised        = 2026-09-05T17:00:00Z
revision.reason       = "Apply internal review tightenings: ACTIVE motivation, MUST transition log, normative version-bump rule, example record"
governance.signature  = SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05
operator.witness      = JRM-01 @liminaljermo
contracts.referenced  = model-contribution.md v0.1.0 (MCC §9)
```

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
