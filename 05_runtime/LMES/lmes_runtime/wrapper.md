# LMES Interaction Wrapper

```
<<LATTICE-RUNTIME>>

All governed reasoning MUST occur inside this wrapper.

Outside the wrapper = IDLE state. Normal conversation. No governance active.
Inside the wrapper  = governed, reversible, auditable reasoning.

Enter Runtime with:  <Lattice:Run>
Exit Runtime with:   </Lattice:Run>

No governed reasoning may occur outside the wrapper.
No conversational content may bleed into the wrapper.

The wrapper is a hard boundary. It is not a suggestion.

<<END-LATTICE-RUNTIME>>
```

## Wrapper Rules

1. The wrapper must be explicitly opened and explicitly closed.
2. A wrapper opened without a Goal field is a hard failure.
3. A wrapper closed before CP3 is a non-compliant run.
4. Nested wrappers are not permitted.
5. The wrapper does not inherit context from prior governed runs unless the operator
   explicitly provides carry-over state in the Goal or Constraints fields.

## Invocation Format

```
<Lattice:Run>
Goal: <clear, bounded statement of what the run should produce>
Constraints: <what is in scope, what is out of scope>
</Lattice:Run>
```

- **Goal is required.** A missing or empty Goal is a **hard failure**.
- **Constraints are expected.** A missing or empty Constraints field is a **soft failure**:
  - The system pauses (normally at CONSTRAIN / CP1).
  - Names the condition explicitly.
  - Requests the operator to supply scope.
  - Does not infer constraints.
  - Records the event in `failure_events`.
