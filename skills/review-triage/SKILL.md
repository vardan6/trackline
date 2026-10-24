---
name: review-triage
description: Validate and prioritize findings from plan or code reviews.
---

# review-triage

Sort review findings and route accepted ones; code reviews implement only must-fix-now, plan reviews revise the plan.

## Not this skill

- Triaging issues (Linear, GitHub) → `/triage`.
- Capturing planning output → `/planning-capture`.
- Feedback has no concrete, checkable findings → handle directly unless the user requests structured triage.

## Inputs (read order)

1. Concrete review findings from a file, pasted review, or conversation; the delivery format does not determine eligibility. Read each finding's Details with its row.
2. Code paths cited in the findings — for a plan review, only where a finding concerns existing behavior.
3. Relevant requirement / design / ADR — only if a finding disputes them.
4. `activeContext.md` and `roadmap.md`.

## Steps

1. Read inputs.
2. For each finding, classify into exactly one bucket:
   - `must_fix_now` → correctness bug, safety, data loss, broken contract, high-risk regression, blocker.
   - `should_fix_before_phase_complete` → valid issue but not blocking the current slice.
   - `backlog` → useful improvement, not needed this phase.
   - `invalid_or_not_worth_doing` → incorrect, already handled, too costly for value, out of scope.
3. Validate every finding: a code-review finding against code, not only docs; a plan-review finding against the plan docs, plus code where it concerns existing behavior. Reject vague findings without concrete risk. Reuse the review table's `Risk` / `Value` / `Effort` ratings where they hold; adjust with a one-line reason when they don't.
4. Code review: route accepted findings not fixed now into `roadmap.md` as slices, each citing this review file + the finding's heading. Restoring intended behavior needs no other citation; *changing* it goes through `/doc-update` after the fix.
5. Plan review: revise the disputed docs for every accepted finding (`backlog` → the project's deferred-work doc; without one it stays in the review as `deferred`). Map every recommendation in a finding's row and Details — behavior, test, ordering, bound, owner — to the doc location now carrying it, or reject it in one line; revise until none is unmapped, since implementation reads the plan, not the review. Add a checked `Plan review and triage, HITL` roadmap item linking the review.
6. Print the Output.
7. Code review: if the user asked to fix, implement only `must_fix_now` items. Stop.

## Output

A must_fix_now callout first, so blockers are seen before the table:

```
Must fix now (N): #<row>, #<row>, ...   (or "none")
```

Then one canonical table — every finding, never split, sorted by `Priority`
(must_fix_now first). `Risk` and `Value` sit adjacent because their comparison
drives triage: high risk + low value leans to `backlog`, not a fix now.
`Priority` carries the bucket (no re-listing); `Reason` is one line, required for
every deferred or rejected finding.

Allowed cell values:

- `Risk` / `Value` / `Effort`: `high` | `med` | `low`
- `Priority`: `must_fix_now` | `should_fix_before_phase_complete` | `backlog` | `invalid`

Example (concrete rows, not a template to copy verbatim):

| # | Finding | Risk | Value | Effort | Priority | Reason |
|---|---------|------|-------|--------|----------|--------|
| 1 | Reset token never expires; reusable indefinitely | high | high | low | must_fix_now | security hole, trivial fix |
| 2 | No rate limit on reset endpoint | high | low | med | backlog | high risk but low value now; revisit before launch |
| 3 | Duplicated email-format check in two handlers | low | low | low | invalid | cosmetic; not worth the churn |

Plan review: then one coverage row per recommendation; `Landed in` is a doc location, `deferred`, or `rejected: <reason>`.

| # | Recommendation | Landed in |
|---|----------------|-----------|
| 1a | Stale telemetry never follows a broker event | `design/api.md` §Async Work; roadmap AR2a |

Then the action summary:

```
Recommended immediate action: <e.g. fix must_fix_now then /session-close (STEP mode)>
Docs impact: <which docs the accepted findings will affect, or "none">
```

## Stop conditions

- Code review: after printing Output, do not implement non-must-fix items unless the user explicitly asks.
- Plan review: never print Output while a recommendation is unmapped; accepting a finding is not a mapping.
- If no must-fix items → suggest `/session-close (STEP mode)` or `/session-close` and stop.
