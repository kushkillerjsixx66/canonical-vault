# LMES Audit Log Schema (AL-Mini v1.1)

Every governed reasoning run MUST end with a complete AUDIT_LOG.
All fields are required. Empty fields must be explicitly marked `none` or `n/a`.

---

## Schema

```
AUDIT_LOG:
  runtime_version: <string>           # e.g. "LMES v1.1"
  timestamp: <ISO 8601 string>        # e.g. "2026-05-17T14:32:00Z"
  goal: <string>
  constraints: <list or string>
  state_transitions: <ordered list>   # e.g. [IDLE, FRAME, CONSTRAIN, CP1, ...]
  steps: <ordered list of reasoning steps>
  sources: <list of evidence, assumptions, or references per step>
  operator_decisions:
    cp1: <string>     # Confirm / Adjust + notes
    cp2: <string>     # Deepen / Redirect / Stop + notes
    cp3: <string>     # Accept / Revise / Reject + notes
  failure_events: <list or "none">
  rollback_events: <list or "none">
  final_output: <string or structured object>
  compliance_status: <"compliant" | "non-compliant" | "partial">
```

---

## Field Definitions

| Field | Purpose |
|-------|---------|
| `runtime_version` | Identifies which version of LMES governed this run |
| `timestamp` | Enables chronological ordering and replayability |
| `goal` | Verbatim goal from the wrapper invocation |
| `constraints` | Verbatim constraints from the wrapper invocation |
| `state_transitions` | Full ordered list of states traversed — enables drift detection |
| `steps` | Complete reasoning steps as produced in REASONING state |
| `sources` | Per-step grounding evidence or named assumptions |
| `operator_decisions` | All three checkpoint decisions with any operator notes |
| `failure_events` | Any hard or soft failures encountered during the run |
| `rollback_events` | Any states returned to via operator authorization |
| `final_output` | The accepted output, or the rejected/partial output with status |
| `compliance_status` | Whether the run met all compliance requirements |

---

## Non-Compliant Run Handling

If a run cannot reach CP3 (operator stop, hard failure, invariant violation):
- Emit a `FAILURE_LOG` using the same schema
- Set `compliance_status: "non-compliant"` or `"partial"`
- Populate `failure_events` with the halt condition
- Leave `final_output` as `"none — run did not complete"`

A FAILURE_LOG is still an audit artifact. It is required, not optional.
