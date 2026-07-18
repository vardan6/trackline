# AGENTS.md

> Router for coding agents. Instructions and routing only — a line stays only
> if it changes a future decision.

## State

- Project state needed → read `activeContext.md`, then `roadmap.md`.
- Read the newest `handoff-*.md` only if either state file references it or
  leaves state unclear.

## Route the work

- Ambiguous continuation ("continue", "where are we?") → `/session-open`.
- Next implementation change, including at session start → `/next-slice`.
- Finished step → `/session-close` STEP mode; ending session → SESSION mode.
- Planning output after research or grilling → `/planning-capture`.
- Review a plan → `/plan-review`; code → `/cross-review`; findings →
  `/review-triage`.
- Durable documentation check → `/doc-update`.
- Cross-tool or cross-model transfer → `/handoff`.

Direct tasks and explicit skill requests skip `/session-open`. One atomic
vertical slice per cycle.

## Rules

- Reuse context already loaded; do not reread unchanged files. Search first
  (`rg` with exact identifiers), read narrow ranges, keep command output small.
- At ~100k tokens suggest `/session-close` or `/handoff`; no new work past
  ~120k. `hooks/README.md` owns the details.
- Code is implementation truth; requirements, design, and ADRs are decision
  truth — report conflicts and ask before changing a standing decision.
- One canonical home per fact. Never create internals docs that mirror code;
  keep status out of requirements and design.

## Docs — load only when the task needs them

- Scope or expected behavior unclear → `docs/requirements/` (finished
  behavior, constraints, acceptance criteria, non-goals, user expectations).
- Designing across modules → `docs/design/` (architecture, algorithms,
  boundaries, protocols, tradeoffs).
- Code looks surprising → `docs/adr/` (durable decisions, non-obvious
  rationale).
- Rare invariants, contracts, gotchas → `docs/implementation-notes.md`.

## Non-obvious gotchas

<!-- Project-specific freezes, hidden invariants, in-progress refactors.
     If empty, leave empty. -->
