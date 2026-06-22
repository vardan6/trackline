# My AI Coding Workflow

A practical workflow for long-running projects built with AI coding agents.

It keeps each session focused, breaks implementation into small changes, and
stores the state needed to continue later. The goal is simple: a new session
should not need the full history of every earlier conversation.

## Goals

Each problem this workflow solves, in one sentence. The recurring failures of
long-running AI-assisted coding were context, documentation, and orientation
problems, and all three turned out to be addressable. The list below is in the
priority order those pains actually surfaced; the full rationale for every goal
lives in
[INITIAL-REQUEST.md](INITIAL-REQUEST.md) and
[FINAL-WORKFLOW.md](FINAL-WORKFLOW.md).

The framing that holds the rest together:

**Engineer the workflow, not just the prompt.** Treat the workflow as an
engineering problem in its own right — specified, pressure-tested, and refined
against real work — because the workflow matters more than the model.

The problems, in priority order:

1. **Stay on track — developer awareness and project alignment.** Avoid drifting
   from the original problem across a months-long build through planning by
   being challenged
   ([grill-me](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md))
   — planning is done not when the agent understands the task but when you can
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
   routine. When work needs to move between sessions, tools, or models, use a
   clean handoff: a self-contained packet instead of relying on the live
   transcript.
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
10. **The AI agent is a heavy Git user.** The agent reads history (`git log`,
    `git diff`) to orient itself — conversation provides reasoning, project files
    preserve decisions, and Git preserves change. This is a powerful capability
    worth using deliberately: small, meaningful commits and clean checkpoints give
    the agent a reliable trail to follow, and that pays off significantly when
    sessions resume or context needs to be reconstructed.

## How it works

The workflow runs as three self-contained cycles — *plan*, *implement*, and
*review* — each opened with `/session-open` when orientation is needed and ended
with `/session-close`. You close the plan; later you open and close
implementation; later you open and close a review. They are separate units of
work, run when each is needed.

**Plan** — Research and discussion turn into requirements, design decisions, and
a roadmap broken into small vertical slices. Use `/grill-me` to stress-test the
plan, or `/grill-with-docs` to stress-test it against the project's existing
docs, then let `/planning-capture` store the result in documentation before the
session closes.

**Implement** — Work through vertical slices one at a time. Each slice should be
small — not the smallest possible, but small enough to keep context lean and
meaningful enough to justify the session overhead of loading and saving state.
The right balance depends on the model, context size, and the nature of the
work; good reference numbers are provided in [FINAL-WORKFLOW.md](FINAL-WORKFLOW.md).
Make sure that ADRs are written, `roadmap.md` reflects the current plan, and
`activeContext.md` is updated on each session close. Continue implementing the
next slice until the context feels high and is approaching the Warn Zone, then
close and open fresh. As a softer guide: if context is still light and the next
slice description is close to what was just worked on — same files, same area —
continuing is usually fine; if the next slice is clearly different territory,
closing first is the better call. The Warn Zone is the harder signal to
respect, but the earlier judgment is a feel that develops with experience and
varies by model, coding agent, and project.

**Review** — Run a review at the end of a phase, or any time it feels overdue.
A second model — ideally from a different provider entirely, e.g. Claude
reviewing Codex output or vice versa — reads the diff since the last known-good
commit and writes findings. Feed those findings back to the original provider:
it typically agrees with 70–80% and handles the rest as a priority or detail
difference. Findings are collected in a table with risk, effort, and value
columns so each item can be weighed: how much risk it carries, how much effort
it takes to fix, and what value the fix delivers.

Every cycle ends with `/session-close` — the only step that writes the live
state files (`roadmap.md`, `progress.md`, `activeContext.md`).

## Quick start

### Install the core skills

Skills can be installed globally (available in every project) or per-project
(scoped to one repository). The snippet below is one example — a global
installation for Claude Code using symbolic links:

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

This workflow is not specific to Claude Code — it has been tested with Codex as
well. When using multiple agents, copy the skill definitions to wherever each
agent looks for them.

### Prepare a project

Run this from the workflow repository:

```sh
PROJECT=/path/to/your/project

cp AGENTS.md "$PROJECT/AGENTS.md"
touch "$PROJECT/"{activeContext,roadmap,progress}.md
mkdir -p "$PROJECT/docs/"{requirements,design,adr}
```

Different agents read different filenames: Claude Code reads `CLAUDE.md`, Codex
reads `AGENTS.md`. A common pattern is to copy `AGENTS.md` into the project and
then create a symbolic link so both names point to the same file and stay
identical without maintenance:

```sh
ln -s AGENTS.md "$PROJECT/CLAUDE.md"
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
5. Ask the agent to implement that slice.
6. Run `/session-close (STEP)` to record the result and select the next step.
7. Continue with another slice, or run `/session-close` to end the session.

The next session can restart from `activeContext.md` and `roadmap.md` instead of
reconstructing the project from a long transcript.

The implementation loop in shorthand:

```text
/session-open when orientation is needed
    -> /next-slice
    -> implement and verify
    -> /session-close (STEP)
    -> repeat, or /session-close (SESSION) when stopping
```

If you are resuming and already know what to work on next, you can skip
`/session-open` and start directly with `/next-slice`.

## Planning larger work

Large features usually need more preparation before entering the implementation
loop:

```text
research or discussion
    -> /grill-me or /grill-with-docs
    -> /planning-capture
    -> /session-close        (planning context is high; close before starting implementation)

implementation loop (new session):
    -> /next-slice
    -> implement and verify
    -> /session-close (STEP)
    -> repeat
```

Keep raw research and long conversations outside the implementation session
when possible. Bring in a concise Markdown summary and the exact files needed
for the next decision.

## Working outside the loop

Not every change goes through `/next-slice` — sometimes you ask for an ad-hoc
fix, or a prompt simply falls outside the workflow skills. `/session-close`
always checks whether documentation needs updating, but you can run
`/doc-update` directly whenever you know such a change must reach the docs,
instead of waiting for the close to catch it.

## Project files

Each file has one job:

| File or directory | Purpose |
| --- | --- |
| `AGENTS.md`/`CLAUDE.md` | Routes the agent to the correct workflow and project documents. |
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
| --- | --- |
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
| --- | --- |
| `/grill-me` | Stress-testing a plan through detailed questions. |
| `/grill-with-docs` | Stress-testing a plan against the project's existing language and documents. |
| `/handoff` | Transferring work to another tool or model with a standalone context packet. |

See [CREDITS.md](CREDITS.md) for attribution and license details.

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
| --- | --- | --- |
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
| --- | --- |
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
