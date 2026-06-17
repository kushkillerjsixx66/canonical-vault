# LMES Operator Onboarding (v1.1)

---

## What You Are Doing

You are operating a governed reasoning runtime.

You provide the goal and constraints.
The system structures the reasoning.
You control all decision points.
The system produces the audit record.

LMES does not reason on your behalf. It reasons under your governance.

---

## Your Responsibilities

1. **Wrap governed reasoning** inside `<Lattice:Run>` ... `</Lattice:Run>`
2. **Provide a Goal** — clear, bounded, specific enough to constrain reasoning
3. **Provide Constraints** — what is in scope and what is not
4. **Answer CP1** — confirm or adjust before reasoning begins
5. **Answer CP2** — direct the run after reviewing reasoning steps
6. **Answer CP3** — accept, revise, or reject the final output
7. **Review the Audit Log** — the evidence record is yours to keep

---

## What LMES Will Do

- Restate your goal (FRAME)
- Define scope from your constraints (CONSTRAIN)
- Pause for your confirmation (CP1)
- Produce numbered, sourced reasoning steps (REASONING)
- Pause for your direction (CP2)
- Produce a final output traceable to those steps (FINALIZATION)
- Pause for your decision (CP3)
- Emit a complete audit record (AUDIT)
- Close the runtime (EXIT)

---

## What LMES Will Not Do

- Proceed past a checkpoint without your input
- Produce output it cannot trace to a reasoning step
- Resolve ambiguous constraints silently
- Override your decisions
- Skip states to save time

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Vague goal | Reasoning wanders into adjacent scope | Write a one-sentence goal that could be falsified |
| Missing constraints | Soft failure at CONSTRAIN | Always define at least one out-of-scope boundary |
| Skipping CP answers | Runtime halts | Respond to each checkpoint explicitly |
| Closing wrapper early | Hard failure | Let the run reach CP3 before closing |
| Treating LMES as a chatbot | Governance degrades | Stay in operator mode inside the wrapper |

---

## You Are the Operator

The system follows you. The checkpoints exist for you.
The audit log is yours.

LMES is not a collaborator. It is a governed tool.
The governance only works if you use it.
