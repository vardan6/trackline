# Final Workflow 3

This version consolidates all project docs again, with `opus/03-final-workflow.md`
treated as the strongest current draft. It supersedes `docs/final-workflow.md`,
`docs/final-workflow2.md`, `opus/02-final-workflow.md`, and
`opus/03-final-workflow.md`.

The main change from `final-workflow2.md`: use root-level fast-state files
(`activeContext.md`, `progress.md`, `roadmap.md`) instead of
`docs/current-state.md`. This matches the latest Opus workflow, the Opus
AGENTS template, and the `session-open` / `cycle-close` skills. If an existing
project already has `docs/current-state.md`, migrate its useful content into
`activeContext.md` and replace it with a pointer or delete it.

## 1. Core Model

Use a 2.5-layer documentation model:

```text
Requirements = what must be true.
Design / ADRs = why the system has this shape.
Fast state = where the project is now and what is next.
Code + tests = how the implementation works.
Implementation notes = rare durable invariants, contracts, gotchas, and
navigation hints.
```

Do not maintain a standing internals, implementation, or reference spec layer.
That layer duplicates code, drifts quickly, burns tokens, and creates a false
second source of truth.

Anything worth saving from an old internals doc becomes one of:

- a requirement, if it describes externally visible behavior
- a design note or ADR, if it explains a decision or tradeoff
- a short implementation note, if it records a durable invariant or gotcha
- a code comment, if the surprise lives at one precise point in code

Everything else is rediscovered from code when needed.

## 2. Documentation Tests

Before documenting anything, ask:

```text
Will this still be useful if the code changes?
```

Before keeping any doc line, AGENTS line, or skill rule, ask:

```text
Would removing this cause the next session to make a different and worse
decision?
```

Document:

- external behavior
- user-visible requirements
- acceptance criteria
- constraints and non-goals
- architecture decisions
- rejected alternatives with reasons
- module boundaries
- protocols, schemas, and external contracts
- safety or correctness invariants
- non-obvious gotchas
- where future agents should begin reading code
- current phase and next step
- dead ends likely to be retried

Usually do not document:

- function-by-function descriptions
- private call chains
- ordinary implementation details
- obvious file maps
- temporary implementation plans after code exists
- raw review discussion history
- full transcripts as active context

## 3. Canonical File Set

Use this structure for long-running projects:

```text
AGENTS.md
activeContext.md
progress.md
roadmap.md
handoff-*.md                 # optional; root, newest wins

requirements/
  <feature>.md

design/
  <feature>.md

docs/
  adr/
    <decision>.md
  implementation-notes.md    # optional and sparse
```

Do not maintain both `activeContext.md` and `docs/current-state.md`. If a repo
already has `docs/current-state.md`, either migrate it into `activeContext.md`
or make it a tiny pointer:

```text
Fast-changing project state lives in ../activeContext.md.
```

## 4. File Responsibilities

### `requirements/`

Human-facing behavior specifications.

Update only when behavior, scope, constraints, acceptance criteria, or non-goals
change.

### `design/`

Human-facing system shape.

Update only when architecture, module boundaries, integration strategy,
technology choices, tradeoffs, or rejected alternatives change.

### `docs/adr/`

Append-only decision records.

Use for non-obvious decisions that future agents might otherwise reverse,
including rejected alternatives and unusual implementation patterns.

### `roadmap.md`

Phase plan and next work.

It should show:

- current phase
- completed steps
- next unchecked step
- blocked or deferred items

Keep this scannable. It is not a planning transcript.

### `activeContext.md`

The live agent state file.

Read it at session start. Update it as work progresses when meaningful state
changes.

It should contain:

- current phase
- current task
- current hypothesis, if relevant
- latest meaningful implementation state
- blocker or risk
- open question
- next atomic step
- discarded-as-noise notes for dead ends likely to be retried
- relevant file pointers

It should not contain:

- every command run
- a diary of the session
- copied requirements or design docs
- obvious implementation details

### `progress.md`

Append-only cycle log.

One short bullet per completed implementation cycle:

