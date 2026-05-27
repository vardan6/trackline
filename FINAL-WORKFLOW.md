# Final Workflow — v7 (Skill-Driven, Strict, Root-State, 6 Canonical)

> Supersedes v3, v4, v5, v6. Combines all prior drafts plus the v3-doc decision
> to keep fast-state files at the repo root, plus the v7 consolidation that
> merges cycle-close into session-close (STEP / SESSION modes).
>
> **This is the wall-chart document.** §1 is the one-page summary to keep open
> while you work. Everything below §1 is justification and detail.

---

## 1. ONE-PAGE WALL CHART

### Modes (always one of these)

```
1. Planning           → /planning-capture (after /grill-me, /to-prd, etc.)
2. Plan review        → /review-triage
3. Implementation     → /next-slice           (inside an implementation cycle)
4. Documentation      → /doc-update
5. Review triage      → /review-triage         (same skill as plan review)
6. Close              → /session-close         (STEP mode = end of step; SESSION mode = end of session)
                        /handoff               (cross-tool / cross-model standalone packet)
```

### Every session begins with `/session-open`. No exceptions.

It declares the mode, names the next step, then stops.

### Doc layout (one canonical structure — fast state at root)

```
AGENTS.md                  ← router only; ~80 lines
activeContext.md           ← cheap session-start file; live agent state
roadmap.md                 ← phases + checkboxes
progress.md                ← append-only cycle log
handoff-*.md               ← only when activeContext.md isn't enough; newest wins
docs/
  requirements/            ← agent-first behavior contract; human-readable product picture
  design/                  ← agent-first implementation guidance; human-readable rationale
  adr/                     ← append-only decisions
  implementation-notes.md  ← rare durable invariants/contracts/gotchas
```

### What belongs where

Documentation is agent-first, human-readable second. Its primary job is to help
coding agents make correct development decisions with minimal context; its
secondary job is to give humans a coherent picture of the project.

Use one canonical home per fact. Prefer pointers over copies, and update the
smallest set of files that preserves decision quality. Lower token use is a
workflow goal, but never by omitting information that would change a future
agent's implementation choice.

`docs/requirements/` describes the finished project from the outside: agreed
behavior, user expectations, constraints, acceptance criteria, non-goals, and
the overall product picture. It is the record of what was decided through
discussion, research, UX/model work, and grill-me style planning. It should not
describe implementation mechanics or temporary status.

`docs/design/` describes how the project is shaped to satisfy the requirements:
technology choices, algorithms, boundaries, protocols, data-flow decisions,
tradeoffs, and approaches for important subfunctions. Coding agents should treat
design docs and ADRs as standing decisions; if an implementation would overturn
one, they should stop and ask instead of silently changing direction.

Current status does not belong in requirements or design docs. Keep live state
in `activeContext.md`, phase/checklist state in `roadmap.md`, and completed
cycle history in `progress.md`. This avoids updating four documents for every
implementation cycle.

Guardrails:

- Design docs must not become implementation specs that duplicate code. Keep
  approach, boundaries, contracts, and tradeoffs; re-derive private mechanics
  from code.
- Code is implementation truth, but design/ADR is decision truth. If they
  disagree, surface the conflict and ask before changing a standing decision.
- Do not duplicate the same fact across requirements, design, ADRs, roadmap,
  and active state. Move it to the best home and link or reference it elsewhere
  only when needed.

### The five rules

1. **`/session-open` first.** Every session. No coding before it runs.
2. **Code is the truth.** Re-derive *how* from code. Don't write internals specs.
3. **Update inline, not in bulk.** During implementation, only `activeContext.md` moves. Bulk doc updates go through `/doc-update` after the work.
4. **Context budget.** Thresholds are **fixed token amounts**, not fractions
   of whatever window the active model advertises. They are empirical
   behavior cliffs calibrated on the Claude 200k era (where "40% / 50% / 60%"
   originally meant 80k / 100k / 120k). Use the table below to translate.
   Warn at ~100k → `/session-close` or `/handoff`. Compact around ~120k,
   not at "90% of the marketed window."
5. **The honest test.** Would removing this line / doc / skill cause a future session to make a *different and worse* decision? If no, delete it.

