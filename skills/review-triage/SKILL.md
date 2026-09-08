---
name: review-triage
description: Validate and prioritize findings from plan or code reviews.
---

# review-triage

Sort review findings, route accepted ones to durable docs, implement only must-fix-now.

## Not this skill

- Triaging issues (Linear, GitHub) → `/triage`.
- Capturing planning output → `/planning-capture`.
- Feedback has no concrete, checkable findings → handle directly unless the user requests structured triage.

## Inputs (read order)

1. Concrete review findings from a file, pasted review, or conversation; the delivery format does not determine eligibility.
2. Relevant code paths cited in the findings.
3. Relevant requirement / design / ADR — only if a finding disputes them.
4. `activeContext.md` and `roadmap.md`.

## Steps

1. Read inputs.
2. For each finding, classify into exactly one bucket:
   - `must_fix_now` → correctness bug, safety, data loss, broken contract, high-risk regression, blocker.
   - `should_fix_before_phase_complete` → valid issue but not blocking the current slice.
   - `backlog` → useful improvement, not needed this phase.
   - `invalid_or_not_worth_doing` → incorrect, already handled, too costly for value, out of scope.
3. Validate every finding against code, not only docs. Reject vague findings without concrete risk. Reuse the review table's `Risk` / `Value` / `Effort` ratings where they hold; adjust with a one-line reason when they don't.
4. Route accepted findings not fixed now into `roadmap.md` as slices, each citing this review file + the finding's heading. Restoring intended behavior needs no other citation; *changing* it goes through `/doc-update` after the fix.
5. Print the Output.
6. If the user asked to fix, implement only `must_fix_now` items. Stop.

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

Then the action summary:

```
Recommended immediate action: <e.g. fix must_fix_now then /session-close (STEP mode)>
Docs impact: <which docs the accepted findings will affect, or "none">
```

## Stop conditions

- After printing Output, do not implement non-must-fix items unless the user explicitly asks.
- If no must-fix items → suggest `/session-close (STEP mode)` or `/session-close` and stop.
