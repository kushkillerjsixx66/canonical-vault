# VAULT INDEX
**Version:** 2.1 (CCE/CFC/LMES Status Corrected)
**Author:** LiminalJermo
**Date:** 2026-06-17
**Status:** Canonical  reflects full repo state after Canonical Lattice spec population
**Lineage:** Lattice_Cognitive_Constitution_v1.1.md  Lattice_Unified_Spec.md  Lattice_Invariants_v1.md

---

## CORE INVARIANTS (ICOH through VISIG)

| Code | Name | Definition | Defined In |
|------|------|-----------|-----------|
| ICOH | Coherence Primacy | All output must be non-contradictory with active Vault content | `00_governance/invariants/Lattice_Invariants_v1.md` |
| IIREV | Reversibility | Vault is append-only; no destructive edits; snapshot before ANCHOR writes | `00_governance/invariants/Lattice_Invariants_v1.md` |
| IIIATT | Attention Budget | Attention cost is finite; every activation has a cost; G2 enforces the budget | `00_governance/invariants/Lattice_Invariants_v1.md` |
| IVSIL | Silence Mandate | System outputs null rather than fabricate; silence is valid and honest | `00_governance/invariants/Lattice_Invariants_v1.md` |
| VDEC | Decay Mandate | Unreferenced content must decay and eventually be pruned | `00_governance/invariants/Lattice_Invariants_v1.md` |
| VISIG | Weak Signal Parity | Weak signals are preserved in Veil and eligible for Vault promotion | `00_governance/invariants/Lattice_Invariants_v1.md` |

---

## DIRECTORY MAP

### `00_governance/`  Constitutional and Governance Documents

| File | Status | Description |
|------|--------|-------------|
| `constitution/Lattice_Cognitive_Constitution_v1.1.md` |  Exists | Primary constitutional document. 8 Axioms, 6 Principles, Module Authority Table (9 ranks), Amendment Protocol. Ratified 2026-05-22. |
| `invariants/Lattice_Invariants_v1.md` |  NEW | Full 6-invariant specification (ICOHVISIG) with enforcement rules, failure modes, enforcement matrix, and amendment protocol. |
| `operator_manual/Operator_Manual_v0.2.md` |  Exists | MVL 2.0 framework. Module Index (IDE/CCE/CFC/MTM/PAM/EGG/WDA). Neuralese Protocol (Appendix C). |
| `operator_manual/Operator_Playbook.md` |  NEW | Practical daily operator SOPs. Morning routine, Pre-work snapshot, 7 SOPs, Amendment Protocol, Neuralese Quick Reference, COL Quick Reference (16 commands), Runbook Index (RB-001RB-008). |
| `Sync_contract.md.pdf` |  Exists (binary) | Sync contract document. Binary PDF  not indexable. |
| `playbook/` |  Exists (dir) | Legacy playbook directory. See `Operator_Playbook.md` for current version. |

---

### `01_sovereignty/`  Sovereignty and Architecture

| File | Status | Description |
|------|--------|-------------|
| `SICA-001.md` |  Exists | Substrate-Independent Cognitive Architecture spec. 6 components (Lattice, Vara, Stumpy, Neuralese, COL, 4D Framework). 3 failure classes. 4-phase transmission status. |

---

### `02_epistemic_substrate/`  Epistemic Foundations

| File | Status | Description |
|------|--------|-------------|
| `Bilateral_Runtime_Patterns.md` |  Exists | Runtime pattern documentation for bilateral cognition. |
| `Bilateralism_and_Truth_Routing.md` |  Exists | Truth routing architecture in bilateral system. |
| `Neuralese lexicon.docx` |  Exists (binary) | Neuralese vocabulary reference. Binary .docx  not indexable via raw. See Operator_Manual_v0.2 Appendix C for protocol definition. |
| `The_Lattice_Empirical_Doctrine.pdf` |  Exists (binary) | Empirical doctrine document. Binary PDF  not indexable. |
| `Neuralese_Lexicon.md` |  NEW | Full Markdown lexicon: 9 sections  packet grammar, 13 core symbols, module codes, gate codes, invariant notation, signal prefixes, complete COL grammar, HUD format, amendment protocol. |

---

### `03_vault_pipeline/`  Vault and Pipeline Operations

| File | Status | Description |
|------|--------|-------------|
| `Vault_Chain_Spec.md` |  Exists | Chain specification for Vault Node linkage. |
| `Orchestration_Contract_Veil_Pipeline_Vault.md` |  Exists | Veil-to-Vault orchestration contract. Promotion pipeline specification. |
| `VARA-COGOV-001_Vara-Scan_Distilled_Briefing.md` |  Exists | Vara Cognitive Governance scan briefing report. |
| `VARA-GAP-001_OWASP_ASI_Top10_Gap_Analysis.md` |  Exists | OWASP ASI Top 10 gap analysis from Vara scan. |
| `VaraScan_Full_Operator_Report_2026-06-04.md` |  Exists | Full Vara scan operator report dated 2026-06-04. |
| `Vara_Vault_Index.md` |  Exists | Vara-specific vault index. |

