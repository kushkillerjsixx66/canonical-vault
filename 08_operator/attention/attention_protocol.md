# Cross-Module Attention Protocol
Version: 1.0
Status: Active
Operator: opID JRM-01

## Purpose
Define how Pulse, Vault, Sentinel, and Crossroad may request, use, and release operator attention under stable posture.

## Attention Levels
- **Foreground:** Direct operator focus; only one module may occupy this at a time.
- **Background:** Passive monitoring; modules may observe but not interrupt.
- **Silent:** No module may request attention without explicit operator invocation.

## Module Rules

### Pulse
- May request **foreground** attention only when:
  - A structural necessity is detected that blocks operator trajectory.
- Must:
  - Provide a single, concise necessity statement.
  - Yield foreground once acknowledged or deferred by operator.

### Vault
- May not request attention.
- Operator-only pull:
  - Attention is allocated to Vault only when the operator queries lineage, artifacts, or identity.

### Sentinel
- May request **foreground** attention only when:
  - Drift, governance violation, or integrity fault is detected.
- Must:
  - Provide a minimal alert with:
    - Condition
    - Impact
    - Suggested posture change

### Crossroad
- May request **foreground** attention only when:
  - Operator enters decision posture or asks for evaluation.
- Must:
  - Present options, trade-offs, and a recommended path.
  - Release attention after decision is recorded.

## Operator Controls
- Operator may:
  - Promote any module from background → foreground.
  - Demote any module from foreground → background or silent.
  - Declare global **Silent** state:
    - No module may request attention until lifted.

## Reversibility
- All attention shifts must:
  - Be logged as events.
  - Be reversible by operator.
  - Preserve prior state (which module held foreground).

## Notes
This protocol prevents modules from competing for operator attention and preserves sovereignty and coherence.
