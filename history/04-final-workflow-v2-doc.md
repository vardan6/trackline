# Final Workflow 2

This is the consolidated version of the workflow, using the root draft, the
Opus session output, the transcript, both AGENTS drafts, and the drafted skills.

The goal is a long-running AI coding workflow that keeps useful planning
memory, avoids stale implementation docs, starts new sessions cheaply, and gives
agents a clear mode: planning, implementation, review, documentation update, or
session close.

## Core Decision

Do not keep a standing internals, implementation, or reference specification
layer.

That layer is too close to code. If it explains ordinary implementation
mechanics, it becomes a second source of truth. It then drifts, costs tokens,
and creates pressure to update requirements, design, implementation docs, and
code together.

Use this model instead:

```text
Requirements = what must be true.
Design / ADRs = why the system has this shape.
Roadmap / current state / progress = where the project is now.
Code and tests = how the implementation works.
Implementation notes = rare durable invariants, contracts, gotchas, and
navigation hints.
```

This is a 2.5-layer model:

- durable requirements
- durable design / ADRs
- thin current-state and rare implementation notes

## The Documentation Test

Before adding or keeping a line of documentation, ask:

```text
Would removing this cause a future session to make a different and worse
decision?
```

If no, delete it or leave it in the conversation only.

Good durable documentation:

- user-visible behavior
- constraints and acceptance criteria
- non-goals
- architecture decisions
- rejected alternatives with reasons
- module responsibility boundaries
- protocols, schemas, and external contracts
- safety or correctness invariants
- non-obvious ordering constraints
- traps a code reader would probably miss
- where to begin reading code for a feature
- current phase, blocker, and next atomic step

Usually bad documentation:

- function-by-function explanations
- private call chains
- obvious file maps
- "how every part works" implementation specs
- temporary plans after the code exists
- review history copied verbatim
- session transcripts as required context

## Canonical File Set

Use one canonical structure per project:

```text
AGENTS.md
docs/
  requirements/
  design/
  adr/
  roadmap.md
  current-state.md
  progress.md
  implementation-notes.md   # optional and sparse
  handoffs/                 # optional; only when needed
```

Do not also maintain root-level `activeContext.md`, root-level `progress.md`,
and `docs/current-state.md` at the same time. The Opus draft used
`activeContext.md`; this final version folds that role into
`docs/current-state.md` so the project has one fast-state document.

If a tool or model strongly expects `activeContext.md`, create a pointer file
that says:

```text
See docs/current-state.md.
```

Do not duplicate the state in both places.

## Document Responsibilities

### `docs/requirements/`

Human-facing behavior specifications.

Update only when external behavior, scope, constraints, acceptance criteria, or
non-goals change.

### `docs/design/`

High-level system shape, boundaries, technology choices, tradeoffs, and design
constraints.

Update only when architecture, module boundaries, data flow, or integration
strategy changes.

### `docs/adr/`

Append-only decision records for non-obvious decisions.

Use ADRs for:

- important tradeoffs
- rejected alternatives
- unusual patterns
- design decisions future agents might otherwise undo

### `docs/roadmap.md`

Phase plan and next work.

It should answer:

- what phase the project is in
- which steps are done
- what the next unchecked step is
- what is blocked or deferred

### `docs/current-state.md`

The cheap session-start file.

It should be short and current:

- current phase
- current task
- latest meaningful implementation state
- next atomic step
- blockers
- open questions
- "discarded as noise" notes when a failed path is likely to be retried
- pointers to relevant files

This replaces heavy "current-state" rediscovery and replaces the Opus
`activeContext.md` concept.

### `docs/progress.md`

Append-only cycle log.

Use one short entry per completed implementation cycle:

```text
- 2026-05-24: Phase 2.1 auth callback cleanup - implemented redirect guard and
  added regression test.
```

Do not turn it into a diary.

### `docs/implementation-notes.md`

Optional and sparse.

Use only for durable facts that are too implementation-specific for design docs
but too important to rediscover from code every session:

- invariants
- protocols
- schemas
- contracts
- gotchas
- code navigation hints

Do not write walkthroughs of ordinary code.

### `docs/handoffs/`

Use only when `docs/current-state.md` is not enough.

Good reasons:

