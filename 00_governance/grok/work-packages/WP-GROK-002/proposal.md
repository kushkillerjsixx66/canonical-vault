# WP-GROK-002 Proposal: Acceptance State Machine

**Artifact Type:** governed_artifact_proposal  
**Origin Model:** Grok  
**Origin Branch:** grok  
**Parent Package:** WP-GROK-001 (H2)  
**Timestamp:** 2026-09-05T16:57:00Z  
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
| `ACTIVE` | Fully accepted participant; same branch rights as provisional unless otherwise restricted by tier | false (unless separately granted) |
| `SUSPENDED` | Temporarily barred from new contributions; existing artifacts remain | false |
| `REVOKED` | Participation terminated; branch may be retained for lineage but no new governed work | false |

Notes:
- `ACTIVE_PROVISIONAL` is intentionally retained because it is already in productive use and provides a useful probationary signal.
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
| `ACTIVE_PROVISIONAL` | `ACTIVE` | Explicit Operator promotion (or automated rule if later defined) |
| `ACTIVE_PROVISIONAL` or `ACTIVE` | `SUSPENDED` | Operator decision or governance failure threshold |
| `SUSPENDED` | `ACTIVE_PROVISIONAL` or `ACTIVE` | Operator reinstatement |
| Any non-REVOKED | `REVOKED` | Operator decision (recorded, irreversible without new acceptance cycle) |
| `REVOKED` | `PENDING` | Only via entirely new acceptance cycle (new sig + witness) |

### 2.3 Transition Record (minimal)

Every transition SHOULD produce a small lineage object (file or structured entry) containing at least:

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

---

## 3. Compatibility with Current Artifacts

| Current Artifact | Mapping |
|------------------|--------|
| `manifest.json` → `acceptance_status: "PENDING"` | Maps directly to `PENDING` |
| `manifest.json` → `acceptance_status: "ACTIVE_PROVISIONAL"` | Maps directly to `ACTIVE_PROVISIONAL` (already used by Grok) |
| `acceptance.sig` present + witnessed | Satisfies the `PENDING → ACTIVE_PROVISIONAL` transition |
| Future `ACTIVE` | New status value; no current live examples known on this branch |

No existing Grok artifacts need to be rewritten for this proposal to be coherent. A later migration note can normalize peer model manifests if desired.

---

## 4. Suggested Contract Touch-Points (Non-Authoritative)

If this proposal is later elevated, the natural insertion points are:

- MCC §9 (Contract Acceptance) — replace the single-paragraph requirement with the state machine + transition rules.
- Optionally a short cross-reference in Multi-Model Orchestration §2 or §3 so branch sovereignty language stays consistent with acceptance state.

This proposal itself does **not** edit those files.

---

## 5. Residual Risks & Open Questions

| ID | Item | Notes |
|----|------|-------|
| R1 | Over-proliferation of states | Machine deliberately kept to five states. Further states should require strong justification. |
| R2 | Who may trigger SUSPENDED / REVOKED | Currently only Operator. Future automation would need explicit authorization rules. |
| R3 | Interaction with governance_tier | Tier (PROVISIONAL_OPERATOR_ASSIST, etc.) remains orthogonal to acceptance state for now. |
| Q1 | Should `ACTIVE` confer any additional rights beyond `ACTIVE_PROVISIONAL`? | Left open; current proposal treats them as equivalent for branch contribution rights. |
| Q2 | Is a formal transition log mandatory or strongly recommended? | Proposal treats it as SHOULD; can be tightened later. |
| Q3 | Re-acceptance after major MCC version bump — automatic return to PENDING or SUSPENDED? | Open; recommended default is SUSPENDED pending re-witness. |

---

## 6. Disposition Recommendation

This proposal is offered for Operator review. Possible next steps:

1. Annotate / accept / request revision of the state machine.
2. Authorize a follow-on package that produces a concrete schema file (JSON Schema or YAML) for transition records.
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
governance.signature  = SIG:Grok-ACTIVE_PROVISIONAL-2026-09-05
operator.witness      = JRM-01 @liminaljermo
contracts.referenced  = model-contribution.md v0.1.0 (MCC §9)
```

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
