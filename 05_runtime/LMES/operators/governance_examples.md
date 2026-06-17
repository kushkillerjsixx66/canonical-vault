# LMES Governance Examples

Extended scenarios illustrating operator decisions and their downstream effects.

---

## Scenario 1: Goal Adjustment at CP1

**Invocation:**
```
<Lattice:Run>
Goal: Evaluate whether to expand into the EU market.
Constraints: Focus on regulatory risk only. No financial modeling. No legal advice.
</Lattice:Run>
```

**FRAME output:**
> Restated goal: Assess the regulatory risk profile of EU market expansion.

**CP1 operator response:**
> Adjust. The goal should also include data privacy risk specifically (GDPR). Please update scope.

**System action:**
- Returns to CONSTRAIN
- Updates scope to include GDPR risk explicitly
- Re-presents to operator
- Proceeds to CP1 again

**Why this matters:** CP1 caught a scope gap before reasoning began.
Catching it here costs one checkpoint. Catching it at CP3 costs the entire run.

---

## Scenario 2: Redirect at CP2

**Invocation:**
```
<Lattice:Run>
Goal: Draft a 90-day onboarding plan for a new VP of Engineering.
Constraints: Small startup. No HR department. No legal advice.
</Lattice:Run>
```

**REASONING output (abbreviated):**
> Step 1: Map technical systems the VP needs to understand...
> Step 2: Identify key engineering team relationships...
> Step 3: Define 30/60/90 success metrics...

**CP2 operator response:**
> Redirect. Steps 1 and 2 are fine but Step 3 is premature. We haven't defined what success
> looks like for this role yet. Redirect to: what questions should we answer first before
> setting 90-day metrics?

**System action:**
- Returns to CONSTRAIN
- Updates constraints to reflect the redirected goal
- Re-runs REASONING from the new constraint frame
- Returns to CP2

**Why this matters:** CP2 is the course-correction point.
Redirecting here is cheaper than revising a finished output at CP3.

---

## Scenario 3: Rejection at CP3

**Invocation:**
```
<Lattice:Run>
Goal: Identify the three highest-priority infrastructure risks for the next quarter.
Constraints: Based on current system architecture. No cost analysis. No vendor recommendations.
</Lattice:Run>
```

**FINALIZATION output (abbreviated):**
> Output: The three highest-priority risks are: (1) single-point-of-failure in the auth service,
> (2) lack of observability in the data pipeline, (3) dependency on an unmaintained library in
> the payments module.

**CP3 operator response:**
> Reject. Risk #3 is out of scope — the payments module is being retired next month.
> Replace with the next-highest risk from the reasoning steps.

**System action:**
- Returns to FINALIZATION
- Removes Risk #3
- Surfaces the next-highest risk from REASONING
- Returns to CP3
- Records the rejection and reason in `operator_decisions`

**Why this matters:** Rejection at CP3 is not a failure. It is governed revision.
The audit log captures both the original output and the operator's reasoning for rejection.

---

## Scenario 4: Stop at CP2

**Invocation:**
```
<Lattice:Run>
Goal: Analyze competitive positioning against the top three market entrants.
Constraints: Based on publicly available information. No speculation.
</Lattice:Run>
```

**REASONING output:**
> Step 1: Identified three market entrants: A, B, C
> Step 2: Analyzed public positioning statements...
> Step 3: [Soft failure] Source gap — insufficient public data on entrant C to ground this step.

**System action at soft failure:**
> [SOFT FAILURE — REASONING GAP]
> Step 3 cannot be grounded. Entrant C has no sufficient public data.
> Options: (a) Exclude entrant C from analysis, (b) replace with next available entrant,
> (c) stop the run.

**CP2 operator response:**
> Stop. We don't have enough data for a useful output. Log the gap and close.

**System action:**
- Emits AUDIT_LOG with `compliance_status: "partial"`
- Records Stop decision and failure event
- Returns to IDLE

**Why this matters:** Stopping at CP2 is a valid outcome.
A partial, honest audit log is more useful than a complete, overconfident one.
