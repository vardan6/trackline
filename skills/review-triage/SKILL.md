---
name: review-triage
description: Triage review findings. Use for review output or /review-triage.
---

# review-triage

Sort review findings, route accepted ones to durable docs, implement only must-fix-now.

## When to use

- After `/review` or `/security-review` produced a findings file.
- After another agent reviewed a plan or implementation.
- User pastes review notes.
- User invokes `/review-triage`.

## Do NOT use when

- Triaging issues (Linear, GitHub) → `/triage`.
- Capturing planning output → `/planning-capture`.
- The "review" is informal feedback in conversation — apply judgment, don't run this skill.

## Inputs (read order)

1. The review file or pasted findings.
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
3. Validate every finding against code, not only docs. Reject vague findings without concrete risk.
4. For accepted findings that change durable behavior, route the change through `/doc-update` after fixing.
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
