---
name: plan-review
description: Cross-model review of a freshly captured plan by a different provider's strongest model. Cross-validates requirements, design, ADRs, and roadmap for gaps, missing items, incorrect or inconsistent logic, and better alternatives; writes a rated findings table to docs/reviews/. Use for /plan-review or when asked to review the plan.
---

# plan-review

Review a freshly captured plan as the second-provider model — ideally the strongest model available from a provider *different* from the one that planned. Findings file only; never edit the plan.

## When to use

- After `/planning-capture` wrote requirements / design / ADRs / roadmap, in a session with a *different provider's* strongest model than the one that planned.
- User invokes `/plan-review`.

## Do NOT use when

- Reviewing implemented code → `/cross-review`.
- Triaging an existing findings file → `/review-triage`.
- The plan is still being discussed → `/grill-me`.

## Inputs (read order)

1. The docs the plan touched: `docs/requirements/`, `docs/design/`, `docs/adr/`, `roadmap.md` — find the recently changed ones via `git log`/`git diff`.
2. `activeContext.md` for scope.
3. Existing code only where the plan makes assumptions about it.

## Steps

1. Read inputs. Identify what the plan commits to: behavior, architecture, sequencing, slice breakdown.
2. Cross-validate the documents against each other: requirements ↔ design ↔ ADRs ↔ roadmap must tell one consistent story. Hunt contradictions, items present in one doc but missing from another, terminology drift, and misspelled names (files, functions, terms) that could misroute a future agent.
3. Challenge the plan: missing requirements, gaps, wrong assumptions about existing code, hidden dependencies between slices, undersized or oversized slices, risky sequencing, incorrect logic, unstated tradeoffs, conflicts with existing ADRs.
4. Propose improvements: what could be done even better — a simpler design, safer sequencing, an existing tool instead of a custom build. If clearly worth it, recommend adding it; if it conflicts with a recorded decision, flag the conflict instead of overriding it. Record these as `enhancement` findings, separate from defects.
5. Verify every claim against the docs (and code, where the plan depends on it). Discard your own vague findings — every kept finding names the doc and the exact claim it disputes.
6. Write findings to `docs/reviews/plan-review-<date>-<topic>.md` in the findings file format below.
7. Print the Output. Do not edit the plan docs.

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

- Never edit requirements / design / ADR / roadmap — findings only.
- If the plan docs cannot be located → ask for paths, then stop.
