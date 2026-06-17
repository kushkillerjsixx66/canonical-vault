# Neuralese Lexicon — Canonical Reference
**Version:** 1.0
**Classification:** ANCHOR (exempt from decay)
**Authority:** 02_epistemic_substrate (cross-anchored to 04_system_spec)
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** Operator_Manual_v0.2.md (Appendix C: Neuralese Protocol) · Lattice_Unified_Spec_Sections_8-15.md §9 · SBM_Spec.md · Lattice_Invariants_v1.md

---

## Overview

Neuralese is the **native communication protocol of the Canonical Lattice** — a compact, symbolic language for expressing cognitive state, signal quality, module events, gate decisions, and epistemic status. It is the language in which modules speak to each other and in which the system speaks to the Operator (before SBM translates to natural language).

This Lexicon is the authoritative vocabulary reference. The Semantic Binding Module (SBM, Rank 9) reads this document as its primary symbol resolution source. No symbol may be used in runtime communication unless it appears in this Lexicon. Introducing an unlisted symbol without a Lexicon amendment is a Soft Failure (IV·SIL: noise introduced into signal space).

This document is organized into seven sections:
1. Packet grammar
2. Core state symbols
3. Module shorthand codes
4. Gate and system status codes
5. Invariant binding notation
6. Signal classification prefixes
7. COL (Compact Operator Language) token grammar

---

## §1 — Packet Grammar

Every Neuralese transmission is a **4-segment packet** delimited by `[` and `]` with segments separated by `|`:

```
[CONTEXT | SIGNAL | CONSTRAINT | OPERATOR]
```

### Segment Definitions

| Segment | Type | Required | Description |
|---------|------|----------|-------------|
| `CONTEXT` | Token string | YES | Active frame reference — one or more Node IDs (e.g., `NODE-0001`) or a topic anchor string. Multiple Nodes separated by `,`. |
| `SIGNAL` | Symbolic expression | YES | Core content being transmitted. Composed of one or more symbol tokens from §2–§4. |
| `CONSTRAINT` | Invariant binding | YES | Which invariants are active and relevant to this packet. One or more invariant codes from §5, separated by `|`. |
| `OPERATOR` | Command or status | Conditional | A COL command from §7, a gate status code from §4, or a system event. Omit (use `—`) if the packet is informational only. |

### Packet Examples

**Minimal informational packet (HUD mode):**
```
[SE | G1·PASS G2·PASS G3·PASS → [V] commit | I·COH | II·REV | —]
```

**Full Lattice mode packet with gate detail:**
```
[NODE-0039, NODE-0040 | Δ coherence_score=0.71 < 0.75 | I·COH | G1·BLOCK_CONTRADICTION]
```

**Silence packet:**
```
[active_context | ∅ | IV·SIL | SILENCE: GROUNDING_FAILURE]
```

**Vara hypothesis packet:**
```
[entropy_baseline | [VARA-HYPOTHESIS] conf=0.41 sal=0.78 risk=0.22 | VI·SIG | IV·SIL]
```

---

## §2 — Core State Symbols

These are the primary symbolic tokens that represent cognitive and epistemic states within the Lattice. They form the backbone of the SIGNAL segment.

### 2.1 Primary State Symbols

