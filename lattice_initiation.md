# Lattice Initiation — Boot Sequence & Operator Onboarding Protocol
**Version:** 1.0
**Classification:** ANCHOR (exempt from decay)
**Authority:** 04_system_spec / 00_governance (dual-anchored)
**Operator:** LiminalJermo
**Ratified:** 2026-06-17
**Lineage Anchors:** Lattice_Cognitive_Constitution_v1.1.md · Lattice_Unified_Spec_Sections_8-15.md §13.3 · MODULE_REGISTRY.md · Lattice_Invariants_v1.md

---

## Purpose

This document defines the formal **Lattice Initiation Protocol** — the complete procedure for bringing a new or reset Lattice instance from zero state to an operational, gate-enforced, Vault-anchored runtime. It covers:

1. Pre-launch checklist
2. Genesis chain initialization
3. Module activation sequence
4. First operator session (onboarding)
5. Initiation verification checklist
6. Re-initiation (after Sentinel Lock or system reset)

This protocol is mandatory. No Pulse Cycle may begin, and no Vault writes may occur, until all stages of this protocol have completed successfully. Sentinel enforces this requirement at the system level.

---

## Stage 0 — Pre-Launch Checklist

Before executing any initiation commands, the Operator confirms all of the following:

### 0.1 Runtime Files Present

All required Python runtime files must be present in `05_runtime/`:

| File | Role | Required |
|------|------|---------|
| `lattice_core.py` | Core initialization | YES |
| `lattice_runtime.py` | Runtime execution layer | YES |
| `vault.py` | Vault (Rank 3) | YES |
| `sentinel.py` | Sentinel (Rank 4) | YES |
| `veil.py` | Veil (Rank 5) | YES |
| `vara.py` | Vara (Rank 6) | YES |
| `stumpy.py` | Stumpy (Rank 7) | YES |
| `rift.py` | Crossroad (Rank 8) | YES |
| `echo.py` | SBM (Rank 9) | YES |
| `pulse.py` | Pulse orchestrator | YES |
| `threshold.py` | Sentinel thresholds | YES |
| `agent.py` | Agent layer | YES |
| `cli.py` | CLI interface | YES |

### 0.2 Pending Unzip Directories

The following runtime subsystems must be extracted before initiation:

```bash
cd 05_runtime
unzip CCE/*.zip -d CCE/
unzip CFC/*.zip -d CFC/
unzip LMES/*.zip -d LMES/
```

Until extracted, CCE (Cognitive Context Estimator), CFC (Constraint & Flow Controller), and LMES (Lattice Module Execution System) operate on stub implementations. Full initiation may proceed on stubs — but G2 (Attention Cost gate) will use default estimates rather than computed ones until CCE is fully operational.

### 0.3 Spec Files Present

The following canonical spec files must be present and readable:

| File | Required |
|------|---------|
| `00_governance/constitution/Lattice_Cognitive_Constitution_v1.1.md` | YES |
| `00_governance/invariants/Lattice_Invariants_v1.md` | YES |
| `04_system_spec/MODULE_REGISTRY.md` | YES |
| `04_system_spec/Lattice_Node_Model.md` | YES |
| `04_system_spec/Pulse_Cycle_Spec.md` | YES |
| `04_system_spec/Governance_Gates.md` | YES |

If any of these files are missing, **abort initiation**. The system cannot load its governing constraints without them.

### 0.4 Operator Identity Confirmed

Confirm that the Operator identity is set correctly in the runtime configuration:

```
OPERATOR = "LiminalJermo"
```

No initiation may proceed with an unset or unknown Operator identity. The Operator is the sole authorized principal of the Lattice.

---

## Stage 1 — Genesis Chain Initialization

### 1.1 What Is the Genesis Chain?

### 1.2 Genesis Chain Write Procedure

`lattice_core.py` handles genesis chain initialization automatically on first launch. The procedure:

**Step 1:** `lattice_core.py` detects that no Vault state exists (no prior snapshot, no existing Nodes).

