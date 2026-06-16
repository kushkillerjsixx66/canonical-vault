# Vault Chain Specification — Canonical Document

**Status:** CANON
**Classification:** Vault / Pipeline Spec

> Concise takeaway: This is the official, governed, lineage-anchored, drift-free specification of the Vault Chain — how governed artifacts are stored, versioned, and made reversible without ever losing lineage.

---

## 0. Purpose

The Vault Chain defines the storage, versioning, and retrieval architecture for all governed artifacts in the Lattice (documents, protocols, doctrines, frames, logs). It ensures every artifact is traceable, reversible, auditable, and never detached from governance.

---

## 1. Vault Chain Components

- **Vault Node** — a single stored artifact + its metadata
- **Chain Link** — the relationship between two Vault Nodes
- **Anchor Block** — the first canonical node in a chain (e.g., v0.2)
- **Governance Header** — invariants + lineage for each node

Together, these form a governed, append-only chain of artifacts.

---

## 2. Vault Node Structure

Each Vault Node contains:

- **Artifact ID** — unique identifier
- **Artifact Type** — Manual, Protocol, Doctrine, Pattern, Log, etc.
- **Version Tag** — e.g., v0.2, v0.2.1, v0.3-draft
- **Lineage Pointer** — upstream governance chain reference
- **Ω-Index References** — which Ω-designations it touches
- **Governance Header** — invariants, constraints, scope
- **Payload Hash** — integrity check of the artifact body
- **Timestamp + Operator ID** — who sealed it, when

> **Invariant:** No node exists without a Governance Header and Lineage Pointer.

---

## 3. Chain Link Semantics

Links define how nodes relate:

- **Successor Link** — v0.2 → v0.3 (canonical evolution)
- **Branch Link** — v0.2 → v0.2-experimental (non-canonical branch)
- **Merge Link** — two branches → new canonical node
- **Deprecation Link** — marks a node as superseded but not deleted

> **Invariant:** Links are append-only; history is never overwritten.

---

## 4. Anchor Blocks

Anchor Blocks are the first canonical nodes in a chain:

- Operator Manual v0.2 (anchor for Operator Manual chain)
- Field Constitution (anchor for Field chain)
- Governance Envelope (anchor for Envelope chain)

All future versions must trace back to an Anchor Block via unbroken links.

---

## 5. Governance Header

Each node's Governance Header includes:

- **Active Governance Pillars** — which were in force at sealing
- **Applicable Doctrines** — e.g., Ω-12, Ω-13, Ω-14
- **Boundary Scope** — where this artifact may be applied
- **Drift Tolerance** — usually zero for canonical artifacts
- **Reversibility Status** — reversible / partially reversible / irreversible

> **Invariant:** No artifact is valid without a Governance Header.

---

## 6. Vault Operations

| Operation | Description |
|---|---|
| **Seal** | Create a new Vault Node with full header + hash |
| **Link** | Connect nodes via Successor/Branch/Merge/Deprecation links |
| **Resolve** | Compute the current canonical node for a given chain |
| **Revert** | Move runtime reference back to a prior node (reversible only) |
| **Audit** | Traverse the chain to inspect lineage, changes, and governance state |

> **Invariant:** All operations are logged as Vault Events.

---

## 7. Runtime Interaction

At runtime, the system:

- Resolves the current canonical node for each active chain
- Verifies payload hash before use
- Checks Governance Header against Governance Envelope
- Refuses to load artifacts with broken lineage or missing headers
- Logs every load/use as a Vault Access Event

No runtime can "silently drift" away from canonical artifacts.

---

## 8. Failure Modes

**Critical failures include:**

| Failure | Description |
|---|---|
| Hash Mismatch | Payload tampered or corrupted |
| Broken Lineage | Missing or invalid Chain Link |
| Header Inconsistency | Governance Header conflicts with Envelope |
| Anchor Loss | Anchor Block missing or unreadable |

**Response:**
- Immediate Vault Halt for affected chain
- Runtime blocked from using that artifact
- Governance review required before re-enablement

---

## 9. Lineage Anchor

The Vault Chain is lineage-bound to:

- Cognitive Constitution
- Governance Envelope
- Operator Manual v0.2
- Ω-12, Ω-13, Ω-14 (for bilateral and runtime-relevant artifacts)

No Vault Node may be sealed without a valid lineage path into these structures.

---

## Canonical Summary

The Vault Chain is the Lattice's governed memory system — an append-only, lineage-anchored chain of artifacts with strict headers, links, and invariants. It guarantees that every document, protocol, and doctrine is traceable, reversible (when allowed), auditable, and never detached from governance.
