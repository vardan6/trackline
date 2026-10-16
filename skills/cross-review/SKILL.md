---
name: cross-review
description: Review implemented work against its specs; best run by the developer in another provider’s session.
---

# cross-review

Review implemented work in the session the developer opened for it. Recommended: the strongest model from a provider *different* from the implementer — the developer chooses the session; this skill never obtains one. Findings file only; never fix anything.

## Not this skill

- Reviewing a plan instead of code → `/plan-review`.
- Triaging an existing findings file → `/review-triage`.
- Asked to fix issues directly — that is implementation, not review.

## Inputs (read order)

1. The diff since the last known-good commit (`git log`, then `git diff <commit>..HEAD`); confirm the range with the user if ambiguous.
2. The requirements / design / ADRs covering the changed area.
3. `roadmap.md` for what the work claimed to deliver.

## Steps

1. Same provider as the implementer (or unknown) → warn: a different provider's session is strongly recommended. Ask whether to continue here; continue only on the developer's confirmation, and record `same-provider review (confirmed)` in the findings header.
2. Read the diff first, then the docs it should satisfy.
3. Cross-validate the implementation **against the documentation**, in both directions: behavior the docs promise that the code does not deliver (misimplementation, missing implementation), and behavior the code has that no doc records. Within the code itself, hunt bugs, gaps, and incorrect logic.
4. Propose improvements: what could be done even better — a simpler or safer approach, an existing utility instead of new code, a missing test or verification. If clearly worth it, recommend adding it; if it conflicts with a recorded design decision or ADR, flag the conflict instead of overriding it. Record these as `enhancement` findings, separate from defects.
5. Verify every claim against code — cite `file:line` for each finding; discard your own vague findings.
6. Write findings to `docs/reviews/code-review-<date>-<topic>.md` in the findings file format below.
7. Print the Output. Do not fix anything.

## Findings file format

Short header — range reviewed, docs consulted, reviewer model + provider, date — then one table. The finding description comes first; the ratings sit in the adjacent columns:

| # | Finding | Evidence (file:line) | Severity | Risk | Value | Effort |
|---|---------|----------------------|----------|------|-------|--------|

- `Severity`: `high` | `med` | `low` | `enhancement` — the reviewer's guess; `/review-triage` decides the final priority.
- `Risk` / `Value` / `Effort`: `high` | `med` | `low` — same values and column order as `/review-triage`, so triage can reuse the ratings directly.
- Detail that does not fit a row (failure scenario, suggested fix, alternative) goes in a `## Details` section below the table, referenced by row number.

## Output

```
Review written: docs/reviews/<file>
Range reviewed: <commit>..HEAD
Findings: <N> (<n> must-fix candidates, <m> enhancements)
Next: original agent validates via /review-triage; accepted findings usually fold into roadmap.md
```

## Stop conditions

- Never launch another coding agent or harness (`claude`, `codex`, `gemini`, …) to get the reviewer; a different-provider review runs in a session the developer opens.
- Never modify code or docs — findings file only.
- If the diff range or scope is unclear → ask one question, then stop.