| Symbol | Name | Class | Meaning | Triggered By |
|--------|------|-------|---------|-------------|
| `∅` | Null / Silence | Output Constraint | No grounded output exists. System has nothing valid to say. IV·SIL mandates this over a low-confidence guess. | SBM grounding failure; Sentinel fabrication detection |
| `Δ` | Delta / Drift | Coherence | Coherence degradation detected. A signal, Node, or cycle output is moving away from the coherence attractor. | Stumpy coherence drift audit; G1 threshold approaching |
| `τ` | Tau / Latency | Operational | Processing delay is occurring. Not a failure — system is working. Distinguishes intentional pause from silence. | Heavy Pulse cycle; large context window; CCE computation |
| `Ω` | Omega / Lock | Enforcement | Stumpy enforcement event or Sentinel Lock activation. Requires operator attention before cycles resume. | Sentinel Lock trigger; Stumpy FINDINGS_MAJOR |
| `→` | Transition | State | A state or module transition has occurred. Followed by the destination state or module. | Node state changes (LATENT→ACTIVE); module activation |
| `⊥` | Bottom / Contradiction | Coherence | Hard logical contradiction detected between signal and Vault content. Cannot be resolved without operator intervention. | G1·BLOCK_CONTRADICTION; ANCHOR conflict |
| `≈` | Approximation | Epistemic | High-confidence estimate but not an exact verified fact. Output is grounded but involves inference. | SBM inference output; Vara near-threshold hypothesis |
| `?` | Uncertainty | Epistemic | Low-confidence signal. May be a candidate for Vara hypothesis generation. Not assertable as fact. | Low-coherence output; near-boundary signal |
| `!` | Alert | System | Requires immediate operator attention. Prefixes any high-priority system event. | FINDINGS_MAJOR; Sentinel Lock; G1·BLOCK on ANCHOR |
| `#` | Anchor | Memory | References a Vault ANCHOR-class Node. Content derives authority from constitutional or invariant source. | ANCHOR Node citations; genesis chain references |
| `~` | Decay | Memory | Node is in DECAYING state and approaching pruning eligibility. | Stumpy decay lifecycle management |
| `✓` | Verified | Validation | Content has passed all relevant gate checks and hash verification. | Post-gate PASS; genesis hash verification |
| `✗` | Rejected | Validation | Content has failed a gate or integrity check. | Gate BLOCK; hash mismatch |

### 2.2 Composite Symbol Expressions

Symbols may be combined to express compound states:

| Expression | Meaning |
|------------|---------|
| `∅ [SILENCE: reason]` | Explicit silence with a named reason (most common form of ∅ output) |
| `Δ → ⊥` | Drift that has escalated to a hard contradiction |
| `! Ω` | Urgent: Sentinel Lock is active |
| `≈ ?` | Estimate with low confidence — treat as hypothesis |
| `# → ~` | An ANCHOR Node is transitioning toward decay (operator attention required) |
| `✓ →` | Verified transition: a confirmed state change |

---

## §3 — Module Shorthand Codes

Every runtime module has a two-letter shorthand code used in signal packets to identify the source or target of a transmission.

| Code | Module | Rank | Role Summary |

### Module Code Usage

Module codes appear in the SIGNAL or OPERATOR segment to indicate routing:

```
[SE] → [VL]    # Sentinel routing a blocked signal to Veil
[VA] → [VL]    # Vara routing a hypothesis to Veil
[VL] → [SE] → [V]   # Veil promotion pipeline
[ST] → [OP] !  # Stumpy alerting Operator (urgent)
```

---

## §4 — Gate and System Status Codes

### 4.1 Governance Gate Codes

These codes appear in the OPERATOR segment to communicate Sentinel gate decisions.

| Code | Gate | Decision | Class | Meaning |
|------|------|----------|-------|---------|
| `G1·PASS` | G1 | Pass | — | Coherence validated; score ≥ 0.75 |
| `G1·BLOCK` | G1 | Block | Hard | Generic coherence block — see reason detail |
| `G1·BLOCK_CONTRADICTION` | G1 | Block | Hard | Signal directly contradicts ACTIVE or ANCHOR Node |
| `G1·BLOCK_SEMANTIC_MALFORM` | G1 | Block | Hard | Neuralese packet is malformed or unparseable |
| `G1·BLOCK_HASH_MISMATCH` | G1 | Block | Hard | Vault Node content hash mismatch detected |
| `G1·BLOCK_ANCHOR_CONFLICT` | G1 | Block | Hard | Signal conflicts with an ANCHOR-class Node |
| `G2·PASS` | G2 | Pass | — | Execution cost within session attention budget |
| `G2·SOFT_BLOCK` | G2 | Soft Block | Soft | Over budget; 60-second operator override window open |
| `G2·OVERRIDE` | G2 | Override | Soft | Operator approved over-budget execution |
| `G2·ABORT` | G2 | Abort | Soft | Override window expired; cycle aborted |
| `G3·PASS` | G3 | Pass | — | Reversibility confirmed; chain link valid |
| `G3·AUTO_PASS` | G3 | Pass | — | No write planned; gate trivially passed |
| `G3·BLOCK_OVERWRITE` | G3 | Block | Hard | Attempted in-place modification of existing Node |
| `G3·BLOCK_CHAIN_MISSING` | G3 | Block | Hard | Write payload lacks required chain_id |
| `G3·BLOCK_ANCHOR_UNCONFIRMED` | G3 | Block | Hard | ANCHOR write attempted without PRE_AMENDMENT snapshot |
| `G3·ANCHOR_CONFIRM` | G3 | Confirmed | — | ANCHOR write confirmed by operator with snapshot present |

