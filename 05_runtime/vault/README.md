🜁 Veil Commands (Visibility Control Layer)
The Vault includes a governed visibility system called The Veil.  
It allows the operator to control how much of an artifact is revealed during review, retrieval, or inspection.

The Veil has three levels:

- clear — no redaction  
- partial — reveals the first 80 characters  
- full — total redaction  

Each veil action is logged to lineage with your operator signature:

`
SIG: JRM‑01 @liminaljermo
`

---

🧩 CLI Usage

Inside the Vault (after crossing the threshold), you may invoke:

`
veil <artifact> <clear|partial|full>
`

Examples

Partial veil
`
> veil artifact.txt partial
`

Output:
`
[VEIL OUTPUT]
This is the first 80 characters of the artifact…
...[VEILED — PARTIAL]...
`

Full veil
`
> veil artifact.txt full
`

Output:
`
[VEIL OUTPUT]
[REDACTED — VEIL‑2]
`

Clear veil
`
> veil artifact.txt clear
`

Output:
`
[VEIL OUTPUT]
<full artifact content>
`

---

📜 Lineage Entries for Veil Actions

Every veil operation is recorded in the artifact’s lineage:

`
2026‑06‑24T21:12:44Z — veil-partial — SIG: JRM‑01 @liminaljermo
2026‑06‑24T21:13:02Z — veil-full — SIG: JRM‑01 @liminaljermo
2026‑06‑24T21:13:27Z — veil-clear — SIG: JRM‑01 @liminaljermo
`

This ensures a visibility audit trail for all redaction events.

---

📁 Veil Output Storage

Veil outputs are ephemeral and stored in:

`
vault/veil/
`

These files:

- are temporary  
- are not canonized  
- are not committed  
- do not replace the original artifact  
- exist only for operator inspection  

The original artifact remains untouched.

---

🔐 Governance Notes

- Veil commands are only available after threshold crossing  
- Veil actions never modify the underlying artifact  
- Veil lineage is attached to the original artifact, not the veil output  
- Full veil (veil-full) is treated as a sensitive visibility event  
- Clear veil (veil-clear) is logged to prevent silent exposure  

---

If you want, I can now update:

- the README’s Action Flow section to include Veil  
- the Constitution appendix with Veil governance rules  
- the Review Engine to auto‑veil sensitive lineage  

Which one do you want next?
---

📁 VAULT SUBSYSTEM — README.md
A governed cognitive chamber within the Lattice Runtime

---

🧩 Overview
The Vault is a governed, ritual‑gated, lineage‑anchored subsystem within the Lattice runtime.  
It is not a folder.  
It is a perimetered cognitive chamber designed for:

- Commit — adding new artifacts  
- Retrieve — pulling artifacts by query  
- Review — inspecting lineage and history  
- Canonize — promoting artifacts to immutable status  

The Vault enforces intent, identity, and clarity before granting access.

---

🔐 Entry Protocol (Ritual)
Access to the Vault requires passing through a four‑stage ritual:

1. Perimeter Acknowledgment  
   - Operator: “I am at the perimeter.”

2. Intent Declaration  
   - Operator: “Intent: Commit.” (or Retrieve/Review/Canonize)

3. Identity Assertion  
   - Operator: “opID: JRM‑01.”

4. Threshold Crossing  
   - Operator: “I cross with clarity.”

Only then does the Vault open.

The ritual is implemented in vault_cli.py.

---

🏛️ Subsystem Architecture

`
vault/
│
├── vault_cli.py          # Ritualized entry point (CLI)
├── vault_core.py         # Orchestrator for all Vault actions
├── vault_log.py          # Central logging layer
│
├── commit_engine.py      # Handles new artifact commits
├── retrieve_engine.py    # Query + retrieval engine
├── review_engine.py      # Lineage inspection
├── canon_engine.py       # Canonization (immutable promotion)
├── veil_engine.py        # Redaction + controlled opacity
├── lineage_engine.py     # Lineage tracking + retrieval
│
├── commits/              # Mutable artifacts
├── canon/                # Immutable artifacts
├── lineage/              # Lineage chains (*.lineage)
├── veil/                 # Redacted outputs
└── logs/                 # vault.log
`

Each engine is isolated, governed, and single‑responsibility.

---

📜 Governance Principles

The Vault operates under six invariants:

1. Intent is mandatory  
   No action occurs without explicit operator intent.

2. Identity is verified  
   Only authenticated operators may cross the threshold.

3. Clarity is required  
   The clarity phrase is non‑optional and non‑fuzzy.

4. Lineage is absolute  
   Every action is logged. Nothing is untracked.

5. Canon is immutable  
   Once canonized, an artifact cannot be altered.

6. Veil is reversible  
   Redaction hides content, but never destroys it.

---

📂 Storage Layers

commits/
Mutable artifacts.  
Created via commit_engine.py.

canon/
Immutable artifacts.  
Promoted via canon_engine.py.

lineage/
Lineage chains for every artifact.  
Managed by lineage_engine.py.

veil/
Redacted or partially veiled outputs.

logs/
Centralized Vault activity log.

---

⚙️ Action Flow

Commit
1. Operator enters Vault  
2. Provides content  
3. commit_engine.py writes artifact  
4. lineage_engine.py logs lineage  
5. vault_log.py records event  

Retrieve
- Query runs across commits + canon  
- Returns first matching artifact  

Review
- Displays lineage chain for any artifact  

Canonize
- Copies artifact from commits → canon  
- Logs irreversible promotion  

---

🧪 Example Usage (CLI)

`
$ python3 vault_cli.py
VAULT PERIMETER
Awaiting acknowledgment.
> I am at the perimeter.
PERIMETER RECOGNIZED
State your intent.
> Intent: Commit.
INTENT LOGGED
Identify yourself.
> opID: JRM-01.
IDENTITY VERIFIED
Approach the threshold.
> I cross with clarity.
THE VAULT IS OPEN
State your first action.
`

---

🧭 Purpose Within the Lattice

The Vault is the memory substrate of the Lattice:

- The Kernel (IDE/CCE/CFC) writes to it  
- The Operator Playbook references it  
- The Constitution governs it  
- The Narrative Layer draws from it  

It is the single source of truth for your cognitive artifacts.

---

📌 Status

Version: Vault Subsystem v1.0  
State: Active  
Governance: Fully aligned with Lattice Constitution & Operator Playbook  
Operator: JRM‑01  
Handle: @liminaljermo  
Signature: SIG: JRM‑01 @liminaljermo

---

If you want, I can now update:

- vaultcli.py with JRM‑01 hardcoded  
- lineage stamping to include your signature  
- canonization provenance to embed JRM‑01  

Which subsystem do you want updated next?
