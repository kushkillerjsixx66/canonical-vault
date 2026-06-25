# Execution Engine  
*Governed execution semantics of the Lattice*

The execution engine defines how operations run inside the runtime.

---

## 1. Execution Semantics

Execution must be:

- reversible  
- lineage-emitting  
- envelope-compliant  
- drift-detectable  
- altitude-declared  

---

## 2. Execution Phases

1. **Interpretation**  
2. **Evaluation**  
3. **Execution**  
4. **Reversibility**  
5. **Lineage Emission**

These phases map directly to the **runtime module** you defined earlier.

---

## 3. Failure Handling

Failures must:

- halt execution  
- emit lineage  
- trigger escalation  
- enter recovery sequences  

See: Operator Playbook Section 7.

---

## 4. Integration

- Vara handles signal decomposition  
- Stumpy handles structural coherence  
- Drift Engine handles drift classification
