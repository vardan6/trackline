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

## Inputs (read order)

1. `activeContext.md` and `roadmap.md`; reuse them if already read and unchanged.
2. Recent git state; start small and inspect only relevant diffs when needed.
3. Every doc the chosen slice cites by Markdown link — never skipped (step 4).
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
   - tiebreak: prefer autonomous work, then whatever unblocks roadmap progress
4. Before implementing, open every doc the slice cites, plus ADRs those pages link, one hop. Fragment link means that section; bare link means the whole file. However self-sufficient the roadmap line looks, it is a pointer, not a substitute. Citable: `requirements/` · `design/` · `adr/` · `reviews/` — never `research/`, capture it first. Accept `no doc governs: <reason>` only when nothing durable is at stake (maintenance, refactor, content-only), or the doc or decision is the slice's own output.
5. Print the Output. Wait for user confirmation, then implement.
6. Code is implementation truth; durable docs are decision truth. Surface conflicts.

## Output

```
Slice: <one sentence>
Why this slice: <one sentence>
Touches: <files / paths>
Docs read: <paths opened, or "none — no doc governs: reason">
Verification: <command or manual check>
Risk: <one line or "low">
Continue prompt: <one-line instruction to resume this slice after interruption>
Confidence: high | medium | low
```

## Stop conditions

- If confidence is low → ask user one specific question, then stop.
- A cited link resolves to no file, its fragment matches zero or several headings, it points into `docs/research/`, or a behavior-changing slice claims no doc governs it → stop and report it; the roadmap line is not a fallback.
- No candidate fits — too large, too ambiguous, or blocked by a dependency or HITL gate → stop; surface the required decision, or suggest `/planning-capture` to refine the roadmap.
- After implementing the slice, do not chain into another slice automatically → `/session-close (STEP mode)`.
