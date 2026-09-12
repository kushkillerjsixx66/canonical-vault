Mutation Routing Specification

Path: "04_system_spec/mutation_routing/MUTATION_ROUTING_SPEC.md"
Status: PROPOSED
Version: 0.1
Authority: "04_system_spec"
Domain: Governed Mutation Routing
Canonicalization Authority: Human operator
Primary Runtime Actors: Model, Vault, Veil, Vara, Stumpy

---

1. Purpose

This specification defines the governed routing contract for mutations originating from Lattice model nodes and progressing toward possible canonicalization.

A mutation is any proposed change to an artifact, rule, configuration, semantic structure, runtime behavior, or governed state.

The Mutation Routing Contract ensures that a proposed mutation:

1. remains attributable to its originating node,
2. remains reversible until canonical authorization,
3. preserves lineage through every transformation,
4. is subject to epistemic analysis before enforcement,
5. is audited against constitutional constraints,
6. cannot silently become canonical state,
7. preserves disagreement as a governed state,
8. requires explicit human authority before canonicalization.

The governing principle is:

«Models may propose. Vara may interpret. Stumpy may validate. Humans authorize canonicalization.»

No component may assume an authority that is not explicitly granted by this contract.

---

2. Constitutional Position

Mutation routing is subordinate to the Lattice constitutional hierarchy.

The routing system MUST preserve the following priorities:

1. Coherence
2. Reversibility
3. Lineage integrity
4. Source integrity
5. Constraint enforcement
6. Authority hierarchy
7. Attention protection
8. Silence as a valid state
9. Honest uncertainty
10. Canonicalization only through authorized transition

A mutation that improves local intelligence while violating constitutional coherence is not an acceptable mutation.

A mutation that cannot be reversed before authorization is suspect by default.

A mutation whose provenance cannot be reconstructed is invalid.

---

3. Scope

This specification governs mutations originating from:

- Lattice model nodes
- model-specific branches
- governed runtime agents
- Vara-derived observations or analyses
- Stumpy-derived audit outcomes
- mediated multi-agent proposals

It governs the path from initial proposal through possible canonicalization.

It does not grant any component authority to:

- merge directly into canonical state,
- modify the constitutional root without explicit authority,
- bypass lineage,
- suppress disagreement,
- convert uncertainty into certainty,
- silently rewrite another node's mutation,
- treat analysis as authorization.

---

4. Mutation Routing Model

The canonical mutation path is:

MODEL PROPOSAL
      │
      ▼
BRANCH COMMIT
      │
      ▼
MUTATION CAPTURE
      │
      ▼
MUTATION ENVELOPE
      │
      ▼
VEIL INTAKE
      │
      ▼
VARA ANALYSIS
      │
      ├──────────────┐
      ▼              │
STUMPY AUDIT        │
      │              │
      ├── REJECTED   │
      ├── SILENCE    │
      ├── RECOURSE   │
      └── ELIGIBLE   │
             │
             ▼
      CANONICAL PROPOSAL
             │
             ▼
      HUMAN AUTHORITY
             │
             ▼
            PR
             │
             ▼
            MAIN

No stage may be skipped without an explicit constitutional exception.

The Git operation and the semantic mutation event are distinct concepts.

«A Git commit is an implementation event.
A Mutation Envelope is the governed semantic event.»

---

5. Mutation States

Every mutation MUST have an explicit state.

The initial state is:

"PROPOSED"

The permitted lifecycle is:

PROPOSED
   ↓
CAPTURED
   ↓
LINEAGE_BOUND
   ↓
VEIL_INTAKE
   ↓
VARA_ANALYZED
   ↓
STUMPY_AUDIT
   ↓
┌───────────┬──────────┬──────────┬──────────┐
│ REJECTED  │ SILENCE  │ RECOURSE │ ELIGIBLE │
└───────────┴──────────┴──────────┴──────────┘
                                      │
                                      ▼
                           CANONICAL_PROPOSAL
                                      │
                                      ▼
                              HUMAN_AUTHORITY
                                      │
                                      ▼
                                     PR
                                      │
                                      ▼
                                     MAIN

