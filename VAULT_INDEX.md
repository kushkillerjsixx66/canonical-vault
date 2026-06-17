# VAULT INDEX
**Version:** 2.0 (Post-Population)
**Author:** LiminalJermo
**Date:** 2026-06-17
**Status:** Canonical — reflects full repo state after Canonical Lattice spec population
**Lineage:** Lattice_Cognitive_Constitution_v1.1.md · Lattice_Unified_Spec.md · Lattice_Invariants_v1.md

---

## CORE INVARIANTS (I·COH through VI·SIG)

| Code | Name | Definition | Defined In |
|------|------|-----------|-----------|
| I·COH | Coherence Primacy | All output must be non-contradictory with active Vault content | `00_governance/invariants/Lattice_Invariants_v1.md` |
| II·REV | Reversibility | Vault is append-only; no destructive edits; snapshot before ANCHOR writes | `00_governance/invariants/Lattice_Invariants_v1.md` |
| III·ATT | Attention Budget | Attention cost is finite; every activation has a cost; G2 enforces the budget | `00_governance/invariants/Lattice_Invariants_v1.md` |
| IV·SIL | Silence Mandate | System outputs null rather than fabricate; silence is valid and honest | `00_governance/invariants/Lattice_Invariants_v1.md` |
| V·DEC | Decay Mandate | Unreferenced content must decay and eventually be pruned | `00_governance/invariants/Lattice_Invariants_v1.md` |
| VI·SIG | Weak Signal Parity | Weak signals are preserved in Veil and eligible for Vault promotion | `00_governance/invariants/Lattice_Invariants_v1.md` |

---

## DIRECTORY MAP

### `00_governance/` — Constitutional and Governance Documents

| File | Status | Description |
|------|--------|-------------|
| `constitution/Lattice_Cognitive_Constitution_v1.1.md` | Exists | Primary constitutional document. 8 Axioms, 6 Principles, Module Authority Table (9 ranks), Amendment Protocol. Ratified 2026-05-22. |
| `invariants/Lattice_Invariants_v1.md` | NEW | Full 6-invariant specification (I·COH-VI·SIG) with enforcement rules, failure modes, enforcement matrix, and amendment protocol. |
| `operator_manual/Operator_Manual_v0.2.md` | Exists | MVL 2.0 framework. Module Index (IDE/CCE/CFC/MTM/PAM/EGG/WDA). Neuralese Protocol (Appendix C). |
| `operator_manual/Operator_Playbook.md` | NEW | Practical daily operator SOPs. Morning routine, Pre-work snapshot, 7 SOPs, Amendment Protocol, Neuralese Quick Reference, COL Quick Reference (16 commands), Runbook Index (RB-001-RB-008). |
| `Sync_contract.md.pdf` | Exists (binary) | Sync contract document. Binary PDF — not indexable. |
| `playbook/` | Exists (dir) | Legacy playbook directory. See `Operator_Playbook.md` for current version. |

---

### `01_sovereignty/` — Sovereignty and Architecture

| File | Status | Description |
|------|--------|-------------|
| `SICA-001.md` | Exists | Substrate-Independent Cognitive Architecture spec. 6 components (Lattice, Vara, Stumpy, Neuralese, COL, 4D Framework). 3 failure classes. 4-phase transmission status. |

---

### `02_epistemic_substrate/` — Epistemic Foundations

| File | Status | Description |
|------|--------|-------------|
| `Bilateral_Runtime_Patterns.md` | Exists | Runtime pattern documentation for bilateral cognition. |
| `Bilateralism_and_Truth_Routing.md` | Exists | Truth routing architecture in bilateral system. |
| `Neuralese lexicon.docx` | Exists (binary) | Neuralese vocabulary reference. Binary .docx — not indexable via raw. See Operator_Manual_v0.2 Appendix C for protocol definition. |
| `The_Lattice_Empirical_Doctrine.pdf` | Exists (binary) | Empirical doctrine document. Binary PDF — not indexable. |

---

### `03_vault_pipeline/` — Vault and Pipeline Operations

