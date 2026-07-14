---
name: planning-capture
description: Capture planning results into durable docs. Use for /planning-capture.
---

# planning-capture

Turn planning output into durable docs. Classify, route, stop.

## When to use

- After `/grill-me`, `/grill-with-docs`, external brainstorm, or research.
- After `/to-prd` or `/to-issues` if their outputs need further routing.
- User says: "capture the plan", "save this as requirements", "write this up".
- User invokes `/planning-capture`.

## Do NOT use when

- Mid-implementation, recording a state change → that goes inline into `docs/current-state.md` via `/cycle-close`.
- After code is written, updating docs → `/doc-update`.
- Triaging a review file → `/review-triage`.

## Inputs (read order)

1. The planning notes / conversation in scope.
2. Existing relevant `docs/requirements/`, `docs/design/`, `docs/adr/` (only the ones the plan touches).
3. `docs/roadmap.md` and `docs/current-state.md`.
4. Code only if needed to avoid contradicting implementation reality.

## Steps

1. Read inputs. Do not load all specs by default.
2. For each non-trivial point in the planning output, classify into exactly one bucket:
   - **Requirement** → external behavior, constraint, acceptance criterion, non-goal, user-facing rule.
   - **Design decision** → architecture, boundary, technology, tradeoff.
   - **ADR** → non-obvious decision, rejected alternative, unusual pattern.
   - **Roadmap** → phase, milestone, sequencing, next work.
   - **Open question** → unresolved decision that may affect implementation.
   - **Risk** → known uncertainty, compatibility issue, correctness concern.
   - **Implementation note** → durable invariant, protocol, contract, gotcha, navigation hint. Sparse.
   - **Temporary** → do not document; leave in conversation.
3. Route each point to the correct doc. Edit existing > create new.
4. Do NOT create an internals or implementation spec.
5. Print the Output.

## Output

```
Updated:
  docs/requirements/: <files or "none">
  docs/design/:       <files or "none">
  docs/adr/:          <new ADRs or "none">
  docs/roadmap.md:    <yes/no>
  docs/implementation-notes.md: <yes/no>
Open questions: <list or "none">
Risks: <list or "none">
Intentionally not documented: <list with reason>
Suggested next skill: <usually /next-slice or /session-close>
```

## Stop conditions

- After printing Output, stop. Do not start implementation.
- If the plan is too vague to classify → ask the user one specific question, then stop.
