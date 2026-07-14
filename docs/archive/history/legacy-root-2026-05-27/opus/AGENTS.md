# AGENTS.md

> Router for coding agents in this project. Not a knowledge base.
> Target ~80 lines. If a line wouldn't change a future decision, delete it.

## Where am I right now?

- Current phase + next step are tracked in `docs/roadmap.md` and `docs/current-state.md`.
- Latest session handoff (if any): newest file in `docs/handoffs/`.

## Workflow rules

1. **Every session starts with `/session-open`.** No exceptions. It reads
   `AGENTS.md` → `docs/current-state.md` → newest `docs/handoffs/*.md` →
   `docs/roadmap.md`, declares the mode, and names the next step. Do not
   pre-read `docs/requirements/` or `docs/design/` unless the next step
   explicitly needs them.
2. **Inside implementation mode** use `/next-slice` to pick the next code
   change. Implement one atomic slice per cycle.
3. **After finishing one step** run `/cycle-close` — ticks roadmap, appends
   `docs/progress.md`, refreshes `docs/current-state.md`, suggests a commit.
   Does NOT touch requirements / design / ADR.
4. **For durable doc updates** (after non-trivial implementation) use
   `/doc-update`. Apply the decision table; "no updates needed" is a valid
   outcome. Never create internals / implementation specs.
5. **For plan or code reviews** use `/review-triage`. Implement only
   `must_fix_now` by default.
6. **For planning sessions** use `/planning-capture` after `/grill-me`,
   `/grill-with-docs`, `/to-prd`, or research.
7. **At ~50% context** suggest `/session-close`. Include the token equivalent
   for the active model: 100k on 200k, 200k on 400k, 500k on 1M, or 525k on
   GPT-5.5's 1,050k. Don't push past ~60%: 120k / 240k / 600k / 630k.
8. **Code is the truth.** Re-derive *how* from code. Do not write internals
   docs that mirror code structure.

## Canonical docs (pull on demand)

- `docs/requirements/` — what the system must do. Read when scope is ambiguous.
- `docs/design/` — high-level shape and tradeoffs. Read when designing across modules.
- `docs/adr/` — recorded decisions and non-obvious mechanics. Search when something looks weird.
- `docs/implementation-notes.md` — rare durable invariants / contracts / gotchas.

## Skills (auto-dispatch via description)

- `/session-open` — mandatory session entry.
- `/next-slice` — pick + start one atomic code change.
- `/planning-capture` — classify planning output into durable docs.
- `/doc-update` — selective durable-doc update.
- `/review-triage` — sort review findings.
- `/cycle-close` — end one roadmap step.
- `/session-close` — end the session.

## Non-obvious gotchas

<!-- Add per-project freezes, hidden invariants, in-progress refactors here.
     If empty, leave empty. Do not pad. -->
