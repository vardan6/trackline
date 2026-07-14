---
name: session-open
description: Start a session and name the next step. Use for /session-open.
---

# session-open

Every session begins here. Cheap, deterministic, no creativity.

## When to use

- First action of any new session.
- User says: "let's continue", "where were we", "what's next", "pick up".
- User invokes `/session-open`.

## Do NOT use when

- Mid-session, picking the next code change → `/next-slice`.
- After finishing a roadmap step → `/cycle-close`.
- Closing a session for handoff → `/session-close`.

## Inputs (read order, stop early if confident)

1. `AGENTS.md`
2. `docs/current-state.md`
3. Newest `docs/handoffs/*.md` (if any)
4. `docs/roadmap.md`
5. Recent git state (last 5 commits + uncommitted diff) — only if 1–4 disagree.
6. Relevant code — only if implementation reality contradicts docs.

Do NOT read `docs/requirements/`, `docs/design/`, or `docs/adr/` at this stage.

## Steps

1. Read inputs in order. Stop at step 4 if state is clear.
2. If docs and reality may diverge, run steps 5–6 to confirm.
3. Identify the mode: planning, plan-review, implementation, review-triage, doc-update, cycle-close, session-close.
4. Identify the next atomic step from `roadmap.md` and `current-state.md`.
5. Print the Output. Stop.

## Output

```
Mode: <mode>
Phase: <phase from roadmap>
State: <one sentence on real current state>
Next: <one sentence atomic step>
Blocker: <if any, else "none">
Confidence: high | medium | low
```

If confidence is low, append one specific question for the user.

## Stop conditions

- After printing Output, stop. Do not implement until the user confirms or redirects.
- `docs/current-state.md` missing → tell the user once; suggest `/cycle-close` after the next step creates it. Do not auto-create.
- `docs/roadmap.md` missing or no unchecked items → ask the user. Do not guess.