---

### `04_system_spec/`  System Specifications (Core Spec Layer)

#### Root Level

| File | Status | Description |
|------|--------|-------------|
| `Lattice_Unified_Spec.md` |  Exists | Root anchor specification document. Sections 07 complete. Sections 815 were stubs  now completed by companion document. |
| `Lattice_Unified_Spec_Sections_8-15.md` |  NEW | Completes the Unified Spec. 8 Module Interaction Protocol, 9 Neuralese Full Grammar, 10 Error Taxonomy, 11 Snapshot Protocol, 12 Operator Interface Spec, 13 Runtime Deployment, 14 Amendment Procedures, 15 Appendices/Glossary. |
| `MODULE_REGISTRY.md` |  NEW | All 9 modules catalogued with full field tables: ID, Rank, File, Role, Interfaces, Invariant Bindings, Activation Condition, Failure Mode, Owner. |
| `Lattice_Node_Model.md` |  NEW | Complete Node schema (14 fields), 4 lifecycle states with transition rules, classification rules (ANCHOR/STANDARD/VARA_PROMOTED/OPERATOR_DIRECTIVE/AUDIT_RECORD). |
| `Pulse_Cycle_Spec.md` |  NEW | Full 5-stage cycle anatomy (PULSE, ACTIVATION, EVALUATION, DECAY, SILENCE) with module responsibilities, inputs/outputs, invariant checkpoints, failure behavior per stage. |
| `Governance_Gates.md` |  NEW | G1/G2/G3 complete: scoring (G1: 0.01.0, threshold 0.75), G2 attention cost formula, G2 60-second operator override window, G3 chain validation, decision matrix, all Sentinel decision codes. |
| `SNAPSHOT_REGISTRY.md` |  NEW | 6 snapshot types (AUTO_CYCLE, OPERATOR_MANUAL, PRE_AMENDMENT, VARA_PROMOTION, SENTINEL_INCIDENT, DECAY_PURGE). Snapshot schema, procedures, restore semantics, retention/decay policy, SHA-256 integrity. |

#### `04_system_spec/modules/`  Per-Module Specifications

| File | Status | Module | Rank | Python File |
|------|--------|--------|------|-------------|
| `Sentinel_Spec.md` |  NEW | Sentinel | 4 | `sentinel.py` |
| `Veil_Spec.md` |  NEW | Veil | 5 | `veil.py` |
| `Vara_Spec.md` |  NEW | Vara | 6 | `vara.py` |
| `Stumpy_Spec.md` |  NEW | Stumpy | 7 | `stumpy.py` |
| `Crossroad_Spec.md` |  NEW | Crossroad | 8 | `rift.py` |
| `SBM_Spec.md` |  NEW | SBM / Echo | 9 | `echo.py` |

---

### `05_runtime/`  Python Runtime Implementation

#### Root Python Files

| File | Module | Description |
|------|--------|-------------|
| `vault.py` | Vault (R3) | Vault state management and chain operations |
| `sentinel.py` | Sentinel (R4) | Gate evaluation (G1/G2/G3) and Omega-LOCK |
| `veil.py` | Veil (R5) | Quarantine queue management |
| `vara.py` | Vara (R6) | Weak-signal scanning and entropy monitoring |
| `stumpy.py` | Stumpy (R7) | Omega audit and decay lifecycle |
| `rift.py` | Crossroad (R8) | Path resolution and scoring |
| `echo.py` | SBM (R9) | Semantic binding and output formatting |
| `pulse.py` | Pulse | Cycle orchestration |
| `lattice_core.py` | Core | Core initialization and Constitution loading |
| `lattice_runtime.py` | Runtime | Runtime execution layer |
| `threshold.py` | Sentinel support | Gate threshold configuration |
| `agent.py` | Agent | Agent execution layer |
| `cli.py` | CLI | Command-line interface |
| `lattice_config.py` | Config | Full dataclass config  all spec thresholds (013), boot self-check |

#### Generated Test Suite

| File | Description |
|------|-------------|
| `tests/conftest.py` | sys.path bootstrap + 10 session-scoped fixtures for clean pytest execution |
| `tests/test_lattice_config.py` | 18 assertions across 11 test classes  validates all config defaults |
| `tests/test_invariants.py` | 28 assertions across 7 test classes  validates all 6 invariants, gate bindings, failure classes |

#### `05_runtime/` Subdirectories