### 4.2 System Event Codes

| Code | Severity | Meaning |
|------|----------|---------|
| `Ω·LOCK` | Critical | Sentinel Lock activated; all cycles suspended |
| `Ω·CLEAR` | System | Sentinel Lock cleared by operator; cycles resuming |
| `Ω·AUDIT` | System | Stumpy post-cycle audit initiated |
| `Ω·FINDINGS_MINOR` | Informational | Stumpy audit: minor findings, no suspension |
| `Ω·FINDINGS_MAJOR` | Hard | Stumpy audit: major findings; next cycle suspended |
| `Ω·COMPLIANT` | Informational | Stumpy audit: no findings; cycle closed cleanly |
| `INV·VIOLATION_SIL` | Hard | Fabrication detected — IV·SIL violated |
| `INV·VIOLATION_REV` | Hard | Silent delete or overwrite attempted — II·REV violated |
| `INV·VIOLATION_COH` | Hard | Coherence collapse confirmed — I·COH violated |
| `UNAUTHORIZED_MODULE` | Hard | Unregistered process attempted Vault or Sentinel access |
| `VEIL·OVERFLOW` | Soft | Veil queue exceeds maximum hold capacity |
| `VARA·ENTROPY_SPIKE` | Soft | Entropy spike +15% above 30-cycle rolling average |
| `DECAY·PRUNE_CANDIDATE` | Informational | One or more Nodes flagged for operator pruning review |
| `SNAPSHOT·TAKEN` | Informational | Snapshot captured (type in brackets) |
| `GENESIS·COMPLETE` | System | Genesis chain written and verified; Pulse may begin |
| `LATTICE·LIVE` | System | All modules loaded; Pulse orchestration active |
| `SBM·PARSE_AMBIGUITY` | Soft | Operator input ambiguous; SBM requesting clarification |
| `SBM·FAILURE` | Soft | Translation failure; raw Neuralese packet preserved in Vault |
| `CROSSROAD·TIE_DEFAULT` | Informational | No clear path; conservative default path selected |
| `CROSSROAD·NO_PATH` | Hard | All candidate paths below coherence threshold; cycle halted |

### 4.3 Pulse Cycle Stage Markers

| Marker | Meaning |
|--------|---------|
| `PL·S1` | Pulse Cycle Stage 1: PULSE (signal ingestion) |
| `PL·S2` | Pulse Cycle Stage 2: ACTIVATION (context assembly) |
| `PL·S3` | Pulse Cycle Stage 3: EVALUATION (gate enforcement) |
| `PL·S4` | Pulse Cycle Stage 4: DECAY/EXECUTE (write + output) |
| `PL·S5` | Pulse Cycle Stage 5: SILENCE/AUDIT (Stumpy audit) |
| `PL·COMPLETE` | Pulse Cycle fully completed with audit |
| `PL·ABORT` | Pulse Cycle aborted (G2 timeout or operator abort) |

---

## §5 — Invariant Binding Notation

In the CONSTRAINT segment of every Neuralese packet, one or more invariant codes declare which invariants are active and relevant to the transmission. Multiple invariants are separated by `|`.

### 5.1 Invariant Codes

