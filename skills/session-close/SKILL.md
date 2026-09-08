---
name: session-close
description: Close a completed step or end a workflow session.
---

# session-close

Reconcile session state; preserve completed outcomes and unfinished work.

## Mode

Two modes, and the choice is the first thing to settle:

- **STEP** — the user is closing one finished roadmap step and continuing
  afterward ("wrap this step", "tick that off", "we're done with this step").
- **SESSION** — the session is ending, including mid-task or after multiple slices.
  Cover the whole session, whether or not STEP closes ran.

Bare `/session-close` with no qualifier is **SESSION**. Ask a clarifying question
only when the user's wording directly conflicts with these defaults.

## Not this skill

- Updating durable docs without closing → `/doc-update`.
- Capturing planning without ending the session → `/planning-capture`.
- Mid-step and continuing → keep going; ending mid-step uses SESSION.

## Inputs (read order)

1. Conversation and any handoff already produced this session: identify scope, outcomes, decisions, verification, and unfinished work. Reuse loaded content.
2. `activeContext.md`, relevant `roadmap.md` items, and recent `progress.md` entries; compare recorded state with those outcomes.
3. Relevant git diffs and session commits, including uncommitted work. A clean diff does not mean nothing happened; do not attribute unrelated changes to this session.

## Steps

1. **Identify mode** (STEP or SESSION) using the rule in "Mode".

2. **Reconcile state:** STEP covers the finished step; SESSION covers all work since the session began.
   - Match verified completed outcomes to roadmap items and tick every completed item in scope. Leave incomplete or unverified work unchecked; preserve unrelated items and other Tracks. Zero completed items is valid.
   - Append missing completion entries to `progress.md`: `- <YYYY-MM-DD>: <step name> — <one-line outcome>`. Record completed unplanned work too. Compare existing entries first; prior STEP closes or repeated closes must not duplicate history.
   - Refresh `activeContext.md` with actual current state and the next action. Preserve unfinished implementation, planning, or review and its resumption point; do not advance past it merely because the session ended.
   - Keep `activeContext.md` tiny. Default shape: mode, phase/slice, one-line state, next atomic step, optional next-after-next, blockers/env. Move history, decision logs, and dead ends to `progress.md`, ADRs, or a handoff only when truly needed.
   - Keep `roadmap.md` checklist-first. Record current phase and unchecked items, but do not let it turn into narrative status reporting.
   - STEP only: do not touch requirements/design/ADRs. If durable behavior, scope, or architecture changed, report `/doc-update` as the next action. SESSION uses the full-session check below.

3. **SESSION-only actions:**
   - **Durable-change test:** inspect the whole session for changed behavior, architecture, contracts, or invariants not yet reflected in durable docs. If none, record "none". Otherwise invoke `/doc-update`, unless the user declined documentation updates; then preserve the pending changes in the handoff and report them as deferred. Do not repeat updates already completed or claim deferred docs are current.
   - Expand the `activeContext.md` update to include:
     - blockers
     - open questions
     - "discarded as noise" — failed hypotheses or dead ends likely to be retried this session
   - Write a handoff whenever work is unfinished, `/handoff` requested a packet, or loose ends exceed `activeContext.md`. Use `handoff-<YYYY-MM-DD-HHMM>.md` at repo root; choose a unique suffix if an unrelated file already occupies that path.
   - Keep the handoff tiny by default. It should bridge the next session, not replay the whole one. Prefer pointers to `activeContext.md`, `roadmap.md`, `progress.md`, commits, or exact files over restating large narratives.
   - Read [HANDOFF-TEMPLATE.md](HANDOFF-TEMPLATE.md) when writing a packet. Link it from `activeContext.md`. Include unfinished work, verification gaps, settled decisions, unresolved questions, and a concrete next action; tailor to the requested recipient or focus.
   - If a handoff already exists from this session, inspect and reuse/update it instead of creating a duplicate. A legacy vendor packet outside the repo is input: preserve its original and write the reconciled packet at repo root. A packet alone never proves state files were updated.
   - **Planning-capture check:** Preserve uncaptured planning in the handoff, separating settled decisions from open questions. Run `/planning-capture` if authorized; otherwise report durable capture as pending. Incomplete planning must not prevent saving session state.

4. **Commit boundary:** never commit automatically. If the user requested a
   commit or a substantial phase/checkpoint just completed, ask whether to
   commit and suggest a message. Do not make committing the next workflow step.

5. Print the Output.

## Output

```
Mode: STEP | SESSION
Roadmap: <completed items reconciled; unfinished items retained; or none>
progress.md: <entries added, or already recorded / none>
activeContext.md: next step → <one sentence>
                  [SESSION only] + blockers, open questions, discarded as noise
Scope/arch changes detected: yes | no — <if yes, recommend /doc-update before continuing>
docs updated this session: <SESSION only — list or "none">
docs intentionally not updated: <SESSION only — list with reason>
handoff file: <SESSION only — handoff-*.md path or "not needed — activeContext.md is enough">
Uncaptured planning: <SESSION only — none | captured | preserved in handoff; durable capture pending>
Commit: <"not requested" or "ask user — <suggested message>">
Suggested next skill: /next-slice (implement) | /session-open (orient)
```

## Stop conditions

- After printing Output, stop. Do not auto-commit, do not chain into the next slice.
- If mode is STEP but scope/architecture changed → stop and suggest `/doc-update` before `/next-slice`.
- If completion is uncertain, leave the item unchecked and record the uncertainty in the handoff. Save known state before asking for missing information.
- If `activeContext.md` does not exist → SESSION mode creates it with the template content (this is the one creation exception — every project needs this file). STEP mode tells the user to invoke SESSION mode first.
- If the user has uncommitted changes, mention them in Output but do not commit unless asked.
- If `activeContext.md`, the latest handoff, or `roadmap.md` have grown into narrative documents, trim them as part of the close-out instead of preserving repeated context.
