---
name: next-slice
description: Pick the next small implementation slice. Use when the user asks what to implement, says let's code, or invokes /next-slice.
---

# next-slice

## When to use

- Implementation mode is established, or explicit `/next-slice` starts it from minimal state.
- User says: "what should I implement", "pick the next step", "let's code".

## Do NOT use when

- State indicates another mode and the user has not explicitly redirected it.
- After finishing a step → `/session-close (STEP mode)`.
- Plan is unclear → `/planning-capture` or `/grill-me` first.

## Inputs (read order, stop when confident)

1. `activeContext.md` and `roadmap.md`; reuse them if already read and unchanged.
2. Recent git state; start small and inspect only relevant diffs when needed.
3. Relevant requirement / design / ADR — only the ones the slice touches.
4. Relevant code area.

## Steps

1. If mode is unknown, confirm implementation from inputs 1; otherwise stop.
2. Identify candidate implementation slices from the current roadmap item.
3. Pick one slice that satisfies all of:
   - vertical: smallest meaningful behavior across relevant layers
   - all dependencies and required HITL decisions, reviews, or approvals are resolved
   - small enough to finish in one session
   - produces a concrete, reviewable artifact or behavior
   - tied to a roadmap item; leaves a clear next step or completes the item
   - low ambiguity
   - easy to verify (test, manual check, or command)
4. Prefer autonomous work, then the smallest slice that unblocks roadmap progress.
5. Print the Output. Wait for user confirmation, then implement.
6. Code is implementation truth; durable docs are decision truth. Surface conflicts.

## Output

```
Slice: <one sentence>
Why this slice: <one sentence>
Touches: <files / paths>
Docs needed: <list or "none">
Verification: <command or manual check>
Risk: <one line or "low">
Continue prompt: <one-line instruction to resume this slice after interruption>
Confidence: high | medium | low
```

## Stop conditions

- If confidence is low → ask user one specific question, then stop.
- If no candidate fits (all are too large or ambiguous) → stop and suggest `/planning-capture` to refine the roadmap.
- If all viable candidates have unresolved dependencies or HITL gates → stop and surface the required decision, review, or approval instead of implementing.
- After implementing the slice, do not chain into another slice automatically → `/session-close (STEP mode)`.
