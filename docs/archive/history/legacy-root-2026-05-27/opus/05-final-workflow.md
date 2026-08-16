# Final Workflow — v5 (Skill-Driven, Strict)

> Supersedes v3 and v4. Combines `docs/final-workflow.md`, `docs/final-workflow2.md`,
> the Opus session transcript, and the locked decisions from this grill-me session.
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
6. Cycle close        → /cycle-close
7. Session close      → /session-close
```

### Every session begins with `/session-open`. No exceptions.

It declares the mode, names the next step, then stops.

### Doc layout (one canonical structure)

```
AGENTS.md                          ← router only; ~80 lines
docs/
  requirements/        ← what must be true (humans)
  design/              ← why the system has this shape (humans)
  adr/                 ← append-only decisions
  roadmap.md           ← phases + checkboxes
  current-state.md     ← cheap session-start file (single fast-state doc)
  progress.md          ← append-only cycle log
  implementation-notes.md ← rare durable invariants/contracts/gotchas
  handoffs/            ← only when current-state isn't enough
```

### The five rules

1. **`/session-open` first.** Every session. No coding before it runs.
2. **Code is the truth.** Re-derive *how* from code. Don't write internals specs.
3. **Update inline, not in bulk.** During implementation, only `docs/current-state.md` moves. Bulk doc updates go through `/doc-update` after the work.
4. **Context budget.** Track both percent and k-tokens. On a 200k window,
   40% = 80k, 50% = 100k, 60% = 120k. On 400k, 40% = 160k, 50% = 200k,
   60% = 240k. On 1M, 40% = 400k, 50% = 500k, 60% = 600k. Warn at ~50%
   → `/session-close`. Compact ~60%, not 90%.
5. **The honest test.** Would removing this line / doc / skill cause a future session to make a *different and worse* decision? If no, delete it.

### Skill cheat-table

| You want to…                            | Run                  |
|-----------------------------------------|----------------------|
| Start a session, know where I am        | `/session-open`      |
| Capture a plan / research / grill-me    | `/planning-capture`  |
| Pick & start the next code change       | `/next-slice`        |
| Update durable docs after coding        | `/doc-update`        |
| Sort review findings                    | `/review-triage`     |
| Finish one roadmap step                 | `/cycle-close`       |
| End the session for the next agent      | `/session-close`     |

### Cycle (the inner loop)

```
/session-open  →  /next-slice  →  implement  →  /cycle-close  →  (next slice or /session-close)
```

### What never goes in docs

- function-by-function descriptions
- private call chains
- temporary implementation plans after the code exists
- review history copied verbatim
- session transcripts

---

## 2. Project shape — meta-project (locked Q1)

This `trackline/` directory is the **source of truth** for the workflow and the
canonical skill set. Both the docs explaining the workflow AND the skills
implementing it live here. New projects install the workflow by:

1. Copying `opus/AGENTS.md` into the project root, with paths adjusted.
2. Creating `docs/` with empty `current-state.md`, `roadmap.md`, `progress.md`.
3. Symlinking or copying the canonical skills from `trackline/skills/` into
   `~/.claude/skills/` (or `.claude/skills/` for project-scoped use).

The skills here ARE the installable artifacts, not just descriptions of them.

## 3. Strict mode discipline (locked Q2)

Mode-awareness is enforced at the entry point:

- `/session-open` is **mandatory** at every session start.
- It reads minimal context in fixed order and outputs a Mode declaration.
- After that, the rest of the workflow runs via auto-dispatch from sharp skill
  descriptions — no router skill, no constant slash-command typing.

If a session somehow proceeds without `/session-open` and the agent is unsure
of the mode, AGENTS.md instructs it to invoke `/session-open` before any other
action.

## 4. Strict skill shape (locked Q3 + Q4)

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

## 5. Canonical skill set (locked Q3)

Seven skills, each living at `trackline/skills/<name>/SKILL.md`:

| Skill              | Mode                  | One-line job                                                |
|--------------------|-----------------------|-------------------------------------------------------------|
| `session-open`     | Entry to every session| Read minimal state, declare mode, name next step. Absorbs old `project-state`. |
| `planning-capture` | Planning              | Classify planning output into requirements / design / ADR / roadmap / risks. |
| `next-slice`       | Implementation        | Pick + start one atomic code change inside implementation mode. |
| `doc-update`       | Doc update            | Selective durable-doc update via decision table. Replaces old `doc-update-lite` and loose `doc-update`. |
| `review-triage`    | Plan / code review    | Sort findings; implement only must-fix-now.                 |
| `cycle-close`      | End of step           | Tick roadmap, append progress, refresh current-state, suggest commit. |
| `session-close`    | End of session        | Update current-state for next session; handoff file only if needed. |

## 6. Global skill audit (locked Q3)

**Keep (orthogonal, light, useful):** `grill-me`, `grill-with-docs`, `to-prd`,
`to-issues`, `review`, `security-review`, `update-config`,
`fewer-permission-prompts`, `tdd`, `diagnose`, `prototype`, `simplify`,
`init`, `write-a-skill`, `triage` (issue triage — distinct from
`review-triage`), `zoom-out` (user-only-invokable), `loop`, `schedule`,
`claude-api`, `keybindings-help`.

**Archive (preserved at `~/.agents/skills-archive/`, not loaded):**

- `caveman` — tempts noise in real work.
- `setup-matt-pocock-skills` — one-time installer, dead weight after first run.
- `handoff` — overlaps with `/session-close`; archive but recoverable.
- `improve-codebase-architecture` — heavyweight, rarely used; archive until needed.

**Naming clarification:** `/triage` is issue triage (Linear/GitHub); `/review-triage`
is plan/code review triage. Distinct skills, distinct jobs.

## 7. AGENTS.md template

The router lives at `trackline/AGENTS.md`. It is ~80 lines and answers
four questions: where am I, what's the workflow, where are docs, what gotchas.

Copy it into new projects, update the paths in §3 to match your `docs/` layout,
and add per-project gotchas at the bottom.

## 8. Harness hooks

Wire via `/update-config`:

- **Stop hook** — print one-line cue ("`current-state.md` last updated N turns ago; consider `/cycle-close` or `/session-close`").
- **Context-threshold hook** — at ~50% warn "consider `/session-close`" and
  include k-tokens: 100k on 200k, 200k on 400k, 500k on 1M, or 525k on
  GPT-5.5's 1,050k.
- **Permission allowlist** — read-only Bash + read-MCP via `/fewer-permission-prompts`.
- **MCP audit** — per project, disable unused servers. Each adds tool schemas to every turn.

## 9. Bootstrap checklist (per new project)

```
1. Copy trackline/AGENTS.md → <project>/AGENTS.md, adjust paths.
2. mkdir -p <project>/docs/{requirements,design,adr,handoffs}
3. touch <project>/docs/{current-state,roadmap,progress}.md
4. Ensure ~/.claude/skills/ contains the 7 canonical skills (symlinked from trackline/skills/).
5. /update-config — wire the Stop + context hooks.
6. Audit MCP servers; disable unused.
7. First session: /session-open.
```

## 10. What changed from v4 → v5

| v4                                                  | v5                                                            |
|-----------------------------------------------------|---------------------------------------------------------------|
| `session-open` optional, default drop                | **Mandatory at every session start; absorbs `project-state`** |
| `next-slice` overlapped with session-open           | Distinct: only inside implementation mode                     |
| Two doc-update skills (loose + lite)                | **One `/doc-update`** (merged best parts; old ones archived)  |
| `project-state` separate skill                      | **Folded into `session-open`**                                |
| Skill internal shape varied                         | **All 7 skills use the same 6-section skeleton**              |
| Global skills listed but not audited                | Audited; `caveman`, `setup-matt-pocock-skills`, `handoff`, `improve-codebase-architecture` archived |
| Wall-chart format implicit                          | **§1 is the explicit one-page chart** to keep open while working |
| "Delete" unused skills                              | **Archive to `~/.agents/skills-archive/`** — recoverable      |

## 11. Final operating principle

The goal is not less documentation — it's less *duplicated* documentation,
fewer ad-hoc prompts, and one predictable place for every recurring action.

Future agents (and future you) need:

- what problem is being solved (`docs/requirements/`)
- what behavior must be preserved (tests + `docs/requirements/`)
- what decisions are already made (`docs/design/`, `docs/adr/`)
- what phase the project is in (`docs/roadmap.md`)
- what the next step is (`docs/current-state.md`)
- where the relevant code lives (the code itself)
- what invariants must not be broken (AGENTS.md gotchas + `docs/implementation-notes.md` + ADRs)

Everything else is discovered from code when needed.

Start every session with `/session-open`. Close every cycle with
`/cycle-close`. Close every session with `/session-close`. Everything in
between auto-dispatches from sharp skill descriptions.
