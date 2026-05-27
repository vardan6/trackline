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

- During implementation (state changes go inline via `/cycle-close`).
- Closing a session for handoff → `/session-close`.
- Capturing planning output → `/planning-capture`.
- Asked to "document everything" → refuse. That is the anti-pattern this skill replaces.

## Inputs (read order)

1. Recent git diff (what actually changed).
2. `docs/current-state.md` and `docs/roadmap.md`.
3. Only the requirements / design / ADR docs that relate to the diff.

Do NOT pre-load all docs.

## Steps

1. Read the diff. Identify what genuinely changed in behavior, architecture, contract, or invariant.
2. Apply the decision table — each row independently:

   | Change                               | Update                                                  |
   |--------------------------------------|---------------------------------------------------------|
   | External behavior / acceptance / non-goal | `docs/requirements/`                                |
   | Architecture / boundary / tradeoff   | `docs/design/` or new `docs/adr/`                       |
   | Phase or next step                   | `docs/roadmap.md` + `docs/current-state.md`             |
   | Durable invariant / contract / gotcha| `docs/implementation-notes.md` or ADR                   |
   | Only code internals                  | No docs                                                 |

3. Edit existing docs first. Create new only when a durable category has no home.
4. Reference code paths instead of explaining all implementation details.
5. Confirm `docs/current-state.md` still names the correct next step. If not, fix that one line.
6. If no durable docs need updates, say so explicitly. That is a valid outcome.
7. Print the Output.

## Output

```
Updated:
  docs/requirements/: <files or "none">
  docs/design/:       <files or "none">
  docs/adr/:          <files or "none">
  docs/roadmap.md:    <yes/no>
  docs/current-state.md: <yes/no — what line changed>
  docs/implementation-notes.md: <yes/no>
Not updated (with reason): <list>
Next session ready: yes | no — <one sentence>
Suggested next skill: <e.g. /cycle-close, /session-close, or "none">
```

## Stop conditions

- After printing Output, stop. Do not chain into commit or session close.
- If the diff is too large to classify in one pass → split into per-feature passes, do not write a megaupdate.