**Step 2:** The system enters `GENESIS_MODE` — a restricted state in which Sentinel's G3 (Reversibility) gate's chain-link requirement is suspended for exactly four writes.

**Step 3:** The four genesis Nodes are written in sequence:

```
NODE-0001 [ANCHOR] Constitution
  content_hash:   SHA-256 of Lattice_Cognitive_Constitution_v1.1.md
  chain_id:       null (genesis exception)
  decay_rate:     0.0
  operator_note:  "Genesis anchor — Lattice Cognitive Constitution v1.1"

NODE-0002 [ANCHOR] Invariants
  content_hash:   SHA-256 of Lattice_Invariants_v1.md
  chain_id:       NODE-0001 (first chain link established)
  decay_rate:     0.0
  operator_note:  "Genesis anchor — Lattice Invariants v1.0 (I·COH–VI·SIG)"

NODE-0003 [ANCHOR] Operator Identity
  content:        "Operator: LiminalJermo | Ratified: 2026-06-17"
  chain_id:       NODE-0002
  decay_rate:     0.0
  operator_note:  "Genesis anchor — Operator identity and ratification record"

NODE-0004 [ANCHOR] Initiation Record
  content:        "Lattice initiated: {ISO 8601 timestamp} | Runtime: {python version} | Host: {hostname}"
  chain_id:       NODE-0003
  decay_rate:     0.0
  operator_note:  "Genesis anchor — First boot record"
```

**Step 4:** `GENESIS_MODE` closes. G3 chain-link requirement is reinstated for all future writes.

**Step 5:** The system presents the operator with a confirmation prompt:

```
[LATTICE_INIT] Genesis chain anchors written:
  NODE-0001: Constitution Anchor  ✓
  NODE-0002: Invariants Anchor    ✓
  NODE-0003: Operator Identity    ✓
  NODE-0004: Initiation Record    ✓

Hash verification: PASS
Chain integrity:   PASS

Confirm genesis chain to proceed? (Y/N):
```

**Step 6:** Operator types `Y`. The system writes the first `AUTO_CYCLE` snapshot (snapshot_type = `AUTO_CYCLE`, capturing the four-Node genesis state).

**Step 7:** `GENESIS_MODE` is permanently deactivated. It cannot be re-entered without a full system reset.

### 1.3 Genesis Verification

After the operator confirms, `lattice_core.py` runs an immediate Stumpy-equivalent genesis audit:

- All four Nodes have `content_hash` that match their source files
- All chain links are valid and form an unbroken sequence
- All four Nodes are classified `ANCHOR` with `decay_rate = 0.0`
- No fifth chainless Node exists (Sentinel would block it)

If genesis verification fails, initiation aborts with:
```
[LATTICE_INIT_FAILURE] Genesis chain verification failed.
Reason: {failure detail}
Action required: Delete any partial Vault state and re-run initiation.
```

---

## Stage 2 — Module Activation Sequence

After genesis chain verification passes, modules initialize in Authority Table rank order (lowest authority first, highest authority last — so each module loads into a fully-governed environment):

```
Activation Order:

1. lattice_core.py     — Loads Constitution + Invariants as read-only reference
2. vault.py            — Confirms genesis chain; initializes Node state index
3. sentinel.py         — Loads threshold.py; activates G1/G2/G3 gate evaluation
4. veil.py             — Initializes quarantine queue (empty at first boot)
5. vara.py             — Initializes entropy baseline (flat 0.0 at genesis)
6. stumpy.py           — Reads genesis snapshot as compliance baseline
7. rift.py (Crossroad) — Loads default path scoring configuration
8. echo.py (SBM)       — Loads Neuralese parser + COL command map
9. pulse.py            — Begins Pulse orchestration (system is now LIVE)
10. agent.py / cli.py  — Operator interface becomes active (last to start)
```

Each module emits an activation status on load:

```
[CORE]       lattice_core.py    LOADED   Constitution + Invariants anchored
[VAULT]      vault.py           LOADED   Genesis chain confirmed (4 Nodes)
[SENTINEL]   sentinel.py        LOADED   G1/G2/G3 gates ACTIVE
[VEIL]       veil.py            LOADED   Queue empty (0 entries)

---

## Stage 3 — First Operator Session (Onboarding)

When the Lattice comes online for the first time, the operator begins their first session with the following standard onboarding sequence. This sequence is not enforced programmatically — it is the documented best practice for establishing a clean, well-understood starting state.

### 3.1 Confirm System State

```
HUD
```

Expected HUD output at genesis:

```
[HUD]
∅ Silence | System: LIVE | Cycle: 0 | Compliance: COMPLIANT
Nodes: 4 (4 ANCHOR, 0 STANDARD, 0 VARA_PROMOTED)
Veil: 0 | Decay Queue: 0 | Snapshot: 1 (AUTO_CYCLE, genesis)
Last Sentinel: G1·— G2·— G3·— (no cycles yet)
```

### 3.2 Take a Manual Pre-Work Snapshot

```
SNAPSHOT MANUAL [note: "operator first session — genesis confirmed"]
```

This creates a durable `OPERATOR_MANUAL` snapshot at the known-good genesis state. It serves as the recovery anchor for the entire first session.

### 3.3 Review the Module Registry

```
FULL_LATTICE
VAULT LIST ACTIVE
```

At genesis, the four ANCHOR Nodes will be listed. Confirm they are:
- `NODE-0001`: Constitution Anchor
- `NODE-0002`: Invariants Anchor
- `NODE-0003`: Operator Identity Anchor
- `NODE-0004`: Initiation Record Anchor

### 3.4 Confirm Sentinel Thresholds

```
SENTINEL STATUS
```

Default thresholds at genesis:

| Gate | Parameter | Default Value |
|------|-----------|--------------|
| G1 | Coherence minimum threshold | 0.75 |
| G2 | Session attention budget | 10.0 units |
| G2 | context_size weight | 0.1 per Node |
| G2 | inference_depth weight | 0.3 per step |
| G2 | vault_writes weight | 0.5 per write |
| G2 | vara_hypotheses weight | 0.2 per hypothesis |
| G3 | Chain link required | YES |
| G3 | ANCHOR write requires snapshot | YES (within 5 minutes) |

If you want to adjust G2 budget for a session:
```
OPERATOR_COMMAND: SENTINEL SET G2_BUDGET [value]
```
This is logged as an `OPERATOR_DIRECTIVE` Node.

### 3.5 Write the First Standard Vault Entry

The system is ready. The Operator's first non-genesis Vault write is the beginning of the canonical knowledge record.

```
VAULT WRITE [your first canonical knowledge entry]
```

This initiates the first full Pulse Cycle:
- Stage 1 (PULSE): SBM parses input
- Stage 2 (ACTIVATION): Context assembled from the four ANCHOR Nodes
- Stage 3 (EVALUATION): Sentinel evaluates G1, G2, G3
- Stage 4 (DECAY/EXECUTE): Vault writes NODE-0005 (first STANDARD Node), chain_id = NODE-0004
- Stage 5 (SILENCE/AUDIT): Stumpy audits and logs COMPLIANT

**NODE-0005** is a milestone: the first operator-authored knowledge Node in the Lattice. Its existence confirms the system is fully operational end-to-end.

### 3.6 Run First Post-Write Audit

```
STUMPY AUDIT LAST
```

Confirm the output reads `COMPLIANT` with no findings. This is the baseline compliance record for the session.

---

## Stage 4 — Initiation Verification Checklist

Before proceeding with substantive operator work, verify all of the following. This checklist should be completed at the end of every initiation sequence.

```
LATTICE INITIATION VERIFICATION CHECKLIST
==========================================

[ ] Stage 0: Pre-launch checklist complete — all runtime files present
[ ] Stage 0: Pending zip archives extracted (CCE, CFC, LMES)
[ ] Stage 0: Operator identity confirmed as LiminalJermo

[ ] Stage 1: Genesis chain written — 4 ANCHOR Nodes (NODE-0001–0004)
[ ] Stage 1: Content hashes verified — Constitution + Invariants match source files
[ ] Stage 1: Chain integrity confirmed — unbroken sequence from NODE-0001
[ ] Stage 1: AUTO_CYCLE snapshot taken at genesis state