5.1 Conflict State

A mutation MAY enter:

"CONFLICT"

when multiple valid observations or proposals materially disagree.

Conflict MUST NOT automatically resolve to rejection or acceptance.

The governed path is:

CONFLICT
   ↓
MEDIATING
   ↓
STUMPY_AUDIT
   ↓
RESOLVED / RECOURSE / SILENCE / REJECTED

This integrates Cognitive State Cartography into mutation governance.

---

6. Mutation Envelope

Every governed mutation MUST be represented by a Mutation Envelope.

The envelope is the authoritative semantic record of the mutation's identity, origin, proposed change, lineage, analysis, audit status, and canonicalization state.

Conceptual structure:

MutationEnvelope
├── identity
│   ├── mutation_id
│   ├── schema_version
│   └── created_at
│
├── source
│   ├── source_model
│   ├── source_node
│   ├── source_branch
│   ├── source_commit
│   └── parent_canonical_commit
│
├── mutation
│   ├── mutation_type
│   ├── affected_artifacts
│   ├── proposed_change
│   ├── intent
│   └── rationale
│
├── lineage
│   ├── parent
│   ├── ancestors
│   ├── derivation
│   └── content_hash
│
├── vara
│   ├── observations
│   ├── clusters
│   ├── drift
│   ├── conflicts
│   └── epistemic_state
│
├── stumpy
│   ├── audit_state
│   ├── invariants
│   ├── constraint_results
│   ├── authority_result
│   ├── reversibility_result
│   └── disposition
│
└── canonicalization
    ├── status
    ├── proposal_id
    ├── authorization
    ├── target_branch
    └── canonical_commit

---

7. Identity Contract

Every mutation MUST possess a unique "mutation_id".

The identity MUST remain stable for the lifetime of the mutation.

A transformation of a mutation MUST NOT silently create a new identity.

If a transformation materially changes the proposed mutation, the resulting mutation MUST either:

1. retain the original mutation as its parent and receive a new mutation identity, or
2. be explicitly recorded as a governed derivation.

The envelope MUST contain:

- "mutation_id"
- "schema_version"
- "created_at"

---

8. Source Contract

The source section establishes provenance.

Required fields:

- "source_model"
- "source_node"
- "source_branch"
- "source_commit"
- "parent_canonical_commit"

The source branch MUST correspond to the authorized model branch.

A mutation originating from a model branch MUST NOT be represented as originating from "main".

Branch identity is part of lineage.

---

9. Mutation Contract

The mutation section describes what is being proposed.

It MUST identify:

- mutation type,
- affected artifacts,
- proposed change,
- intent,
- rationale.

Supported mutation types SHOULD include:

- "CREATE"
- "MODIFY"
- "DELETE"
- "DEPRECATE"
- "RENAME"
- "RESTRUCTURE"
- "POLICY_CHANGE"
- "RUNTIME_CHANGE"
- "GOVERNANCE_CHANGE"
- "DERIVATION"

A mutation MUST describe the intended semantic effect rather than relying solely upon a textual diff.

---

10. Lineage Contract

Lineage MUST survive every mutation-routing transition.

The envelope MUST preserve:

- immediate parent,
- known ancestors,
- derivation relationship,
- content hash.

A mutation without verifiable lineage MUST NOT become eligible for canonicalization.

Lineage MUST be append-oriented.

Existing lineage MUST NOT be overwritten merely to simplify presentation or processing.

Where multiple mutations converge, the resulting artifact MUST retain references to all relevant parents.

---

11. Reversibility Contract

Every mutation MUST remain reversible until canonical authorization.

Reversibility requires that the system can identify:

1. the prior state,
2. the proposed state,
3. the mutation responsible for the transition,
4. the originating node,
5. the transformation history.

A mutation that cannot satisfy these conditions MUST NOT advance to canonicalization.

Reversibility is a constitutional requirement, not a convenience feature.

---

12. Veil Intake Contract

