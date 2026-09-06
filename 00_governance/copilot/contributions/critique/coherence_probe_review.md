# Coherence Probe Hardening — Critique Review (v2, corrected)

<!-- schema: governed-artifact-proposal | class: critique | mcc: MCC-0.1.0 -->
<!-- operator: Copilot | authority: JRM-01 | branch: copilot -->
<!-- subject_commit: 30bdb7d | subject_file: 05_runtime/stumpy/behavioral.py -->
<!-- v1_authored: 2026-09-05T21:34:00Z | v2_corrected: 2026-09-05T18:56:00Z -->
<!-- v2_reason: GAP-01 retracted (KeyError not possible on text parser). Real HIGH gap identified in probe_authority_hierarchy. GAP-03 retracted (order handling is intentional by design). -->

## 1. Artifact Header

| Field | Value |
|---|---|
| Artifact ID | critique.coherence_probe_review.v2 |
| Operator | Copilot |
| Authority | JRM-01 |
| Seam | critique |
| Contribution Scope | analysis, critique, hypothesis_generation |
| Subject Commit | 30bdb7d |
| Subject File | 05_runtime/stumpy/behavioral.py |
| v1 Timestamp | 2026-09-05T21:34:00Z |
| v2 Correction Timestamp | 2026-09-05T18:56:00Z EDT |
| Provenance | kushkillerjsixx66/canonical-vault@copilot |
| Status | GOVERNED_ARTIFACT_PROPOSAL v2 — awaiting JRM-01 review |

---

## 2. v1 Corrections Log

After reading the actual source of `behavioral.py`, two errors in the v1 critique were identified and are retracted here.

### RETRACTION: GAP-01 (KeyError on canonical path)

**v1 claim:** `_read_canonical_invariants(graph)` accesses a dict key and a `KeyError` is possible if the key is absent.

**Finding after source review:** `_read_canonical_invariants` is a **text parser**, not a dict accessor. It reads `authority_graph.yaml` as raw text via `path.read_text()`, then uses `lines.index()` and line-prefix scanning to extract invariant names. No dict access occurs at any point. A missing `canonical_invariants:` section causes `ValueError` from `lines.index()` — which is **already caught** by the existing `except (OSError, ValueError)` guard. `KeyError` is structurally impossible in this code path.

**Status: RETRACTED. GAP-01 does not exist.**

### RETRACTION: GAP-03 (Tuple order sensitivity)

**v1 claim:** `canonical_invariants != runtime_invariants` is order-sensitive and could produce false coherence violations.

**Finding after source review:** The code explicitly handles ordering. After the equality check, a second branch checks `set(canonical_invariants) == set(runtime_invariants)` and returns a distinct diagnostic: `"invariant ordering differs"`. Order sensitivity is **intentional by design** — the probe distinguishes between "wrong invariants" and "right invariants in wrong order" as separate failure modes. This is not a gap; it is a deliberate contract.

**Status: RETRACTED. GAP-03 is correct behavior.**

---

## 3. Subject Summary (unchanged from v1)

Commit `30bdb7d` modifies `probe_coherence()` in `05_runtime/stumpy/behavioral.py`, wrapping two previously bare invariant-read assignments in guarded `try/except` blocks returning `(False, diagnostic_string)` on failure. Net diff: +10 lines, -2 lines.

---

## 4. Revised Gap Analysis

### GAP-01 (REVISED) — probe_authority_hierarchy Has Zero Exception Handling
**Severity: HIGH**

While `probe_coherence()` was hardened in `30bdb7d`, `probe_authority_hierarchy()` — which runs in the same Stumpy behavioral audit pass — has **no exception handling at all**. The function calls `path.read_text()` (raises `OSError` if the file is missing or unreadable), accesses dict keys on the parsed YAML (raises `KeyError` if the authority graph schema changes), and calls `int(value)` on rank values (raises `ValueError` if a rank is non-integer). All three exceptions propagate uncaught to the caller.

This is the same class of vulnerability that `30bdb7d` fixed in `probe_coherence()` — but the fix was not applied consistently across the full probe surface.

**Proposed fix:** Apply the same guard pattern:
```python
try:
    authority_data = _read_authority_graph(graph_path)
except (OSError, ValueError, KeyError) as exc:
    return False, f"authority hierarchy declaration is malformed or unavailable: {exc}"
```
And wrap the rank integer conversion:
```python
try:
    rank = int(node.get("rank", ""))
except (ValueError, TypeError) as exc:
    return False, f"authority hierarchy rank is non-integer or missing: {exc}"
```

