# Final Workflow — Vibe Coding for Long-Running Projects (v4)

> Reconciles v3 (`03-final-workflow.md`) with `docs/final-workflow2.md`.
> Supersedes both. The big changes from v3 are: one canonical file layout
> under `docs/` (no root-level duplication), `activeContext.md` folded into
> `docs/current-state.md`, and a deduplicated skill set with optional rituals
> clearly labeled.

---

## 1. Guiding principles

1. **Two audiences, two doc sets.** Humans get narrative requirements +
   design. Agents get a thin router + on-demand retrieval. Never merge them.
2. **Drift kills middle layers.** Code + tests are the truth. Keep durable
   *why/what* docs (requirements, ADRs). Drop the internals / implementation /
   reference spec layer. Agents re-derive *how* from code on demand.
3. **Split docs by volatility, not abstraction.**
   - *Slow-churn:* `docs/requirements/`, `docs/design/`, `docs/adr/`.
   - *Fast-churn:* `docs/roadmap.md`, `docs/current-state.md`,
     `docs/progress.md`.
4. **One canonical state file.** `docs/current-state.md` is the single
   fast-state document. Do not also keep root-level `activeContext.md`. If
   a tool insists on the name, make `activeContext.md` a one-line pointer.
5. **Context budget is real.** Track both percent and k-tokens. On a 200k
   window, 40% = 80k, 50% = 100k, 60% = 120k. On 400k, 40% = 160k, 50% =
   200k, 60% = 240k. On 1M, 40% = 400k, 50% = 500k, 60% = 600k. Compact at
   ~60%, not 90%.
6. **Skills dispatch via description, not a router.** Many small skills with
   sharp frontmatter beats one router. Don't keep two skills whose
   descriptions overlap.
7. **Mode awareness.** Before acting, the agent identifies the mode:
   planning, plan-review, implementation, documentation update, review
   triage, cycle close, or session close.
8. **The honest test for any doc line / AGENTS.md line / skill:** would
   removing it cause the next session to make a *different and worse*
   decision? If no, delete it.
9. **The honest test for any new doc:** will this still be useful if the
   code changes? If no, leave it in the conversation or the commit message.

## 2. Doc layers — the final set

| Path                              | Audience | Volatility   | Update trigger                          |
|-----------------------------------|----------|--------------|-----------------------------------------|
| `AGENTS.md`                       | Agents   | Low          | Workflow rule changes only              |
| `docs/requirements/*.md`          | Humans   | Low          | External behavior / scope               |
| `docs/design/*.md`                | Humans   | Low          | Architectural changes only              |
| `docs/adr/*.md`                   | Both     | Append-only  | Per non-obvious decision                |
| `docs/roadmap.md`                 | Both     | Medium       | Phase start / phase complete            |
| `docs/current-state.md`           | Agents   | High         | Meaningful state changes (see §3.3)     |
| `docs/progress.md`                | Both     | Append-only  | One bullet at each cycle close          |
| `docs/implementation-notes.md`    | Both     | Rare         | Only for invariants/contracts/gotchas   |
| `docs/handoffs/*.md`              | Agents   | Per-session  | Only when current-state isn't enough    |

**Document this** (still useful if code changes):
external behavior, user-visible requirements, non-goals, architecture
decisions, rejected alternatives, module boundaries, protocols / schemas,
safety or correctness invariants, non-obvious gotchas, where future agents
should begin reading code, current phase and next step.

**Don't document this** (re-derivable from code):
function-by-function descriptions, private call chains, ordinary
implementation details, temporary implementation plans after code exists,
review discussion history, obvious code structure, session transcripts.

**Killed:**

- The internals / implementation / reference spec layer. Survivors become
  ADRs or short code comments at the surprise.
- Root-level duplicates (`activeContext.md`, `progress.md`, `roadmap.md` at
  the repo root). Everything lives under `docs/`. The Opus draft put fast
  state at root; v2 folded it into `docs/`. v4 follows v2.

## 3. Document responsibilities

### 3.1 `docs/requirements/`

Human-facing behavior specs. Update only when external behavior, scope,
constraints, acceptance criteria, or non-goals change.

### 3.2 `docs/design/` and `docs/adr/`

High-level system shape, boundaries, tradeoffs, technology choices.
Update only when architecture, module boundaries, data flow, or integration
strategy changes. Use ADRs for non-obvious decisions, rejected alternatives,
and unusual patterns future agents might otherwise undo.