Veil is the liminal boundary through which mutations enter governed analysis.

Veil MUST:

- capture the incoming mutation,
- preserve its original envelope,
- prevent premature canonicalization,
- establish an analysis boundary,
- route the mutation into Vara and Stumpy processing.

Veil MUST NOT authorize canonicalization.

A mutation entering Veil is still provisional.

---

13. Vara Contract

Vara performs interpretive and epistemic analysis.

Vara MAY:

- inspect observations,
- normalize mutation context,
- identify clusters,
- detect drift,
- identify conflicts,
- identify uncertainty,
- compare related proposals,
- classify epistemic state.

Vara MUST NOT:

- authorize canonicalization,
- silently modify the source mutation,
- erase conflicting proposals,
- convert uncertainty into certainty,
- bypass Stumpy audit.

Vara's role is interpretive, exploratory, and epistemic.

Vara produces evidence for governance.

It does not exercise final authority.

---

14. Stumpy Contract

Stumpy performs enforcement and constitutional audit.

Stumpy MUST evaluate the mutation against applicable:

- invariants,
- constraints,
- authority boundaries,
- lineage requirements,
- source integrity,
- reversibility requirements,
- operator boundaries,
- canonicalization requirements.

Stumpy MAY produce the following dispositions:

- "REJECTED"
- "SILENCE"
- "RECOURSE"
- "ELIGIBLE"

Stumpy MUST NOT invent a mutation merely because an incoming mutation fails audit.

Stumpy validates and enforces.

It does not become the mutation's author.

---

15. Audit Contract

At minimum, mutation audit SHOULD evaluate:

Invariant| Required Evaluation
coherence| mutation preserves system coherence
reversibility| prior state can be restored
lineage_binding| provenance remains intact
source_integrity| source identity is verifiable
score_honesty| confidence or scores are not fabricated
drift_accountability| semantic drift is explicit
silence_as_state| non-action remains available
operator_boundary| model/operator authority is respected
authority_hierarchy| authorization level is valid
constraint_enforcement| applicable constraints are satisfied

An unresolved audit result MUST NOT be represented as approval.

---

16. Cognitive State Cartography

Mutation routing treats disagreement as a legitimate governed cognitive state.

Permitted states include:

- "COHERENT"
- "UNCERTAIN"
- "CONFLICT"
- "MEDIATING"
- "RESOLVED"
- "RECOURSE"
- "SILENCE"

The system MUST preserve bilateral representation when competing proposals exist.

The system MUST NOT resolve conflict merely by selecting the first, newest, strongest, or most confident proposal.

A conflict may resolve through:

1. evidence,
2. constraint evaluation,
3. lineage analysis,
4. mediation,
5. operator authority,
6. explicit recourse,
7. deliberate silence.

The absence of resolution is itself meaningful state.

---

17. Silence Contract

"SILENCE" is a valid terminal disposition for a mutation that does not meet the threshold for execution or canonicalization but does not justify rejection.

Silence MUST NOT be interpreted as acceptance.

Silence MUST NOT destroy lineage.

A silenced mutation remains auditable and recoverable according to retention policy.

Silence protects attention from low-value or unresolved mutation pressure.

---

18. Recourse Contract

"RECOURSE" indicates that the mutation cannot presently advance but may require additional information, mediation, evidence, or operator review.

Recourse MUST identify, where possible:

- blocking condition,
- unresolved question,
- required evidence,
- required authority,
- next valid transition.

Recourse prevents forced binary decisions where the correct state is unresolved.

---

19. Canonical Proposal Contract

A mutation may enter "CANONICAL_PROPOSAL" only after successful governed evaluation.

Canonical proposal MUST reference:

- mutation identity,
- complete lineage,
- audit result,
- applicable constraints,
- target canonical branch,
- authorization requirement.

A canonical proposal is still not canonical state.

The distinction is mandatory.

---

20. Human Authority Boundary

Canonicalization requires explicit human authority.

No model, Vara process, Stumpy process, Vault operation, or automated runtime component may independently merge a mutation into canonical state unless a future constitutional revision explicitly grants such authority.