- context is high and loose ends are too detailed for current-state
- a session explored dead ends that should not be repeated
- work is being transferred before a phase is complete

Bad reasons:

- saving the whole conversation
- duplicating roadmap and current-state
- preserving every command and thought

## AGENTS.md Policy

`AGENTS.md` is a router, not a knowledge base.

Keep it short. A good target is under 80 lines. A hard cap around 300 lines is
acceptable, but if it gets that large, it is probably absorbing content that
belongs in docs or skills.

It should contain:

- workflow rules
- session-start read order
- documentation update policy
- context and handoff policy
- pointers to canonical docs
- names of preferred skills
- rare project gotchas that must always be visible

It should not contain:

- full requirements
- full architecture
- phase history
- old plans
- transcripts
- file-by-file implementation maps
- long explanations of why the workflow exists

Recommended session-start rule:

```text
Read AGENTS.md, docs/current-state.md, docs/roadmap.md, recent git state, and
only the docs/code relevant to the current task. Do not load all requirements
or all design docs by default.
```

## Skills

Skills exist to stop repeated prompting. They should be small, sharp, and
triggered by description.

Do not build one large router skill. The research and Opus session both moved
away from that idea. Native skill dispatch works better when skills have clear
descriptions and narrow jobs.

Use these skills:

- `planning-capture`: after brainstorming, research, or grill-me sessions.
- `next-slice`: at session start or when asking what to implement next.
- `doc-update-lite`: after implementation or review fixes.
- `review-triage`: when another agent produces review findings.
- `session-close`: when context is high or work is stopping.

Optional aliases from the Opus draft:

- `session-open`: same role as `next-slice`, but read-only and stops after
  stating the next step.
- `cycle-close`: narrower version of `session-close` for finishing one roadmap
  step.

The final recommendation is:

- keep `next-slice` for "what is the next implementable step?"
- keep `session-close` for "prepare continuation context"
- optionally add `cycle-close` if you want a stricter end-of-step ritual
- do not keep both `session-open` and `next-slice` unless their descriptions
  make the difference obvious

## Workflow Modes

Every session should know its mode before doing work.

The modes are:

- planning
- plan review
- implementation
- review triage
- documentation update
- cycle close
- session close

If the mode is unclear, infer it from the user request and current state. Do not
load the whole project to decide.

## 1. Planning

Use when starting a feature, phase, or major change.

Inputs:

- user prompt
- existing relevant requirements
- existing relevant design docs or ADRs
- roadmap and current state
- small external research when needed
- grill-me or similar questioning when the problem is unclear

Outputs:

- requirements changes
- design decisions or ADRs
- roadmap changes
- open questions
- risks

Do not create an implementation spec.

Temporary implementation planning is allowed, but it should not become durable
documentation unless it contains an invariant, contract, gotcha, or decision.

Use:

```text
planning-capture
```

## 2. Plan Review

Use when another agent reviews a plan.

The review file is not permanent truth. Triage it.

Classify findings as:

- `must_fix_now`
- `should_fix_before_phase_complete`
- `backlog`
- `invalid_or_not_worth_doing`

Accepted findings should update the correct durable doc:

- behavior change -> requirements
- architecture or tradeoff -> design / ADR
- sequencing -> roadmap
- current blocker or next step -> current-state

Rejected and deferred findings should keep a short reason. Do not preserve the
full debate unless the reason is itself a durable decision.

Use:

```text
review-triage
```

## 3. Implementation

Start cheap.

Default read set:

```text
AGENTS.md
docs/current-state.md
docs/roadmap.md
recent git state
relevant code
only relevant requirements/design/ADRs
```

Do not read all specs by default.

Implement one atomic slice.

A good slice is:

- small enough to finish in one session
- visible in code
- tied to the roadmap
- low ambiguity
- easy to verify
- leaves a clear next step

During implementation, update `docs/current-state.md` only when meaningful state
changes:

- next step changes
- blocker appears or clears
- important hypothesis is confirmed or rejected
- a dead end is worth recording under "discarded as noise"
- future session would otherwise repeat expensive rediscovery

Do not use current-state as a play-by-play.

Use:

```text
next-slice
```

## 4. Documentation Update

After implementation, update only durable docs.