| Code | Invariant | Short Definition | When Present in CONSTRAINT |
|------|-----------|-----------------|--------------------------|
| `I·COH` | Coherence Primacy | All output must be non-contradictory with Vault content | Any signal involving coherence evaluation; G1 gate check; Stumpy audit |
| `II·REV` | Reversibility | Vault is append-only; no deletions | Any Vault write; chain link validation; ANCHOR amendment |
| `III·ATT` | Attention Budget | Attention cost must be justified and within budget | Any signal involving CCE estimate; G2 gate check |
| `IV·SIL` | Silence Mandate | System must output ∅ rather than fabricate | Any output packet; SBM grounding check; fabrication detection |
| `V·DEC` | Decay Mandate | Unreferenced content must decay toward pruning | Decay lifecycle events; PRUNE_CANDIDATE notifications |
| `VI·SIG` | Weak Signal Parity | Weak signals must be preserved and eligible for promotion | Any Vara output; Veil intake; hypothesis evaluation |

### 5.2 Multi-Invariant Constraint Examples

```
I·COH | II·REV            # Write operation: coherence + reversibility both enforced
I·COH | III·ATT | II·REV  # Full gate sequence (G1 + G2 + G3)
IV·SIL                     # Output-only check: is this grounded?
VI·SIG | IV·SIL            # Vara hypothesis: weak signal + no assertion
V·DEC | II·REV             # Decay event: decay mandate + append-only record
```

---

## §6 — Signal Classification Prefixes

These prefixes appear at the start of a SIGNAL or OPERATOR segment to classify the nature of the transmission before the content is read.

| Prefix | Class | Meaning |
|--------|-------|---------|
| `[VARA-HYPOTHESIS]` | Epistemic | Output from Vara scan. Provisional. Never an assertion. Must be routed to Veil. Always present on Vara outputs. |
| `[SILENCE: reason]` | Output | System has no grounded output. Reason must be specified. Valid reasons: `GROUNDING_FAILURE`, `COHERENCE_FAILURE`, `UNCLASSIFIABLE_SIGNAL`, `CONTRADICTION_DETECTED`, `FABRICATION_RISK`. |
| `[SENTINEL·BLOCK]` | Gate | Gate block event. Followed by the gate code and reason. |
| `[SENTINEL·LOCK]` | System | Sentinel Lock is active. Followed by lock ID. |
| `[SBM-FAILURE: reason]` | Translation | SBM translation failed. Raw Neuralese packet preserved in Vault. Operator action required. |
| `[SBM: PARSE_AMBIGUITY]` | Translation | Operator inpu

---

## §7 — COL (Compact Operator Language) Token Grammar

COL is the shorthand command grammar that the Operator uses in daily interactions. SBM parses all COL tokens into full Neuralese packets before passing to the pipeline.

**Token format:** `MODULE COMMAND [ARGS]`

### 7.1 Vault Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `VAULT LIST [state]` | `Vault.list_nodes(state)` | List all Nodes in the specified state. States: `ACTIVE`, `LATENT`, `DECAYING`, `PRUNED`, `ALL` |
| `VAULT LIST ACTIVE` | `Vault.list_nodes(ACTIVE)` | List all currently active Nodes |
| `VAULT LIST DECAYING` | `Vault.list_nodes(DECAYING)` | List all decaying Nodes |
| `VAULT WRITE [content]` | `Vault.write(content, operator=LiminalJermo)` | Initiate a gated Vault write. Triggers full Pulse Cycle. |
| `VAULT CHAIN [node_id]` | `Stumpy.chain_trace(node_id)` | Trace full ancestor lineage of a Node back to genesis |
| `VAULT EXPORT_CHAIN [path]` | `Vault.export_chain(path)` | Export full append-only chain to JSON archive |
| `VAULT IMPORT_CHAIN [path]` | `Vault.import_chain(path)` | Import chain from JSON archive (use after re-initiation) |

