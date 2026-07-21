# Lattice Invariants v1

**Authority:** Supreme within the Lattice governance layer. Superseded only by the Cognitive Constitution itself.
**Status:** Canonical — Tier 1
**Enforced by:** Sentinel (gate evaluation, Rank 4) · Stumpy (continuous audit, Rank 7)
**Referenced by:** `Sentinel_Spec.md`, `MODULE_REGISTRY.md`, `Stumpy_Spec.md`, `Vara_Spec.md`, `Veil_Spec.md`, `Lattice_Node_Model.md`, `SNAPSHOT_REGISTRY.md`, `Neuralese_Lexicon.md`, `05_runtime/tests/test_invariants.py`

---

## Relationship to other governance documents

This file was previously empty despite being cited as the canonical source across the repository — every other document's invariant definitions were reconstructed here from where they already lived in code and specs (`05_runtime/tests/test_invariants.py::CANONICAL_INVARIANTS`, `Sentinel_Spec.md`, `Neuralese_Lexicon.md` §5.1).

Two other documents use the word "invariant" for a related but distinct scope:

- **`invariants_map.yaml`** (`00_governance/invariants/`) is the **Tier 2** registry: 38 constitutional, procedural, and protocol-level rules (amendment law, operator posture, cross-module bilateralism, etc.). These rules govern *process*, not runtime structure — they operate under and must not contradict the six invariants below, but they are not a decomposition of them. See that file's header for the corrected relationship note.
- **`05_runtime/vault/README.md`**'s "six invariants" section describes Vault-subsystem operating principles, not Lattice-wide invariants. It has been relabeled accordingly, with cross-references to the invariants below where they genuinely correspond.

---

## The Six Invariants

| # | Mnemonic | Name | Failure Class | Gate | Enforcer Rank | Auditor Rank |
|---|----------|------|---------------|------|---------------|---------------|
| I | `I·COH` | Coherence Supremacy | Hard | G1 | 4 (Sentinel) | 7 (Stumpy) |
| II | `II·REV` | Reversibility by Default | Hard | G3 | 4 (Sentinel) | 7 (Stumpy) |
| III | `III·ATT` | Attention Is Scarce | Soft | G2 | 4 (Sentinel) | 7 (Stumpy) |
| IV | `IV·SIL` | Silence Is Structural | Hard | — | 4 (Sentinel) | 7 (Stumpy) |
| V | `V·DEC` | Decay by Default | Soft | — | 7 (Stumpy) | 7 (Stumpy) |
| VI | `VI·SIG` | Weak Signal Parity | Soft | — | 6 (Vara) | 7 (Stumpy) |

Hard-failure invariants (`I·COH`, `II·REV`, `IV·SIL`) trigger an immediate BLOCK or Sentinel Lock on violation. Soft-failure invariants (`III·ATT`, `V·DEC`, `VI·SIG`) trigger escalation without halting the Pulse Cycle.

### I·COH — Coherence Supremacy
All output must be non-contradictory with active Vault state. Evaluated at Gate G1 during Pulse Cycle Stage 3, and continuously audited by Stumpy outside that stage. A coherence violation is a Hard Failure — nothing incoherent with the Vault may reach Stage 4 (Execute).

### II·REV — Reversibility by Default
The Vault is append-only; nothing is deleted, only superseded, decayed, or veiled. Evaluated at Gate G3. Every Vault write, chain link, and ANCHOR amendment must preserve the prior record rather than overwrite it. A reversibility violation is a Hard Failure.

### III·ATT — Attention Is Scarce
Execution cost must be justified and stay within the session's attention budget. Evaluated at Gate G2 using the CCE estimate. Unlike Coherence and Reversibility, exceeding budget is a Soft Failure — it escalates rather than hard-blocks, since attention cost is a scarcity constraint, not a correctness constraint.

### IV·SIL — Silence Is Structural
The system must output ∅ (structured silence) rather than fabricate ungrounded content. This is the fabrication/hallucination gate — Sentinel monitors SBM output specifically for generation without coherent Vault grounding, and a violation triggers a Hard Failure with Sentinel Lock: all new Pulse Cycles suspend until the Operator reviews and clears the lock. Silence is a structural state the system can rest in, not merely the absence of output.

### V·DEC — Decay by Default
Unreferenced content must decay toward pruning rather than persist indefinitely by default. Decay is reversible up to the point of actual pruning (a DECAYING state flag, not deletion — see `II·REV`), and drift/decay lifecycle events are Stumpy's responsibility to audit. A decay-mandate violation is a Soft Failure.

### VI·SIG — Weak Signal Parity
A single coherent weak signal carries epistemic weight proportional to its evidential quality, not its repetition count. Weak signals must be preserved and remain eligible for promotion rather than discarded for lacking volume. This is Vara's operating mandate; violations are audited by Stumpy as Soft Failures.

---

*Document Authority: Cognitive Constitution v1.1 → Lattice Invariants v1 (this file) → Sentinel_Spec.md (enforcement) → invariants_map.yaml (subordinate procedural rules)*