### Skill cheat-table

| You want to…                            | Run                  |
|-----------------------------------------|----------------------|
| Start a session, know where I am        | `/session-open`      |
| Capture a plan / research / grill-me    | `/planning-capture`  |
| Pick & start the next code change       | `/next-slice`        |
| Update durable docs after coding        | `/doc-update`        |
| Sort review findings                    | `/review-triage`     |
| Finish one roadmap step (continuing)    | `/session-close` (STEP mode) |
| End the session for the next agent      | `/session-close` (SESSION mode) |
| Cross-tool/model standalone transfer    | `/handoff`           |

### Cycle (the inner loop)

```
/session-open  →  /next-slice  →  implement  →  /session-close (STEP)  →  (next slice OR /session-close SESSION to stop)
```

### What never goes in docs

- function-by-function descriptions
- private call chains
- temporary implementation plans after the code exists
- review history copied verbatim
- session transcripts

### Context windows and working zones

Thresholds are **fixed token amounts**, not fractions of the marketed
window. They are empirical behavior cliffs anchored on the Claude 200k era,
where "40% / 50% / 60%" originally meant 80k / 100k / 120k tokens. On a
larger window the cliff sits at a *smaller* percentage; the absolute token
count is what actually correlates with degraded behavior. Treat the
percentage as a status-line readout, not a target.

**Canonical thresholds (read these, not the percentages):**

| Threshold | Behavior label | What to do                                            |
|-----------|----------------|-------------------------------------------------------|
| `≤ 60k`   | calm           | full smart zone; do anything                          |
| `~ 80k`   | smart-cap      | last clean working point; finish the current slice    |
| `~ 100k`  | warn           | recommend `/session-close` after this step           |
| `~ 120k`  | dumb           | stop new code changes; close session or handoff now  |
| `~ 180k`  | force-compact  | `/compact` or `/handoff` immediately                  |

**Same thresholds expressed as a % of the effective product window
(read only to interpret status-line readouts):**

| Product surface / model                          | Effective window for this workflow | 60k (calm) | 80k (smart-cap) | 100k (warn) | 120k (dumb) | 180k (force-compact) |
|--------------------------------------------------|-----------------------------------:|-----------:|----------------:|------------:|------------:|---------------------:|
| Codex: GPT-5.2-Codex / GPT-5.3-Codex / GPT-5.4 / GPT-5.5 | 258.4k | 23% | 31% | 39% | 46% | 70% |
| Claude Code: Opus 4.7                            | 1,000k | 6% | 8% | 10% | 12% | 18% |
| Claude Code: Sonnet 4.6 / Haiku 4.5              | 200k | 30% | 40% | 50% | 60% | 90% |

Notes:

- Codex API/model pages may advertise larger raw API windows. For this
  workflow, use the **effective Codex product window shown by the
  CLI/status telemetry**. Recent local Codex sessions report
  `model_context_window: 258400` for `gpt-5.2-codex`, `gpt-5.3-codex`,
  `gpt-5.4`, and `gpt-5.5`.
- Re-check the live status line after Codex upgrades. If Codex starts
  reporting a different `model_context_window`, update this table and the
  hook docs, but keep the fixed token thresholds unless real behavior says
  otherwise.

**How to read this:**

- "Compact around 120k" means *120,000 tokens*, full stop — on every
  model.
- A status line saying "46%" on Codex's current 258.4k effective window
  means ~120k tokens used — that is the **dumb zone**.
- A status line saying "12%" on Opus 4.7's 1M Claude Code window means ~120k tokens
  used — that is the **dumb zone**, even though the percentage looks
  small.
- A status line saying "50%" on Sonnet 4.6 or Haiku 4.5 means ~100k
  tokens — that is the **warn zone**.
- People say "I'm at 50%" colloquially; that phrase has always implicitly
  meant *the 200k-era 50%*, i.e. ~100k tokens. Don't reinterpret it
  against a 1M window.
- If you only remember one number: **start closing at 100k, stop coding
  at 120k.** Everything else is conversion.

