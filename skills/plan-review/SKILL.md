---
name: plan-review
description: Review captured plans; best run by the developer in another provider’s session.
---

# plan-review

Cross-validate the captured plan docs in the session the developer opened for it. Recommended: the strongest model from a provider *different* from the planner — the developer chooses the session; this skill never obtains one. Findings file only; never edit the plan.

## Not this skill

- Reviewing implemented code → `/cross-review`.
- Triaging an existing findings file → `/review-triage`.
- The plan is still being discussed → `/grill-me`.

## Inputs (read order)

1. The docs the plan touched: `docs/requirements/`, `docs/design/`, `docs/adr/`, `roadmap.md` — find the recently changed ones via `git log`/`git diff`.
2. `activeContext.md` for scope.
3. Existing code only where the plan makes assumptions about it.

## Steps

1. Same provider as the planner (or unknown) → warn: a different provider's session is strongly recommended. Ask whether to continue here; continue only on the developer's confirmation, and record `same-provider review (confirmed)` in the findings header.
2. Read inputs. Identify what the plan commits to: behavior, architecture, sequencing, slice breakdown.
3. Cross-validate the documents against each other: requirements ↔ design ↔ ADRs ↔ roadmap must tell one consistent story. Hunt contradictions, items present in one doc but missing from another, terminology drift, and misspelled names (files, functions, terms) that could misroute a future agent.
4. Challenge the plan: missing requirements, gaps, wrong assumptions about existing code, hidden dependencies between slices, undersized or oversized slices, risky sequencing, incorrect logic, unstated tradeoffs, conflicts with existing ADRs.
5. Propose improvements: what could be done even better — a simpler design, safer sequencing, an existing tool instead of a custom build. If clearly worth it, recommend adding it; if it conflicts with a recorded decision, flag the conflict instead of overriding it. Record these as `enhancement` findings, separate from defects.
6. Verify every claim against the docs (and code, where the plan depends on it). Discard your own vague findings — every kept finding names the doc and the exact claim it disputes.
7. Write findings to `docs/reviews/plan-review-<date>-<topic>.md` in the findings file format below.
8. Print the Output. Do not edit the plan docs.

## Findings file format

Short header — scope (docs reviewed), reviewer model + provider, date — then one table. The finding description comes first; the ratings sit in the adjacent columns:

| # | Finding | Why it matters | Severity | Risk | Value | Effort |
|---|---------|----------------|----------|------|-------|--------|

- `Severity`: `high` | `med` | `low` | `enhancement` — the reviewer's guess; `/review-triage` decides the final priority.
- `Risk` / `Value` / `Effort`: `high` | `med` | `low` — same values and column order as `/review-triage`, so triage can reuse the ratings directly.
- Detail that does not fit a row (evidence, suggested wording, alternatives) goes in a `## Details` section below the table, referenced by row number.

## Output

```
Review written: docs/reviews/<file>
Findings: <N> (<n> high-severity, <m> enhancements)
Next: original planner validates via /review-triage, revisits the plan, then commit
```

## Stop conditions

- Never launch another coding agent or harness (`claude`, `codex`, `gemini`, …) to get the reviewer; a different-provider review runs in a session the developer opens.
- Never edit requirements / design / ADR / roadmap — findings only.
- If the plan docs cannot be located → ask for paths, then stop.
