---
name: session-open
description: Orient a resumed project when the user asks to continue, recover state, or identify the next workflow action. Use for /session-open.
---

# session-open

Recover project state and route to the correct workflow. Do not select an implementation slice.

## When to use

- User says: "let's continue", "where were we", "what's next", "pick up".
- User invokes `/session-open`.

## Do NOT use when

- The user gave a direct task that does not require roadmap state.
- The user explicitly invoked another applicable skill.
- Mid-session, picking the next code change → `/next-slice`.
- After finishing a roadmap step → `/session-close (STEP mode)`.
- Closing a session for handoff → `/session-close`.

## Inputs (read order, stop early if confident)

1. `activeContext.md` (treat as a cheap session-start file, not a history dump)
2. `roadmap.md`
3. Newest `handoff-*.md` — only if 1–2 reference it or state remains unclear.
4. Recent git state — only if state files disagree; inspect only relevant output.
5. Relevant code — only when an identified conflict requires verification.

Do NOT read `docs/requirements/`, `docs/design/`, or `docs/adr/` at this stage.
If `activeContext.md`, the newest handoff, or `roadmap.md` are long and narrative, flag that as workflow drift and recommend tightening them at the next `/session-close`.

## Steps

1. Reuse current state already in the conversation; do not reread unchanged files.
2. Read inputs 1–2 only when needed. Stop if they establish clear state.
3. Use inputs 3–5 only under their stated conditions.
4. Identify the project mode, including any mode explicitly named by the project.
5. Name the next workflow action. For implementation, route to `/next-slice`.
6. Print the Output. Stop.

## Output

```
Mode: <mode>
Phase: <phase from roadmap>
State: <one sentence on real current state>
Next: <one sentence workflow action>
Blocker: <if any, else "none">
Confidence: high | medium | low
```

If confidence is low, append one specific question for the user.

## Stop conditions

- After printing Output, stop. Do not implement until the user confirms or redirects.
- `activeContext.md` missing → report it; SESSION `/session-close` can create it.
- Roadmap missing or complete → ask only when roadmap continuation is required.