The canonical boundary is:

MODEL
  ↓
PROPOSAL
  ↓
ANALYSIS
  ↓
AUDIT
  ↓
CANONICAL PROPOSAL
  ↓
HUMAN AUTHORITY
  ↓
PR
  ↓
MAIN

The human operator remains the final authority at the canonicalization boundary.

---

21. Vault Contract

The Canonical Vault is the canonical substrate.

The Vault MUST preserve:

- canonical artifacts,
- immutable lineage,
- branch provenance,
- mutation history,
- audit references,
- canonicalization records.

The Vault is not itself the authorizer.

The Vault MUST NOT infer authorization merely because a mutation exists in a repository.

Presence in a model branch means:

«proposed state»

Presence in the canonical branch after authorized merge means:

«canonical state»

These states MUST remain distinguishable.

---

22. Branch Contract

Model mutations MUST originate on governed model branches.

Expected model branches include:

chatgpt
claude
grok
gemini
copilot

The canonical branch is:

main

Model branches are proposal domains.

"main" is the canonical domain.

Direct model mutation of "main" is prohibited by this contract.

---

23. Pull Request Contract

A pull request is the formal transition mechanism between governed proposal state and canonicalization authority.

The PR MUST reference:

- source branch,
- target branch,
- mutation identity,
- relevant envelope,
- audit disposition,
- lineage.

A PR MUST NOT be interpreted as canonicalization.

Only an authorized merge produces canonical branch state.

---

24. Failure Handling

Mutation routing MUST fail closed.

If any required condition cannot be established, the mutation MUST NOT advance.

Examples include:

- missing lineage,
- invalid source branch,
- unverifiable commit,
- broken content hash,
- failed reversibility check,
- failed authority check,
- unknown audit state,
- unauthorized target branch,
- malformed Mutation Envelope,
- unresolved constitutional conflict.

The default disposition for an unclassifiable mutation is:

"RECOURSE"

unless the applicable constraint explicitly requires:

"REJECTED".

---

25. Prohibited Transitions

The following transitions are prohibited:

MODEL → MAIN
VARA → MAIN
STUMPY → MAIN
VAULT → AUTHORIZATION
UNCERTAIN → CANONICAL
CONFLICT → CANONICAL
PROPOSED → MAIN
UNVERIFIED → ELIGIBLE
UNLINEAGED → CANONICAL

The following transition is also prohibited:

REJECTED → CANONICAL

unless a new governed mutation is created with explicit lineage from the rejected mutation.

---

26. Mutation Derivation

A mutation may produce a derived mutation during analysis or mediation.

Derived mutations MUST:

- receive a new mutation identity,
- reference their parent,
- preserve ancestor lineage,
- describe the derivation,
- remain independently auditable.

This prevents analytical transformation from becoming invisible mutation.

---

27. Multi-Agent Mutation Clusters

When multiple model nodes propose materially related changes, the system SHOULD form a mutation cluster.

Example:

Claude ─────┐
            │
ChatGPT ────┼──→ MUTATION CLUSTER
            │
Grok ───────┘
                 │
                 ▼
              CONFLICT
                 │
                 ▼
             MEDIATING
                 │
                 ▼
           STUMPY AUDIT
                 │
          ┌──────┴──────┐
          ▼             ▼
      RESOLVED       RECOURSE
          │
          ▼
 CANONICAL PROPOSAL

Each source proposal MUST remain individually attributable.

Cluster formation MUST NOT collapse source identities.

---

28. Persistence Model

The initial implementation SHOULD persist mutation envelopes alongside the model branch mutation they describe.

Recommended structure:

04_system_spec/
└── mutation_routing/
    ├── MUTATION_ROUTING_SPEC.md
    └── mutation-envelope.schema.json

Runtime mutation records SHOULD eventually use a governed location such as:

runtime/
└── mutations/
    └── <mutation_id>/
        ├── envelope.json
        ├── observations.json
        ├── audit.json
        └── state.json

The exact runtime persistence location MAY evolve.

