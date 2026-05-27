# My AI Coding Workflow

Complete, installable workflow for long-running AI-assisted coding projects.
Self-contained: docs + skills + AGENTS.md template + design history.

## What's inside

```
README.md                    ← this file
FINAL-WORKFLOW.md            ← THE wall-chart document. Keep §1 open while you work.
AGENTS.md                    ← router template to copy into each new project
INITIAL-REQUEST.md           ← the original request that started this design
SESSION-TRANSCRIPT.md        ← the Opus session that produced the workflow
skills/                      ← 6 canonical skills (the installable artifacts)
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

## Install the skills (user-global)

```sh
cd /path/to/my-workflow
for s in session-open planning-capture next-slice doc-update review-triage session-close; do
  ln -sfn "$(pwd)/skills/$s" "$HOME/.claude/skills/$s"
done
```

For project-scoped install, symlink into `<project>/.claude/skills/` instead.

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
| `handoff` (global) | Cross-tool / cross-model standalone-packet transfer.                     |

All skills use the same 6-section structure: When to use, Do NOT use when,
Inputs (read order), Steps, Output, Stop conditions. Predictable enough to
follow yourself.

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
