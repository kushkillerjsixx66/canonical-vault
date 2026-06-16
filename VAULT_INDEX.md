# VAULT_INDEX — Canonical Vault Registry

**Operator:** LiminalJermo
**Repo:** canonical-vault
**Status:** Active
**Last Updated:** 2026-06-15

---

## Vault Invariants

| ID | Invariant | Definition |
|---|---|---|
| I·COH | Coherence | Every artifact must increase or preserve system coherence. Incoherent artifacts are not stored. |
| II·REV | Reversibility | All vault entries are append-only. No silent overwrites. Deprecation links replace deletion. |
| III·ATT | Attention | Every artifact must justify its attention cost. Low-signal artifacts are pruned. |
| IV·SIL | Silence | The vault does not speak unless queried. Noise is a vault failure mode. |
| V·DEC | Decay | Artifacts that are not actively referenced decay toward archival status. Persistence is not assumed. |
| VI·SIG | Signal | Weak signals are stored at full standing. Magnitude is not assessed at intake. |

---

## Directory Index

### 00_governance/
| File | Status | Date | Notes |
|---|---|---|---|
| `constitution/Lattice_Cognitive_Constitution_v1.1.md` | CANON | 2026-05-22 | Supreme governing instrument. Fixed core: Preamble. |
| `constitution/VARA-CONST-P0_Constitutional_Clauses.md` | CANON | 2026-06-02 | P0 clauses C01, C03, C06 |
| `operator_manual/Operator_Manual_v0.2.md` | STABLE | 2026-05-22 | MVL 2.0. Anchor block for Operator Manual chain. |
| `playbook/Operator_Playbook_Omega-12.pdf` | CANON | 2026-05-29 | Ω-12 Principle of Emergent Sequence |

### 01_sovereignty/
| File | Status | Date | Notes |
|---|---|---|---|
| `SICA-001.md` | PRE-TRANSMISSION | 2026-05-31 | Primary sovereignty doc. Controlled distribution. |

### 02_epistemic_substrate/
| File | Status | Date | Notes |
|---|---|---|---|
| `Bilateralism_and_Truth_Routing.md` | CANON | 2026-06-14 | Most recent doc. Triple-gate architecture. |
| `Bilateral_Runtime_Patterns.md` | CANON | 2026-06-08 | Eight canonical runtime patterns. |
| `Neuralese_Lexicon.docx` | ACTIVE DEVELOPMENT | 2026-05-10 | 26-letter lexicon. Binary: Drive source. |
| `Empirical_Doctrine.pdf` | CANON | 2026-01-30 | Binary: Drive source. |

### 03_vault_pipeline/
| File | Status | Date | Notes |
|---|---|---|---|
| `Vault_Chain_Spec.md` | CANON | 2026-06-08 | Storage, versioning, retrieval architecture. |
| `Orchestration_Contract_Veil_Pipeline_Vault.md` | CANON | 2026-06-05 | Ω-11. Five-stage orchestration loop. |
| `Vara_Vault_Index.md` | REFERENCE | 2026-05-18 | Sourced from Drive. |
| `VARA-COGOV-001_Vara-Scan_Distilled_Briefing.md` | REFERENCE | 2026-05-24 | Sourced from Drive. |
| `VARA-GAP-001_OWASP_ASI_Top10_Gap_Analysis.docx` | REFERENCE | 2026-06-02 | Binary. Sourced from Drive. |
| `VaraScan_Full_Operator_Report_2026-06-04.md` | REFERENCE | 2026-06-04 | Sourced from Drive. |

