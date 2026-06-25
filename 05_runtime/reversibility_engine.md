# Reversibility Engine  
*Rollback and undo system for the Lattice*

The reversibility engine ensures that runtime operations can be undone unless explicitly declared irreversible.

---

## 1. Reversibility Classes

- **R0 — Fully reversible**  
- **R1 — Conditionally reversible**  
- **R2 — Irreversible (requires intent)**  

---

## 2. Rollback Rules

- rollback must preserve lineage  
- rollback must restore prior state  
- rollback must not violate invariants  
- rollback must be logged  

---

## 3. Integration

Reversibility is required by:

- AMP  
- Ω‑13  
- Vault Pipeline  
- Operator Playbook Section 7
