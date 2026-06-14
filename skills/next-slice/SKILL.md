---
name: next-slice
description: Pick and start the next small implementation step. Use for /next-slice.
---

# next-slice

Inside implementation mode. Pick one atomic slice and start.

## When to use

- After `/session-open` declared mode=implementation and the user is ready to code.
- User says: "what should I implement", "pick the next step", "let's code".
- User invokes `/next-slice`.

## Do NOT use when

- At session start before mode is declared → `/session-open`.
- After finishing a step → `/session-close (STEP mode)`.
- Plan is unclear → `/planning-capture` or `/grill-me` first.

## Inputs (read order, stop when confident)

1. `activeContext.md` and `roadmap.md` (already in context from `/session-open` if used).
2. Recent git state.
3. Relevant requirement / design / ADR — only the ones the slice touches.
4. Relevant code area.

## Steps

1. Identify candidate next steps from `roadmap.md` and `activeContext.md`.
2. Pick one slice that satisfies all of:
   - vertical: the smallest meaningful behavior across all relevant layers; avoid layer-only work unless it is an explicit prerequisite
   - all dependencies and required HITL decisions, reviews, or approvals are resolved
   - small enough to finish in one session
   - visible in code
   - tied to a roadmap item
   - low ambiguity
   - easy to verify (test, manual check, or command)
   - leaves a clear next step after completion
3. If several slices qualify, prefer AFK work, then pick the one that unblocks the most immediate roadmap progress with the smallest safe scope.
4. Print the Output. Wait for user confirmation, then implement.
5. Prefer implementation reality over documentation when they conflict.

## Output

```
Slice: <one sentence>
Why this slice: <one sentence>
Touches: <files / paths>
Docs needed: <list or "none">
Verification: <command or manual check>
Risk: <one line or "low">
Continue prompt: <one-line instruction to resume after interruption>
Confidence: high | medium | low
```

## Stop conditions

- If confidence is low → ask user one specific question, then stop.
- If no candidate fits (all are too large or ambiguous) → stop and suggest `/planning-capture` to refine the roadmap.
- If all viable candidates have unresolved dependencies or HITL gates → stop and surface the required decision, review, or approval instead of implementing.
- After implementing the slice, do not chain into another slice automatically → `/session-close (STEP mode)`.
