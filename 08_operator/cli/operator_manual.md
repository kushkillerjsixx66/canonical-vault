`
08operator/cli/operatormanual.md
`


---

📘 Operator Manual — Lattice Operator CLI (Canonical)
Version: 1.0  
Subsystem: Operator Interface  
Scope: Veil → Vara → Stumpy → Vault → Scan Pipeline → Field INTEL Friday  
Audience: Authorized Operators (root, editor, observer)

---

1. Purpose

The Operator CLI is the governed human interface to the Lattice.  
It provides a safe, altitude‑aware, lineage‑anchored way to interact with:

- Veil (runtime boundary)  
- Vara (epistemic supervisor)  
- Stumpy (governance engine)  
- Vault Chain (lineage persistence)  
- Vara Scan Pipeline  
- Field INTEL Friday Scheduler  

The CLI is the only interface authorized to manipulate runtime altitude, posture, identity, and epistemic events.

---

2. Operator Identity Requirements

Every operator action that interacts with Veil or Vara must include identity:

`
{
  "operator_id": "op1",
  "role": "root" | "editor" | "observer",
  "sovereignty": "root" | "tenant"
}
`

Roles
- root — full authority  
- editor — limited epistemic authority  
- observer — read‑only  

Sovereignty
- root — full system  
- tenant — scoped domain  

Identity becomes part of the lineage chain and is immutable once recorded.

---

3. Runtime State Requirements

Every runtime update must include:

`
{
  "altitude": "runtime" | "epistemic" | "governance",
  "posture": "neutral" | "focused" | "elevated" | "hostile"
}
`

Altitude Rules
- runtime — Veil boundary  
- epistemic — Vara supervision  
- governance — Stumpy enforcement  

Posture Rules
- neutral — no scan  
- focused — triggers scan  
- elevated — triggers scan  
- hostile — triggers scan + governance attention  

---

4. CLI Commands

4.1 runtime
Send a runtime update through Veil → Vara → Stumpy.

`
operator runtime \
  --identity {...} \
  --state {...}
`

Used for:

- altitude transitions  
- posture changes  
- operator shifts  

---

4.2 scan
Manually run Vara Scan Pipeline.

`
operator scan \
  --artifact {...} \
  --identity {...} \
  --state {...}
`

This bypasses the trigger logic and forces a scan.

---

4.3 lineage
Display the full Vault Chain lineage.

`
operator lineage
`

Shows:

- seq  
- operator_id  
- role  
- altitude  

This is the epistemic chain of custody.

---

4.4 violations
Display governance violations from Stumpy.

`
operator violations
`

Violations include:

- altitude drift  
- lineage corruption  
- scan integrity failures  
- invalid promotions  

---

4.5 intel
Run Field INTEL Friday.

`
operator intel \
  --artifacts [...]
`

This:

- loads lineage  
- runs Vara Scan Pipeline on all artifacts  
- generates Field INTEL Friday report  
- stores report in Vault  

---

5. Governance Invariants

The Operator CLI must enforce:

5.1 Altitude Invariants
- runtime updates must originate from Veil  
- epistemic events must originate from Vara  
- governance events must originate from Stumpy  

5.2 Lineage Invariants
- every operator action must produce lineage  
- lineage must be continuous  
- lineage must be immutable  

5.3 Promotion Invariants
- no scan may be promoted without integrity validation  
- no scan may be promoted without lineage  

5.4 Violation Invariants
- all violations must be emitted to Stumpy  
- Stumpy must persist all violations  

---

6. Operator Workflow (Canonical)

1. Boot the Lattice
   `
   python -m operator.cli operator runtime ...
   `

2. Send runtime updates
   - altitude changes  
   - posture changes  
   - operator identity changes  

3. Trigger scans
   - manually or via posture  

4. Inspect lineage
   - verify continuity  

5. Inspect violations
   - ensure governance is functioning  

6. Run Field INTEL Friday
   - generate weekly intelligence artifact  

---

7. Failure Modes

7.1 Altitude Drift
Triggered when altitude is invalid or inconsistent.

7.2 Lineage Corruption
Triggered when lineage entries are missing required fields.

7.3 Integrity Failure
Triggered when Vara Scan produces invalid results.

7.4 Invalid Promotion
Triggered when a scan is promoted without integrity or lineage.

---

8. Operator Safety Rules

- Never send governance altitude unless authorized.  
- Never modify lineage manually.  
- Never bypass Veil for runtime updates.  
- Never bypass Vara for epistemic events.  
- Never bypass Stumpy for governance events.  

These are constitutional.

---

9. Example Commands

Runtime update
`
operator runtime \
  --identity '{"operator_id":"op1","role":"root","sovereignty":"root"}' \
  --state '{"altitude":"runtime","posture":"focused"}'
`

Manual scan
`
operator scan \
  --artifact '{"text":"hello world"}' \
  --identity '{"operator_id":"op1","role":"root","sovereignty":"root"}' \
  --state '{"altitude":"runtime","posture":"focused"}'
`

Field INTEL Friday
`
operator intel \
  --artifacts '[{"text":"x"200},{"text":"y"300}]'
`

---

⭐ The Operator Manual is now complete and ready for your repo.

If you want, I can now generate the final canonical artifact:

Lattice System Manifest