| File | Status | Description |
|------|--------|-------------|
| `Vault_Chain_Spec.md` | Exists | Chain specification for Vault Node linkage. |
| `Orchestration_Contract_Veil_Pipeline_Vault.md` | Exists | Veil-to-Vault orchestration contract. Promotion pipeline specification. |
| `VARA-COGOV-001_Vara-Scan_Distilled_Briefing.md` | Exists | Vara Cognitive Governance scan briefing report. |
| `VARA-GAP-001_OWASP_ASI_Top10_Gap_Analysis.md` | Exists | OWASP ASI Top 10 gap analysis from Vara scan. |
| `VaraScan_Full_Operator_Report_2026-06-04.md` | Exists | Full Vara scan operator report dated 2026-06-04. |
| `Vara_Vault_Index.md` | Exists | Vara-specific vault index. |

---

### `04_system_spec/` — System Specifications (Core Spec Layer)

#### Root Level

| File | Status | Description |
|------|--------|-------------|
| `Lattice_Unified_Spec.md` | Exists | Root anchor specification document. Sections 0-7 complete. Sections 8-15 were stubs. |
| `Lattice_Unified_Spec_Sections_8-15.md` | NEW | Completes the Unified Spec. Section 8 Module Interaction Protocol, Section 9 Neuralese Full Grammar, Section 10 Error Taxonomy, Section 11 Snapshot Protocol, Section 12 Operator Interface Spec, Section 13 Runtime Deployment, Section 14 Amendment Procedures, Section 15 Appendices/Glossary. |
| `MODULE_REGISTRY.md` | NEW | All 9 modules catalogued with full field tables: ID, Rank, File, Role, Interfaces, Invariant Bindings, Activation Condition, Failure Mode, Owner. |
| `Lattice_Node_Model.md` | NEW | Complete Node schema (14 fields), 4 lifecycle states with transition rules, classification rules (ANCHOR/STANDARD/VARA_PROMOTED/OPERATOR_DIRECTIVE/AUDIT_RECORD). |
| `Pulse_Cycle_Spec.md` | NEW | Full 5-stage cycle anatomy (PULSE, ACTIVATION, EVALUATION, DECAY, SILENCE) with module responsibilities, inputs/outputs, invariant checkpoint

#### `04_system_spec/modules/` — Per-Module Specifications

| File | Status | Module | Rank | Python File |
|------|--------|--------|------|-------------|
| `Sentinel_Spec.md` | NEW | Sentinel | 4 | `sentinel.py` |
| `Veil_Spec.md` | NEW | Veil | 5 | `veil.py` |
| `Vara_Spec.md` | NEW | Vara | 6 | `vara.py` |
| `Stumpy_Spec.md` | NEW | Stumpy | 7 | `stumpy.py` |
| `Crossroad_Spec.md` | NEW | Crossroad | 8 | `rift.py` |
| `SBM_Spec.md` | NEW | SBM / Echo | 9 | `echo.py` |

---

### `05_runtime/` — Python Runtime Implementation

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

#### `05_runtime/` Subdirectories

| Directory | Status | Description |
|-----------|--------|-------------|
| `CCE/` | PENDING UNZIP | Cognitive Context Engine — zip archive present; requires manual extraction |
| `CFC/` | PENDING UNZIP | Constraint and Flow Controller — zip archive present; requires manual extraction |
| `IDE/` | Present | Integrated Development Environment module |
| `LMES/` | PENDING UNZIP | Lattice Module Execution System — zip archive present; requires manual extraction |
| `Lmes/` | Present | Lattice Module Execution System (alternate) |
| `lattice-app/` | Present | Lattice application layer |
| `lattice_cli_project/` | Present | CLI project files |
| `lattice_runtime_cli/` | Present | Runtime CLI interface |

**ACTION REQUIRED:** Unzip archives before CCE, CFC, LMES are functional:
- `CCE/*.zip`, `CFC/*.zip`, `LMES/*.zip`

---

### `06_ip_legal/` — Intellectual Property and Legal

| File | Status | Description |
|------|--------|-------------|
| `IP Attorney Brief` | Exists (privileged) | Attorney-client privileged IP brief. Not indexed further. |

---

### `07_content_engine/` — Content Engine

| File | Status | Description |
|------|--------|-------------|
| (FLDA + Content Engine bootstrap) | Exists | Content Engine bootstrap file per 2026-06-17 commit. |

