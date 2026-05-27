# Agent Instructions

## Workflow

- `rel-claude-v1/FINAL-WORKFLOW.md` is the canonical workflow. Older `docs/`
  and `opus/` workflow drafts are historical unless explicitly requested.
- Prefer implementation reality over stale documentation.
- Keep always-loaded context small; load only the docs needed for the current task.
- Before acting, identify the current mode: planning, implementation, review, documentation update, or session close.
- Use skills for repeated workflows instead of asking the user to repeat long prompts.

## Documentation Policy

- Requirements docs define what must be true.
- Design docs and ADRs define why the system has its shape.
- `roadmap.md`, `activeContext.md`, and `progress.md` define where the project is and what is next.
- Code is the source of truth for how the implementation works.
- Do not create internals specs that duplicate code structure.
- Write implementation notes only for durable invariants, protocols, contracts, gotchas, or navigation.
- Documentation is agent-first and human-readable second.
- Keep one canonical source of truth per fact; prefer pointers over repeated explanations.

## Documentation Update Triggers

- Update requirements only when external behavior, constraints, acceptance criteria, or non-goals change.
- Update design/ADR docs only when architectural decisions, tradeoffs, technology choices, or boundaries change.
- Update `roadmap.md`, `activeContext.md`, or `progress.md` when progress, phase, blockers, or the next step changes.
- Update implementation notes only when a durable invariant, gotcha, protocol, or code navigation hint changes.
- If no durable docs need updates, say so explicitly.

## Session Start

- Inspect `activeContext.md`, `roadmap.md`, newest `handoff-*.md` if present, relevant requirements/design docs, recent git state, and relevant code.
- Do not load all docs by default.
- Determine one next atomic step before implementing.

## Session Close

- When context is high or work is stopping, prepare a concise continuation note.
- Include changed files, current state, next atomic step, blockers, docs updated, and docs intentionally not updated.
- Reference existing docs and code paths instead of repeating their content.

## Preferred Skills

- `planning-capture` for saving durable planning results.
- `next-slice` for finding the next implementable step.
- `doc-update` for selective documentation updates.
- `review-triage` for processing review findings.
- `session-close` for handoff and continuation readiness.
