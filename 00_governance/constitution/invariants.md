

---

Lattice Invariants
Non‑negotiable constraints of the system

These invariants are absolute.  
They cannot be violated by any module, runtime, or operator action without triggering a governance fault.

---

1. Lineage Is Mandatory

Every meaningful action must emit lineage.

- All writes (commits, updates, promotions)  
- All transformations (pipeline steps, module passes)  
- All governance changes (amendments, protocol updates)

If it changes reality, it must change lineage.

---

2. Canon Is Immutable

Once an artifact is canonized:

- It cannot be edited.  
- It cannot be overwritten.  
- It can only be:
  - referenced  
  - superseded  
  - archived (with lineage)

Canon is append‑only truth, not a workspace.

---

3. Intent Must Be Explicit

No action may occur without explicit intent.

- No silent side effects  
- No hidden writes  
- No implicit destructive operations  

Intent must be:

- declared  
- logged  
- traceable to an operator or process identity  

---

4. Boundaries Are Real

Modules and subsystems must respect their declared boundaries.

- No cross‑cutting mutation of foreign domains  
- No direct access to internal state of other modules  
- All cross‑module interaction must go through:
  - contracts  
  - protocols  
  - governed interfaces  

If a boundary is crossed, it must be declared and governed.

---

5. Drift Must Be Detectable

All systems drift.  
The Lattice must see it.

- Each module must declare:
  - its constraint classes  
  - its drift domains  
- Drift must be:
  - measurable  
  - logged  
  - recoverable (when possible)

Undetected drift is a governance failure.

---

6. Reversibility Is Preferred

When possible, actions should be reversible.

- Use:
  - non‑destructive writes  
  - versioned artifacts  
  - reversible transforms  
- When irreversibility is required:
  - canonize  
  - log rationale in lineage  
  - mark as irreversible in metadata  

Irreversible actions are exceptional, not default.

---

7. Governance Supersedes Runtime

Runtime behavior is subordinate to governance.

- If runtime conflicts with governance:
  - governance wins  
  - runtime halts or degrades gracefully  
- Governance rules:
  - cannot be silently bypassed  
  - must be explicitly amended  

No optimization is allowed to violate governance.

---

8. Operator Identity Is Stable

The sovereign operator identity:

- opID: JRM‑01  
- SIG: JRM‑01 @liminaljermo

is:

- stable  
- non‑spoofable  
- non‑mutable via runtime  

Any identity‑related change must occur via constitutional amendment.

---

9. Visibility Is Governed

Access to information is not arbitrary.

- The Veil governs:
  - what is visible  
  - at what altitude  
  - under what conditions  
- Redaction:
  - must not destroy underlying truth  
  - must be lineage‑tracked  

Opacity is a governance tool, not a hack.

---

10. Archive Is Not Deletion

Moving something to 07_archive/:

- does not erase it  
- does not break lineage  
- does not remove responsibility  

Archive is cold storage, not oblivion.

---

