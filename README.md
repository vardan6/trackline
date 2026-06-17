# My AI Coding Workflow

A practical workflow for long-running projects built with AI coding agents.

It keeps each session focused, breaks implementation into small changes, and
stores the state needed to continue later. The goal is simple: a new session
should not need the full history of every earlier conversation.

## Goals

Each problem this workflow solves, in one sentence. The recurring failures of
long-running AI-assisted coding were almost never "the AI is not smart enough" —
they were context, documentation, and orientation problems, and all three turned
out to be addressable. The list below is in the priority order those pains
actually surfaced; the full rationale for every goal lives in
[INITIAL-REQUEST.md](INITIAL-REQUEST.md) and
[FINAL-WORKFLOW.md](FINAL-WORKFLOW.md).

The framing that holds the rest together:

- **Engineer the workflow, not just the prompt.** Treat the workflow as an
  engineering problem in its own right — specified, pressure-tested, and refined
  against real work — because the workflow matters more than the model.

The problems, in priority order:

1. **Stay on track — developer awareness and project alignment.** Avoid drifting
   from the original problem across a months-long build through planning by being
   challenged
   ([grill-me](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md)) —
   planning is done not when the agent understands the task but when you can
   defend it — an always-current roadmap/progress/activeContext trio, and mode
   discipline (planning, implementing, reviewing, or closing).
