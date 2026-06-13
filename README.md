# My AI Coding Workflow

Complete, installable workflow for long-running AI-assisted coding projects.
Self-contained: docs + skills + AGENTS.md template + design history.

## What's inside

```
README.md                    ← this file
FINAL-WORKFLOW.md            ← THE wall-chart document. Keep §1 open while you work.
AGENTS.md                    ← router template to copy into each new project
CREDITS.md                   ← attribution for vendored third-party skills (Matt Pocock, MIT)
INITIAL-REQUEST.md           ← the original request that started this design
SESSION-TRANSCRIPT.md        ← the Opus session that produced the workflow
skills/                      ← 6 canonical skills (authored here) + 3 vendored (Matt Pocock, MIT)
  skills/LICENSE-mattpocock  ← MIT license covering the vendored skills
hooks/                       ← context-zone Stop hook (smart / warn / dumb zones)
history/                     ← earlier design drafts, for traceability
```

## Read order

1. **`FINAL-WORKFLOW.md`** — start here. §1 is the one-page wall chart.
2. `AGENTS.md` — the per-project router you copy into new projects.
3. `skills/*/SKILL.md` — each canonical skill in the 6-section skeleton.
4. `INITIAL-REQUEST.md` + `SESSION-TRANSCRIPT.md` — the reasoning behind the design.
5. `history/` — earlier drafts (v1–v4) preserved for traceability.

## The workflow in one line

```
/session-open  →  /next-slice  →  implement  →  /session-close (STEP)  →  (next slice OR /session-close SESSION to stop)
```

Every session begins with `/session-open`. No exceptions.

## Why this workflow exists

This is a **context-engineering** workflow for keeping AI coding agents inside
a useful working range: small loaded state, atomic slices, explicit closeout,
and durable handoff state instead of one ever-growing transcript.

Canonical explanation: `FINAL-WORKFLOW.md` §1, "Context windows and working
zones". Hook mechanics: `hooks/README.md`.

## Planning in practice

Planning mode is not fully formalized in this repository yet. In practice,
larger projects usually start before `/planning-capture` with a longer
**context engineering** phase.

This section is also a small portfolio note: it shows how I structure
AI-assisted work before code starts, not only which commands I run.

My current planning flow typically looks like this:

1. During normal daily activity, I often start early exploration in ChatGPT on
   my phone. That can include **deep research**, tradeoff clarification, and a
   30-minute back-and-forth before I even sit down at the PC.
2. At the end of that discussion, I ask ChatGPT to summarize the conversation as
   a Markdown file. I then download that file and place it in the project so it
   can be reused as compact planning context.
3. For larger implementation work, I usually run a long `grill-me` or
   `grill-with-docs` session. These **grilling sessions** often begin with a
   large prompt, a set of files, and direct file references inside the prompt.
   This workflow is adapted from Matt Pocock's public agent-skills repo,
   especially
   [`grill-me`](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md)
   and
   [`grill-with-docs`](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md).