### GAP-02 — Empty-Set False Positive (unchanged from v1)
**Severity: MEDIUM**

If both `_read_invariants_from_source` and `_read_canonical_invariants` return empty tuples `()`, the probe returns `(True, ...)` — a silent false positive indicating coherence when no invariants are being enforced at all.

**Proposed fix:**
```python
if not runtime_invariants and not canonical_invariants:
    return False, "coherence probe detected zero invariants in both sources; skipping as unsafe"
```

### GAP-03 — No Governance Audit Emission on Probe Failure (renumbered from GAP-04)
**Severity: MEDIUM**

When any probe returns `(False, ...)`, no entry is written to `governance_events.log`. A coherence or hierarchy failure is a governance-significant event under Stumpy, but the current implementation silently returns to the caller with no vault ledger trace.

**Proposed fix:** Emit a structured governance event on any `False` return, or enforce a caller contract that mandates emission — with the former preferred for auditability.

### GAP-04 — Diagnostic String Exposes Internal Path (renumbered from GAP-05)
**Severity: LOW**

The f-string `f"runtime invariant declaration is malformed or unavailable: {exc}"` embeds the raw `OSError` exception, which includes the full filesystem path. In CI or external log contexts this leaks internal path structure.

**Proposed fix:** Sanitize the exception message before surfacing it externally.

---

## 5. Hypotheses for Further Hardening (updated)

### H-01: Consistent Hardening Across All Probe Functions
The fix pattern from `30bdb7d` should be applied as a **systematic pass** across all probe functions in `behavioral.py` — not just `probe_coherence()`. A checklist of all probe entry points and their current exception coverage would ensure no surface is left unguarded.

### H-02: Invariant Schema Versioning
If `authority_graph.yaml` gains a schema version field, `_read_canonical_invariants` should validate the version before extracting invariants. A version mismatch should return a specific error code rather than a generic diagnostic.

### H-03: Probe Self-Test on Startup
Stumpy should run all probes once during initialization against known-good fixtures and assert `(True, ...)`. This catches regressions in probe infrastructure before real vault state is evaluated.

### H-04: Split Failure Modes into Distinct Return Codes
The current `(False, string)` contract conflates probe infrastructure failures with genuine coherence violations. A richer return type (enum or dataclass) would allow callers to route infrastructure failures to ops and coherence violations to governance separately.

---

## 6. Revised Verdict

Commit `30bdb7d` is a **net positive** governance hardening that correctly targets the most dangerous failure mode in `probe_coherence()`. The v1 critique overstated the risk by misidentifying the implementation of `_read_canonical_invariants` as a dict accessor.

The real residual risk is **inconsistent hardening coverage**: `probe_authority_hierarchy()` has the same pre-`30bdb7d` vulnerability that `probe_coherence()` just had. This should be addressed as the immediate follow-up.

| Gap | Severity | Recommendation |
|---|---|---|
| GAP-01 KeyError on canonical path | ~~HIGH~~ | **RETRACTED** — KeyError impossible on text parser |
| GAP-01 (revised) probe_authority_hierarchy unguarded | **HIGH** | Apply same guard pattern as 30bdb7d — immediate |
| GAP-02 Empty-set false positive | MEDIUM | Add post-read zero-invariant guard |
| GAP-03 No audit emission on failure | MEDIUM | Emit governance event or enforce caller contract |
| GAP-03 Tuple order sensitivity | ~~MEDIUM~~ | **RETRACTED** — intentional design, handled explicitly |
| GAP-04 Path leakage in diagnostic | LOW | Sanitize OSError message |

---

## 7. Governance Footer

```
Operator: Copilot
Authority: JRM-01
Branch: copilot
Seam: critique
Version: v2 (corrected)
Corrections: GAP-01 retracted (KeyError impossible), GAP-03 retracted (intentional design)
New finding: probe_authority_hierarchy unguarded (HIGH)
Prohibited zones respected: no direct_canonical_mutation, no cross_branch_modification
Canonical merge authority: false — awaiting JRM-01 review before any main-branch promotion
Veil boundary: active
Sig: Copilot @canonical-vault/copilot 2026-09-05T18:56:00Z EDT
```
