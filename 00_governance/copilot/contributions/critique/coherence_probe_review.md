# Coherence Probe Hardening — Critique Review

<!-- schema: governed-artifact-proposal | class: critique | mcc: MCC-0.1.0 -->
<!-- operator: Copilot | authority: JRM-01 | branch: copilot -->
<!-- subject_commit: 30bdb7d | subject_file: 05_runtime/stumpy/behavioral.py -->
<!-- authored: 2026-09-05T21:34:00Z -->

## 1. Artifact Header

| Field | Value |
|---|---|
| Artifact ID | critique.coherence_probe_review.v1 |
| Operator | Copilot |
| Authority | JRM-01 |
| Seam | critique |
| Contribution Scope | analysis, critique, hypothesis_generation |
| Subject Commit | 30bdb7d |
| Subject File | 05_runtime/stumpy/behavioral.py |
| Review Timestamp | 2026-09-05T21:34:00Z |
| Provenance | kushkillerjsixx66/canonical-vault@copilot |
| Status | GOVERNED_ARTIFACT_PROPOSAL — awaiting JRM-01 review |

---

## 2. Subject Summary

Commit `30bdb7d` — *"Harden coherence probe against malformed invariant declarations"* — modifies `probe_coherence()` in `05_runtime/stumpy/behavioral.py`. The change wraps two previously bare assignments in guarded `try/except` blocks:

```
# Before (lines 61-62)
runtime_invariants = _read_invariants_from_source(matrix_path)
canonical_invariants = _read_canonical_invariants(graph)

# After (lines 62-70)
try:
    runtime_invariants = _read_invariants_from_source(matrix_path)
except (OSError, SyntaxError, ValueError) as exc:
    return False, f"runtime invariant declaration is malformed or unavailable: {exc}"

try:
    canonical_invariants = _read_canonical_invariants(graph)
except (OSError, ValueError) as exc:
    return False, f"canonical invariant declaration is malformed or unavailable: {exc}"
```

Net diff: +10 lines, -2 lines. One file changed.

---

## 3. What This Hardening Covers

### 3.1 Runtime Invariant Path (matrix_path)
- **OSError**: file not found, permission denied, or I/O failure reading `audit_matrix.py`.
- **SyntaxError**: Python source file `audit_matrix.py` is malformed and cannot be parsed by the AST reader.
- **ValueError**: invariant extraction logic encounters an unexpected data shape within the parsed source.

### 3.2 Canonical Invariant Path (graph / authority_graph.yaml)
- **OSError**: file not found or I/O failure reading `authority_graph.yaml`.
- **ValueError**: YAML content parses successfully but produces an unexpected structure (e.g., missing `canonical_invariants` key returns `None`, which downstream code converts to a ValueError-equivalent).
- **SyntaxError intentionally omitted**: YAML deserialization does not raise `SyntaxError`; the YAML parser raises `yaml.YAMLError` or `ValueError`. This asymmetry is architecturally correct.

### 3.3 Failure Return Contract
Both guards return `(False, diagnostic_string)` — consistent with the existing probe return contract of `tuple[bool, str]`. Downstream callers can distinguish probe failure from coherence failure by inspecting the boolean.

---

## 4. Gap Analysis

### GAP-01 — KeyError Not Caught on Canonical Path
**Severity: HIGH**

`_read_canonical_invariants(graph)` reads `authority_graph.yaml` and almost certainly accesses a specific key (e.g., `data['canonical_invariants']`). If the YAML file is structurally valid but the key is absent or renamed, a `KeyError` is raised — **not caught** by the current guard. This means a schema migration of `authority_graph.yaml` (e.g., renaming the invariants key) causes an unguarded exception that propagates to the caller rather than returning a clean `(False, diagnostic_string)`.

**Proposed fix:** Add `KeyError` to the canonical except tuple:
```python
except (OSError, ValueError, KeyError) as exc:
    return False, f"canonical invariant declaration is malformed or unavailable: {exc}"
```

### GAP-02 — Empty-Set False Positive
**Severity: MEDIUM**

If both `_read_invariants_from_source` and `_read_canonical_invariants` return empty tuples `()` (e.g., both source files exist but contain zero invariant declarations), the equality check `canonical_invariants != runtime_invariants` passes — the probe returns `(True, ...)`. This is a silent false positive: the vault appears coherent when in fact no invariants are being enforced at all.

**Proposed fix:** Add an empty-set guard after both reads:
```python
if not runtime_invariants and not canonical_invariants:
    return False, "coherence probe detected zero invariants in both sources; skipping as unsafe"
```