4. The prompt itself may be typed or dictated. I often use
   [Handy](https://github.com/cjpais/handy), an offline speech-to-text tool, with
   Whisper Large for higher-accuracy transcription.
5. A serious grilling session can take hours, sometimes close to half a day, and
   can involve dozens of questions or, in larger cases, well over a hundred.

The practical rule is: big implementations usually begin with **context
engineering** first, then a long grilling pass, then `/planning-capture`, and
only after that move into the implementation workflow captured in this
repository.

Another practical rule is that I do not try to carry the entire raw planning
conversation into the coding session. I prefer to bring a distilled Markdown
summary plus the relevant files.

## Install the skills (user-global)

```sh
cd /path/to/my-workflow
for s in session-open planning-capture next-slice doc-update review-triage session-close; do
  ln -sfn "$(pwd)/skills/$s" "$HOME/.claude/skills/$s"
done
```

For project-scoped install, symlink into `<project>/.claude/skills/` instead.

The three vendored Matt Pocock skills (MIT — see `CREDITS.md`) can be installed
the same way. Skip this if you already have them from upstream
(`mattpocock/skills`):

```sh
for s in grill-me grill-with-docs handoff; do
  ln -sfn "$(pwd)/skills/$s" "$HOME/.claude/skills/$s"
done
```

## Install the context-zone hook (recommended)

Auto-nudges the agent when context climbs into warn / dumb zones, so you
don't have to watch `/context` yourself. See `hooks/README.md`.

```sh
# Then merge hooks/settings.snippet.json into ~/.claude/settings.json
# and replace /absolute/path/... with the real path to context-zone.sh.
```

## Bootstrap a new project

```sh
PROJECT=/path/to/your/project
cp AGENTS.md "$PROJECT/AGENTS.md"
touch "$PROJECT/"{activeContext,roadmap,progress}.md
mkdir -p "$PROJECT/docs/"{requirements,design,adr}
# First session in the project: /session-open
```

## The 6 canonical skills

| Skill              | When                                                                     |
|--------------------|--------------------------------------------------------------------------|
| `session-open`     | Every session start. Mandatory.                                          |
| `planning-capture` | After /grill-me, /to-prd, research, or brainstorm.                       |
| `next-slice`       | Inside implementation mode, to pick the next change.                     |
| `doc-update`       | After non-trivial coding, to refresh durable docs.                       |
| `review-triage`    | After /review or /security-review.                                       |
| `session-close`    | STEP mode: after finishing a roadmap step. SESSION mode: end of session, day, or context around 100k tokens: ~39% on Codex 258.4k, 50% on Sonnet 4.6 / Haiku 4.5, 10% on Opus 4.7. Auto-detected. |

All six use the same 6-section structure: When to use, Do NOT use when,
Inputs (read order), Steps, Output, Stop conditions. Predictable enough to
follow yourself.

## Vendored skills (Matt Pocock, MIT)

Three skills used by this workflow are authored by Matt Pocock and vendored into
`skills/` under the MIT License (see `CREDITS.md` and `skills/LICENSE-mattpocock`).
They follow their upstream format, not the 6-section skeleton above.

| Skill              | When                                                                      |
|--------------------|---------------------------------------------------------------------------|
| `grill-me`         | Planning. Get relentlessly interviewed to stress-test a plan/design.      |
| `grill-with-docs`  | Planning. Same, but challenged against the project's domain model + docs.  |
| `handoff`          | Cross-tool / cross-model standalone-packet transfer between sessions.     |

## Version control gap

Git workflow is not yet covered deeply enough in this repository. That is a
real gap, because good AI-assisted implementation depends on clean **version
control** boundaries: commits, branches, pushes, and pull requests that make
work easy to review and recover.

This is the direction the workflow should probably move toward:

- Use short-lived topic branches for non-trivial work instead of piling all
  changes onto `main`. GitHub documents
  [branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
  as a way to isolate development work and
  [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
  as the review and discussion path before merge.
- Keep commits small and meaningful so an agent can reason about what changed,
  what should be reverted, and what belongs in a follow-up commit.
- Open draft pull requests early for larger work so review, checks, and scope
  discussion can happen before the branch is considered ready.
- Treat commit history as part of the workflow artifact, not just a transport
  layer. Good history improves debugging, rollback, review, and future agent
  context.

This repo should eventually explain how to incorporate branch creation,
checkpoint commits, pushes, pull requests, and merge strategy into the workflow
without making the loop heavy.

## Core rule

> Requirements define what must be true. Design docs define why the system has
> its shape. Code defines how implementation works. Low-level notes exist only
> for durable invariants, contracts, gotchas, and navigation.

The first audience is the coding agent during development; the second audience
is the human who needs a coherent project picture. Docs should therefore be
precise, actionable, and cheap to load before they are narrative.

Keep one canonical source of truth per fact. Prefer pointers over repeated
explanations, and update the smallest set of docs that preserves decision
quality for future agents.

Requirements are the durable agreement layer: the finished-project behavior,
user expectations, constraints, acceptance criteria, non-goals, and overall
product picture that came out of discussion, research, UX/model work, and
planning. Design docs are the durable implementation-decision layer:
technology choices, algorithms, boundaries, protocols, and tradeoffs. Current
status stays in `activeContext.md`, `roadmap.md`, and `progress.md`, not in
requirements or design.

Two guardrails keep this useful: design docs must not duplicate private code
mechanics, and agents must surface code-vs-design conflicts before changing a
standing decision.

## Version

Root package. Synthesizes prior design drafts plus the grill-me-driven
finalization. See `history/` for the trail.
