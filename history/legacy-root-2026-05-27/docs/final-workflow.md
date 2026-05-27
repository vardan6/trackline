# Final Workflow After Research

## Research Summary

The research direction was consistent across modern AI coding-agent guidance:

- Keep always-loaded project instructions short and specific.
- Use project memory files such as `AGENTS.md` or `CLAUDE.md` for durable rules only.
- Move optional workflows into skills or commands instead of loading them every session.
- Prefer code and recent implementation state over stale documentation.
- Avoid documentation that duplicates low-level implementation details.
- Use handoffs and current-state notes to continue work without loading full history.

References used during the session:

- Anthropic Claude Code best practices: `https://code.claude.com/docs/en/best-practices`
- Anthropic Claude Code memory: `https://code.claude.com/docs/en/memory`
- GitHub Copilot coding agent best practices: `https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results`
- GitHub Copilot CLI customization comparison: `https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/agents/copilot-cli/comparing-cli-features`
- Agent configuration research: `https://arxiv.org/abs/2602.14690`

## Core Decision

Do not maintain a full third "internals specification" layer as a normal documentation layer.

The internals layer is risky because it tends to duplicate code. Once it duplicates code, it becomes a second source of truth. It then drifts, costs tokens, and creates maintenance pressure without reliably improving implementation quality.

Use this model instead:

```text
Requirements docs = what must be true.
Design docs / ADRs = why the system has this shape.
Roadmap/current-state = where the project is and what is next.
Code = how the implementation works.
Implementation notes = rare notes for durable invariants, contracts, gotchas, and navigation.
```

This is a 2.5-layer documentation model:

- Requirements
- Design / ADRs
- Thin implementation notes only where useful

## Documentation Rules

Before documenting anything, ask:

```text
Will this still be useful if the code changes?
```

Document it if the answer is yes.

Examples that should be documented:

- external behavior
- user-visible requirements
- non-goals
- architecture decisions
- rejected alternatives
- module responsibility boundaries
- protocols and schemas
- safety or correctness invariants
- non-obvious gotchas
- where future agents should begin reading code
- current phase and next step

Examples that should not usually be documented:

- function-by-function descriptions
- private call chains
- ordinary implementation details
- temporary implementation plans after code already exists
- review discussion history
- code structure that is obvious from the code itself

## Recommended Document Set

Use this structure for long-running projects:

```text
docs/requirements/
  Human-facing behavior specifications.

docs/design/
  Architecture specs, design decisions, and ADRs.

docs/roadmap.md
  Phase plan, milestones, and next planned work.

docs/current-state.md
  Short machine-facing status for fast session startup.

docs/implementation-notes.md
  Optional, sparse notes for invariants, contracts, gotchas, and navigation.
```

Avoid these:

```text
docs/internals/full-implementation-spec.md
docs/how-every-function-works.md
docs/session-history-everything.md
```

## Workflow Overview

The workflow has five loops:

1. Planning loop
2. Plan review loop
3. Implementation loop
4. Session-close loop
5. Review triage loop

Each loop has a specific documentation output. Agents should know which loop they are in before acting.

## 1. Planning Loop

Use this when starting a feature, phase, or major change.

Inputs:

- user prompt
- existing requirements
- existing design docs
- relevant roadmap/current-state docs
- small external research if needed
- `grill-me` or similar questioning sessions when the problem is unclear

Outputs:

- requirements delta
- design decisions or ADR delta
- phase roadmap update
- open questions
- known risks

Do not produce a full implementation spec. If implementation planning is needed, keep it temporary or store only the durable constraints.

## 2. Plan Review Loop

Use this when another agent reviews the plan.

The review should not become permanent history by default. Store only the triaged outcome:

```text
accepted plan changes
rejected concerns with reason
remaining risks
deferred items
```

Accepted changes should update requirements, design, or roadmap documents depending on their type.

## 3. Implementation Loop

Each implementation session should start with minimal state discovery.

Read only:

```text
AGENTS.md
docs/current-state.md
docs/roadmap.md
the relevant requirement/design doc
recent git state
the relevant code area
```

Do not load all requirements, all design docs, all review files, or all old handoffs.

The session should implement one atomic next slice.

Good slice shape:

```text
small enough to finish in one session
visible in code
low ambiguity
clear verification path
clear next step after completion
```

## 4. Session-Close Loop

Use this when context is high or work is stopping. Record both percent and
k-tokens: 35-40% means 70k-80k on a 200k model, 140k-160k on a 400k model,
and 350k-400k on a 1M model.

Do not ask the agent to "save everything." Instead ask it to create a short continuation packet.

The session-close output should include:

- what changed
- files touched
- current project state
- next atomic step
- blockers or risks
- docs updated
- docs intentionally not updated, with reason

The handoff should reference existing docs and code paths instead of repeating them.

## 5. Review Triage Loop

Use this after a meaningful implementation slice or before closing a phase.

Review findings should be classified as:

- `must_fix_now`
- `should_fix_before_phase_complete`
- `backlog`
- `invalid_or_not_worth_doing`

Only `must_fix_now` findings are implemented immediately by default.

For each accepted review point, record why it matters. For each rejected or deferred point, record the reason.

## Skill Set

Use skills to avoid repeating long prompts.

Recommended skills:

- `planning-capture` - capture planning output into requirements, design, roadmap, and open questions.
- `next-slice` - start a session by finding the next atomic implementable step.
- `doc-update-lite` - selectively update durable docs after implementation.
- `review-triage` - classify review findings and decide what to implement now.
- `session-close` - prepare a concise handoff and update continuation docs.

Existing skills that may still be useful:

- `grill-me` - for questioning plans before they harden.
- `handoff` - for compact transfer to another agent, though `session-close` is more specific to this workflow.
- `project-state` - useful if kept lightweight and implementation-first.

## AGENTS.md Guidance

`AGENTS.md` should stay small. It should contain durable behavior instructions for agents, not project history, full workflows, or large documentation.

Good content for `AGENTS.md`:

- testing policy
- documentation update policy
- context-management policy
- session-start policy
- session-close policy
- pointers to docs and skills

Bad content for `AGENTS.md`:

- full requirements
- full architecture
- phase history
- old plans
- long explanations of the workflow
- details that should live in skills

## Standard Prompts

Planning:

```text
Use the planning-capture workflow. Capture only durable requirements, design decisions, roadmap changes, open questions, and risks. Do not create an internals spec or duplicate code-level implementation details.
```

Implementation:

```text
Use the next-slice workflow. Determine the next atomic implementable step from current state, roadmap, relevant docs, recent git state, and code. Then implement that slice only.
```

Documentation after implementation:

```text
Use doc-update-lite. Update only durable docs affected by this change. Do not mirror implementation details that are obvious from code. State which docs were updated and which were intentionally left unchanged.
```

Review:

```text
Use review-triage. Classify each review finding as must fix now, should fix before phase complete, backlog, or invalid/not worth doing. Implement only must-fix-now items unless I ask otherwise.
```

Session close:

```text
Use session-close. Prepare the project for the next session with minimal token cost: update current-state/roadmap if needed, create a short handoff if useful, and identify the next atomic step.
```

## Final Operating Principle

The goal is not less documentation. The goal is less duplicated documentation.

The most useful context for future coding agents is:

- what problem is being solved
- what behavior must be preserved
- what decisions are already made
- what phase the project is in
- what the next step is
- where the relevant code lives
- what invariants must not be broken

Everything else should be discovered from code when needed.
