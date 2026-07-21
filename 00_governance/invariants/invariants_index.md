

---

Invariants Index
A governed index of Tier 2 constitutional, procedural, and protocol rules

**This index covers the Tier 2 registry (`invariants_map.yaml`) only.** The
six Lattice Invariants — the structural constraints enforced by Sentinel and
audited by Stumpy — are defined separately in `Lattice_Invariants_v1.md` and
sit above everything indexed here. See that file for the authority ordering.

This index provides a unified map of all invariants across the Lattice governance layer.  
It links the constitutional invariants, YAML‑based constraint definitions, drift domains, and audit policies into a single navigable reference.

Invariants define what cannot break.  
This index defines where they live.

---

1. Constitutional Invariants
These are the supreme invariants within the Tier 2 registry, defined in:

- constitution/invariants.md  
- constitution/lattice_constitution.md  

They include:

- Lineage is mandatory  
- Canon is immutable  
- Intent is explicit  
- Boundaries are real  
- Drift must be detectable  
- Reversibility is preferred  
- Governance supersedes runtime  
- Operator identity is stable  
- Visibility is governed  
- Archive is not deletion  

These invariants apply to every layer of the Tier 2 process registry.

---

2. Constraint Classes
Defined in:

- constraint_classes.yaml  

Constraint classes describe the structural limits of modules and subsystems.

Examples include:

- Structural constraints  
- Temporal constraints  
- Semantic constraints  
- Boundary constraints  
- Reversibility constraints  
- Canonization constraints  

Constraint classes determine what a module is allowed to do.

---

3. Drift Domains
Defined in:

- drift_domains.yaml  

Drift domains define:

- where drift can occur  
- how drift manifests  
- how drift is measured  
- how drift is recovered  

Drift domains ensure that all deviation is detectable.

---

4. Audit Policies
Defined in:

- audit_policy.yaml  

Audit policies govern:

- how invariants are checked  
- how violations are detected  
- how lineage is validated  
- how governance faults escalate  

Audit policies ensure continuous integrity.

---

5. Governance Principles
Defined in:

- principles.yaml  
- constitution/governance_principles.md  

These principles guide:

- interpretation of invariants  
- application of governance  
- posture of the system  
- operator‑system interaction  

Principles are the interpretive layer of invariants.

---

6. Operator Manual Invariants
Defined across:

- execution_postures.yaml  
- operator_manual/failure_modes.md  
- recovery_sequences.yaml  
- operator_manual/section_7_operator_playbook.md  

These invariants govern:

- operator posture  
- failure handling  
- recovery behavior  
- escalation ladders  

They ensure operator‑runtime coherence.

---

7. Protocol‑Level Invariants
Defined in:

- protocols/  
  - Ω‑13 (Bilateralism)  
  - Ω‑14 (Governance Envelope)  
  - AMP (Altitude Modulation Protocol)  
  - Escalation ladders  
  - Bilateralism map  

Protocol invariants govern:

- cross‑module binding  
- altitude shifts  
- governance envelopes  
- escalation behavior  

These invariants ensure system‑wide coherence.

---

8. Vault Invariants
Defined implicitly across:

- Vault CLI  
- Vault Core  
- Commit Engine  
- Canon Engine  
- Veil Engine  
- Lineage Engine  

Vault invariants include:

- commit → review → canon lifecycle  
- immutable canon  
- mandatory lineage  
- veil‑layer visibility control  
- threshold ritual  

These invariants protect the memory substrate. See also `05_runtime/vault/README.md`'s Vault Operating Principles, which cross-reference the Tier 1 invariants directly.

---

9. Runtime Invariants
Defined across:

- runtime spine  
- module bindings  
- pipeline contracts  
- execution rules  

Runtime invariants ensure:

- no cross‑boundary mutation  
- no silent writes  
- no ungoverned execution  
- no lineage gaps  

These invariants protect the execution layer.

---

10. Amendment Invariants
Defined in:

- constitution/amendment_laws.md  

Amendments must:

- preserve core invariants  
- preserve operator identity  
- preserve kernel immutability  
- be lineage‑tracked  
- be ratified  

These invariants protect the Constitution itself.

---

Summary Table

| Domain | Source | Purpose |
|-------|--------|---------|
| Constitutional Invariants | constitution/invariants.md | Tier 2 process laws |
| Constraint Classes | constraint_classes.yaml | Structural limits |
| Drift Domains | drift_domains.yaml | Drift detection & recovery |
| Audit Policies | audit_policy.yaml | Integrity enforcement |
| Governance Principles | principles.yaml / constitution/governance_principles.md | Interpretive layer |
| Operator Manual | operator_manual/ | Runtime posture & behavior |
| Protocols | protocols/ | Cross‑module governance |
| Vault Invariants | vault subsystem | Memory substrate rules |
| Runtime Invariants | runtime layer | Execution boundaries |
| Amendment Invariants | constitution/amendment_laws.md | Constitutional evolution |

---

