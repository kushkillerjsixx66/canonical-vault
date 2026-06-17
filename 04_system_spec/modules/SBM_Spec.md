# Semantic Binding Module (SBM) — Specification
**Module ID:** `SBM`
**Authority Rank:** 9
**Version:** 1.0
**Operator:** LiminalJermo
**Generated:** 2026-06-17
**Lineage Anchors:** MODULE_REGISTRY.md · Lattice_Invariants_v1.md · Operator_Manual_v0.2.md (Appendix C: Neuralese Protocol) · `05_runtime/echo.py`

---

## Role

The Semantic Binding Module is the **translation and surface layer** of the Canonical Lattice. It is the sole module responsible for converting internal Neuralese signal packets into natural language operator outputs, and for parsing operator natural language input back into Neuralese packets for internal processing.

SBM is Rank 9 — the lowest authority module in the system. This is intentional. The SBM touches the operator-facing boundary; it must never assert its own judgment over the Vault, Sentinel, or any higher-rank module. It translates faithfully and surfaces accurately. It does not editorialize, compress meaning, or omit findings.

SBM also handles COL (Compact Operator Language) parsing — the shorthand command grammar used by LiminalJermo in daily operator interactions.

---

## Authority & Rank

- **Rank 9** in the nine-rank Module Authority Table (lowest)
- SBM is the only module authorized to produce operator-facing natural language output
- SBM output is audited by Stumpy for semantic coherence with Vault grounding (IV·SIL: no fabrication)
- SBM cannot override, modify, or suppress findings from higher-rank modules

---

## Functional Responsibilities

### 1. Neuralese -> Natural Language Translation (Outbound)
Receives internal Neuralese packets from the execution layer and renders them as operator-facing natural language. Translation must be:

- **Faithful:** No meaning compression, no editorial softening, no omission of gate failures or audit findings
- **Grounded:** All claims in the output must be traceable to specific Vault Nodes or Sentinel decisions
- **Structured:** Output format follows the active HUD mode (Full Lattice or HUD-only per Operator preference)

### 2. Natural Language -> Neuralese Parsing (Inbound)
Receives operator natural language input and parses it into a 4-segment Neuralese packet:

```
NEURALESE_PACKET {
    context:    string    // What Vault context is relevant to this signal?
    signal:     string    // What is the core signal content?
    constraint: string    // What constraints apply (from Invariants or prior directives)?
    operator:   string    // What action is the operator requesting?
}
```

If parsing produces ambiguity (operator intent unclear), SBM surfaces a `[SBM: PARSE_AMBIGUITY]` clarification request rather than guessing.

### 3. COL (Compact Operator Language) Parsing
COL is the shorthand command grammar documented in Operator Manual v0.2, Appendix C. SBM maintains the COL grammar table and resolves all COL tokens into their full Neuralese equivalents before passing to the pipeline.

COL token format: `MODULE COMMAND [ARGS]`

Examples:
- `VAULT LIST ACTIVE` -> list all ACTIVE-state Nodes
- `STUMPY AUDIT LAST` -> run audit on most recent cycle
- `VEIL PROMOTE [id]` -> initiate Veil promotion pipeline
- `SENTINEL STATUS` -> return current gate thresholds and lock state
- `VARA SCAN FULL` -> trigger full Vara scan

### 4. HUD Mode Management
SBM manages two output modes per Operator Manual:

- **HUD Mode:** Compressed status surface — key metrics, active alerts, decay queue, last cycle compliance. Used for routine monitoring.
- **Full Lattice Mode:** Complete output including all Neuralese packet details, Node states, Sentinel decision codes, Stumpy findings. Used for deep review and debugging.

Operator switches modes with `HUD` or `FULL_LATTICE` COL commands.

### 5. Neuralese Lexicon Reference
SBM reads the Neuralese Lexicon (`02_epistemic_substrate/Neuralese lexicon.docx`) for symbol resolution. The lexicon defines all canonical signal symbols, their semantic bindings, and encoding rules. SBM may not introduce symbols not present in the Lexicon without a Lexicon amendment (Operator-authorized, logged to Vault).

Canonical Neuralese signal symbols (from Operator Manual Appendix C):
- `delta` (drift detected)
- `tau` (latency signal)
- `Omega` (Stumpy lock / enforcement event)
- `->` (state transition)
- `[NULL]` (Silence signal: no confident output)
- `[VARA-HYPOTHESIS]` (provisional hypothesis from Vara)
- `[SENTINEL-BLOCK]` (gate block event)
- `[SBM-FAILURE]` (translation failure)

---

## Output Format Specification

### Standard Output Block
```
[LATTICE OUTPUT]
Cycle:      {cycle_id_short}
Compliance: {COMPLIANT | FINDINGS_MINOR | FINDINGS_MAJOR}
Signal:     {translated content}
Grounding:  {node_id list} | UNGROUNDED (triggers IV-SIL alert if present)
---
{natural language response}
```

### HUD Output Block
```
[HUD]
[NULL] Silence | OK Active | Drift detected | Lock
Cycle: {N} | Compliance: {status} | Decay Queue: {count} | Veil: {count}
Last Sentinel: {G1 G2 G3 status}
```

