---
name: doc-update-lite
description: Selectively update durable project docs after implementation.
argument-hint: "Optional: implemented change or docs scope"
---

# Doc Update Lite

Use this skill after implementation, review fixes, or phase progress.

## Goal

Update only documentation that has durable value.

## Decision Table

Update requirements when:

- external behavior changed
- constraints changed
- acceptance criteria changed
- user-facing non-goals changed

Update design or ADR docs when:

- architecture changed
- module boundaries changed
- technology choices changed
- tradeoffs or rejected alternatives changed

Update roadmap/current-state when:

- a phase or subphase progressed
- the next step changed
- blockers changed
- the implementation state changed in a way future sessions must know

Update implementation notes only when:

- a durable invariant changed
- a protocol, schema, or contract changed
- there is a non-obvious gotcha
- future agents need a navigation hint to find code quickly

Do not update docs for:

- private helper changes
- obvious code structure
- function-by-function behavior
- temporary implementation plans
- review discussion history
- formatting-only or mechanical changes

## Required Behavior

- Prefer editing existing docs.
- Create new docs only when a durable category has no home.
- Keep updates concise.
- Reference code paths instead of explaining all implementation details.
- Explicitly say when no durable docs needed updates.

## Final Response

Report:

- docs updated
- docs intentionally not updated
- reason for any skipped docs
- next recommended action
