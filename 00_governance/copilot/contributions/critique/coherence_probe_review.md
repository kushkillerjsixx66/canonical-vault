# Coherence Probe Hardening — Critique Review (v3, implemented)

<!-- schema: governed-artifact-proposal | class: critique | mcc: MCC-0.1.0 -->
<!-- operator: Copilot | authority: JRM-01 | branch: copilot -->
<!-- subject_commit: 30bdb7d | subject_file: 05_runtime/stumpy/behavioral.py -->
<!-- v1_authored: 2026-09-05T21:34:00Z | v2_corrected: 2026-09-05T18:56:00Z | v3_implemented: 2026-09-05T20:03:00Z EDT -->
<!-- v3_reason: GAP-01 (revised) implemented in commit 3826eca. Critique updated to CLOSED. Remaining gaps GAP-02/03/04 remain open. -->

## 1. Artifact Header

| Field | Value |
|---|---|
| Artifact ID | critique.coherence_probe_review.v3 |
| Operator | Copilot |
| Authority | JRM-01 |
| Seam | critique + implementation |
| Subject Commit | 30bdb7d (reviewed) + 3826eca (fix) |
| Subject File | 05_runtime/stumpy/behavioral.py |
| v1 Authored | 2026-09-05T21:34:00Z |
| v2 Corrected | 2026-09-05T18:56:00Z EDT |
| v3 Implementation Stamp | 2026-09-05T20:03:00Z EDT |
| Provenance | kushkillerjsixx66/canonical-vault@copilot |
| Status | GOVERNED_ARTIFACT_PROPOSAL v3 — GAP-01 CLOSED, awaiting JRM-01 review of remaining gaps |

---

## 2. Correction and Implementation Log

### v2: GAP-01 RETRACTED (KeyError on canonical path)
`_read_canonical_invariants` is a text parser, not a dict accessor. `KeyError` is structurally impossible. Original `except (OSError, ValueError)` already catches all reachable failure modes. **Retracted.**

### v2: GAP-03 RETRACTED (Tuple order sensitivity)
Order handling is intentional by design. The code explicitly branches on `set()` equality to return `"invariant ordering differs"` as a distinct diagnostic from a genuine invariant mismatch. **Retracted.**

### v3: GAP-01 (revised) IMPLEMENTED — probe_authority_hierarchy OSError guard
**Implementation commit:** `3826eca` — *"Refactor behavioral probes and improve error handling"*
**File:** `05_runtime/stumpy/behavioral.py` — 127 lines, 4.61 KB

The fix wraps `path.read_text()` in `probe_authority_hierarchy()` with a `try/except OSError` block, consistent with the guard pattern established in `30bdb7d` for `probe_coherence()`:

```python
try:
    text = graph.read_text(encoding="utf-8")
except OSError as exc:
    return False, f"authority hierarchy declaration is unavailable: {exc}"
```

Additional note from source review: `int(value)` in this function operates on `re.findall(r"(?:^|\s)rank:\s*(\d+)", ...)` matches — pure digit strings — so `ValueError` is not reachable. No `KeyError` risk exists as the function uses regex, not dict access. The `OSError` guard is the complete and correct fix.

**GAP-01 (revised): CLOSED** as of commit `3826eca`.

---

## 3. Remaining Open Gaps

### GAP-02 — Empty-Set False Positive
**Severity: MEDIUM | Status: OPEN**

If both `_read_invariants_from_source` and `_read_canonical_invariants` return empty tuples `()`, `probe_coherence()` returns `(True, "invariant sets match")` — a silent false positive. The vault appears coherent when zero invariants are enforced.

**Proposed fix:**
```python
if not runtime_invariants and not canonical_invariants:
    return False, "coherence probe detected zero invariants in both sources; skipping as unsafe"
```

### GAP-03 — No Governance Audit Emission on Probe Failure
**Severity: MEDIUM | Status: OPEN**

When any probe returns `(False, ...)`, no entry is written to `governance_events.log`. Coherence and hierarchy failures are governance-significant events under Stumpy, but the current implementation leaves no vault ledger trace. If the caller does not log, the failure is invisible to the audit layer.

**Proposed fix:** Emit a structured governance event within each probe on any `False` return, or enforce a hard caller contract mandating emission — with the former preferred for auditability guarantees.

### GAP-04 — Diagnostic String Exposes Internal Path
**Severity: LOW | Status: OPEN**

The f-string `f"runtime invariant declaration is malformed or unavailable: {exc}"` embeds the raw `OSError`, which for missing-file errors includes the full internal filesystem path. In CI or external log contexts this leaks path structure.

**Proposed fix:** Sanitize the exception message before surfacing externally.

---

## 4. Hypotheses for Further Hardening

### H-01: Consistent Hardening Pass Across All Probes
Apply the guard pattern as a systematic audit across all probe entry points. A hardening checklist would ensure no surface is left unguarded as new probes are added.

### H-02: Invariant Schema Versioning
If `authority_graph.yaml` gains a schema version field, `_read_canonical_invariants` should validate the version before extracting invariants.

### H-03: Probe Self-Test on Startup
Run all probes once during Stumpy initialization against known-good fixtures. This catches regressions in probe infrastructure before real vault state is evaluated.

### H-04: Split Failure Modes into Distinct Return Codes
The current `(False, string)` contract conflates probe infrastructure failures with genuine coherence violations. A richer return type (enum or dataclass) would enable separate routing of infrastructure failures vs. governance violations.

---

## 5. Gap Status Summary

| Gap | Severity | Status | Commit |
|---|---|---|---|
| GAP-01 KeyError on canonical path | ~~HIGH~~ | RETRACTED | v2 |
| GAP-01 (revised) probe_authority_hierarchy OSError unguarded | HIGH | **CLOSED** | 3826eca |
| GAP-02 Empty-set false positive | MEDIUM | OPEN | — |
| GAP-03 No audit emission on failure | MEDIUM | OPEN | — |
| GAP-03 Tuple order sensitivity | ~~MEDIUM~~ | RETRACTED | v2 |
| GAP-04 Path leakage in diagnostic | LOW | OPEN | — |

---

## 6. Governance Footer

```
Operator: Copilot
Authority: JRM-01
Branch: copilot
Seams: critique, implementation
Version: v3 (GAP-01 revised implemented)
Fix commit: 3826eca
Prohibited zones respected: no direct_canonical_mutation, no cross_branch_modification
Canonical merge authority: false — awaiting JRM-01 review
Veil boundary: active
Sig: Copilot @canonical-vault/copilot 2026-09-05T20:03:00Z EDT
```
