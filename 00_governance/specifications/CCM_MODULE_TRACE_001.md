# CCM MODULE TRACE 001
## Registry → Specification → Contract → Runtime → Test → Evidence

**Status:** DRAFT / PRE-CANONICAL
**Parent:** `CANONICAL_CONSISTENCY_MATRIX.md`
**Observed branch:** `main`

## Executive Finding

The module architecture is substantially specified, but the current runtime contains a pronounced **specification-to-implementation gap** for several legacy module entry points.

The strongest example is not subtle: the module specifications describe Sentinel, Veil, Stumpy, Crossroad, and SBM as governed modules with substantial behavior, while the referenced runtime files for Sentinel, Veil, Crossroad, Stumpy, and SBM are lightweight primitives that do not implement those specifications.

This is precisely the distinction Stumpy must preserve:

> **A specified capability is not an implemented capability. An implemented file is not evidence of implemented specification semantics.**

## 1. Module Trace Matrix

| Module | Registry | Spec | Contract / Schema | Runtime Target | Observed Runtime | Tests / Evidence | Current Classification |
|---|---|---|---|---|---|---|---|
| Vault | ✓ | ✓ | ✓ | `05_runtime/vault.py` | substantial governed implementation | present/partial | `IMPLEMENTED / VERIFICATION REQUIRED` |
| Sentinel | ✓ | ✓ | ✓ | `05_runtime/sentinel.py` | `inspect(signal) -> signal is not None` | invariant smoke tests only | `SPECIFICATION DRIFT / CRITICAL` |
| Veil | ✓ | ✓ | ✓ | `05_runtime/veil.py` | `filter(pulse) -> pulse` | no demonstrated contract suite | `SPECIFICATION DRIFT / HIGH` |
| Vara | ✓ | ✓ | ✓ | `05_runtime/vara.py` + scan stack | substantial scan implementation | Vara tests present | `IMPLEMENTED / CROSS-LAYER VERIFICATION REQUIRED` |
| Stumpy | ✓ | ✓ | ✓ | `05_runtime/stumpy.py` | five-name membership check | invariant smoke tests explicitly skip absent richer API | `SPECIFICATION DRIFT / CRITICAL` |
| Crossroad | ✓ | ✓ | ✓ | `05_runtime/rift.py` | `explore(state) -> state` | no demonstrated module conformance | `SPECIFICATION DRIFT / HIGH` |
| SBM | ✓ | ✓ | ✓ | `05_runtime/echo.py` | history append only | no demonstrated module conformance | `SPECIFICATION DRIFT / HIGH` |

## 2. Authority / Specification Trace

### 2.1 Registry

`MODULE_REGISTRY.md` declares nine ranked modules and states that modules not listed are unauthorized. It maps Stumpy to `05_runtime/stumpy.py`, Sentinel to `05_runtime/sentinel.py`, Veil to `05_runtime/veil.py`, Vara to `05_runtime/vara.py`, Crossroad to `05_runtime/rift.py`, and SBM to `05_runtime/echo.py`.

The registry therefore makes the runtime files normative implementation references rather than incidental examples.

### 2.2 Sentinel

The Sentinel specification requires G1/G2/G3 evaluation, invariant monitoring, unauthorized-module rejection, fabrication detection, Sentinel Lock, structured decisions, and lock clearance.

The referenced runtime implementation currently exposes only:

```python
class Sentinel:
    def inspect(self, signal):
        return signal is not None
```

**Classification:** `SPECIFICATION_DRIFT`.

This is not a minor missing feature. The implementation does not instantiate the specified enforcement model.

### 2.3 Veil

The Veil specification requires quarantine intake, hypothesis staging, operator review queues, governed promotion, governed discard, overflow handling, structured entries, and Stumpy logging.

The referenced runtime implementation currently exposes only:

```python
class Veil:
    def filter(self, pulse):
        return pulse
```

**Classification:** `SPECIFICATION_DRIFT`.

### 2.4 Crossroad

The Crossroad specification requires path resolution, coherence/attention scoring, tie-breaking, rejected-path preservation, operator override, and Stumpy logging.

The referenced runtime implementation currently exposes only:

```python
class Rift:
    def explore(self, state):
        return state
```

**Classification:** `SPECIFICATION_DRIFT`.

There is also a naming mismatch: specification identity is `CROSSROAD`, implementation class is `Rift`. That can be valid as an implementation alias, but no explicit adapter/identity contract was observed in this pass.

### 2.5 SBM

The SBM specification requires bidirectional Neuralese translation, COL parsing, grounding, HUD modes, failure semantics, and Stumpy cooperation.

The referenced runtime implementation currently exposes only an `Echo` object with an append-only history method.

**Classification:** `SPECIFICATION_DRIFT`.

### 2.6 Stumpy

The Stumpy specification requires independent evidence acquisition, claim extraction, comparison, verification, epistemic-state classification, evidence-bound reporting, escalation, recursive auditability, and non-circularity.

The referenced runtime implementation currently contains an initializer with five invariant names and an `audit(result)` method that returns whether each name occurs as a key in the supplied result.

This does not implement the specified audit pipeline.

The repository's own Stumpy V1 specification explicitly states that the lightweight `05_runtime/stumpy.py` implementation is insufficient and should be treated as a legacy primitive until replaced or wrapped.

**Classification:** `KNOWN LEGACY PRIMITIVE / SPECIFICATION DRIFT`.

## 3. Strongest Implemented Path: Governance Boundary → Vault

The newer governance runtime is materially stronger than the legacy module entry points.

`GovernanceBoundary.execute()`:

1. obtains active and anchor Vault state;
2. calls `AuthoritativeGovernanceEngine.evaluate_request()`;
3. creates a transition and lineage event;
4. quarantines denied decisions;
5. commits mutation only through the Vault for recognized mutating actions;
6. returns a governed response.

The contracts include validated operator context, explicit intent, governed requests, structured gate results, governance decisions, transition objects, lineage events, and commit receipts.

The Vault enforces decision allowance, cryptographic lineage binding, schema validation, append-only node insertion, destructive reset prohibition, and root-hash generation.

**Classification:** `SUBSTANTIAL IMPLEMENTATION / NEEDS END-TO-END CONFORMANCE TESTING`.

## 4. Critical Runtime Contradictions

### MT-001 — Sentinel specification/runtime divergence

**Expected:** full G1/G2/G3 enforcement and lock behavior.

**Observed:** null-check only in legacy entry point.

**Severity:** CRITICAL.

### MT-002 — Stumpy specification/runtime divergence

**Expected:** independent evidence-bound constitutional auditor.

**Observed:** key-presence checker.

**Severity:** CRITICAL.

### MT-003 — Veil specification/runtime divergence

**Expected:** governed quarantine/promotion/discard state machine.

**Observed:** identity filter.

**Severity:** HIGH.

### MT-004 — Crossroad specification/runtime divergence

**Expected:** path-selection decision engine.

**Observed:** identity explorer.

**Severity:** HIGH.

### MT-005 — SBM specification/runtime divergence

**Expected:** semantic binding / Neuralese boundary.

**Observed:** history recorder.

**Severity:** HIGH.

## 5. Epistemic Trace

The epistemic substrate has a coherent declared chain:

```text
Empirical Doctrine
        ↓
Epistemic Laws
        ↓
Evidence Classes
        ↓
Signal Qualification
        ↓
Epistemic Constraints
        ↓
Substrate Model / Principles
        ↓
Vara
```

The evidence layer requires classed evidence, qualified signals, origin/integrity/drift/noise/reversibility/lineage fields, and no silent epistemic mutation.

This is a strong specification chain.

However, the current Vara scan stack does not itself visibly enforce every substrate field. Its `Signal` structure contains source, plane, content, URL, velocity, novelty, cluster, and related scan metadata, but does not itself expose the complete qualification schema (`origin`, `integrity`, `drift`, `noise`, `reversibility`, `lineage`) as mandatory fields.

**Classification:** `EPISTEMIC SPECIFICATION → RUNTIME COVERAGE GAP`.

This should be tested at the integration boundary rather than inferred from the existence of the YAML constraints.

## 6. Governance Gate Divergence

The canonical Governance Gates specification says all three gates are evaluated sequentially and that a G2 soft block may be overridden by the operator.

The newer authoritative governance engine instead returns `BLOCK` for an over-budget G2 result and does not expose the documented 60-second override path in the observed implementation.

The engine does, however, explicitly preserve `ABSTAIN`, `SILENCE`, evidence references, evaluator identity/version, and structured decision hashes.

**Classification:** `PARTIAL SEMANTIC ALIGNMENT / IMPLEMENTATION DIVERGENCE`.

This is a more nuanced finding than simply "broken": the newer engine contains stronger epistemic semantics in some areas while diverging from older gate behavior in others.

## 7. Test Integrity Finding

`test_invariants.py` defines the six canonical invariants and tests their metadata. Its optional runtime tests gracefully `skip` if richer runtime symbols are absent.

That means a green test run cannot be interpreted as proof that Sentinel or Stumpy implement their specifications.

This is exactly the distinction required by the Stumpy conformance contract:

`TESTED ≠ IMPLEMENTED ≠ ENFORCED ≠ VERIFIED`.

## 8. Revised Invariant Ontology Finding

The earlier matrix characterization should be refined.

The repository now contains a reasonably explicit three-level model:

```text
Constitution Article III
        ↓
Lattice_Invariants_v1.md
  six Tier-1 structural invariants
        ↓
invariants_map.yaml
  Tier-2 procedural/protocol/runtime rules
```

`invariants.md` contains the ten broad constitutional constraint statements, while `Lattice_Invariants_v1.md` explicitly states that `invariants_map.yaml` is Tier 2 and that the six invariants are Tier 1.

The remaining problem is therefore **not simply cardinality contradiction**. It is whether the relationship between the Constitution's seven Article III statements, the ten broad constraint statements, and the six Tier-1 runtime invariants is formally defined as derivation, refinement, or parallel classification.

This is a lower-level ontology problem than previously recorded, and should be resolved without deleting useful domain distinctions.

## 9. Traceability Standard

For every module, the final matrix should eventually establish:

```text
MODULE_ID
  → authoritative registry entry
  → governing invariant(s)
  → module specification
  → interface contract/schema
  → actual runtime implementation
  → conformance tests
  → observable evidence
  → Stumpy finding
```

Any missing link receives an explicit state. No link may be inferred solely from naming similarity.

## 10. Current Overall Assessment

The repository is best characterized as:

**ARCHITECTURALLY RICH / PARTIALLY ENFORCED / CROSS-LAYER DRIFT PRESENT / VERIFICATION INCOMPLETE**.

The most consequential discovery of this pass is that the repository contains **two generations of runtime architecture**:

1. a newer constitutional governance kernel with serious contracts, lineage, hashing, structured decisions, and Vault enforcement;
2. older lightweight module primitives still referenced by canonical module specifications.

The next audit pass must determine which generation is authoritative, whether adapters bridge them, and whether the legacy surfaces are intentionally retained or are accidental implementation drift.

Until that is resolved, a claim of full repository conformance would be dishonest.
