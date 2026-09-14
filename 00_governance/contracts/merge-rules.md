# Canonical Merge Rules

**Version:** 0.1.0  
**Applies to:** Model-specific branches and canonical `main`  
**Depends on:** Model Contribution Contract (MCC) v0.1.0

## 1. Authority Model

`main` is the canonical governed state.

Model branches are controlled divergence surfaces. Branch commits have no canonical authority merely because they exist, pass tests, or receive model consensus.

**Models propose. Stumpy audits. The operator authorizes canonical mutation.**

## 2. Merge Preconditions

A branch contribution is merge-eligible only when all applicable conditions are satisfied:

1. The branch identifies its model and declared scope.
2. The proposed artifact has complete required lineage.
3. The artifact satisfies the MCC artifact boundaries.
4. Required Lattice kernel constraints are satisfied.
5. Stumpy has completed a canonical comparison audit.
6. All material `CONFLICT`, `SEMANTIC_DRIFT`, `INVARIANT_VIOLATION`, and `UNVERIFIED` findings have an explicit disposition.
7. Required operator review is complete.
8. An authorized operator explicitly approves the merge.

Failure of any mandatory precondition blocks merge.

## 3. Merge States

Every proposed contribution receives one governed disposition:

- `PASS` — eligible for authorized merge.
- `PASS_WITH_RECOURSE` — eligible only with a recorded follow-up governance action.
- `MEDIATING` — unresolved disagreement requires governance review.
- `REJECT` — contribution does not satisfy merge requirements.
- `QUARANTINED` — branch or artifact is temporarily prohibited from transmission.
- `SILENCE` — insufficient evidence exists for a safe disposition; no canonical mutation occurs.

## 4. Stumpy Audit Boundary

Stumpy may:

- Compare branch state against canonical state.
- Detect additions, deletions, conflicts, omissions, and semantic drift.
- Validate lineage and declared metadata.
- Identify cross-branch convergence or disagreement.
- Produce an audit record.
- Recommend merge, rejection, mediation, quarantine, or recourse.

Stumpy may not:

- Merge a model branch into `main` by its own authority.
- Rewrite canonical artifacts to resolve a disagreement.
- Suppress a material conflict.
- Treat model consensus as equivalent to operator authorization.

## 5. Conflict Handling

A conflict is evidence, not automatically an error.

When a branch contradicts canonical material:

```text
BRANCH
  ↓
STUMPY COMPARISON
  ↓
CONFLICT RECORD
  ↓
EVIDENCE + LINEAGE REVIEW
  ↓
OPERATOR MEDIATION
  ↓
RESOLVE / REJECT / RECOURSE / SILENCE
```

Canonical state remains unchanged until an authorized resolution is committed.

## 6. Cross-Branch Convergence

When independent model branches produce materially similar challenges, Stumpy must record the convergence rather than silently promoting it to canonical truth.

Convergence increases review priority but does not independently grant merge authority.

## 7. Merge Scope

A merge must identify exactly which artifacts and commits are being promoted.

Unrelated branch changes must not enter canonical state through an approved contribution.

Partial merges are permitted when lineage and audit boundaries remain reconstructable.

## 8. Lineage Preservation

A successful merge must preserve:

- Source model
- Source branch
- Source commit
- Transmission record
- Stumpy audit record
- Operator identity/witness
- Authorization timestamp
- Resulting canonical commit

The resulting canonical state must be reconstructable back to its originating branch contribution.

## 9. Rejection and Quarantine

Rejected artifacts remain attributable to their originating branch and are not silently deleted as if they never existed.

Quarantine may be applied when there is evidence of:

- repeated invariant violation
- lineage corruption
- unauthorized cross-branch modification
- fabricated provenance
- uncontrolled transmission
- material governance failure

Quarantine status itself must be recorded.

## 10. Canonical Mutation Rule

No model, branch, audit process, automated test, or Stumpy classification can independently mutate canonical governance state.

The minimum canonical mutation chain is:

```text
MODEL CONTRIBUTION
      ↓
LINEAGE VALIDATION
      ↓
STUMPY AUDIT
      ↓
GOVERNANCE DISPOSITION
      ↓
AUTHORIZED OPERATOR APPROVAL
      ↓
MERGE
      ↓
POST-MERGE AUDIT
```

## 11. Post-Merge Verification

After an authorized merge:

1. The resulting canonical commit is recorded.
2. The merged artifacts are re-audited against declared invariants.
3. Lineage is verified from source branch through canonical commit.
4. Any failed post-merge invariant triggers remediation rather than silent correction.

## 12. Constitutional Principle

> **Divergence is permitted. Canonical mutation is governed.**

The purpose of branching is to allow independent cognition without sacrificing coherence, reversibility, or lineage.
