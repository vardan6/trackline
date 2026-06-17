---
name: session-close
description: Close a finished step or prepare handoff. Use for /session-close.
---

# session-close

Close one step or end the session. Two modes, auto-detected, but bare
`/session-close` defaults to SESSION mode.

## When to use

**STEP mode** — finishing one roadmap step, continuing afterward:
- Just finished a roadmap step.
- User says: "wrap this step", "close the cycle", "we're done with this step", "tick that off".

**SESSION mode** — ending the session (may also be ending a step at the same time):
- Context around 100k tokens (`hooks/README.md` owns the per-model percentages).
- End of day or end of phase.
- Switching agents.
- User says: "wrap up", "let's stop here", "end the session", "we're done for today".
- User invokes `/session-close`.

If the user explicitly invokes `/session-close` with no qualifier, treat it as
**SESSION mode by default**. Only use **STEP mode** when the user clearly says
they are closing just one finished step and will continue working afterward.
Ask a clarifying question only when the user's wording directly conflicts with
those defaults.

## Do NOT use when

- Updating durable docs without closing → `/doc-update`.
- Capturing a planning session → `/planning-capture`.
- Transferring to a non-Claude tool or different model that doesn't know this workflow → `/handoff` (standalone packet).
- Mid-step, still implementing → keep going; this skill runs at the *end* of a step.

## Inputs (read order)

1. `roadmap.md` (find the unchecked step that was just finished).
2. `activeContext.md` (current "in progress" section).
3. Recent git diff (verify what actually shipped).
4. **SESSION mode only:** the conversation — identify what was decided, tried, and discarded across the whole session.

## Steps

1. **Identify mode** (STEP or SESSION) using the default rule in "When to use".

2. **STEP actions** (always run):
   - Confirm the step just finished from `activeContext.md` + the current unchecked item in `roadmap.md`. Confirm in one sentence with the user if ambiguous.
   - Tick the checkbox in `roadmap.md` for the finished step. Do not reword surrounding items.
   - Append one bullet to `progress.md`:
     `- <YYYY-MM-DD>: <step name> — <one-line outcome>`. No multi-line entries.
   - Refresh `activeContext.md`: replace the "current task / in progress" section with the next unchecked step from `roadmap.md`.
   - Keep `activeContext.md` tiny. Default shape: mode, phase/slice, one-line state, next atomic step, optional next-after-next, blockers/env. Move history, decision logs, and dead ends to `progress.md`, ADRs, or a handoff only when truly needed.
   - Keep `roadmap.md` checklist-first. Record current phase and unchecked items, but do not let it turn into narrative status reporting.
   - Do NOT touch `docs/requirements/`, `docs/design/`, `docs/adr/` in STEP mode. If the step changed scope or architecture, stop and tell the user — run `/doc-update` before continuing.

3. **SESSION-only actions** (run after STEP actions when in SESSION mode):
   - Run the `/doc-update` decision table once: did any durable doc change across the session? Update only those.
   - Expand the `activeContext.md` update to include:
     - blockers
     - open questions
     - "discarded as noise" — failed hypotheses or dead ends likely to be retried this session
   - Decide if a handoff file is needed. Create `handoff-<YYYY-MM-DD-HHMM>.md` at repo root ONLY if:
     - loose ends are too detailed for `activeContext.md`, OR
     - mid-phase transfer with non-trivial context that doesn't belong in `activeContext.md`.
   - Keep the handoff tiny by default. It should bridge the next session, not replay the whole one. Prefer pointers to `activeContext.md`, `roadmap.md`, `progress.md`, commits, or exact files over restating large narratives.
   - If a handoff file is needed, fill the template below.
   - **Planning-capture check:** If `/grill-me`, brainstorm, or research ran this session with no following `/planning-capture`, that planning will die with the conversation — ask whether to run `/planning-capture` first (default yes). `/grill-with-docs` captures inline, so it needs no prompt. Otherwise resolve silently. Gate only; do not capture here.

4. **Commit boundary:** never commit automatically. If the user requested a
   commit or a substantial phase/checkpoint just completed, ask whether to
   commit and suggest a message. Do not make committing the next workflow step.

5. Print the Output.

## Handoff template (SESSION mode only, if needed)

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
<usually /session-open for orientation or /next-slice for implementation>
```

## Output

```
Mode: STEP | SESSION
Roadmap: <step> — ticked.
progress.md: <bullet added>
activeContext.md: next step → <one sentence>
                  [SESSION only] + blockers, open questions, discarded as noise
Scope/arch changes detected: yes | no — <if yes, recommend /doc-update before continuing>
docs updated this session: <SESSION only — list or "none">
docs intentionally not updated: <SESSION only — list with reason>
handoff file: <SESSION only — handoff-*.md path or "not needed — activeContext.md is enough">
Uncaptured planning: <SESSION only — "none" | "/grill-me ran, not captured — asked">
Commit: <"not requested" or "ask user — <suggested message>">
Suggested next skill: /next-slice (implement) | /session-open (orient)
```

## Stop conditions

- After printing Output, stop. Do not auto-commit, do not chain into the next slice.
- If mode is STEP but scope/architecture changed → stop and suggest `/doc-update` before `/next-slice`.
- If SESSION mode finds uncaptured planning (`/grill-me`/brainstorm/research with no following `/planning-capture`) → ask before closing; don't print a clean close. Happy path closes silently.
- If `activeContext.md` does not exist → SESSION mode creates it with the template content (this is the one creation exception — every project needs this file). STEP mode tells the user to invoke SESSION mode first.
- If the user has uncommitted changes, mention them in Output but do not commit unless asked.
- If `activeContext.md`, the latest handoff, or `roadmap.md` have grown into narrative documents, trim them as part of the close-out instead of preserving repeated context.