```text
- 2026-05-24: Phase 2.1 auth callback cleanup - implemented redirect guard and
  added regression test.
```

### `docs/implementation-notes.md`

Optional and sparse.

Use only for durable implementation-level facts:

- invariants
- protocols
- schemas
- contracts
- ordering constraints
- gotchas
- navigation hints

Do not turn it into an internals spec.

### `handoff-*.md`

Use only when `activeContext.md` is not enough.

Good reasons:

- context is high and there are loose ends
- a session explored dead ends that should not be repeated
- another agent needs a transfer packet before the phase is complete

Bad reasons:

- preserving the whole conversation
- duplicating `roadmap.md`
- duplicating `activeContext.md`
- recording every command and thought

## 5. AGENTS.md

`AGENTS.md` is a router, not a knowledge base.

Target under 80 lines. Treat 300 lines as a hard upper limit. If it grows past
that, content is probably leaking from docs or skills into always-loaded
context.

It should answer only:

- where the current phase and live state are
- what read order to use at session start
- which docs are canonical and when to pull them
- what workflow rules must always be visible
- what gotchas code alone will not reveal
- which skills map to repeated workflow transitions

It should not contain:

- full requirements
- full architecture
- phase history
- old plans
- transcripts
- implementation walkthroughs
- file-by-file maps that code can answer

Recommended template:

```text
Read order: AGENTS.md -> activeContext.md -> newest handoff-*.md -> roadmap.md.
Do not pre-read requirements/ or design/ unless the current task needs them.
Append meaningful state changes to activeContext.md.
After a finished roadmap step, run cycle-close.
At ~50% context, suggest handoff and state k-tokens; do not push past ~60%
(100k/120k on 200k, 200k/240k on 400k, 500k/600k on 1M).
Never create internals specs. Code + tests are the implementation truth.
```

## 6. Workflow Modes

Before acting, identify the mode:

- planning
- plan review
- implementation
- review triage
- doc update
- cycle close
- session close

The mode determines what to read, what to update, and which skill to use.

## 7. Planning Loop

Use when starting a feature, phase, or major change.

Inputs:

- user prompt
- existing relevant requirements
- relevant design docs or ADRs
- `roadmap.md`
- `activeContext.md`
- small external research when needed
- `grill-me` or `grill-with-docs` when the idea needs stress-testing

Outputs:

- requirements changes
- design decisions or ADRs
- roadmap changes
- open questions
- risks

Do not produce a full implementation spec. Temporary implementation ideas can
stay in the conversation or issue body until code exists.

Use:

```text
planning-capture
```

## 8. Plan Review Loop

Use when another agent reviews a plan.

Review findings are input, not permanent truth. Triage them into:

- `must_fix_now`
- `should_fix_before_phase_complete`
- `backlog`
- `invalid_or_not_worth_doing`

Accepted findings update the correct durable place:

- behavior or scope -> `requirements/`
- architecture or tradeoff -> `design/` or `docs/adr/`
- sequence or milestone -> `roadmap.md`
- immediate live state -> `activeContext.md`

Rejected and deferred findings get a one-line reason. Do not preserve the whole
argument unless it becomes an ADR.

Use:

```text
review-triage
```

## 9. Implementation Loop

Use for one roadmap step at a time.

Default read order:

```text
AGENTS.md
activeContext.md
newest handoff-*.md, if any
roadmap.md
recent git state
relevant code
only relevant requirements/design/ADRs
```

Do not load all specs by default.

A good implementation slice is:

- small enough to finish in one session
- visible in code
- tied to a roadmap item
- low ambiguity
- easy to verify
- able to leave a clear next step

Update `activeContext.md` only for meaningful state changes:

- next step changes
- blocker appears or clears
- important hypothesis is confirmed or rejected
- a dead end should be remembered as noise
- future agents need a file pointer or gotcha

Use:

```text
session-open
next-slice
```

Use `session-open` when you only need cheap orientation and a one-line next
step. Use `next-slice` when the next step requires some inference from git,
docs, and code.

## 10. Cycle Close

Use after finishing one roadmap step.

Minimum actions:

- identify the completed roadmap step
- tick the roadmap checkbox
- append one short `progress.md` entry
- refresh `activeContext.md` with the next step
- preserve open questions and discarded-as-noise notes
- state whether durable docs were intentionally untouched
- suggest a commit message, but do not commit unless asked

Do not update `requirements/`, `design/`, or `docs/adr/` during cycle close
unless the cycle actually changed scope or architecture. If it did, run the doc
update explicitly.

Use:

```text
cycle-close
```

## 11. Doc Update Loop

Use after implementation, review fixes, or planning changes.

Decision table:

```text
External behavior changed?  Update requirements/.
Architecture changed?       Update design/ or docs/adr/.
Phase or next step changed?  Update roadmap.md and activeContext.md.
Invariant/gotcha changed?   Update docs/implementation-notes.md or ADR.
Only code internals changed? Usually update no durable docs.
```

Always say when no durable docs needed updates. That prevents fake doc churn.

Use:

```text
doc-update-lite
```

## 12. Code Review And Triage

Run review after meaningful slices, before phase completion, or on request.

Do not implement every finding automatically. Implement only `must_fix_now` by
default:

- correctness bug
- safety issue
- data loss risk
- broken contract
- high-risk regression
- blocker

Everything else becomes phase-completion work, backlog, or rejected with a
reason.

Use:

```text
review-triage
```

## 13. Session Close

Use when context is high, work is stopping, the day ends, or another agent will
continue.

Do not ask the agent to save everything. Ask it to prepare continuation context.

First update `activeContext.md`. Create `handoff-*.md` only if live state needs
extra detail.

Session-close output should include:

- date
- task focus
- changed files
- implemented behavior
- current state
- next atomic step
- blockers or risks
- docs updated
- docs intentionally not updated
- discarded dead ends, if relevant
- suggested next skill

Use:

```text
session-close
handoff
```

Prefer `session-close` for this workflow. Use generic `handoff` when transferring
to another model or tool that expects a standalone packet.

## 14. Handoff Template

Use this only when `activeContext.md` is not enough.

```text
# Handoff - <date> <time>

## Where We Are
<current phase and literal next step>

## Open Loops
- <unfinished item with path:line if useful>

## Decisions Made
- <decision and one-line why; promote to ADR if durable>

## Discarded As Noise
- <dead end, failed hypothesis, or rejected approach likely to be retried>

## Context For Next Agent
- Files touched: <list>
- Tests run: <command + result>
- Docs updated: <list>
- Docs intentionally not updated: <list + reason>
- Outstanding question for the human: <if any>
- Suggested next skill: <session-open | next-slice | review-triage>
```

## 15. Context Budget

Context is a budget, not a storage layer.

Rules:

- keep always-loaded instructions short
- do not pre-load all docs
- do not keep transcripts in active context
- do not maintain implementation specs
- read specs on demand
- update `activeContext.md` inline instead of rediscovering state
- suggest handoff around 50% of the active model window, with the token
  equivalent written out
- compact around 60%, not 90%, again with the token equivalent written out
- audit unused MCP/tool servers because schemas cost tokens every turn

The target is to spend context on the current implementation problem, not on
old background.

Reference table:

| Model family / mode | Official context window | 30% | 40% | 50% | 60% |
|---------------------|-------------------------|-----|-----|-----|-----|
| Claude current Sonnet / Opus 1M models | 1,000k | 300k | 400k | 500k | 600k |
| Claude older 200k models | 200k | 60k | 80k | 100k | 120k |
| GPT-5.5 | 1,050k | 315k | 420k | 525k | 630k |
| GPT-5.3-Codex / GPT-5 | 400k | 120k | 160k | 200k | 240k |
| GPT-5.3 Chat / GPT-4.5 / GPT-4o | 128k | 38k | 51k | 64k | 77k |

There is no official GPT-4.4 model in the checked OpenAI docs. If that name
means GPT-4.5 or GPT-4o in a local tool, use the 128k row.

Do not treat 240k as a universal 100%. It is 60% of a 400k model, 24% of a
1M model, and about 23% of GPT-5.5's 1,050k window.