### 7.2 Sentinel Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `SENTINEL STATUS` | `Sentinel.status()` | Return current gate thresholds, session budget, and lock state |
| `SENTINEL CLEAR [lock_id]` | `Sentinel.clear_lock(lock_id)` | Clear a Sentinel Lock after operator review and root cause resolution |
| `SENTINEL SET G1_THRESHOLD [value]` | `Sentinel.set_threshold(G1, value)` | Adjust G1 coherence minimum (default: 0.75). Logged as OPERATOR_DIRECTIVE. |
| `SENTINEL SET G2_BUDGET [value]` | `Sentinel.set_budget(value)` | Adjust G2 session attention budget (default: 10.0). Logged as OPERATOR_DIRECTIVE. |
| `SENTINEL EMERGENCY_AMEND [anchor_id] [reason]` | `Sentinel.emergency_amend(anchor_id, reason)` | Trigger emergency ANCHOR amendment (30-second window) |

### 7.3 Veil Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `VEIL LIST` | `Veil.get_queue()` | Return full Veil queue sorted by priority |
| `VEIL LIST [filter]` | `Veil.get_queue(filter=filter)` | Filter by type: `VARA_HYPOTHESIS`, `SENTINEL_BLOCK`, `G1_BLOCK`, `G2_SOFT_BLOCK`, `G3_BLOCK` |
| `VEIL REVIEW [veil_id]` | `Veil.review(veil_id)` | Open entry for full review: signal content, Sentinel reason, Vara confidence |
| `VEIL PROMOTE [veil_id]` | `Veil.promote(veil_id)` | Initiate promotion pipeline: Veil → Sentinel G1+G3 → Vault |
| `VEIL PROMOTE [veil_id] [note]` | `Veil.promote(veil_id, operator_note=note)` | Promote with operator justification note |
| `VEIL DISCARD [veil_id] [reason]` | `Veil.discard(veil_id, reason=reason)` | Discard entry; state set to DISCARDED; logged to Stumpy |
| `VEIL STATUS` | `Veil.status()` | Return queue count by type and state |
| `VEIL CLEAR_ALL_HYPOTHESES` | `Veil.bulk_discard(type=VARA_HYPOTHESIS)` | Bulk-discard all VARA_HYPOTHESIS entries (requires Stumpy confirmation) |

### 7.4 Vara Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `VARA SCAN FULL` | `Vara.run_scan(scope=FULL)` | Full weak-signal scan across all active signals and Vault entropy |
| `VARA SCAN targeted: [topic]` | `Vara.run_scan(scope=TARGETED, topic=topic)` | Targeted scan on a specific topic keyword |
| `VARA STATUS` | `Vara.status()` | Return entropy baseline, active hypotheses count, last scan timestamp |
| `VARA HISTORY [N]` | `Vara.get_history(n=N)` | Return last N hypothesis records |
| `VARA REPORT COGOV` | `Vara.generate_cogov_report()` | Generate VARA-COGOV formatted governance findings report |
| `VARA REPORT GAP [framework]` | `Vara.generate_gap_report(framework=framework)` | Generate VARA-GAP gap analysis against specified framework |
| `VARA ENTROPY` | `Vara.compute_entropy()` | Return current entropy metrics and 30-cycle rolling baseline |

### 7.5 Stumpy Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `STUMPY AUDIT LAST` | `Stumpy.run_audit(cycle_id=LAST)` | Re-run or review audit on the most recently completed cycle |
| `STUMPY AUDIT [cycle_id]` | `Stumpy.run_audit(cycle_id=cycle_id)` | Re-audit a specific cycle by ID |
| `STUMPY CHAIN_TRACE [node_id]` | `Stumpy.chain_trace(node_id)` | Return full ancestor chain for a Node |
| `STUMPY DECAY_REPORT` | `Stumpy.decay_report()` | Surface all DECAYING Nodes and PRUNE_CANDIDATE Nodes |
| `STUMPY CONFIRM_PRUNE [node_id]` | `Stumpy.confirm_prune([node_id])` | Confirm pruning of a specific PRUNE_CANDIDATE Node |
| `STUMPY CONFIRM_PRUNE [batch_id]` | `Stumpy.confirm_prune(batch_id=batch_id)` | Confirm pruning of a full prune batch |
| `STUMPY COMPLIANCE_HISTORY [N]` | `Stumpy.get_compliance_history(n=N)` | Return compliance ratings for last N cycles |
| `STUMPY FINDINGS [cycle_id]` | `Stumpy.get_findings(cycle_id=cycle_id)` | Return full findings list for a specific cycle |