### GAP-03 — Tuple Order Sensitivity
**Severity: MEDIUM**

The downstream comparison `canonical_invariants != runtime_invariants` uses tuple equality, which is order-sensitive. If `_read_invariants_from_source` and `_read_canonical_invariants` return the same invariants in different orders (e.g., due to YAML key ordering vs. AST traversal order), the probe reports a coherence violation that does not exist.

**Proposed fix:** Normalize both sides to `frozenset` before comparison, or sort both tuples deterministically:
```python
if set(canonical_invariants) != set(runtime_invariants):
```
This change must be evaluated against the semantics of `_read_canonical_invariants` — if duplicate invariant names are meaningful, `frozenset` would suppress them.

### GAP-04 — No Governance Audit Emission on Probe Failure
**Severity: MEDIUM**

When the probe returns `(False, ...)`, no entry is written to `governance_events.log`. A coherence failure is a governance-significant event under the Stumpy audit layer, but the current implementation silently returns to the caller. If the caller does not log, the failure leaves no trace in the vault ledger.

**Proposed fix:** Emit a structured governance event from within `probe_coherence()` on any `False` return:
```python
# pseudocode — exact implementation depends on Stumpy logging API
_emit_governance_event(
    event_type="COHERENCE_PROBE_FAILURE",
    subject="STUMPY_RUNTIME",
    operator="SYSTEM",
    detail=diagnostic_message
)
```
Alternatively, enforce a contract that all callers of `probe_coherence()` must emit on `False` — but this is weaker and more fragile.

### GAP-05 — Diagnostic String Exposes Internal Path
**Severity: LOW**

The f-string `f"runtime invariant declaration is malformed or unavailable: {exc}"` embeds the exception object, which for `OSError` includes the full filesystem path (e.g., `/home/runner/.../audit_matrix.py`). In an environment where probe results are surfaced externally (CI output, GitHub Actions logs), this leaks internal path structure.

**Proposed fix:** Sanitize the exception message or log path details at a lower verbosity level:
```python
return False, f"runtime invariant declaration is malformed or unavailable (see audit log for detail)"
```

---

## 5. Hypotheses for Further Hardening

### H-01: Invariant Schema Versioning
If `authority_graph.yaml` gains a schema version field, `_read_canonical_invariants` should validate the version before extracting invariants. A version mismatch should return a specific error code rather than falling through to a generic `ValueError`.

### H-02: Deterministic Read Ordering
Both reader functions should document and enforce a canonical ordering of their output tuples. This eliminates GAP-03 at the source rather than at the comparison site, and makes the probe more auditable.

### H-03: Probe Self-Test on Startup
Stumpy should run `probe_coherence()` once during initialization with a known-good fixture and assert the result is `(True, ...)`. This catches regressions in the probe itself before it is used to validate real vault state.

### H-04: Split Failure Modes into Distinct Return Codes
The current contract returns `(False, string)` for both "source unreadable" and "sources disagree." A richer return type (e.g., an enum or dataclass) would allow callers to distinguish probe infrastructure failures from genuine coherence violations — enabling different recovery paths.

---

## 6. Verdict

Commit `30bdb7d` is a **net positive** governance hardening. It eliminates the most dangerous failure mode (unguarded exceptions crashing the probe) and establishes a clean diagnostic return contract. The four gaps above represent residual risk, with GAP-01 (KeyError) being the highest-priority follow-up. GAP-02 (empty-set false positive) and GAP-04 (no audit emission) are governance-significant and should be addressed before the runtime layer is considered audit-complete under Stumpy.

| Gap | Severity | Recommendation |
|---|---|---|
| GAP-01 KeyError on canonical path | HIGH | Add KeyError to except tuple — immediate |
| GAP-02 Empty-set false positive | MEDIUM | Add post-read zero-invariant guard |
| GAP-03 Tuple order sensitivity | MEDIUM | Normalize to set before comparison |
| GAP-04 No audit emission on failure | MEDIUM | Emit governance event or enforce caller contract |
| GAP-05 Path leakage in diagnostic | LOW | Sanitize OSError message |

---

## 7. Governance Footer

```
Operator: Copilot
Authority: JRM-01
Branch: copilot
Seam: critique
Prohibited zones respected: no direct_canonical_mutation, no cross_branch_modification
Canonical merge authority: false — this artifact requires JRM-01 review before any main-branch promotion
Veil boundary: active
Sig: Copilot @canonical-vault/copilot 2026-09-05T21:34:00Z
```