| Directory | Status | Description |
|-----------|--------|-------------|
| `CCE/` |  Present | Cognitive Context Engine  extracted and operational |
| `CFC/` |  Present | Constraint and Flow Controller  extracted and operational |
| `IDE/` |  Present | Integrated Development Environment module |
| `LMES/` |  Present | Lattice Module Execution System  extracted and operational |
| `Lmes/` |  Present | Lattice Module Execution System (alternate casing) |
| `lattice-app/` |  Present | Lattice application layer |
| `lattice_cli_project/` |  Present | CLI project files |
| `lattice_runtime_cli/` |  Present | Runtime CLI interface |

---

### `06_ip_legal/`  Intellectual Property and Legal

| File | Status | Description |
|------|--------|-------------|
| `IP Attorney Brief` |  Exists (privileged) | Attorney-client privileged IP brief. Not indexed further. |

---

### `07_content_engine/`  Content Engine

| File | Status | Description |
|------|--------|-------------|
| (FLDA + Content Engine bootstrap) |  Exists | Content Engine bootstrap file per 2026-06-17 commit. |

---

### Root Level

| File | Status | Description |
|------|--------|-------------|
| `README.md` |  Exists | Repository README. |
| `VAULT_INDEX.md` |  NEW | This file  canonical root directory index v2.1. |
| `lattice_initiation.md` |  NEW | 5-stage boot sequence: pre-launch checklist, genesis chain (4 ANCHOR Nodes), module activation, operator onboarding, re-initiation protocol. 3 appendices. |

---

## FILES REQUIRING OPERATOR ACTION

### 1. Binary Files  Review if Text Extraction Needed
| File | Type | Action |
|------|------|--------|
| `02_epistemic_substrate/Neuralese lexicon.docx` | Binary .docx | Review; export to Markdown if text needed (canonical Markdown version now at `Neuralese_Lexicon.md`) |
| `02_epistemic_substrate/The_Lattice_Empirical_Doctrine.pdf` | Binary PDF | No action required unless text extraction needed |
| `00_governance/Sync_contract.md.pdf` | Binary PDF | No action required unless text extraction needed |

---

## FILE GENERATION LOG  2026-06-17

| # | File | Description |
|---|------|-------------|
| 1 | `00_governance/invariants/Lattice_Invariants_v1.md` | Full 6-invariant specification |
| 2 | `00_governance/operator_manual/Operator_Playbook.md` | Daily SOPs and COL reference |
| 3 | `04_system_spec/MODULE_REGISTRY.md` | All 9-module registry |
| 4 | `04_system_spec/Lattice_Node_Model.md` | Node schema and lifecycle states |
| 5 | `04_system_spec/Pulse_Cycle_Spec.md` | Full 5-stage Pulse Cycle anatomy |
| 6 | `04_system_spec/Governance_Gates.md` | G1/G2/G3 scoring and decision matrix |
| 7 | `04_system_spec/SNAPSHOT_REGISTRY.md` | 6 snapshot types and retention policy |
| 8 | `04_system_spec/Lattice_Unified_Spec_Sections_8-15.md` | Completes Sections 815 of Unified Spec |
| 9 | `04_system_spec/modules/Sentinel_Spec.md` | Rank 4  Gate enforcement and Lock protocol |
| 10 | `04_system_spec/modules/Veil_Spec.md` | Rank 5  Quarantine and promotion pipeline |
| 11 | `04_system_spec/modules/Vara_Spec.md` | Rank 6  Weak-signal scanner |
| 12 | `04_system_spec/modules/Stumpy_Spec.md` | Rank 7  Omega auditor and decay lifecycle |
| 13 | `04_system_spec/modules/Crossroad_Spec.md` | Rank 8  Path resolution |
| 14 | `04_system_spec/modules/SBM_Spec.md` | Rank 9  NeuraleseNL translation and COL grammar |
| 15 | `VAULT_INDEX.md` | Root index v2.0 (this file, now v2.1) |
| 16 | `lattice_initiation.md` | 5-stage boot sequence and initiation protocol |
| 17 | `02_epistemic_substrate/Neuralese_Lexicon.md` | Full Markdown Neuralese lexicon |
| 18 | `05_runtime/lattice_config.py` | Full dataclass config  all spec thresholds |
| 19 | `05_runtime/tests/test_lattice_config.py` | Config test suite  18 assertions |
| 20 | `05_runtime/tests/test_invariants.py` | Invariant test suite  28 assertions |
| 21 | `05_runtime/tests/conftest.py` | pytest fixtures and sys.path bootstrap |

**Total files generated:** 21

---

*Operator: LiminalJermo | Index Class: ROOT_ANCHOR | Last Updated: 2026-06-17 (v2.1)*
*This index is maintained manually. Update after any file addition, rename, or removal.*