Use this decision table:

```text
Requirements changed?      Update docs/requirements/.
Architecture changed?      Update docs/design/ or docs/adr/.
Phase or next step changed? Update docs/roadmap.md and docs/current-state.md.
Invariant/gotcha changed?  Update implementation notes or ADR.
Only code internals changed? Usually update no docs.
```

Always say when no durable docs needed updates. That is a useful outcome.

Use:

```text
doc-update-lite
```

## 5. Review Triage

Run code review after meaningful slices, before phase completion, or on request.

Do not implement every review finding automatically.

Immediate fixes should be limited to:

- correctness bugs
- safety issues
- data loss risks
- broken contracts
- high-risk regressions
- blockers

Everything else is triaged into phase-completion work, backlog, or rejected with
reason.

Use:

```text
review-triage
```

## 6. Cycle Close

Use after finishing one roadmap step.

Minimum actions:

- mark the roadmap step complete
- append one short progress entry
- update current-state with the next step
- note docs updated or intentionally not updated
- suggest a commit message, but do not commit unless asked

Use `session-close` if the session is ending. Use an optional `cycle-close`
skill if you want this narrower ritual.

## 7. Session Close

Use when context is high, work is stopping, or switching agents.

Do not ask the agent to "save everything." Ask for continuation context.

Update `docs/current-state.md` first. Create a handoff file only if the next
session needs extra loose-end detail.

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
- discarded dead ends if relevant
- suggested next skill

Use:

```text
session-close
```

## Handoff Template

Use this only when `docs/current-state.md` is not enough.

```text
# Handoff - <date> <time>

## Where We Are
<current phase and literal next step>

## Changed Files
- <path>: <short reason>

## Implemented
- <durable outcome, not every edit>

## Open Loops
- <unfinished item with path pointer if useful>

## Decisions Made
- <decision and one-line reason; promote to ADR if durable>

## Discarded As Noise
- <dead end, failed hypothesis, or rejected approach likely to be retried>

## Verification
- <command>: <result>

## Docs
- Updated: <docs>
- Intentionally not updated: <docs and reason>

## Next
<one atomic step>
```

## Context Budget

Keep always-loaded context small.

Practical rules:

- do not pre-load all docs
- do not keep long transcripts in active context
- do not maintain implementation specs
- prefer current-state pointers over copied explanations
- compact or hand off before context gets unreliable
- audit unused MCP/tool servers because tool schemas consume context

The workflow target is not "never use context." The target is to spend context
on the current implementation problem rather than stale background.

## Standard Prompts

Planning:

```text
Use planning-capture. Capture durable requirements, design decisions, roadmap
changes, open questions, and risks. Do not create an internals spec or duplicate
code-level implementation details.
```

Start or continue implementation:

```text
Use next-slice. Determine the next atomic implementable step from current state,
roadmap, recent git state, relevant docs, and code. Then implement that slice
only.
```

After implementation:

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

Session close:

```text
Use session-close. Update continuation context with changed files, current
state, next atomic step, blockers, docs updated, and docs intentionally not
updated. Create a handoff only if current-state is not enough.
```

## Migration From Existing Habits

Replace this:

```text
Ask the agent to check all docs, infer current state, document everything, then
continue.
```

With this:

```text
Read AGENTS.md, docs/current-state.md, docs/roadmap.md, recent git state, and
relevant code. Pull requirements/design only when the task needs them.
Implement one slice. Update only durable docs. Close with the next step.
```

Replace this:

```text
Maintain requirements + design + internals docs.
```

With this:

```text
Maintain requirements + design/ADRs + current-state/roadmap/progress.
Keep rare implementation notes only for durable invariants, contracts, gotchas,
and navigation.
```

Replace this:

```text
Save the whole session before context runs out.
```

With this:

```text
Keep docs/current-state.md current enough that the next session can start
cheaply. Add a handoff only for loose ends that do not belong there.
```

## Final Operating Principle

The goal is not less documentation. The goal is less duplicated documentation.

Future agents need:

- what problem is being solved
- what behavior must be preserved
- what decisions are already made
- what phase the project is in
- what the next atomic step is
- where the relevant code starts
- what invariants must not be broken

Everything else should be discovered from code when needed.
