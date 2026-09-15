# Canonical Vault Reconciliation Audit — 2026-09-15

**Status:** AUDIT / PROPOSAL ONLY
**Canonical authority:** `Lattice Cognitive Governance Substrate — Unified Canonical Reference v1.0` (CGS-v1.0, dated 2026-09-01), consolidated canonical reference.
**Target branch:** `chatgpt`
**Purpose:** Identify Vault artifacts whose module, authority, pipeline, contract, or runtime references predate the canonical seven-module execution spine.

## Canonical execution spine

The authoritative pipeline is:

`RIP/CF-0 → M1 IDE → M2 CCE → M3 CFC → M4 SBM → M5 IDE-2 → M6 PAM → M7 MTM → Runtime/WDA/Executor`

Canonical module positions:

| Position | Module | Primary handoff |
|---|---|---|
| M1 | Intent Decomposition Engine (IDE) | Governed Intent Graph (IG-G) |
| M2 | Constraint Cartography Engine (CCE) | ConstraintResolutionResult + CCEValidationReport |
| M3 | Crash-Free Constraint Engine (CFC) | Constraint Package (CP) + CFCReport |
| M4 | Semantic Binding Module (SBM) | Semantic Binding Package (SBP) + SemanticBindingReport |
| M5 | Intent Signal Bridge (IDE-2) | Governed Semantic-Intent Bridge Packet |
| M6 | Principle Alignment Module (PAM) | Principle-Anchored Intent Graph (PA-IG) + PrincipleAlignmentReport |
| M7 | Mechanism Translation Module (MTM) | Mechanism Execution Contract (MEC) |

The canonical reference explicitly states that its September 1 consolidation supersedes fragmented Vault references and that M1–M7 are authoritative for cross-document references.

## Findings

### HIGH — stale authority hierarchy / module model

These files still encode the pre-consolidation nine-rank hierarchy and/or treat SBM as Rank 9 output boundary:

- `llms-full.txt`
- `lattice_initiation.md`
- `04_system_spec/Lattice_Unified_Spec_Sections_8-15.md`
- `04_system_spec/modules/SBM_Spec.md`
- `04_system_spec/modules/Sentinel_Spec.md`
- `04_system_spec/modules/Veil_Spec.md`
- `04_system_spec/modules/Stumpy_Spec.md`
- `04_system_spec/modules/Crossroad_Spec.md`
- `00_system/manifest/subsystems/copilot/MODULE_INTERACTION_RULES_1.0.md`

These are not merely cosmetic references. Several describe authority, routing, or output boundaries, so they can misrepresent actual governance behavior if treated as current.

### HIGH — stale execution pipeline

- `03_vault_pipeline/pipeline_runtime.py` still documents `IDE → CCE → CFC → SBM → PAM → MTM → WDA`, omitting M5 IDE-2.
- `05_runtime/pipeline/cli.py` exposes an older stage model and should be reconciled with the seven-module spine.

### HIGH — stale module/version indexes

- `versions/modules.json` uses a legacy v0.1.0 registry centered on SBM/PAM/MTM/WDA and does not represent the canonical M1–M7 positions.
- `04_system_spec/MODULE_REGISTRY.md` is being reconciled separately in the existing Module Registry PR.

### MEDIUM — contract graph reconciliation required

The Vault contains both legacy root-level contracts and newer `00_governance/contracts` entries. In particular:

- `contracts/sbm_pam.json`
- `00_governance/contracts/sbm_pam.json`
- `00_governance/contracts/pam_mtm.json`
- `00_governance/contracts/contract_index.json`
- `vault/00_spec/vault_record_types.json`
- `vault/00_spec/vault_spec.json`

The contract graph should be checked against the canonical M4→M5→M6→M7 handoffs. No contract should imply a direct SBM→PAM path now that IDE-2 is canonical M5.

### MEDIUM — top-level discovery and integration surfaces

These should be reconciled after the core module and contract surfaces:

- `INDEX.md`
- `VAULT_INDEX.md`
- `README.md`
- `00_system/manifest/INTEGRATION_MAP.md`
- `00_system/SYSTEM_COHERENCE_MAP_1.0.md`
- `00_system/manifest/governance/OPERATOR_SOVEREIGNTY_INTERFACE_1.0.md`

### MEDIUM — runtime governance references

`05_runtime/vara_sentinel.py` and `05_runtime/stumpy/behavioral.py` contain authority-rank assumptions. Runtime enforcement code requires special handling: documentation may be updated directly, but executable authority checks must be compared against the actual current governance model before modification.

## Preservation rule

Historical artifacts must not be silently rewritten merely because they are old. If a document records a superseded architecture, preserve its historical content where appropriate and mark the conflicting architectural reference as **DEPRECATED / HISTORICAL**. Current discovery surfaces and active specifications must point to CGS-v1.0.

## Recommended reconciliation order

1. Complete `MODULE_REGISTRY.md` reconciliation (existing PR).
2. Reconcile active module specifications and authority references.
3. Insert IDE-2 into runtime/pipeline documentation and verify executable routing.
4. Reconcile M4→M5→M6→M7 contracts and contract indexes.
5. Rebuild `versions/modules.json` as a canonical-position registry or explicitly mark it legacy.
6. Reconcile `INDEX.md`, `VAULT_INDEX.md`, `README.md`, integration maps, and exported `llms*.txt` surfaces.
7. Run Stumpy/Vault consistency audit against the resulting tree.

## Evidence snapshot

The current Vault search shows the legacy hierarchy in active files, including `Rank 9` SBM references and a pipeline implementation that omits IDE-2. The canonical reference dated September 1, 2026 defines the seven-module spine and explicitly resolves prior module-index collisions in favor of M1–M7.

**No historical artifact should be deleted as part of this audit.**
