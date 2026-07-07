# AGENTS.md

> Router for coding agents. Keep only rules that change a future decision.

## Current state

- Read `activeContext.md` and `roadmap.md` when project state is needed.
- Read the newest `handoff-*.md` only when those files reference it or leave
  state unclear.

## Route the work

- Ambiguous continuation ("continue", "where are we?") → `/session-open`.
- Next implementation change, including at session start → `/next-slice`.
- Finished step or session → `/session-close` (STEP or SESSION mode).
- Planning output after research or grilling → `/planning-capture`.
- Review a plan → `/plan-review`; review code → `/cross-review`; triage
  findings → `/review-triage`.
- Durable documentation check → `/doc-update`.
- Cross-tool or cross-model transfer → `/handoff`.

Direct tasks and explicit skill requests do not require `/session-open` first.
Implement one atomic vertical slice per cycle.

## Working rules

- Reuse context already loaded; do not reread unchanged files.
- Locate with `rg`/`grep`, then read narrow ranges and keep command output small.
- Use exact identifiers so searches target the relevant code.
- At about 100k tokens, suggest `/session-close` or `/handoff`; do not begin new
  work around 120k. `hooks/README.md` owns threshold details.
- Code is current implementation truth. Requirements, design, and ADRs are
  decision truth; report conflicts and ask before changing a standing decision.
- Do not create internals documents that mirror code.

## Canonical documents

- `docs/requirements/` — finished behavior, constraints, acceptance criteria,
  non-goals, and user expectations. Pull when scope or expected behavior is unclear.
- `docs/design/` — architecture, algorithms, boundaries, protocols, and
  tradeoffs. Pull before designing across modules.
- `docs/adr/` — durable decisions and non-obvious rationale. Search when code
  looks surprising.
- `docs/implementation-notes.md` — rare invariants, contracts, and gotchas.
- `activeContext.md`, `roadmap.md` — live state and planned work.

Keep one source of truth per fact. Keep current status out of requirements and
design, and load durable documents only when the task needs them.

## Non-obvious gotchas

<!-- Add project-specific freezes, hidden invariants, or in-progress refactors.
     If empty, leave empty. -->