The `hooks/context-zone.sh` Stop hook compares the live transcript token
count against these fixed thresholds (not against the model window), so
sessions on Codex 258.4k, Claude Code 200k, and Opus 4.7 1M get nudged at
the same actual context size.

---

## 2. Project shape — meta-project

This `my-workflow/` directory is the **source of truth** for the workflow and
the canonical skill set. Both the docs explaining the workflow AND the skills
implementing it live here. New projects install the workflow by:

1. Copying `AGENTS.md` into the project root.
2. Creating the root fast-state files (`activeContext.md`, `roadmap.md`,
   `progress.md`) and the `docs/` subdirectories.
3. Symlinking or copying the canonical skills from `skills/` into
   `~/.claude/skills/` (or `.claude/skills/` for project-scoped use).

The skills here ARE the installable artifacts, not just descriptions of them.

## 3. Strict mode discipline

Mode-awareness is enforced at the entry point:

- `/session-open` is **mandatory** at every session start.
- It reads minimal context in fixed order and outputs a Mode declaration.
- After that, the rest of the workflow runs via auto-dispatch from sharp skill
  descriptions — no router skill, no constant slash-command typing.

If a session somehow proceeds without `/session-open` and the agent is unsure
of the mode, AGENTS.md instructs it to invoke `/session-open` before any other
action.

## 4. Strict skill shape

Every canonical skill uses the same 6-section skeleton. Budget ~40 lines, hard
cap 60:

```
## When to use
## Do NOT use when           ← names sister skills + boundaries
## Inputs (read order)       ← fixed file list; auditable
## Steps                     ← numbered, fixed order; judgment fills slots
## Output                    ← fixed template
## Stop conditions           ← prevents skill drift / over-reach
```

This shape is what makes the workflow predictable enough to follow yourself.

## 5. Canonical skill set

Six skills, each at `skills/<name>/SKILL.md`:

| Skill              | Mode                  | One-line job                                                |
|--------------------|-----------------------|-------------------------------------------------------------|
| `session-open`     | Entry to every session| Read minimal state, declare mode, name next step. Absorbs old `project-state`. |
| `planning-capture` | Planning              | Classify planning output into requirements / design / ADR / roadmap / risks. |
| `next-slice`       | Implementation        | Pick + start one atomic code change inside implementation mode. |
| `doc-update`       | Doc update            | Selective durable-doc update via decision table. Replaces old `doc-update-lite` and loose `doc-update`. |
| `review-triage`    | Plan / code review    | Sort findings; implement only must-fix-now.                 |
| `session-close`    | Close (STEP / SESSION)| STEP: tick roadmap + progress.md + activeContext.md + commit suggestion. SESSION: same + `/doc-update` sweep + optional handoff file. Absorbs the old `cycle-close`. |

## 6. Useful global skills

**Always available (orthogonal, light, useful):** `grill-me`,
`grill-with-docs`, `to-prd`, `to-issues`, `review`, `security-review`,
`update-config`, `fewer-permission-prompts`, `tdd`, `diagnose`, `prototype`,
`simplify`, `init`, `write-a-skill`, `triage` (issue triage — distinct from
`review-triage`), `zoom-out` (user-only-invokable), `loop`, `schedule`,
`claude-api`, `keybindings-help`, **`handoff`** (cross-tool standalone
transfer — use when handing off to a non-Claude tool or another model;
`/session-close` is preferred for in-workflow ending).

**Archived (preserved at `~/.agents/skills-archive/`, not loaded):**
`caveman`, `setup-matt-pocock-skills`, `improve-codebase-architecture`.

**Naming clarification:** `/triage` is issue triage (Linear/GitHub);
`/review-triage` is plan/code review triage. Distinct skills, distinct jobs.

**`/handoff` vs `/session-close`:** Both transfer to a next session.
`/session-close` is the workflow-native ending — updates `activeContext.md`,
applies doc-update rules, writes `handoff-*.md` only if needed.
`/handoff` is a standalone packet for cross-tool / cross-model transfer
(e.g. handing the session to a different agent or tool that doesn't know
your workflow). Use `/session-close` by default; reach for `/handoff` when
the receiver isn't another Claude session in this workflow.

## 7. AGENTS.md template

