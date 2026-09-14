# CANONICAL VAULT INDEX

**Version:** 3.0  
**Class:** `ROOT_ANCHOR`  
**Status:** Canonical repository map  
**Last Updated:** 2026-09-09  
**Lineage:** `04_system_spec/Lattice_Node_Model.md` · `04_system_spec/Canonical_Vault_Self_Audit_Spec.md` · `00_governance/invariants/Lattice_Invariants_v1.md`

---

## Purpose

This index describes the current repository topology using repository-relative paths. Directory declarations provide coverage for descendants; explicit file entries identify canonical anchors and operational infrastructure.

The index is governed. The Canonical Vault Self-Audit observes divergence and reports it; it does not silently rewrite this file or promote discovered artifacts to canonical status.

## Canonical Repository Domains

| Domain | Coverage | Role |
|---|---|---|
| Governance | `00_governance/` | Constitution, invariants, contracts, governance rules, Stumpy and Veil governance substrate |
| System | `00_system/` | System coherence maps, manifests, integration and architecture artifacts |
| Sovereignty | `01_sovereignty/` | Sovereignty and architecture layer |
| Epistemic Substrate | `02_epistemic_substrate/` | Bilateral cognition, Neuralese, empirical doctrine and epistemic foundations |
| Vault Pipeline | `03_vault_pipeline/` | Vault, Veil, Vara and promotion pipeline specifications and reports |
| System Specification | `04_system_spec/` | Normative Lattice specifications, module registry, node model, gates, snapshots and self-audit specification |
| Runtime | `05_runtime/` | Python runtime, modules, execution spine, tests, Vault, Vara, Stumpy and Veil implementations |
| IP / Legal | `06_ip_legal/` | Ownership, licensing, attribution and legal constraints |
| Content Engine | `07_content_engine/` | Content contracts, workflows, Field Intel Friday and content lifecycle |
| Operator | `08_operator/` | Operator identity, mandate, attention, posture, cycle and CLI |
| Boot | `09_boot/` | Lattice boot contracts, sequence and tests |
| Simulation | `10_simulation/` | Runtime simulator, contract and tests |
| Canon | `canon/` | Canon engine, orchestration, VARA and paradox subsystems |
| Contracts | `contracts/` | Cross-module contracts |
| Vault Runtime | `vault/` | Vault specifications, runtime, lineage, governance and state |
| Versions | `versions/` | Versioned module and policy registries |
| Legacy / Compatibility | `governance` · `runtime` | Existing compatibility and legacy surfaces retained in repository state |
| Test Suite | `tests/` | Repository-wide integration, adversarial, constitutional and Stumpy tests |
| Exports | `exports/` | Export surface |

## Root / Compatibility Artifacts

The following tracked root-level and compatibility artifacts are intentionally represented explicitly because they are not covered by the primary numbered domain directories:

- `conftest.py` — repository test configuration
- `lattice_initiation.md` — initiation / orientation artifact
- `llms-full.txt` — expanded machine-readable repository context
- `llms.txt` — compact machine-readable repository context
- `governance` — legacy governance compatibility surface
- `runtime` — legacy runtime compatibility surface

## Canonical Anchors

### Governance

- `00_governance/invariants/Lattice_Invariants_v1.md`
- `00_governance/constitution/lattice_constitution.md`
- `00_governance/contracts/governance_envelope.json`
- `00_governance/governance_lineage/constitutional_remediation.lineage`

### Sovereignty / Epistemic / Pipeline

- `01_sovereignty/SICA-001.md`
- `02_epistemic_substrate/Neuralese_Lexicon.md`
- `03_vault_pipeline/Vault_Chain_Spec.md`

### System Specification

- `04_system_spec/Lattice_Unified_Spec.md`
- `04_system_spec/Lattice_Node_Model.md`
- `04_system_spec/MODULE_REGISTRY.md`
- `04_system_spec/Governance_Gates.md`
- `04_system_spec/SNAPSHOT_REGISTRY.md`
- `04_system_spec/Canonical_Vault_Self_Audit_Spec.md`

### Runtime / Audit

- `05_runtime/lattice_runtime.py`
- `05_runtime/vault.py`
- `05_runtime/vara.py`
- `05_runtime/stumpy.py`
- `05_runtime/audit/canonical_self_audit.py`
- `05_runtime/audit/test_canonical_self_audit.py`
- `05_runtime/audit/reports/2026-09-09_self_audit_v0.1.md`

### Repository Infrastructure

- `.github/workflows/canonical-self-audit.yml`
- `.devcontainer/devcontainer.json`
- `.gitignore`
- `pyproject.toml`
- `README.md`
- `INDEX.md`
- `LATTICE_GLOSSARY_SPINE.md`

## Current State Notes

The repository has materially expanded since the previous index revision dated 2026-06-17. The previous index attempted to enumerate selected files and used section-relative paths, which produced false divergence when compared against Git-tracked repository-relative paths.

Version 3.0 therefore establishes directory coverage as the primary map primitive and reserves explicit entries for canonical anchors. This keeps the index auditable without pretending that every implementation file is itself a canonical anchor.

## Audit Governance

The canonical self-audit follows:

`OBSERVE → DISTILL → CONSTRAIN → REPORT → OPERATOR DECISION → RE-AUDIT`

Automatic audit behavior is limited to enumeration, comparison, detection and reporting. It MUST NOT rewrite canonical specifications, delete artifacts, promote discoveries, guess conflicts, claim tests passed without evidence, or suppress findings.

## Remediation Record

The v0.1 audit of revision `31bebf184b84c38eee387bdc4625664c44ed4c35` produced `REQUIRES_OPERATOR` with three findings: `IDX-002`, `IDX-003`, and `HY-001`. The machine-readable report was retrieved from GitHub Actions before remediation. The audit record is preserved at `05_runtime/audit/reports/2026-09-09_self_audit_v0.1.md`.

The v0.2 re-audit of remediation revision `e36bccea1e6b7c154ed5c920d9dbffca129c09d0` reduced the remaining index divergence to six explicitly unrepresented root/compatibility artifacts: `conftest.py`, `governance`, `lattice_initiation.md`, `llms-full.txt`, `llms.txt`, and `runtime`. These are classified as repository infrastructure or legacy/compatibility surfaces and are explicitly represented above.

Tracked `.patch_backup_*` trees were removed through governed change. Their historical commits remain preserved in Git history.

---

*Operator: LiminalJermo*  
*Index Class: ROOT_ANCHOR*  
*Maintenance rule: update after governed repository topology changes; re-audit after every mutation.*