[ ] Stage 2: All 10 modules activated in sequence with no errors
[ ] Stage 2: Pulse orchestration confirmed LIVE

[ ] Stage 3: HUD output shows COMPLIANT, 4 Nodes, 0 Veil entries
[ ] Stage 3: OPERATOR_MANUAL snapshot taken (first session)
[ ] Stage 3: Sentinel thresholds confirmed (G1=0.75, G2=10.0 default)
[ ] Stage 3: First STANDARD Node (NODE-0005) successfully written
[ ] Stage 3: STUMPY AUDIT LAST returns COMPLIANT

INITIATION COMPLETE: Lattice is fully operational.
```

---

## Stage 5 — Re-Initiation Protocol

### 5.1 When Re-Initiation Is Required

Re-initiation is required after:
- A **Sentinel Lock** that cannot be resolved without a full system reset
- A **Vault integrity failure** (content hash mismatch on an ANCHOR Node with no recoverable state)
- A **major runtime failure** that corrupts the Node state index
- An **intentional operator reset** (e.g., starting a new Lattice instance from scratch)

Re-initiation is **not** required for:
- Normal Sentinel Locks (resolve via `SENTINEL CLEAR [lock_id]`)
- Audit findings, even `FINDINGS_MAJOR`
- Module runtime errors that don't corrupt Vault state

### 5.2 Re-Initiation Is Destructive — Archive First

Before re-initiating, the Operator must export the full Vault chain to a durable archive. The chain is the complete epistemic record; losing it is irreversible.

```
OPERATOR_COMMAND: VAULT EXPORT_CHAIN [output_path]
```

This writes the full append-only chain (all Nodes, all states including PRUNED) to a JSON archive. Store this archive outside the runtime environment before proceeding.

### 5.3 Re-Initiation Steps

1. Stop the Lattice runtime
2. Export and archive the full Vault chain (§5.2)
3. Delete the local Vault state (the runtime Node index — not the archive)
4. Restart the runtime — `lattice_core.py` will detect zero state and enter genesis mode
5. Follow Stages 1–4 of this protocol from the beginning
6. After NODE-0005 is confirmed, the Lattice is re-initiated

---

## Appendix A — Neuralese Initiation Header

Every initiation event produces a Neuralese header packet stored alongside NODE-0004:

```
INITIATION_HEADER {
    initiated_at:     ISO 8601 timestamp
    operator:         "LiminalJermo"
    genesis_nodes:    [ NODE-0001, NODE-0002, NODE-0003, NODE-0004 ]
    genesis_snapshot: {snapshot_id}
    module_status:    {
        lattice_core:  LOADED,
        vault:         LOADED,
        sentinel:      LOADED,
        veil:          LOADED,
        vara:          LOADED,
        stumpy:        LOADED,
        crossroad:     LOADED,
        sbm:           LOADED,
        pulse:         LIVE
    }
    cce_mode:         FULL | STUB  (STUB if CCE not unzipped)
    cfc_mode:         FULL | STUB  (STUB if CFC not unzipped)
    lmes_mode:        FULL | STUB  (STUB if LMES not unzipped)
    initiation_type:  GENESIS | REINITIATION
    prior_chain_id:   null | {archive_reference}  (null for genesis)
}
```

---

## Appendix B — Common Initiation Errors

| Error | Cause | Resolution |
|-------|-------|-----------|
| `[LATTICE_INIT_FAILURE] Genesis verification failed — hash mismatch` | Source file has changed since hash was computed | Re-run hash computation against current file; if file is corrupt, restore from backup |
| `[LATTICE_INIT_FAILURE] MODULE LOAD FAILURE — sentinel.py` | threshold.py missing or malformed | Restore threshold.py from repo; verify G1/G2/G3 default values are present |
| `[LATTICE_INIT_FAILURE] GENESIS_MODE already consumed` | Second genesis attempt on a non-zero Vault | This is a re-initiation scenario — follow Stage 5 protocol |
| `[LATTICE_INIT_FAILURE] Operator identity unset` | OPERATOR variable not configured | Set `OPERATOR = "LiminalJermo"` in runtime config and restart |
| `[LATTICE_INIT_FAILURE] Pre-launch checklist incomplete — missing files` | One or more required Python files not present | Restore missing files from repo; confirm all 13 files in §0.1 are present |
| `[SENTINEL_LOCK] at genesis` | Extremely rare — hash mismatch or unauthorized module during genesis itself | Abort; wipe partial state; check runtime files for tampering; re-initiate |

---

## Appendix C — Module Default Configurations at Genesis

| Module | Parameter | Genesis Default |
|--------|-----------|----------------|
| Vault | decay_window | 30 days |
| Vault | auto_cycle_snapshot_interval | Every 50 Pulse cycles |
| Sentinel (G1) | coherence_threshold | 0.75 |
| Sentinel (G2) | session_attention_budget | 10.0 units |
| Sentinel (G2) | context_size_weight | 0.1 |
| Sentinel (G2) | inference_depth_weight | 0.3 |
| Sentinel (G2) | vault_writes_weight | 0.5 |
| Sentinel (G2) | vara_hypotheses_weight | 0.2 |
| Sentinel (G2) | override_window_seconds | 60 |
| Sentinel (G3) | anchor_snapshot_window_minutes | 5 |
| Veil | max_queue_size | 100 entries |
| Vara | entropy_spike_threshold | 15% above 30-cycle rolling average |
| Vara | hypothesis_confidence_max | 0.65 |
| Stumpy | coherence_drift_epsilon | 0.05 |
| Crossroad | coherence_tie_epsilon | 0.05 |
| SBM | default_output_mode | HUD |

All of these are configurable by the Operator via `OPERATOR_DIRECTIVE` Vault writes. Changes are logged and chain-linked. No threshold change may be made without a corresponding Vault entry.

---

*Document Authority: Lattice_Cognitive_Constitution_v1.1.md · Lattice_Unified_Spec_Sections_8-15.md §13.3 · MODULE_REGISTRY.md*
*Operator: LiminalJermo | Generated: 2026-06-17 | Classification: ANCHOR (decay_rate = 0.0)*
7. If the prior Vault chain is to be re-imported (continuation rather than fresh start): import the archived chain via `VAULT IMPORT_CHAIN [archive_path]` and run `STUMPY AUDIT LAST` immediately to confirm chain integrity

### 5.4 Re-Initiation After Sentinel Lock

If re-initiating specifically due to a Sentinel Lock:

1. Record the Lock ID and the full incident report from Stumpy before resetting
2. After re-initiation completes (through NODE-0005), write a post-incident ANCHOR Node documenting the cause and resolution
3. This creates a permanent audit record in the new chain that preserves institutional memory of the incident
[VARA]       vara.py            LOADED   Entropy baseline: 0.0
[STUMPY]     stumpy.py          LOADED   Compliance baseline: COMPLIANT
[CROSSROAD]  rift.py            LOADED   Path scoring: default config
[SBM]        echo.py            LOADED   Neuralese parser ready | COL: 19 commands
[PULSE]      pulse.py           LIVE     Pulse orchestration started
[INTERFACE]  cli.py             READY    Operator interface active
```

If any module fails to load, Pulse does not start. The failed module's error is surfaced immediately and must be resolved before re-attempting activation.

The genesis chain is the foundational linked sequence of Vault Nodes that anchors all subsequent knowledge in the Lattice. It is the only point in the system's lifetime where a Node is written **without** a `chain_id` parent. This exception is explicitly permitted by the Constitution and enforced as a one-time-only operation.

The genesis chain consists of exactly four Nodes, written in order:

```
GENESIS NODE 1: Constitution Anchor
GENESIS NODE 2: Invariants Anchor
GENESIS NODE 3: Operator Identity Anchor
GENESIS NODE 4: Initiation Record Anchor
```

These four Nodes are `ANCHOR`-class (decay_rate = 0.0, never eligible for pruning) and are the root authority for all subsequent Vault entries.