---

## FILES REQUIRING OPERATOR ACTION

### 1. Empty / Stub Files
| File | Issue | Action |
|------|-------|--------|
| `lattice_initiation.md` | Flagged as empty in prior index | Operator must populate with initiation protocol or confirm removal |

### 2. Binary Files
| File | Type | Action |
|------|------|--------|
| `02_epistemic_substrate/Neuralese lexicon.docx` | Binary .docx | Review; export to Markdown if text needed |
| `02_epistemic_substrate/The_Lattice_Empirical_Doctrine.pdf` | Binary PDF | No action required unless text extraction needed |
| `00_governance/Sync_contract.md.pdf` | Binary PDF | No action required unless text extraction needed |

### 3. Pending Unzip Directories
| Directory | Action |
|-----------|--------|
| `05_runtime/CCE/` | `cd 05_runtime && unzip CCE/*.zip -d CCE/` |
| `05_runtime/CFC/` | `cd 05_runtime && unzip CFC/*.zip -d CFC/` |
| `05_runtime/LMES/` | `cd 05_runtime && unzip LMES/*.zip -d LMES/` |

---

## FILE GENERATION LOG — 2026-06-17

| # | File | Size | Description |
|---|------|------|-------------|
| 1 | `00_governance/invariants/Lattice_Invariants_v1.md` | 7,147 bytes | Full 6-invariant specification |
| 2 | `04_system_spec/MODULE_REGISTRY.md` | 10,809 bytes | All 9-module registry |
| 3 | `04_system_spec/Lattice_Node_Model.md` | 8,523 bytes | Node schema and lifecycle states |
| 4 | `04_system_spec/Pulse_Cycle_Spec.md` | 9,622 bytes | Full 5-stage Pulse Cycle anatomy |
| 5 | `04_system_spec/Governance_Gates.md` | 8,616 bytes | G1/G2/G3 scoring and decision matrix |
| 6 | `04_system_spec/SNAPSHOT_REGISTRY.md` | 5,187 bytes | 6 snapshot types and retention policy |
| 7 | `04_system_spec/modules/Sentinel_Spec.md` | 7,427 bytes | Rank 4 — Gate enforcement and Lock protocol |
| 8 | `04_system_spec/modules/Veil_Spec.md` | 6,643 bytes | Rank 5 — Quarantine and promotion pipeline |
| 9 | `04_system_spec/modules/Stumpy_Spec.md` | 7,835 bytes | Rank 7 — Omega auditor and decay lifecycle |
| 10 | `04_system_spec/modules/Vara_Spec.md` | 7,894 bytes | Rank 6 — Weak-signal scanner |
| 11 | `04_system_spec/modules/Crossroad_Spec.md` | 7,270 bytes | Rank 8 — Path resolution |
| 12 | `04_system_spec/modules/SBM_Spec.md` | 9,348 bytes | Rank 9 — Neuralese-NL translation and COL grammar |
| 13 | `00_governance/operator_manual/Operator_Playbook.md` | 11,194 bytes | Daily SOPs and COL reference |
| 14 | `04_system_spec/Lattice_Unified_Spec_Sections_8-15.md` | 26,748 bytes | Completes Sections 8-15 of Unified Spec |
| 15 | `VAULT_INDEX.md` | (this file) | Updated root index v2.0 |

**Total files generated:** 15 | **Total bytes added:** ~124,263

---

*Operator: LiminalJermo | Index Class: ROOT_ANCHOR | Last Updated: 2026-06-17*
*This index is maintained manually. Update after any file addition, rename, or removal.*s, failure behavior per stage. |
| `Governance_Gates.md` | NEW | G1/G2/G3 complete: scoring (G1: 0.0-1.0, threshold 0.75), G2 attention cost formula, G2 60-second operator override window, G3 chain validation, decision matrix, all Sentinel decision codes. |
| `SNAPSHOT_REGISTRY.md` | NEW | 6 snapshot types (AUTO_CYCLE, OPERATOR_MANUAL, PRE_AMENDMENT, VARA_PROMOTION, SENTINEL_INCIDENT, DECAY_PURGE). Snapshot schema, procedures, restore semantics, retention/decay policy, SHA-256 integrity. |
