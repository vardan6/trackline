---
name: session-close
description: Prepare continuation context before stopping. Use for /session-close or /handoff.
---

# session-close

End the session cheaply for the next agent. No "save everything."

## When to use

- Context above ~50% of the active model window: about 100k on 200k, 200k on
  400k, 500k on 1M, or 525k on GPT-5.5's 1,050k window.
- End of day or end of phase.
- Switching agents.
- User says: "wrap up", "let's stop here", "end the session", "handoff".
- User invokes `/session-close` or `/handoff`.

## Do NOT use when

- Just finishing one step but continuing → `/cycle-close`.
- Updating durable docs only → `/doc-update`.
- Capturing a planning session → `/planning-capture`.

## Inputs (read order)

1. Git state (changed files this session, staged + unstaged).
2. `docs/current-state.md` and `docs/roadmap.md`.
3. The current conversation — identify what was decided, tried, and discarded.

## Steps

1. Identify what actually changed this session: shipped behavior, failed approaches, decisions made, open loops.
2. Run the `/doc-update` decision table once: did any durable doc change? Update only those.
3. Update `docs/current-state.md`:
   - current phase
   - next atomic step
   - blockers
   - open questions
   - "discarded as noise" — failed hypotheses or dead ends likely to be retried
4. Decide if a handoff file is needed. Create `docs/handoffs/<YYYY-MM-DD-HHMM>.md` ONLY if:
   - loose ends are too detailed for `current-state.md`, OR
   - mid-phase transfer with non-trivial context that doesn't belong in current-state.
   Otherwise skip the handoff file.
5. If a handoff file is needed, fill the template below.
6. Print the Output.

## Handoff template (only if used)

```
# Handoff — <date> <time>

## Where we are
<current phase + literal next step>

## Changed files
- <path>: <short reason>

## Implemented
- <durable outcome, not every edit>

## Open loops
- <unfinished item; file:line if useful>

## Decisions made
- <decision + one-line why; promote to ADR if durable>

## Discarded as noise
- <dead end or failed hypothesis likely to be retried>

## Verification
- <command>: <result>

## Docs
- Updated: <docs>
- Intentionally not updated: <docs and reason>

## Next
<one atomic step>

## Suggested next skill
<usually /session-open at next start, then /next-slice>
```

## Output

```
current-state.md: updated (phase, next step, blockers, open questions, discarded).
docs updated this session: <list or "none">
docs intentionally not updated: <list with reason>
handoff file: <docs/handoffs/...md or "not needed — current-state is enough">
Next session: invoke /session-open first, expect mode=<mode>, next=<one sentence>.
```

## Stop conditions

- After printing Output, stop. Do not commit, do not start new work.
- If the user has uncommitted changes, mention them in Output but do not commit unless asked.
- If `docs/current-state.md` does not exist, create it with the template content (this is the one creation exception — every project needs this file).
