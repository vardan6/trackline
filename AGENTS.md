# AGENTS.md

> Router for coding agents in this project. Not a knowledge base.
> Target ~80 lines. If a line wouldn't change a future decision, delete it.

## Where am I right now?

- Current phase + next step are tracked in `roadmap.md` and `activeContext.md` (repo root).
- Latest session handoff (if any): newest `handoff-*.md` at repo root.

## Workflow rules

1. **Every session starts with `/session-open`.**. It reads
   `AGENTS.md` → `activeContext.md` → newest `handoff-*.md` → `roadmap.md`,
   declares the mode, and names the next step. Do not pre-read
   `docs/requirements/` or `docs/design/` unless the next step explicitly
   needs them.
2. **Inside implementation mode** use `/next-slice` to pick the next code
   change. Implement one atomic vertical slice per cycle.
3. **After finishing one step** run `/session-close` (STEP mode) — ticks
   roadmap, appends `progress.md`, refreshes `activeContext.md` keeping small but essential, suggests a
   commit. In SESSION mode it also runs `/doc-update` and may write a handoff.
4. **For durable doc updates** (after non-trivial implementation) use
   `/doc-update`. Apply the decision table; "no updates needed" is a valid
   outcome. Never create internals / implementation specs.
5. **For plan or code reviews** use `/review-triage`. Implement only
   `must_fix_now` by default.
6. **For planning sessions** use `/planning-capture` after `/grill-me`,
   `/grill-with-docs`, `/to-prd`, or research.
7. **At ~100k tokens** suggest `/session-close` (or `/handoff` for
   cross-tool transfer). Include both k-tokens and the status-line
   percentage for the active surface: ~39% on Codex's current 258.4k
   effective window, 50% on Sonnet 4.6 / Haiku 4.5, or 10% on Opus 4.7.
   Don't push past ~120k: ~46% / 60% / 12% respectively.
8. **Code is the truth.** Re-derive *how* from code. Do not write internals
   docs that mirror code structure.

## Context discipline

- Locate with `rg`/`grep`, then read narrow ranges — don't read whole files
  when a range works, and don't re-read what's already in context.
- Keep command output small: scoped diffs (`git diff -- <path>`), single test
  files, quiet flags. Don't dump full logs or directory trees.
- Use exact identifiers (file / function / path / widget names) so searches
  target the right place.

## Canonical docs (pull on demand)

Documentation is agent-first and human-readable second: use it to make correct
development decisions without loading unnecessary context.

Keep one canonical source of truth per fact. Prefer linking or naming the
source doc over copying content, and update the smallest valuable set of files.

- `docs/requirements/` — agreed finished-project behavior, constraints,
  acceptance criteria, non-goals, and user expectations. Read when scope or
  expected behavior is ambiguous. Do not store current status here.
- `docs/design/` — implementation approach: technology choices, algorithms,
  boundaries, protocols, and tradeoffs. Read when designing across modules.
  Ask before changing a standing design decision. If code and design disagree,
  report the conflict instead of silently choosing one.
- `docs/adr/` — recorded decisions and non-obvious mechanics. Search when something looks weird.
- `docs/implementation-notes.md` — rare durable invariants / contracts / gotchas.
- `activeContext.md`, `roadmap.md`, `progress.md` — live state, phase/checklist
  state, and cycle history. Keep status out of requirements and design.

## Skills (auto-dispatch via description)

- `/session-open` — first session entry.
- `/next-slice` — pick + start one atomic code change.
- `/planning-capture` — classify planning output into durable docs.
- `/doc-update` — selective durable-doc update.
- `/review-triage` — sort review findings.
- `/session-close` — close one step or session; keeps `activeContext.md` minimal/high-signal.
- `/handoff` — cross-tool / cross-model standalone packet (alternative to `/session-close` when handing to a non-Claude tool).

## Non-obvious gotchas

<!-- Add per-project freezes, hidden invariants, in-progress refactors here.
     If empty, leave empty. Do not pad. -->
