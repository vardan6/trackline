---
name: cycle-close
description: Close a finished roadmap step. Use for /cycle-close or "wrap this step".
---

# cycle-close

End-of-step ritual. Deterministic. No creativity.

## When to use

- Immediately after finishing one roadmap step.
- User says: "wrap this up", "close the cycle", "we're done with this step".
- User invokes `/cycle-close`.

## Do NOT use when

- Updating requirements / design / ADR → `/doc-update`.
- Closing the whole session → `/session-close`.
- Picking the next step → `/next-slice` (after this skill, not instead of).

## Inputs (read order)

1. `docs/roadmap.md` (find the unchecked step that was just finished).
2. `docs/current-state.md` (current "in progress" section).
3. Recent git diff (verify what actually shipped).

## Steps

1. Identify the step just finished from the last entry in `current-state.md` and the current unchecked item in `roadmap.md`. Confirm in one sentence with the user if ambiguous.
2. Tick the checkbox in `docs/roadmap.md` for the finished step. Do not reword surrounding items.
3. Append one bullet to `docs/progress.md`:
   `- <YYYY-MM-DD>: <step name> — <one-line outcome>`. No multi-line entries.
4. Refresh `docs/current-state.md`: replace the "current task / in progress" section with the next unchecked step from `roadmap.md`. Keep "open questions" and "discarded as noise" sections intact.
5. Do NOT touch `docs/requirements/`, `docs/design/`, `docs/adr/`. If the cycle changed scope or architecture, stop and tell the user — that is `/doc-update`'s job, not this skill's.
6. Suggest a commit message. Do not run `git commit` unless the user confirms.
7. Print the Output.

## Output

```
Roadmap: <step> — ticked.
progress.md: <bullet added>
current-state.md: next step → <one sentence>
Scope/arch changes detected: yes | no — <if yes, recommend /doc-update>
Suggested commit:
  chore(cycle): <phase> step <n> — <one-line>
Suggested next skill: /next-slice (continue) or /session-close (stop)
```

## Stop conditions

- After printing Output, stop. Do not auto-commit, do not chain into the next slice.
- If scope or architecture changed → stop and suggest `/doc-update` before continuing.
- If the user wants to stop the session here → `/session-close`.