The router lives at `AGENTS.md` in the rel package. It is ~80 lines and
answers four questions: where am I, what's the workflow, where are docs, what
gotchas. Copy it into new projects and add per-project gotchas at the bottom.

## 8. Harness hooks

Wire via `/update-config`, or use the bundled hook in `hooks/`:

- **Stop hook — context-zone** (`hooks/context-zone.sh`). Reads the session
  transcript, prefers a live token count from the hook payload when
  available, otherwise approximates token usage (`bytes ÷ 4`), and emits a
  `systemMessage` the agent acts on next turn:
  - `<80k` smart zone — silent (about 31% on Codex 258.4k; 40% on Sonnet
    4.6 / Haiku 4.5; 8% on Opus 4.7).
  - `80k–99k` warn — "consider `/session-close` after this step."
  - `100k–119k` ask — "ask the user: `/session-close` (SESSION) or `/handoff` now?"
  - `≥120k` dumb zone — "stop new code changes; close the session now"
    (120k is about 46% on Codex 258.4k; 60% on Sonnet 4.6 / Haiku 4.5;
    12% on Opus 4.7).
  Thresholds overridable per project via env:
  `CONTEXT_{WARN,ASK,DUMB,FORCE}_TOKENS`. `CONTEXT_REFERENCE_WINDOW` only
  affects the fallback displayed percentage when the live model window is
  unavailable. See `hooks/README.md`.
- **Permission allowlist** — read-only Bash + read-MCP via `/fewer-permission-prompts`.
- **MCP audit** — per project, disable unused servers. Each adds tool schemas to every turn.

## 9. Bootstrap checklist (per new project)

```
1. Copy AGENTS.md → <project>/AGENTS.md.
2. touch <project>/{activeContext,roadmap,progress}.md
3. mkdir -p <project>/docs/{requirements,design,adr}
4. Ensure ~/.claude/skills/ contains the 6 canonical skills (symlinked from this repo's `skills/`).
5. /update-config — wire the Stop + context hooks.
6. Audit MCP servers; disable unused.
7. First session: /session-open.
```

## 10. What changed across versions

**v6 → v7 (this version):**

| Change                                              | Reason                                                        |
|-----------------------------------------------------|---------------------------------------------------------------|
| `cycle-close` merged into `session-close`           | Initial request named only "session close" and "handoff" — `cycle-close` was a design-time addition. Two close-skills with overlapping behavior was friction. `/session-close` now has STEP and SESSION modes, auto-detected. |
| Canonical set: 7 → 6 skills                         | Same reason; cleaner cheat-table.                             |

**v5 → v6:**

| Change                                              | Reason                                                        |
|-----------------------------------------------------|---------------------------------------------------------------|
| `docs/current-state.md` → root `activeContext.md`   | Match Cline / Memory Bank convention; discoverability; align with originally-written Opus skills |
| `docs/roadmap.md` → root `roadmap.md`               | Same as above                                                 |
| `docs/progress.md` → root `progress.md`             | Same as above                                                 |
| `docs/handoffs/*.md` → root `handoff-*.md`          | Same as above; newest wins                                    |
| `handoff` was archived                              | Restored as cross-tool / cross-model standalone-packet skill  |
| `INITIAL-REQUEST.md` was opus-only                  | Merged with formal `docs/initial-request.md`; nothing dropped |

## 11. Final operating principle

The goal is not less documentation — it's less *duplicated* documentation,
fewer ad-hoc prompts, and one predictable place for every recurring action.

Future agents (and future you) need:

- what problem is being solved (`docs/requirements/`)
- what behavior must be preserved (tests + `docs/requirements/`)
- what decisions are already made (`docs/design/`, `docs/adr/`)
- what phase the project is in (`roadmap.md`)
- what the next step is (`activeContext.md`)
- where the relevant code lives (the code itself)
- what invariants must not be broken (AGENTS.md gotchas + `docs/implementation-notes.md` + ADRs)

Everything else is discovered from code when needed.

Start every session with `/session-open`. Close every step or session with
`/session-close` (STEP or SESSION mode, auto-detected). Use `/handoff` only
when handing off to a non-Claude tool. Everything in between auto-dispatches
from sharp skill descriptions.