## 16. Skill Inventory

Core workflow skills:

- `planning-capture`: capture planning into durable docs.
- `session-open`: cheap session bootstrap.
- `next-slice`: infer one atomic implementation step.
- `cycle-close`: finish one roadmap step.
- `doc-update-lite`: update only durable docs.
- `review-triage`: classify review findings.
- `session-close`: prepare continuation context.

Useful existing skills:

- `grill-me`
- `grill-with-docs`
- `to-prd`
- `to-issues`
- `review`
- `project-state`
- `handoff`
- `update-config`
- `fewer-permission-prompts`

Do not build:

- `next-step` router skill
- full workflow router skill
- custom heavy `current-state` skill

Sharpen skill descriptions instead of adding a router.

## 17. Harness Configuration

Configure when available:

- stop hook: remind when `activeContext.md` has not been updated recently
- context-threshold hook: warn around 50% to consider handoff; include the
  token equivalent, e.g. 100k on 200k, 200k on 400k, 500k on 1M, or 525k on
  GPT-5.5's 1,050k window
- permission allowlist: reduce repeated prompts for safe read-only operations
- MCP audit: disable unused servers for the project

These are workflow accelerators, not required documentation.

## 18. Bootstrap Checklist

For a new long-running project:

1. Add compact `AGENTS.md`.
2. Create root `activeContext.md`, `progress.md`, and `roadmap.md`.
3. Create `requirements/`, `design/`, and `docs/adr/`.
4. Move existing human-facing specs into requirements and design.
5. Extract durable decisions from internals docs into ADRs or implementation
   notes.
6. Archive or delete the old internals docs.
7. Install or copy the core workflow skills.
8. Configure context and stop hooks if supported.
9. After two weeks, delete or revise skills you did not actually use.

## 19. Standard Prompts

Planning:

```text
Use planning-capture. Capture durable requirements, design decisions, roadmap
changes, open questions, and risks. Do not create an internals spec.
```

Start a session:

```text
Use session-open. Read AGENTS.md, activeContext.md, newest handoff if any, and
roadmap.md. State the next step only.
```

Continue implementation:

```text
Use next-slice. Determine the next atomic implementable step from active
context, roadmap, recent git state, relevant docs, and code. Then implement
that slice only.
```

Close a roadmap step:

```text
Use cycle-close. Tick the roadmap item, append one progress entry, refresh
activeContext.md with the next step, and suggest a commit message.
```

Update docs:

```text
Use doc-update-lite. Update only durable docs affected by this change. If no
durable docs need updates, say so explicitly.
```

Review:

```text
Use review-triage. Classify findings as must_fix_now,
should_fix_before_phase_complete, backlog, or invalid_or_not_worth_doing.
Implement only must_fix_now items unless I ask otherwise.
```

End a session:

```text
Use session-close. Update activeContext.md first. Create a handoff only if
active context is not enough. Include changed files, next atomic step, blockers,
docs updated, docs intentionally not updated, and discarded dead ends.
```

## 20. Migration From Earlier Drafts

From `final-workflow2.md`:

- replace `docs/current-state.md` with root `activeContext.md`
- replace `docs/progress.md` with root `progress.md`
- replace `docs/roadmap.md` with root `roadmap.md`
- keep the same no-internals rule and durable-doc rules

From `opus/03-final-workflow.md`:

- remove the open TODO about where fast-state files live
- root-level fast-state files are the final recommendation
- keep the five-loop workflow and skill mapping

From the root `AGENTS.md` draft:

- keep the documentation policy
- update paths to root `activeContext.md`, `progress.md`, and `roadmap.md`

From the Opus AGENTS draft:

- keep the router style and fixed read order
- keep the hard pressure toward short instructions

## 21. Final Operating Principle

The goal is not less documentation. The goal is less duplicated documentation.

Future agents need:

- what problem is being solved
- what behavior must be preserved
- what decisions are already made
- what phase the project is in
- what the next atomic step is
- where the relevant code starts
- what invariants must not be broken

Everything else should be loaded on demand or discovered from code.
