# LMES Diagrams (v1.1)

Diagram source files are defined below as text specifications.
Render using any Mermaid-compatible tool, or commission as graphics.

---

## lmes_architecture

```
Wrapper (outer boundary)
└── Runtime Protocol (inner engine)
    ├── State Machine (IDLE → EXIT)
    ├── Invariants (governance layer)
    │   ├── Reversibility
    │   ├── Lineage
    │   ├── Operator Primacy
    │   └── Non-Obfuscation
    ├── Failure Modes (hard / soft / drift)
    └── Audit Log (evidence layer)
```

---

## runtime_flow (Mermaid source)

```mermaid
flowchart TD
    IDLE --> FRAME
    FRAME --> CONSTRAIN
    CONSTRAIN --> CP1
    CP1 -->|Confirm| REASONING
    CP1 -->|Adjust| FRAME
    REASONING --> CP2
    CP2 -->|Deepen/Proceed| FINALIZATION
    CP2 -->|Redirect| CONSTRAIN
    CP2 -->|Stop| AUDIT_PARTIAL[AUDIT partial]
    FINALIZATION --> CP3
    CP3 -->|Accept| AUDIT
    CP3 -->|Revise| FINALIZATION
    CP3 -->|Reject| AUDIT_REJECTED[AUDIT rejected]
    AUDIT --> EXIT
    AUDIT_PARTIAL --> EXIT
    AUDIT_REJECTED --> EXIT
    EXIT --> IDLE
    FRAME -->|Hard Failure| FAILURE_LOG
    CONSTRAIN -->|Hard Failure| FAILURE_LOG
    REASONING -->|Hard Failure| FAILURE_LOG
    FAILURE_LOG --> EXIT
```

---

## runtime_state_machine (Mermaid source)

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> FRAME : <Lattice:Run> invoked
    FRAME --> CONSTRAIN : Goal restated
    CONSTRAIN --> CP1 : Scope declared
    CP1 --> REASONING : Confirm
    CP1 --> FRAME : Adjust goal
    CP1 --> CONSTRAIN : Adjust constraints
    REASONING --> CP2 : Steps complete
    CP2 --> FINALIZATION : Deepen/Proceed
    CP2 --> CONSTRAIN : Redirect
    CP2 --> AUDIT : Stop (partial)
    FINALIZATION --> CP3 : Output ready
    CP3 --> AUDIT : Accept/Reject
    CP3 --> FINALIZATION : Revise
    CP3 --> REASONING : Re-reason
    AUDIT --> EXIT : Log emitted
    EXIT --> IDLE : Wrapper closed
    FRAME --> EXIT : Hard failure
    CONSTRAIN --> EXIT : Hard failure
    REASONING --> EXIT : Hard failure
```