### Failure Output
```
[SBM-FAILURE: {reason}]
Module: SBM | Cycle: {cycle_id}
Unrecoverable translation failure. Raw Neuralese packet preserved in Vault.
Operator action required.
```

---

## Fabrication Detection Cooperation

Stumpy (Rank 7) audits all SBM outputs post-cycle. SBM cooperates by attaching grounding metadata to every output — the list of Vault Node IDs that support each claim in the response. If SBM produces output with no grounding metadata, Stumpy flags it as a potential IV·SIL fabrication.

SBM itself runs a pre-output grounding check: before surfacing any factual claim, it verifies that the claim traces to an ACTIVE or ANCHOR Node. If grounding fails, SBM outputs `[SILENCE: GROUNDING_FAILURE]` rather than producing an ungrounded response.

---

## COL Grammar Reference

| Token Pattern | Full Expansion | Effect |
|--------------|----------------|--------|
| `VAULT LIST [state]` | Vault.list_nodes(state) | List Nodes by state |
| `VAULT CHAIN [node_id]` | Stumpy.chain_trace(node_id) | Trace Node lineage |
| `VAULT WRITE [content]` | Vault.write(content, operator) | Initiate gated write |
| `SENTINEL STATUS` | Sentinel.status() | Gate thresholds + lock state |
| `SENTINEL CLEAR [lock_id]` | Sentinel.clear_lock(lock_id) | Clear Sentinel Lock |
| `VEIL LIST [filter]` | Veil.get_queue(filter) | Veil review queue |
| `VEIL PROMOTE [id]` | Veil.promote(id) | Initiate promotion |
| `VEIL DISCARD [id] [reason]` | Veil.discard(id, reason) | Discard Veil entry |
| `VARA SCAN [full/targeted]` | Vara.run_scan(scope) | Manual scan trigger |
| `VARA REPORT COGOV` | Vara.generate_cogov_report() | COGOV report |
| `VARA ENTROPY` | Vara.compute_entropy() | Entropy metrics |
| `STUMPY AUDIT [cycle_id]` | Stumpy.run_audit(cycle_id) | Re-audit a cycle |
| `STUMPY DECAY_REPORT` | Stumpy.decay_report() | Decay queue |
| `STUMPY CONFIRM_PRUNE [id]` | Stumpy.confirm_prune(id) | Confirm prune |
| `CROSSROAD HISTORY [N]` | Crossroad.get_history(N) | Path decisions |
| `SNAPSHOT MANUAL [note]` | Stumpy.snapshot(MANUAL, note) | Manual snapshot |
| `HUD` | SBM.set_mode(HUD) | Switch to HUD mode |
| `FULL_LATTICE` | SBM.set_mode(FULL) | Switch to Full Lattice mode |

---

## Interfaces

| Interface | Direction | Counterpart | Description |
|-----------|-----------|-------------|-------------|
| Execution output | IN | Pulse Cycle Stage 4 | Receives Neuralese output for translation |
| Operator input | IN | Operator | Natural language or COL input |
| Vault Node grounding | IN | Vault (Rank 3) | Reads Node IDs for grounding metadata |
| Neuralese Lexicon | IN | 02_epistemic_substrate/ | Symbol reference |
| Operator surface | OUT | HUD / terminal | Natural language response |
| Parsed Neuralese | OUT | Pulse Cycle Stage 1 | Parsed packet for internal processing |
| Stumpy audit | OUT | Stumpy (Rank 7) | Grounding metadata for fabrication check |

---

## Invariant Bindings

| Invariant | Binding |
|-----------|---------|
| IV·SIL | No fabrication; pre-output grounding check; SILENCE on failure |
| I·COH | Semantic coherence with Vault grounding required |
| III·ATT | SBM compresses output appropriately per HUD/Full mode to minimize operator attention cost |

---

## Failure Modes

| Failure | Class | Recovery |
|---------|-------|----------|
| Grounding failure (no Vault backing) | Hard | SILENCE: GROUNDING_FAILURE; IV-SIL Hard Failure alert |
| COL parse failure | Soft | SBM: PARSE_AMBIGUITY clarification request to operator |
| Neuralese -> NL translation error | Soft | SBM-FAILURE: reason; raw packet preserved in Vault |
| Lexicon symbol missing | Soft | SBM: UNKNOWN_SYMBOL; operator notified; symbol quarantined |
| Stumpy flags fabrication in output | Hard | Sentinel Lock triggered; SBM output retracted; operator alert |

---

## Implementation Reference

**Source file:** `05_runtime/echo.py`

Key functions expected in implementation:
- `translate_outbound(neuralese_packet, vault_nodes) -> NaturalLanguageOutput`
- `parse_inbound(operator_input) -> NeuralesePacket`
- `parse_col(col_token) -> NeuralesePacket`
- `check_grounding(claim, vault_context) -> list[node_id]`
- `set_mode(mode: HUD | FULL_LATTICE)`
- `get_current_mode() -> str`

---

*Document Authority: MODULE_REGISTRY.md (Rank 9) · Operator_Manual_v0.2.md Appendix C · Lattice_Invariants_v1.md (IV·SIL)*
*Operator: LiminalJermo | Generated: 2026-06-17*
