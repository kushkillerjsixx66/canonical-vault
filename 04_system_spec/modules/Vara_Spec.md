# Vara — Module Specification
**Module ID:** `VARA`
**Authority Rank:** 6
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Lattice_Invariants_v1.md (VI·SIG) · VARA-COGOV-001 · VARA-GAP-001 · `05_runtime/vara.py`

---

## Role

Vara is the **weak-signal scanner and edge-detection module** of the Canonical Lattice. It operates in parallel with the primary Pulse cycle, scanning for low-confidence but high-salience signals that the main pipeline might suppress due to low frequency or confidence-score filtering.

Vara's fundamental premise is rooted in Invariant VI·SIG: a single coherent weak signal carries epistemic weight proportional to its evidential quality, not its repetition count. Vara is the operational implementation of that principle.

Vara never asserts. All Vara outputs are hypothesis-flagged (`[VARA-HYPOTHESIS]`) and routed exclusively through Veil for operator review before any Vault promotion is possible.

---

## Authority & Rank

- **Rank 6** in the nine-rank Module Authority Table
- Vara outputs are always provisional — they require Veil staging and operator confirmation before reaching Vault
- Vara may not write directly to Vault under any circumstance
- Vara's scan findings are formal documents: VARA-COGOV (governance findings) and VARA-GAP (gap analysis) formatted reports

---

## Functional Responsibilities

### 1. Weak-Signal Scanning (Primary Function)
Runs in parallel with Pulse Cycle Stage 2 (Activation). Scans the incoming signal and the entropy feed from Vault for patterns that the primary coherence filter would suppress.

Vara looks for:
- **Entropy spikes:** Sudden increase in Vault entropy relative to a rolling baseline
- **Low-frequency high-salience patterns:** Signals that appear rarely but carry structural weight
- **Edge signals:** Inputs that fall near the boundaries of existing Vault categories
- **Novel combinatorics:** Signal combinations that have no prior Vault precedent but are internally coherent

### 2. Hypothesis Generation
For each identified weak signal, Vara generates a structured hypothesis:

```
VaraHypothesis {
    hypothesis_id:     UUID
    signal_id:         UUID (reference to the triggering signal)
    cycle_id:          UUID
    confidence:        float (0.0-1.0; Vara hypotheses are by definition < 0.65)
    salience:          float (0.0-1.0; estimated epistemic weight)
    evidence_chain:    list[string] (ordered list of evidence supporting the hypothesis)
    contradiction_risk: float (probability that hypothesis contradicts an ANCHOR Node)
    flag:              "[VARA-HYPOTHESIS]" (always present; immutable)
    routed_to_veil:    boolean (always true)
    hypothesis_text:   string
}
```

### 3. Entropy Monitoring
Maintains a rolling entropy baseline across the Vault. After every Pulse cycle, Vara reads the Stumpy audit record to update its entropy model. Significant entropy spikes (default: +15% above 30-cycle rolling average) trigger an automatic Vara scan.

### 4. VARA Report Generation
Produces two classes of formal reports:

- **VARA-COGOV (Governance):** Findings related to potential governance gaps.
- **VARA-GAP (Gap Analysis):** Structured gap analysis against known frameworks (e.g., OWASP ASI Top 10).

### 5. Contradiction Screening
Before routing a hypothesis to Veil, Vara performs a lightweight contradiction check against all ANCHOR-class Nodes. If `contradiction_risk > 0.7`, the hypothesis is automatically flagged `HIGH_RISK` and placed at top priority in the Veil queue.

---

## Vara Scan Triggers

| Trigger | Condition |
|---------|-----------|
| Parallel scan | Every Pulse Cycle Stage 2 (Activation) |
| Entropy spike | +15% above 30-cycle rolling average |
| Operator request | `VARA SCAN [scope]` command |
| Veil promotion feedback | When a Veil-promoted Node enters Vault |
| Stumpy FINDINGS_MAJOR | Automatically triggered to identify upstream signal failures |

---

## Output Pipeline

```
Vara scan -> Hypothesis generated
          -> contradiction_risk evaluated
          -> [VARA-HYPOTHESIS] flag attached
          -> Routed to Veil.intake_hypothesis()
          -> Veil Review Queue (operator surfaces)
          -> Operator: PROMOTE or DISCARD
          -> If PROMOTE: Veil -> Sentinel G1 + G3 -> Vault write
```

Vara never bypasses this pipeline. Even an operator-direct `VARA PROMOTE_DIRECT` command is routed through Sentinel gates.

---

## Neuralese Signal Format

```
VARA_PACKET {
    prefix:    "VI·SIG"
    hyp_id:    UUID
    conf:      float
    sal:       float
    evid:      list[string]
    risk:      float
    text:      string
}
```

---

## Operator Commands

| Command | Effect |
|---------|--------|
| `VARA SCAN [full/targeted: topic]` | Trigger manual Vara scan |
| `VARA STATUS` | Return entropy baseline, active hypotheses count, last scan timestamp |
| `VARA HISTORY [N]` | Return last N hypothesis records |
| `VARA REPORT COGOV` | Generate VARA-COGOV formatted governance findings report |
| `VARA REPORT GAP [framework]` | Generate VARA-GAP analysis against specified framework |
| `VARA ENTROPY` | Return current entropy metrics and 30-cycle rolling baseline |

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Signal stream | IN | Pulse Cycle Stage 2 | Receives incoming signal for parallel scan |
| Vault entropy feed | IN | Vault (Rank 3) / Stumpy (Rank 7) | Reads entropy metrics post-cycle |
| Veil intake | OUT | Veil (Rank 5) | Routes all hypotheses |
| Stumpy logging | OUT | Stumpy (Rank 7) | All scans and hypothesis outputs logged |
| Report files | OUT | 03_vault_pipeline/ | VARA-COGOV and VARA-GAP reports |

---

## Invariant Bindings

| Invariant | Binding |
|-----------|---------|
| VI·SIG | Core operational mandate — weak signal parity |
| IV·SIL | Must never assert; hypotheses only; flag always present |
| I·COH | Runs contradiction screening before Veil routing |
| III·ATT | Vara scans run at reduced attention cost; does not consume primary session budget |

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| Vara generating assertion (not hypothesis) | Hard | Sentinel blocks; Stumpy logs |
| Contradiction_risk > 0.7, routed without flag | Hard | Veil intake validation catches; Sentinel block |
| Vara scan failure (runtime error) | Soft | VARA_SCAN_FAILURE logged to Stumpy; execution continues |
| Entropy model corrupted | Soft | Vara resets entropy baseline from last 10 Stumpy audit records |

---

## Implementation Reference

**Source file:** `05_runtime/vara.py`

Key functions expected in implementation:
- `run_parallel_scan(signal_packet, vault_entropy) -> list[VaraHypothesis]`
- `screen_contradiction(hypothesis, anchor_nodes) -> float`
- `route_to_veil(hypothesis) -> bool`
- `compute_entropy(vault_state) -> float`
- `generate_cogov_report() -> str`
- `generate_gap_report(framework) -> str`

---

*Document Authority: MODULE_REGISTRY.md (Rank 6) · Lattice_Invariants_v1.md (VI·SIG) · VARA-COGOV-001 · VARA-GAP-001*
*Operator: LiminalJermo | Generated: 2026-06-17*