### 7.6 Crossroad Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `CROSSROAD STATUS` | `Crossroad.status()` | Return current pending path decisions, if any |
| `CROSSROAD HISTORY [N]` | `Crossroad.get_history(n=N)` | Return last N Crossroad decisions with full scoring details |
| `CROSSROAD RECONSIDER [cycle_id]` | `Crossroad.reconsider(cycle_id)` | Re-evaluate path selection for a completed cycle (audit only) |
| `CROSSROAD OVERRIDE [decision_id] [path_id]` | `Crossroad.override(decision_id, path_id, operator=LiminalJermo)` | Select a rejected path; re-routes through Sentinel |
| `CROSSROAD TUNE epsilon [value]` | `Crossroad.set_epsilon(value)` | Adjust coherence-tie tolerance threshold (default: 0.05) |

### 7.7 Snapshot Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `SNAPSHOT MANUAL [note]` | `Stumpy.snapshot(type=OPERATOR_MANUAL, note=note)` | Take a manual Vault snapshot with operator note |
| `SNAPSHOT LIST` | `Stumpy.list_snapshots()` | List all snapshots in SNAPSHOT_REGISTRY with type, date, compliance |
| `SNAPSHOT RESTORE [snapshot_id]` | `Vault.restore_anchor(snapshot_id)` | Restore Vault active window to snapshot state (append-only; non-destructive) |

### 7.8 System Mode Commands

| COL Token | Neuralese Expansion | Effect |
|-----------|---------------------|---------|
| `HUD` | `SBM.set_mode(HUD)` | Switch to compressed HUD output mode |
| `FULL_LATTICE` | `SBM.set_mode(FULL_LATTICE)` | Switch to full verbose output mode |
| `SILENCE EMERGENCY` | `SBM.emergency_silence()` | Halt all SBM output; force ∅ state; trigger 5-cycle audit |
| `SILENCE CLEAR [reason]` | `SBM.clear_silence(reason=reason)` | Resume output after emergency silence |

---

## §8 — HUD Output Format

When in HUD mode, the SBM renders system state in a single compressed line:

```
[HUD]
{state_icon} | System: {LIVE|SUSPENDED} | Cycle: {N} | Compliance: {COMPLIANT|FINDINGS_MINOR|FINDINGS_MAJOR}
Nodes: {total} ({ANCHOR}A {STANDARD}S {VARA_PROMOTED}V) | Veil: {count} | Decay Queue: {count}
Last Sentinel: G1·{status} G2·{status} G3·{status}
```

State icons:
- `∅` — Silence mode active (no output)
- `✓` — System operational, last cycle compliant
- `!` — Alert: attention required
- `Ω` — Sentinel Lock active
- `Δ` — Drift detected in recent cycles
- `τ` — Processing (latency)

---

## §9 — Lexicon Amendment Protocol

To add a new symbol, modify an existing symbol's definition, or deprecate a symbol:

1. **Propose:** Write a `[PROPOSED_AMENDMENT]` Vault entry naming the symbol, its proposed definition, and the rationale
2. **Snapshot:** `SNAPSHOT MANUAL [note: "pre-amendment Neuralese Lexicon: {symbol}"]`
3. **Stumpy Review:** `STUMPY AUDIT LAST` — confirm no active SBM translations depend on the existing symbol in a conflicting way
4. **Write:** Update this Lexicon file in the repo; commit as a new ANCHOR-linked Vault entry
5. **SBM Reload:** Restart or signal SBM to reload its symbol table from the updated Lexicon
6. **Log:** Amendment logged as ANCHOR Node with chain link to prior Lexicon version