### 04_system_spec/
| File | Status | Date | Notes |
|---|---|---|---|
| `Lattice_Unified_Spec.md` | AUTHORITATIVE | 2026-06-11 | Root anchor. Supersedes all prior individual specs. |
| `Lattice_System_Architecture.md` | REFERENCE | 2026-05-27 | Sourced from Drive. |
| `Canon_Vara_Scan_Operator_Architecture_v0.1.0.md` | REFERENCE | 2026-06-01 | Sourced from Drive. |
| `Unified_Document_Briefing_Canonical.md` | REFERENCE | 2026-06-06 | Sourced from Drive. |
| `lattice_initiation.md` | REFERENCE | 2026-06-13 | Sourced from Drive. Empty on read — pending re-pull. |
| `appendices/Lattice_Adversarial_Audit_Report.pdf` | REFERENCE | 2026-05-19 | Binary. |
| `appendices/Lattice_Governance_Architecture.pdf` | REFERENCE | 2026-05-15 | Binary. |
| `appendices/Technical_Continuum_v2.pdf` | SUPERSEDED | 2026-04-07 | Absorbed into Unified Spec. |
| `appendices/Portability_Spec.pdf` | SUPERSEDED | 2026-05-19 | Absorbed into Unified Spec. |
| `appendices/System_Appendix.pdf` | SUPERSEDED | 2026-05-19 | Absorbed into Unified Spec. |
| `appendices/Red_Team_Appendix.pdf` | SUPERSEDED | 2026-05-19 | Absorbed into Unified Spec. |
| `appendices/Flow_State_Spec.pdf` | SUPERSEDED | 2026-05-19 | Absorbed into Unified Spec. |
| `appendices/Usage_Playbook.pdf` | SUPERSEDED | 2026-05-19 | Absorbed into Unified Spec. |

### 05_runtime/
| File | Status | Date | Notes |
|---|---|---|---|
| `lattice_runtime.py` | STABLE | 2026-05-19 | Core: Vault, Echo, Sentinel, Pulse, Threshold, Veil, Rift, Vara, Stumpy, Agent, Lattice, CommandParser |
| `lattice_cli_project/` | PENDING UNZIP | 2026-05-19 | Sourced from Drive zip. |
| `lattice_runtime_cli/` | PENDING UNZIP | 2026-05-19 | Sourced from Drive zip. |
| `LMES_v1.1/` | PENDING UNZIP | 2026-05-19 | Lattice Memory/Module Execution System v1.1 |

### 06_ip_legal/
| File | Status | Date | Notes |
|---|---|---|---|
| `IP_Attorney_Brief.md` | CONFIDENTIAL | 2026-06-11 | Attorney-client privileged. FTO + provisional patent strategy. |
| `Case_Law_and_Prevent_Registry.md` | REFERENCE | 2026-06-11 | Sourced from Drive. |

### 07_content_engine/
| File | Status | Date | Notes |
|---|---|---|---|
| `Threshold_Tuesday_Operator_Edition.md` | REFERENCE | 2026-06-09 | Sourced from Drive. |

### exports/
| File | Notes |
|---|---|
| `SICA-001.pdf` | PDF export of `01_sovereignty/SICA-001.md` |

---

## Pending Actions

- [ ] Pull and unzip `lattice_cli_project.zip` → `05_runtime/lattice_cli_project/`
- [ ] Pull and unzip `lattice_runtime_cli.zip` → `05_runtime/lattice_runtime_cli/`
- [ ] Pull and unzip `LMES_v1.1.zip` → `05_runtime/LMES_v1.1/`
- [ ] Pull binary files from Drive: Neuralese_Lexicon.docx, Empirical_Doctrine.pdf, all appendices
- [ ] Re-pull `lattice_initiation` (empty on read)
- [ ] Pull remaining Drive docs: Vara_Vault_Index, VARA-COGOV-001, VaraScan Report, Case Law doc, Threshold Tuesday
- [ ] Reconcile runtime zips against `lattice_runtime.py` — consolidate into single source
- [ ] Add VARA-CONST-P0 once pulled from Drive

---

## Lineage Anchor

All artifacts in this vault trace lineage to:
- `00_governance/constitution/Lattice_Cognitive_Constitution_v1.1.md` (January 20, 2026 — primary priority date)
- `00_governance/operator_manual/Operator_Manual_v0.2.md` (anchor block)
- `03_vault_pipeline/Vault_Chain_Spec.md` (storage protocol)
