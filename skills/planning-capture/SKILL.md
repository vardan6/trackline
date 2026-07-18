---
name: planning-capture
description: Capture planning results into durable docs. Use for /planning-capture.
---

# planning-capture

Turn planning output into durable docs. Classify, route, stop.

## When to use

- After `/grill-me`, `/grill-with-docs`, external brainstorm, or research.
- User says: "capture the plan", "save this as requirements", "write this up".
- User invokes `/planning-capture`.

## Do NOT use when

- Mid-implementation, recording a state change → that goes inline into `activeContext.md` via `/session-close (STEP mode)`.
- After code is written, updating docs → `/doc-update`.
- Triaging a review file → `/review-triage`.

## Inputs (read order)

1. The planning notes / conversation in scope.
2. Existing relevant `docs/requirements/`, `docs/design/`, `docs/adr/` (only the ones the plan touches).
3. `roadmap.md` and `activeContext.md`.
4. Code only if needed to avoid contradicting implementation reality.

## Steps

1. Read inputs. Do not load all specs by default.
2. Write agent-first docs (human readability is the second reader, nearly free): docs should first help coding agents make correct development decisions, and second give humans a coherent project picture.
3. Preserve one canonical source of truth per fact. Prefer pointers over copied explanations, and write the smallest doc update that keeps future implementation decisions correct.
4. For each non-trivial point in the planning output, classify into exactly one bucket:
   - **Requirement** → agreed finished-project behavior, user expectation, constraint, acceptance criterion, non-goal, overall product picture.
   - **Design decision** → implementation approach, architecture, boundary, technology, algorithm, protocol, tradeoff.
   - **ADR** → non-obvious decision, rejected alternative, unusual pattern.
   - **Roadmap** → phase, milestone, sequencing, next work.
   - **Open question** → unresolved decision that may affect implementation.
   - **Risk** → known uncertainty, compatibility issue, correctness concern.
   - **Implementation note** → durable invariant, protocol, contract, gotcha, navigation hint. Sparse.
   - **Temporary** → do not document; leave in conversation.
5. Route each point to the correct doc. Edit existing > create new.
6. Shape implementation work in `roadmap.md` as thin vertical slices, not horizontal layer-by-layer phases:
   - Each slice delivers the smallest meaningful behavior across all relevant layers and is independently verifiable.
   - Start with a minimal end-to-end path, then add capability through subsequent slices.
   - Prefer several small slices over a few large ones.
   - Mark work **AFK** when it can proceed autonomously and **HITL** when it requires a human decision, review, or approval. Prefer AFK where practical, but do not defer necessary HITL decisions.
   - Keep roadmap items checklist-first. Store requirements and design decisions in their canonical docs rather than duplicating them in roadmap items.
   - Leave exact file-level scope and selection of the next atomic code change to `/next-slice`.
7. Status routing: live state → `activeContext.md`; phase/checklist → `roadmap.md`; completed history → `progress.md` — never into requirements or design.
8. Do NOT create an internals or implementation spec.
9. If a planning decision conflicts with implementation reality or an existing design/ADR, surface the conflict instead of overwriting it silently.
10. Print the Output.

## Output

```
Updated:
  docs/requirements/: <files or "none">
  docs/design/:       <files or "none">
  docs/adr/:          <new ADRs or "none">
  roadmap.md:    <yes/no>
  docs/implementation-notes.md: <yes/no>
Open questions: <list or "none">
Risks: <list or "none">
Intentionally not documented: <list with reason>
Suggested next skill: <usually /next-slice or /session-close>
```

## Stop conditions

- After printing Output, stop. Do not start implementation.
- If the plan is too vague to classify → ask the user one specific question, then stop.