2. **Context is a budget, not a window.** Keep the agent inside its reliable
   *smart zone* and out of the *dumb zone* by treating context as an absolute
   token budget rather than a fraction of the advertised window — long-context
   degradation such as [lost in the middle](https://arxiv.org/abs/2307.03172)
   (Liu et al.) and [context rot](https://www.trychroma.com/research/context-rot)
   (Chroma Research) starts well before the window is full, so a lean context is
   a quality decision first and a cost decision second.
3. **No documentation drift / single source of truth.** Keep *code as the truth*,
   drop the internals layer that goes stale, give every fact *one canonical home*,
   and apply the deletion test — would removing this make a future session decide
   worse? — so stale duplicated docs never become a second source of truth the
   agent trusts completely.
4. **Status separate from knowledge.** Keep current status in small live-state
   files (`activeContext.md`, `roadmap.md`, `progress.md`) so moving the work
   forward never means editing requirements or design.
5. **Session continuity through externalized state.** Let each session open
   already oriented by reading a few small curated files instead of re-deriving
   the whole project from history — keeping in mind that save and restore also
   cost tokens, so the state files stay small and the close stays cheap and
   routine.
6. **Reusable skills instead of repeated prompts.** Move the prompts you retype
   every session into named skills that guide the workflow and manage its flow
   from session-open through session-close.
7. **Atomic vertical slices.** Implement one small vertical slice at a time so the
   developer can review and understand each change, and the agent never needs the
   whole project in working memory.
8. **Cross-model code review.** Have a second, stronger, and always different
   model write findings to a Markdown file scoped to the diff since the last
   known-good commit, let the original agent validate each against the code, and
   implement only the confirmed ~70–80% (triaged must-fix-now,
   before-phase-complete, backlog, or invalid).
9. **Thin instruction files, exact names.** Keep `AGENTS.md` / `CLAUDE.md` as a
   thin router and name things exactly (page, widget, file, function, path),
   because everything you load competes for the model's attention. A minimal or
   even absent file is often best for small, focused tasks, but this workflow
   deliberately keeps `AGENTS.md` because it is load-bearing — it declares the
   mode, names the next step, and points at the docs.
10. **Git history is agent fuel.** Keep small, meaningful commits and clean
    checkpoints, because the agent reads history (`git log`, `git diff`,
    `git blame`) to orient itself — conversation provides reasoning, project files
    preserve decisions, and Git preserves change.

And one supporting capability the loop relies on:

- **Clean handoffs.** Transfer work to another session, tool, or model with a
  self-contained packet instead of relying on the live transcript.

## How it works

The workflow has three parts:

1. **Plan the work.** Turn research and discussion into requirements, design
   decisions, and a short roadmap.
2. **Implement one small slice at a time.** Choose the smallest meaningful
   change, finish it, and verify it.
3. **Leave the project ready to continue.** Update the roadmap and compact
   project state before moving to another step or ending the session.

The implementation loop is:

```text
/session-open when orientation is needed
    -> /next-slice
    -> implement and verify
    -> /session-close (STEP)
    -> repeat, or /session-close (SESSION) when stopping
```

If you already know that you want the next implementation slice, start directly
with `/next-slice`.

## Quick start

### 1. Install the core skills

The following example installs the skills globally for Claude Code:

```sh
cd /path/to/my-workflow
mkdir -p "$HOME/.claude/skills"

for skill in \
  session-open \
  planning-capture \
  next-slice \
  doc-update \
  review-triage \
  session-close
do
  ln -sfn "$(pwd)/skills/$skill" "$HOME/.claude/skills/$skill"
done
```

For a project-only installation, use `<project>/.claude/skills/` instead of
`$HOME/.claude/skills/`.

### 2. Prepare a project

Run this from the workflow repository:

```sh
PROJECT=/path/to/your/project

cp AGENTS.md "$PROJECT/AGENTS.md"
touch "$PROJECT/"{activeContext,roadmap,progress}.md
mkdir -p "$PROJECT/docs/"{requirements,design,adr}
```

Add at least one unchecked step to `roadmap.md` so the agent has a concrete
starting point:

```md
# Roadmap

## Phase 1 - First useful outcome

- [ ] Describe the first small result to implement.
```

Then open the project with your coding agent. Use `/session-open` to inspect
project state:

```text
/session-open
```

The agent reads the current project state, identifies the active mode, and
names the next workflow action. It does not select an implementation slice
unless you run `/next-slice`.

## A typical session

Suppose the roadmap says the next feature is password reset.

1. Run `/session-open` when resuming without a specific task.
2. Confirm that implementation is the correct mode and password reset is next.
3. Run `/next-slice`.
4. The agent chooses one small vertical slice, such as letting a user submit
   their email, recording the reset request, and showing a confirmation.
5. The agent implements and verifies that slice.
6. Run `/session-close (STEP)` to record the result and select the next step.
7. Continue with another slice, or run `/session-close` to end the session.

The next session can restart from `activeContext.md` and `roadmap.md` instead of
reconstructing the project from a long transcript.

## Project files

Each file has one job:

| File or directory | Purpose |
|---|---|
| `AGENTS.md` | Routes the agent to the correct workflow and project documents. |
| `activeContext.md` | Small snapshot of the current state, next step, and blockers. |
| `roadmap.md` | Checklist of phases and unfinished work. |
| `progress.md` | Short history of completed steps. |
| `docs/requirements/` | What the finished project must do. |
| `docs/design/` | Important implementation decisions and tradeoffs. |
| `docs/adr/` | Durable decisions that need a recorded rationale. |
| `docs/implementation-notes.md` | Rare contracts, invariants, and gotchas that are not obvious from code. |
| `handoff-*.md` | Optional transfer packet when compact project state is not enough. |

The core documentation rule is:

> Requirements define what must be true. Design explains why the system has
> its shape. Code defines how it works.

Current status belongs in `activeContext.md`, `roadmap.md`, and `progress.md`,
not in requirements or design documents.

## Skills

### Core workflow

| Skill | Use it when |
|---|---|
| `/session-open` | Recovering state when resuming without a specific task. |
| `/planning-capture` | Turning research, brainstorming, or a planning session into durable project documents. |
| `/next-slice` | Choosing the next small implementation change. |
| `/doc-update` | Checking whether completed work changed requirements, design, ADRs, or durable implementation notes. |
| `/review-triage` | Sorting review findings by what must be fixed now and what can wait. |
| `/session-close (STEP)` | Finishing one roadmap step while continuing the session. |
| `/session-close` | Ending the session and leaving compact state for the next one. |

### Planning and handoff

This repository also vendors three skills by
[Matt Pocock](https://github.com/mattpocock/skills) under the MIT License:

| Skill | Use it when |
|---|---|
| `/grill-me` | Stress-testing a plan through detailed questions. |
| `/grill-with-docs` | Stress-testing a plan against the project's existing language and documents. |
| `/handoff` | Transferring work to another tool or model with a standalone context packet. |

Install them the same way if they are not already available:

```sh
cd /path/to/my-workflow
mkdir -p "$HOME/.claude/skills"

for skill in grill-me grill-with-docs handoff
do
  ln -sfn "$(pwd)/skills/$skill" "$HOME/.claude/skills/$skill"
done
```

See [CREDITS.md](CREDITS.md) for attribution and license details.

## Planning larger work

Large features usually need more preparation than the implementation loop:

```text
research or discussion
    -> /grill-me or /grill-with-docs
    -> /planning-capture
    -> /next-slice
    -> implementation loop
```

Keep raw research and long conversations outside the implementation session
when possible. Bring in a concise Markdown summary and the exact files needed
for the next decision.

## Optional setup

### Context-zone hook

The optional hook warns the agent when a session is becoming too large. It can
suggest closing the session or creating a handoff before context quality
degrades.

Claude Code and Codex use different registration files, so follow the complete
instructions in [hooks/README.md](hooks/README.md).

### Command-line tools

These tools help agents locate information and keep command output small:

| Tool | Purpose | Debian or WSL install |
|---|---|---|
| `rg` | Fast, git-aware text search. | `sudo apt install ripgrep` |
| `fdfind` | Focused file discovery without printing an entire tree. | `sudo apt install fd-find` |
| `jq` | Select only the needed fields from JSON output. | `sudo apt install jq` |
| `sg` | Structural code search for larger refactors. | `npm install -g @ast-grep/cli` |

Install tools in the environment where the agent runs, not only in your
interactive shell.

### RTK

RTK is an optional command-output proxy. It can reduce noisy shell output
before that output reaches the model.

RTK is a personal optimization, not a requirement of this workflow. It also
does not replace the instruction to search first, read narrow ranges, and avoid
dumping large files or logs.

## Current limitations

- Git branching, pull-request, and merge guidance is not yet formalized.
- Context thresholds are practical guardrails based on repeated use and prior
  research, not universal guarantees for every task or model.
- The workflow is strict by design, but each project still needs judgment about
  what counts as a useful implementation slice.

Active improvements are tracked in [roadmap.md](roadmap.md).

## Repository guide

| Path | What it contains |
|---|---|
| [FINAL-WORKFLOW.md](FINAL-WORKFLOW.md) | Full operating manual: every step, what it solves, and the generic flow. |
| [AGENTS.md](AGENTS.md) | Router template copied into projects. |
| [`skills/`](skills/) | Core and vendored skill definitions. |
| [CREDITS.md](CREDITS.md) | Attribution and license details for vendored skills. |
| [hooks/README.md](hooks/README.md) | Context hook behavior and installation. |
| [INITIAL-REQUEST.md](INITIAL-REQUEST.md) | Original problems that led to the workflow. |
| [`history/`](history/) | Earlier design iterations retained for traceability. |

For normal use, start with this README and `AGENTS.md`. Read
`FINAL-WORKFLOW.md` when you need the complete rationale or want to change the
workflow itself.
