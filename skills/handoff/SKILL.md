---
name: handoff
description: Close session state and prepare a continuation packet for another session, agent, or tool.
argument-hint: "What will the next session be used for?"
---

# handoff

## Not this skill

- Ending without requesting a transfer packet → `/session-close`.

## Inputs (read order)

1. Requested recipient or next-session focus, if provided.
2. Installed `/session-close` skill; required dependency, shipped alongside this skill.

## Steps

1. Run `/session-close` in SESSION mode with a handoff packet required. Pass the recipient/focus and any existing packet from this session. Its procedure owns state reconciliation and the handoff template; do not duplicate either here.
2. Confirm its output accounts for roadmap completion, progress history, current state, unfinished work, and the repository-root packet. A separate user invocation of `/session-close` is unnecessary.

## Output

Return the session-close summary and the handoff path, including any deferred documentation or unresolved work.

## Stop conditions

- If `/session-close` is unavailable, report the missing dependency; do not claim state was saved.
- Stop after the summary. Do not commit or start the next session's work.
