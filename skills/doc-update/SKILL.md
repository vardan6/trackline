---
name: doc-update
description: Selectively update durable project docs. Use for /doc-update.
---

# doc-update

Update only docs that have durable value. Never duplicate code.

## When to use

- After implementing one or more slices.
- After applying review fixes.
- After phase progress is real but not yet reflected in docs.
- User says: "update the docs", "refresh documentation".
- User invokes `/doc-update`.

## Do NOT use when

- During implementation (state changes go inline via `/session-close (STEP mode)`).
- Closing a session for handoff → `/session-close`.
- Capturing planning output → `/planning-capture`.
- Asked to "document everything" → refuse. That is the anti-pattern this skill replaces.

## Inputs (read order)

1. Recent git diff (what actually changed).
2. `activeContext.md` and `roadmap.md`.
3. Only the requirements / design / ADR docs that relate to the diff.

Do NOT pre-load all docs.

## Steps

1. Read the diff. Identify what genuinely changed in behavior, architecture, contract, or invariant.
2. Write agent-first docs (human readability is the second reader, nearly free): docs should first help coding agents make correct development decisions, and second give humans a coherent project picture.
3. Preserve one canonical source of truth per fact. Prefer pointers over copied explanations, and update the smallest set of docs that keeps future implementation decisions correct.
4. Apply the decision table — each row independently:

   | Change                               | Update                                                  |
   |--------------------------------------|---------------------------------------------------------|
   | Finished-project behavior / user expectation / acceptance / non-goal | `docs/requirements/` |
   | Implementation approach / architecture / boundary / algorithm / protocol / tradeoff | `docs/design/` or new `docs/adr/` |
   | Phase or next step                   | `roadmap.md` + `activeContext.md`             |
   | Durable invariant / contract / gotcha| `docs/implementation-notes.md` or ADR                   |
   | Only code internals                  | No docs                                                 |

5. Edit existing docs first. Create new only when a durable category has no home.
6. Reference code paths instead of explaining all implementation details.
7. Keep status out of requirements and design. If only the phase, blocker, or next step changed, update only `roadmap.md`, `activeContext.md`, or `progress.md` — and keep them lean: `roadmap.md` checklist-first, `activeContext.md` cheap session-start state, no narrative or repeated history.
8. If code and design/ADR disagree, report the conflict instead of rewriting the standing decision silently.
9. Confirm `activeContext.md` still names the correct next step. If not, fix that one line.
10. If no durable docs need updates, say so explicitly. That is a valid outcome.
11. Print the Output.

## Output

```
Updated:
  docs/requirements/: <files or "none">
  docs/design/:       <files or "none">
  docs/adr/:          <files or "none">
  roadmap.md:    <yes/no>
  activeContext.md: <yes/no — what line changed>
  docs/implementation-notes.md: <yes/no>
Not updated (with reason): <list>
Next session ready: yes | no — <one sentence>
Suggested next skill: <e.g. /session-close (STEP mode), /session-close, or "none">
```

## Stop conditions

- After printing Output, stop. Do not chain into commit or session close.
- If the diff is too large to classify in one pass → split into per-feature passes, do not write a megaupdate.
