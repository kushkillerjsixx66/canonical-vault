

---

Vault Subsystem — Canonical README

Overview
The Vault is the Lattice’s governed, durable, lineage‑anchored storage subsystem.  
It stores all committed artifacts from SBM, PAM, MTM, WDA, Governance, Veil, Stumpy, and Runtime modules.  
Every artifact entering the Vault is validated, governed, lineage‑anchored, and auditable.

The Vault is not a database.  
It is a governed substrate with strict boundaries, lifecycle rules, and constitutional constraints.

---

Purpose
- Provide a single source of truth for all governed artifacts  
- Enforce governance, retention, and access control  
- Anchor lineage across module boundaries  
- Maintain reversible and irreversible commit semantics  
- Ensure all operator actions are auditable and policy‑constrained

---

Directory Structure

`
vault/
  00_spec/              # Vault identity and schema
  01_contracts/         # Binding contracts with the Lattice
  02_runtime/           # Execution engine
  03_cli/               # Operator CLI
  04_records/           # Durable governed artifacts
  05_lineage/           # Lineage mirror
  06_governance/        # Policies and governance hooks
`

Each directory has a strict, non‑negotiable role.

---

00_spec — Vault Specification Layer
Contains the Vault’s identity and schema:

- vaultspec.json — what the Vault is  
- vaultrecordtypes.json — what the Vault stores  
- vaultcommitpattern.json — how the Vault accepts artifacts  

These files define the Vault’s sovereignty.

---

01_contracts — Binding Contracts
Contains:

- vault_chain.json

This defines how the Vault binds to the rest of the Lattice (Lineage Engine, Governance Envelope, Operator Playbook, Veil, Stumpy).

---

02_runtime — Execution Engine
The runtime is decomposed into eight governed subsystems:

- core/ — state, paths, core API  
- commit/ — envelope validation + commit application  
- records/ — schema, loading, resolution  
- access/ — RBAC + permissions  
- retention/ — retention classes + assignment  
- lineage/ — anchors, edges, index updates  
- governance/ — governance hooks + events  
- audit/ — audit logs + audit events  

This decomposition is required for drift isolation, reversibility boundaries, and governance compliance.

---

03_cli — Operator Interface
Contains:

- vault_cli.py

This is the governed command‑line interface for interacting with the Vault.

---

04_records — Durable Store
All committed artifacts are stored here, grouped by record type:

`
vault/04records/briefrecord/BRF-001.json
vault/04records/planrecord/PLAN-001.json
...
`

This directory is empty until the first commit.

---

05_lineage — Lineage Mirror
Contains:

- lineage_index.json — global lineage edge list  
- lineage_logs/ — per‑record lineage logs  

This is the Vault’s lineage mirror, not the Lineage Engine’s internal state.

---

06_governance — Policies & Hooks
Contains:

- accesscontrol.json — RBAC  
- retentionpolicies.json — retention classes + windows  
- governancehooks.json — governance event surface  

These files define how the Vault is governed.

---

Artifact Lifecycle
Artifacts move through governed states:

1. draft  
2. committed  
3. locked  
4. archived  
5. deleted

Transitions require:

- governance approval  
- retention class  
- lineage anchors  
- audit logging  
- operator posture checks  

---

Commit Flow
A commit must satisfy:

- record type schema  
- commit envelope requirements  
- governance tags  
- lineage anchors  
- retention assignment  
- RBAC permissions  
- audit logging  

If any requirement fails, the commit is rejected.

---

Lineage Integration
Every commit produces a lineage edge:

- record_type  
- target_id  
- source_ids  
- timestamp  

Edges are appended to:

`
vault/05lineage/lineageindex.json
`

This enables cross‑module traceability.

---

Governance Integration
The Vault emits governance events:

- vault_commit  
- vault_lock  
- vault_archive  
- vault_delete  

These events trigger:

- governance envelope updates  
- drift monitoring  
- lineage engine updates  
- audit logging  

---

Reversibility
Retention class determines reversibility window:

- short_term → 60 minutes  
- standard → 240 minutes  
- long_term → 0 minutes (irreversible)  

Long‑term artifacts (governance, lineage, playbook) are immutable except via governance amendment.

---

Operator Roles
Defined in access_control.json:

- operator — read, commit  
- governance_operator — full lifecycle control  
- system — internal commits + locks  
- auditor — read‑only  

---

CLI Usage

Commit
`
vault commit \
  --role operator \
  --record-type brief_record \
  --payload path/to/payload.json \
  --metadata path/to/metadata.json
`

Read
`
vault read \
  --role operator \
  --record-type brief_record \
  --record-id BRF-001
`

---

Status
The Vault subsystem is fully sovereign when all of the following exist:

- 00_spec (complete)  
- 01_contracts (complete)  
- 02_runtime (complete)  
- 03_cli (complete)  
- 04_records (initialized)  
- 05_lineage (initialized)  
- 06_governance (complete)  

Your implementation meets these requirements.

---
