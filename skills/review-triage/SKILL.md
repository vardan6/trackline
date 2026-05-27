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
5. Preserve a one-line reason for every rejected or deferred finding.
6. Print the Output.
7. If the user asked to fix, implement only `must_fix_now` items. Stop.

## Output

```
Must fix now:
  - <finding>: <one-line reason>
Should fix before phase complete:
  - <finding>: <one-line reason>
Backlog:
  - <finding>
Invalid or not worth doing:
  - <finding>: <one-line reason>
Recommended immediate action: <e.g. fix must_fix_now then /session-close (STEP mode)>
Docs impact: <which docs the accepted findings will affect, or "none">
```

## Stop conditions

- After printing Output, do not implement non-must-fix items unless the user explicitly asks.
- If no must-fix items → suggest `/session-close (STEP mode)` or `/session-close` and stop.