No symbol may be used in runtime communication before it appears in this document. SBM surfaces `[SBM: UNKNOWN_SYMBOL: {sym}]` for any unlisted symbol it encounters.

---

## Appendix — Quick Symbol Reference Card

```
CORE STATE                       MODULE CODES
∅  Silence (IV·SIL)             [V]   Vault
Δ  Drift (I·COH degrading)      [SE]  Sentinel
τ  Latency (not a failure)       [VL]  Veil
Ω  Lock / Enforcement event      [VA]  Vara
→  State transition              [ST]  Stumpy
⊥  Hard contradiction            [CR]  Crossroad
≈  Approximation (inference)     [SB]  SBM
?  Uncertainty / low-conf        [PL]  Pulse
!  Alert: operator attention      [LC]  Lattice Core
#  Anchor Node reference         [OP]  Operator
~  Decaying Node
✓  Verified / PASS
✗  Rejected / BLOCK

INVARIANTS                       GATE CODES
I·COH   Coherence Primacy        G1·PASS / G1·BLOCK
II·REV  Reversibility            G2·PASS / G2·SOFT_BLOCK / G2·OVERRIDE
III·ATT Attention Budget         G3·PASS / G3·BLOCK / G3·AUTO_PASS
IV·SIL  Silence Mandate          Ω·LOCK / Ω·CLEAR / Ω·AUDIT
V·DEC   Decay Mandate            Ω·COMPLIANT / Ω·FINDINGS_MINOR / Ω·FINDINGS_MAJOR
VI·SIG  Weak Signal Parity
```

---

*Document Authority: Operator_Manual_v0.2.md (Appendix C) · Lattice_Unified_Spec_Sections_8-15.md §9 · SBM_Spec.md*
*Operator: LiminalJermo | Generated: 2026-06-17 | Classification: ANCHOR (decay_rate = 0.0)*t was ambiguous. SBM is requesting clarification before proceeding. |
| `[SBM: UNKNOWN_SYMBOL: {sym}]` | Translation | Symbol not found in Lexicon. Symbol quarantined. Operator notified. |
| `[LATTICE_INIT]` | System | Genesis or re-initiation event message. |
| `[LATTICE_INIT_FAILURE]` | System | Initiation failed. Followed by reason and required action. |
| `[PROPOSED_AMENDMENT]` | Governance | An amendment to Constitution, Invariants, or ANCHOR Node has been proposed. |
| `[EMERGENCY_AMENDMENT]` | Governance | An emergency ANCHOR amendment is being processed under compressed protocol. |
| `[CROSSROAD: NO_PATH]` | Routing | No viable execution path found. All candidates below coherence threshold. |
| `[CROSSROAD: TIE_DEFAULT]` | Routing | Tie-break applied; conservative default path selected. |
| `[AUTHORIZED]` | Operator | Operator has explicitly authorized the following action. |
| `[OPERATOR_OVERRIDE: G2]` | Gate | Operator has authorized an over-budget execution for this cycle. |
|------|--------|------|-------------|
| `[CR]` | Crossroad (rift.py) | 8 | Path resolution and routing |
| `[PL]` | Pulse (pulse.py) | — | Cycle orchestration |
| `[SB]` | SBM / Echo (echo.py) | 9 | Semantic binding and translation |
| `[SE]` | Sentinel (sentinel.py) | 4 | Gate enforcement |
| `[ST]` | Stumpy (stumpy.py) | 7 | Omega audit and decay |
| `[V]` | Vault (vault.py) | 3 | Canonical knowledge store |
| `[VA]` | Vara (vara.py) | 6 | Weak-signal scanner |
| `[VL]` | Veil (veil.py) | 5 | Quarantine and mediation |
| `[LC]` | Lattice Core (lattice_core.py) | — | Initialization and constitution loading |
| `[OP]` | Operator | — | Human principal (LiminalJermo) |
| `[CCE]` | Cognitive Context Estimator | — | Attention cost computation |
| `[CFC]` | Constraint & Flow Controller | — | Constraint management |