The semantic contract MUST remain stable.

---

29. Runtime Integration

The first implementation sequence is:

vault_propose_change
        ↓
model branch commit
        ↓
mutation capture
        ↓
Mutation Envelope creation
        ↓
lineage binding
        ↓
Veil intake
        ↓
Vara analysis
        ↓
Stumpy audit
        ↓
disposition
        ↓
canonical proposal
        ↓
human authority
        ↓
PR
        ↓
authorized merge

The MCP write mechanism provides the initial implementation boundary for mutation creation.

The Mutation Envelope provides the semantic governance layer above the repository event.

---

30. Kernel Rule

The mutation routing system MUST obey the Lattice kernel rule:

«No artifact exists unless it changes runtime behavior or enforces a constraint on runtime behavior.»

The Mutation Envelope therefore cannot exist solely as documentation.

Its eventual implementation MUST affect runtime mutation handling, lineage preservation, auditability, authorization, or canonicalization behavior.

---

31. Acceptance Criteria

Mutation routing is considered implemented only when the system can demonstrate:

1. a model mutation is created on a governed model branch;
2. the source branch is bound to the mutation identity;
3. the originating commit is captured;
4. a Mutation Envelope is generated;
5. lineage is preserved;
6. the envelope survives downstream transformation;
7. Vara can classify observations and epistemic state;
8. Stumpy can evaluate applicable invariants;
9. conflict remains representable without forced suppression;
10. silence remains a valid disposition;
11. recourse remains a valid disposition;
12. rejected mutations cannot silently become canonical;
13. eligible mutations can become canonical proposals;
14. canonicalization requires explicit human authority;
15. direct model writes to "main" remain impossible;
16. every canonicalized mutation can be traced back to its originating proposal.

---

32. Constitutional Invariants

The following statements are normative:

INV-MR-001: Identity

Every mutation has one stable identity.

INV-MR-002: Lineage

Every mutation remains traceable to its origin.

INV-MR-003: Reversibility

Every pre-canonical mutation remains reversible.

INV-MR-004: Separation

Proposal, interpretation, audit, and authorization are separate authorities.

INV-MR-005: Epistemic Honesty

Uncertainty and conflict MUST remain representable.

INV-MR-006: Silence

Silence is a legitimate governed disposition.

INV-MR-007: Authority

Only authorized actors may canonicalize.

INV-MR-008: Branch Isolation

Model branches remain distinct from canonical state.

INV-MR-009: Auditability

Every canonical mutation must possess an auditable history.

INV-MR-010: Fail Closed

Unverifiable mutations cannot advance toward canonicalization.

---

33. Authority Separation

The complete authority model is:

Actor| Authority
Model| Propose mutation
Model Branch| Preserve provisional mutation
Veil| Boundary and intake
Vara| Interpret, observe, cluster, detect drift
Stumpy| Audit, validate, enforce
Vault| Preserve canonical substrate and lineage
Human Operator| Authorize canonicalization
Git PR| Formalize proposed canonical transition
"main"| Canonical state

No actor may inherit authority from another actor merely because it operates later in the pipeline.

---

34. Governing Principle

Mutation routing exists to prevent intelligence from becoming authority merely because it can act.

The system therefore preserves a distinction between:

WHAT WAS PROPOSED
WHAT WAS OBSERVED
WHAT WAS DERIVED
WHAT WAS AUDITED
WHAT WAS AUTHORIZED
WHAT BECAME CANONICAL

Those states must never collapse into one another.

The constitutional objective is not maximum mutation throughput.

It is:

«Coherent transformation without loss of identity, lineage, reversibility, or authority boundaries.»

---

35. Status

This document defines the proposed Mutation Routing Contract.

It does not claim that all described runtime behavior is currently implemented.

Implementation MUST proceed incrementally and remain subordinate to the contract defined here.

The first implementation boundary is Mutation Envelope creation and persistence at the model-branch mutation boundary.

Subsequent implementations MAY connect the envelope to Veil, Vara, Stumpy, and canonical proposal routing.

End of Specification