### 3.3 `docs/current-state.md` — the cheap session-start file

Replaces the old `current-state` skill and the Opus `activeContext.md`. Keep
it short and current:

- current phase
- current task
- latest meaningful implementation state
- next atomic step
- blockers
- open questions
- "discarded as noise" notes when a failed path may be retried
- pointers to relevant files

Update only on meaningful state changes — next step changes, blocker appears
or clears, important hypothesis confirmed or rejected, dead end worth
recording, future session would otherwise repeat expensive rediscovery. Not
a play-by-play.

### 3.4 `docs/roadmap.md`

Phase plan and next work. Answers: what phase, which steps done, what's the
next unchecked step, what's blocked.

### 3.5 `docs/progress.md`

Append-only cycle log. One bullet per completed cycle:

```
- 2026-05-24: Phase 2.1 auth callback cleanup — implemented redirect guard and added regression test.
```

Not a diary.

### 3.6 `docs/implementation-notes.md`

Optional and sparse. Only for durable facts too implementation-specific for
design but too important to rediscover every session — invariants, protocols,
schemas, contracts, gotchas, navigation hints. No walkthroughs of ordinary
code.

### 3.7 `docs/handoffs/`

Only when `docs/current-state.md` isn't enough — high context with detailed
loose ends, dead ends worth not re-exploring, mid-phase transfers. Not a
place to save the whole conversation.

## 4. AGENTS.md — the router

AGENTS.md is a router, not a knowledge base. Target ~80 lines. Hard cap ~300.
If it gets that large, it's absorbing content that belongs in docs or skills.

**Include:**

- session-start read order
- workflow rules (when to append to current-state, when to cycle-close, when
  to handoff)
- documentation update policy
- context and handoff policy
- pointers to canonical docs
- names of preferred skills
- rare project gotchas that must always be visible

**Exclude:**

- full requirements, full architecture, phase history, old plans, transcripts
- file-by-file implementation maps
- long explanations of the workflow itself

**Canonical session-start rule:**

```
Read AGENTS.md, docs/current-state.md, docs/roadmap.md, recent git state,
and only the docs/code relevant to the current task. Do not load all
requirements or all design docs by default.
```

The draft at `opus/AGENTS.md` is the template (update its file paths to
match the `docs/` layout above).

## 5. Workflow modes

Every session knows its mode before doing work. If unclear, infer from the
user request and current state — don't load the whole project to decide.

| Mode               | Skill              | Output                                                  |
|--------------------|--------------------|---------------------------------------------------------|
| Planning           | `planning-capture` | Requirements / design / roadmap / open questions / risks|
| Plan review        | `review-triage`    | Triaged findings, accepted changes routed to durable docs |
| Implementation     | `next-slice`       | One atomic slice in code, current-state updated inline  |
| Documentation update | `doc-update-lite`| Only durable docs touched; explicit "no updates needed" allowed |
| Review triage      | `review-triage`    | Same as plan review                                     |
| Cycle close        | `session-close` (or optional `cycle-close`) | Roadmap ticked, progress bullet, current-state next-step refreshed |
| Session close      | `session-close`    | Continuation context; handoff file only if needed       |

### 5.1 Planning

Inputs: user prompt, relevant requirements / design / ADRs, roadmap and
current-state, small external research, `/grill-me` when unclear. Outputs:
requirements changes, design / ADR updates, roadmap changes, open questions,
risks. Temporary implementation planning is allowed but does **not** become
durable unless it contains an invariant, contract, gotcha, or decision.

### 5.2 Plan review

Review files are not permanent truth. Classify via `/review-triage`:

- `must_fix_now`
- `should_fix_before_phase_complete`
- `backlog`
- `invalid_or_not_worth_doing`

Route accepted findings:

- behavior change → `docs/requirements/`
- architecture or tradeoff → `docs/design/` or `docs/adr/`
- sequencing → `docs/roadmap.md`
- current blocker or next step → `docs/current-state.md`

Rejected and deferred findings keep a short reason. Do not preserve the full
debate unless the reason is itself a durable decision.

### 5.3 Implementation

Default read set:

```
AGENTS.md
docs/current-state.md
docs/roadmap.md
recent git state
relevant code
only relevant requirements/design/ADRs
```

