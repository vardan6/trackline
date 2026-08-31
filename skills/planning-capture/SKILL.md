---
name: planning-capture
description: Capture planning results into durable docs. Use for /planning-capture.
---

## When to use

- After grilling, brainstorming, or research; or when the user invokes `/planning-capture` or asks to capture/save/write up a plan.

## Do NOT use when

- Mid-implementation state change → `/session-close (STEP)`.
- Post-code doc update → `/doc-update`.
- Review triage → `/review-triage`.

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
   - **Requirement** → finished behavior, expectation, constraint, acceptance criterion, non-goal.
   - **Design** → approach, architecture, boundary, protocol, tradeoff.
   - **ADR** → non-obvious decision or rejected alternative.
   - **Roadmap** → phase, sequencing, next work.
   - **Open question** → unresolved decision.
   - **Risk** → uncertainty, compatibility, correctness concern.
   - **Implementation note** → rare invariant, contract, gotcha, navigation hint.
   - **Temporary** → leave in conversation.
5. Route each point to the correct doc. Edit existing > create new.
   - Keep headings unique within a file: duplicates get position-dependent anchors (`#retry`, `#retry-1`), so a later insertion silently repoints existing citations.
   - Link each new ADR from the design section it governs, in the same pass. An unlinked ADR is unreachable.
6. Shape implementation work in `roadmap.md` as thin vertical slices, not horizontal layer-by-layer phases:
   - Deliver the smallest meaningful, independently verifiable behavior across relevant layers; start end-to-end, then add capability in small slices.
   - Mark work **AFK** when it can proceed autonomously and **HITL** when it requires a human decision, review, or approval. Prefer AFK where practical, but do not defer necessary HITL decisions.
   - Keep roadmap items checklist-first; point to canonical requirements/design instead of copying prose.
   - Every behavior- or decision-changing slice cites ≥1 doc as a relative Markdown link — whole file by default, `#heading` fragment past ~150 lines. Citable: `requirements/` · `design/` · `adr/` · `reviews/`; never `research/` — capture it (step 4) and cite that. Otherwise record `no doc governs: <reason>`: maintenance, refactor, content-only, or the slice's own output is the doc or decision. Cite links, never paste prose — `/next-slice` opens exactly what is cited.
   - Leave file scope and selection of the next atomic code change to `/next-slice`.
7. Status routing: live state → `activeContext.md`; phase/checklist → `roadmap.md`; completed history → `progress.md` — never into requirements or design.
8. Do NOT create an internals or implementation spec.
9. If a planning decision conflicts with implementation reality or an existing design/ADR, surface the conflict instead of overwriting it silently.
10. Print the Output.

## Output
```
Updated:
  docs/requirements/: <files or "none">
  docs/design/:       <files or "none">
  docs/adr/:          <new ADRs + the section each links from, or "none">
  roadmap.md:    <yes/no — slices claiming "no doc governs": N of M>
  docs/implementation-notes.md: <yes/no>
Open questions: <list or "none">
Risks: <list or "none">
Intentionally not documented: <list with reason>
Suggested next skill: <usually /next-slice or /session-close>
```

## Stop conditions
- After Output, stop without implementation; if the plan is too vague to classify, ask one specific question and stop.
