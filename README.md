# canonical-vault

**Operator:** LiminalJermo
**Classification:** Canonical Lattice Repository
**Status:** Active

---

The canonical source of truth for the Lattice — a governance-first cognitive operating system.

This repo is governed by the same invariants as every Lattice artifact: Coherence, Reversibility, Attention, Silence, Decay, Signal (I·COH through VI·SIG). See `VAULT_INDEX.md` for the full registry.

---

## Structure

```
canonical-vault/
├── VAULT_INDEX.md              ← master registry + vault invariants
├── 00_governance/              ← Constitution, Operator Manual, Playbook
├── 01_sovereignty/             ← SICA-001
├── 02_epistemic_substrate/     ← Neuralese Lexicon, Empirical Doctrine, Bilateralism
├── 03_vault_pipeline/          ← Vault Chain Spec, Orchestration Contract, VaraScans
├── 04_system_spec/             ← Unified Spec (root anchor), Architecture, Appendices
├── 05_runtime/                 ← Source code: lattice_runtime.py, CLI, LMES
├── 06_ip_legal/                ← IP Brief, Case Law (attorney-client privileged)
├── 07_content_engine/          ← Threshold Tuesday and content artifacts
└── exports/                    ← PDF/docx exports of primary .md sources
```

---

## Governance

The authoritative document is `04_system_spec/Lattice_Unified_Spec.md`. Where conflicts exist between any artifact and the Unified Spec, the Unified Spec governs.

The Cognitive Constitution (`00_governance/constitution/Lattice_Cognitive_Constitution_v1.1.md`) is the supreme governing instrument. No artifact in this repo may contradict it.

**Amendment protocol:** All changes must be versioned, diffable, and roll-backable. No silent edits. See Constitution Part V for full protocol.

---

## Runtime

```bash
python 05_runtime/lattice_runtime.py
```

Commands:
- `<Signal:Send> message`
- `<Vault:Retrieve>`
- `<Vault:Export>`
- `<Echo:Trace>`
- `<Stumpy:Audit>`
- `→ value` (measurement operator)
- `‰ name` (operator identity)
- `exit`

---

*"The Lattice does not optimize for comfort. It optimizes for truth."*
# canonical-vault-