A good slice:

- small enough to finish in one session
- visible in code
- tied to the roadmap
- low ambiguity
- easy to verify
- leaves a clear next step

Update `docs/current-state.md` only on meaningful state changes (§3.3). Watch
the context meter; at ~50% the harness should warn with k-tokens — see §7.

### 5.4 Documentation update

Decision table (after implementation, review fixes, or phase progress):

```
Requirements changed?           Update docs/requirements/.
Architecture changed?           Update docs/design/ or docs/adr/.
Phase or next step changed?     Update docs/roadmap.md and docs/current-state.md.
Invariant/gotcha changed?       Update docs/implementation-notes.md or an ADR.
Only code internals changed?    Usually update no docs.
```

Saying "no durable docs needed updates" is a valid and useful outcome.

### 5.5 Review triage

Code review runs after meaningful slices, before phase completion, or on
request. Same classification as §5.2. Immediate fixes are limited to
correctness, safety, data loss, broken contracts, high-risk regressions, and
blockers. Everything else is phase-completion, backlog, or rejected with
reason.

### 5.6 Cycle close

After finishing one roadmap step:

- mark the roadmap step complete
- append one short `docs/progress.md` entry
- update `docs/current-state.md` with the next step
- note docs updated or intentionally not updated
- suggest a commit message (don't commit unless asked)

Use `/session-close` if the session is also ending, or the optional narrower
`/cycle-close` skill if you want this as a strict end-of-step ritual.

### 5.7 Session close

When context is high, work is stopping, or switching agents. Don't ask the
agent to "save everything." Ask for continuation context. Update
`docs/current-state.md` first; write a `docs/handoffs/*.md` only if extra
loose-end detail is needed.

Session-close output: date, task focus, changed files, implemented behavior,
current state, next atomic step, blockers/risks, docs updated, docs
intentionally not updated, discarded dead ends, suggested next skill.

## 6. Handoff template

Use only when `docs/current-state.md` isn't enough.

```
# Handoff — <date> <time>

## Where we are
<current phase + literal next step>

## Changed files
- <path>: <short reason>

## Implemented
- <durable outcome, not every edit>

## Open loops
- <unfinished item; pointer to file:line if useful>

## Decisions made
- <decision + one-line why; promote to ADR if durable>

## Discarded as noise
- <dead end, failed hypothesis, or rejected approach likely to be retried>

## Verification
- <command>: <result>

## Docs
- Updated: <docs>
- Intentionally not updated: <docs and reason>

## Next
<one atomic step>

## Suggested next skill
<e.g. /next-slice, /session-close>
```

## 7. Harness configuration (`settings.json`)

Wire via the `update-config` skill:

- **Stop hook** — print a one-line state cue (e.g. "`docs/current-state.md`
  last updated N turns ago; consider `/session-close`").
- **Context-threshold hook** — at ~50% warn "consider `/handoff` before
  context gets tight" and include k-tokens: 100k on 200k, 200k on 400k,
  500k on 1M, or 525k on GPT-5.5's 1,050k.
- **Permission allowlist** — read-only Bash + read-MCP via
  `/fewer-permission-prompts`.
- **MCP audit** — disable Gmail / Calendar / Drive (or any unused server) per
  project. Each adds tool schemas to every turn — the silent token killer.

## 8. Skill inventory

### Canonical set (keep)

| Skill              | Mode                     | Purpose                                              |
|--------------------|--------------------------|------------------------------------------------------|
| `planning-capture` | Planning                 | Classify planning output into durable docs           |
| `next-slice`       | Implementation (open + cycle) | Pick + start the next atomic implementable step |
| `doc-update-lite`  | Documentation update     | Selective durable-doc update; never internals        |
| `review-triage`    | Plan / code review       | Sort findings; implement only must-fix-now           |
| `session-close`    | Session end              | Continuation context; optional handoff via template  |

### Reused (already loaded by the harness)

`grill-me`, `grill-with-docs`, `to-prd`, `to-issues`, `review`, `doc-update`,
`project-state`, `handoff`, `update-config`, `fewer-permission-prompts`.

### Optional (keep only if descriptions stay sharply distinct)

- `session-open` — read-only bootstrap; stops after stating the next step.
  Overlaps with `next-slice`. **Keep one, not both**, unless their
  descriptions make the difference obvious. Default: drop `session-open`.
- `cycle-close` — narrow end-of-step ritual (roadmap tick + progress bullet +
  current-state refresh). Overlaps with `session-close`. Keep only if you
  want a stricter ritual when the session isn't also ending.

### Killed

- Custom `current-state` skill — replaced by `project-state` +
  `docs/current-state.md`.
- A `next-step` router skill — Claude already dispatches via skill
  descriptions; a router duplicates that and burns context.
- Root-level `activeContext.md` as a separate file — folded into
  `docs/current-state.md`. Keep only a one-line pointer file if a tool
  requires the name.

## 9. Standard prompts (when not using a skill)

- **Planning:** "Use `planning-capture`. Capture durable requirements,
  design decisions, roadmap changes, open questions, risks. No internals."
- **Implementation:** "Use `next-slice`. Determine the next atomic step from
  current state, roadmap, recent git, relevant docs, and code. Then
  implement that slice only."
- **Doc update:** "Use `doc-update-lite`. Update only durable docs affected
  by this change. If no durable docs need updates, say so explicitly."
- **Review:** "Use `review-triage`. Classify findings. Implement only
  must-fix-now unless I say otherwise."
- **Session close:** "Use `session-close`. Update continuation context with
  changed files, current state, next atomic step, blockers, docs updated,
  and docs intentionally not updated. Create a handoff only if current-state
  isn't enough."

## 10. Bootstrap checklist (once per project)

1. Drop in `AGENTS.md` (template at `opus/AGENTS.md`; update its paths to
   match the `docs/` layout in §2).
2. Create `docs/` with empty `current-state.md`, `roadmap.md`, `progress.md`
   and the `requirements/`, `design/`, `adr/`, `handoffs/` subdirectories
   (lazy — make as needed).
3. Move existing human-facing specs into `docs/requirements/` and
   `docs/design/`.
4. Extract non-obvious bits from current internals docs into `docs/adr/`,
   then archive or delete the internals docs.
5. Audit MCP servers; disable unused ones.
6. Configure Stop + context-threshold hooks via `update-config`.
7. After two weeks: audit which skills you actually invoked. Delete the rest.

## 11. Migration from existing habits

| Replace                                                | With                                                               |
|--------------------------------------------------------|--------------------------------------------------------------------|
| "Check all docs, infer state, document everything"    | Read AGENTS.md + `current-state.md` + `roadmap.md` + git + code    |
| Requirements + design + internals docs                 | Requirements + design/ADRs + current-state/roadmap/progress        |
| "Save the whole session before context runs out"      | Keep `current-state.md` cheap; handoff only for loose ends         |
| `activeContext.md` at repo root + `docs/current-state.md` | Single `docs/current-state.md`; activeContext.md is a pointer if needed |
| Both `session-open` and `next-slice`                   | `next-slice` only                                                  |
| Both `cycle-close` and `session-close`                 | `session-close`; add `cycle-close` only if you want a strict ritual|

## 12. What changed from v3 → v4

| v3                                                  | v4                                                            |
|-----------------------------------------------------|---------------------------------------------------------------|
| `activeContext.md` + `progress.md` + `roadmap.md` at repo root | All under `docs/`; activeContext folded into `docs/current-state.md` |
| Both `session-open` and `next-slice` listed         | `next-slice` is canonical; `session-open` optional, default drop |
| Both `cycle-close` and `session-close` listed       | `session-close` canonical; `cycle-close` optional ritual only |
| Five loops                                          | Seven explicit modes (planning, plan-review, implementation, doc update, review triage, cycle close, session close) |
| Handoff at repo root (`handoff-*.md`)              | `docs/handoffs/*.md`, only when current-state isn't enough    |
| Doc layout table mixed root + docs/                 | Single canonical layout under `docs/`                         |

## 13. Final operating principle

The goal is not less documentation — it's less *duplicated* documentation.

The useful context for future agents:

- what problem is being solved (`docs/requirements/`)
- what behavior must be preserved (tests + `docs/requirements/`)
- what decisions are already made (`docs/design/`, `docs/adr/`)
- what phase the project is in (`docs/roadmap.md`)
- what the next step is (`docs/current-state.md`)
- where the relevant code lives (the code itself)
- what invariants must not be broken (AGENTS.md gotchas +
  `docs/implementation-notes.md` + ADRs)

Everything else is discovered from code when needed.
