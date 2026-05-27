# Final Workflow — Vibe Coding for Long-Running Projects (v3)

> Synthesis of everything in this folder: the original request (`00`), the
> session transcript (`01`), the first synthesis (`02`), the parallel
> `docs/final-workflow.md`, both `AGENTS.md` drafts, and all skills in
> `skills/` and `opus/skills/`. This is the consolidated baseline — supersedes
> `02-final-workflow.md` and `docs/final-workflow.md`.

---

## 1. Guiding principles

1. **Two audiences, two doc sets.** Humans get narrative requirements +
   design. Agents get a thin router + on-demand retrieval. Never merge them.
2. **Drift kills middle layers.** Code + tests are the truth. Keep durable
   *why/what* docs (requirements, ADRs). Drop the internals / implementation /
   reference spec layer. Agents re-derive *how* from code on demand.
3. **Split docs by volatility, not abstraction.**
   - *Slow-churn:* `requirements/`, `design/`, `docs/adr/` — decisions, not
     implementations.
   - *Fast-churn:* `activeContext.md`, `progress.md`, `roadmap.md` — appended
     inline as work happens.
4. **Context budget is real.** System prompt + tools + MCP burn 30-40k tokens
   before you type. Cap working context by token count, not raw percentage:
   document around 60k-80k, warn around 100k, compact around 120k.
5. **Skills dispatch via description, not a router.** Many small skills with
   sharp frontmatter beats one big router. Sharpen descriptions so existing
   skills fire automatically at the right transition.
6. **Mode awareness.** Before acting, the agent knows which loop it is in:
   planning, plan-review, implementation, review-triage, or session-close.
   AGENTS.md and skill descriptions are what make this automatic.
7. **The honest test for any doc line / AGENTS.md line / skill:** would
   removing it cause the next session to make a *different and worse*
   decision? If not, delete it.
8. **The honest test for any new doc:** will this still be useful if the code
   changes? If no, leave it in the conversation or the commit message.

## 2. Doc layers — the final set

| Layer                | Audience    | Volatility   | Update trigger                |
|----------------------|-------------|--------------|-------------------------------|
| `requirements/*.md`  | Humans      | Low          | External behavior / scope     |
| `design/*.md`        | Humans      | Low          | Architectural changes only    |
| `docs/adr/*.md`      | Both        | Append-only  | Per non-obvious decision      |
| `roadmap.md`         | Both        | Medium       | Phase start / phase complete  |
| `activeContext.md`   | Agents      | High         | Inline, as the agent works    |
| `progress.md`        | Both        | High         | End of each cycle             |
| `AGENTS.md`          | Agents      | Low          | Workflow rule changes only    |
| `handoff-*.md`       | Agents      | Per-session  | At `/handoff` invocation      |

**Document this** (still useful if code changes):
external behavior, user-visible requirements, non-goals, architecture
decisions, rejected alternatives, module boundaries, protocols / schemas,
safety or correctness invariants, non-obvious gotchas, where future agents
should begin reading code, current phase and next step.

**Don't document this** (re-derivable from code):
function-by-function descriptions, private call chains, ordinary
implementation details, temporary implementation plans after code exists,
review discussion history, obvious code structure.

**Killed:**

- `docs/internals/` — implementation / reference spec layer. Survivors become
  ADRs or short code comments at the surprise.
- A separate `current-state.md` doc — replaced by `activeContext.md` +
  `progress.md` (Cline pattern, cheaper to update inline).

## 3. The workflow — five loops

Each loop has a specific documentation output. The agent identifies the loop
before acting.

### 3.1 Planning loop

When: starting a feature, phase, or major change.

1. External brainstorm, `/grill-me`, or `/grill-with-docs` for stress-testing.
2. `/to-prd` → writes to `requirements/<feature>.md`.
3. Design pass → `design/<feature>.md` and ADRs under `docs/adr/` as decisions
   crystallize. **Skip if the feature is small enough that code is the
   design.**
4. `/to-issues` or `roadmap.md` checkboxes to phase the plan.
5. Invoke `/planning-capture` to classify the planning output into
   requirements / design / roadmap / open questions / risks. **Never** into a
   full implementation spec.

### 3.2 Plan-review loop

When: a second agent reviews the plan.

- Review findings are not permanent history.
- Triage via `/review-triage` into `must_fix_now`, `should_fix_before_phase_complete`,
  `backlog`, `invalid_or_not_worth_doing`.
- Accepted changes update requirements / design / roadmap. Rejected and
  deferred points get a one-line reason kept with the triage output.

### 3.3 Implementation loop (the inner loop)

For each phase step:

1. **Open session** — invoke `/session-open` (or read in fixed order:
   `AGENTS.md` → `activeContext.md` → newest `handoff-*.md` → `roadmap.md`).
   Do not pre-read `requirements/` or `design/` unless the next step
   explicitly needs them.
2. **Confirm next step** — invoke `/next-slice` if the next atomic step isn't
   already obvious from the read-order above.
3. **Implement** — append meaningful state changes to `activeContext.md` as
   you work (current hypothesis, what was tried, what's blocking). Not a
   play-by-play.
4. **Watch the context meter** — around 100k tokens the harness warns (see
   §6). Don't push past 120k before handing off.
5. **Close the cycle** — invoke `/cycle-close`: tick the roadmap checkbox,
   append a one-line entry to `progress.md`, refresh `activeContext.md`'s
   "in progress" section to the next step, suggest a commit. **Do not** touch
   `requirements/`, `design/`, `docs/adr/`.
6. **Review** (every few cycles, or on request) — `/review` or dispatch a
   fresh agent → findings markdown → back to §3.2.

### 3.4 Review-triage loop

Already covered as §3.2 — same skill (`/review-triage`) used for plan review
and code review findings. Only `must_fix_now` is implemented by default.

### 3.5 Session-close loop

When: context warning, end of phase, end of day.

1. Invoke `/session-close` (or `/handoff`).
2. Apply `/doc-update-lite` rules to update only durable docs.
3. Write `handoff-YYYY-MM-DD-HHMM.md` using the §4 template — including
   **"Discarded as noise"** so the next session doesn't re-litigate dead ends.
4. Reference paths instead of copying doc content into the handoff.

## 4. Handoff template

```
# Handoff — <date> <time>

## Where we are
<one paragraph: current phase + the literal next step>

## Open loops
- <thing not finished; pointer to file:line if applicable>

## Decisions made this session
- <decision + one-line why; promote to ADR if non-obvious>

## Discarded as noise
- <hypothesis that didn't pan out, dead end explored — so next session
  doesn't re-litigate it>

## Context for next agent
- Files touched: <list>
- Tests run: <command + result>
- Docs updated: <list>
- Docs intentionally not updated: <list + reason>
- Outstanding question for the human: <if any>
- Suggested next skill: <e.g. /session-open, /next-slice>
```

## 5. AGENTS.md — the router

Hard cap: ~80 lines. AGENTS.md is a router, not a knowledge base. It answers
four questions and nothing else:

1. **Where am I?** Pointer to `roadmap.md` and `activeContext.md`.
2. **What's the workflow?** 5-10 lines of rules (read-order at session start,
   when to append to `activeContext.md`, when to run `/cycle-close`, when to
   `/handoff`, never touch internals docs, never pre-load specs).
3. **Where are canonical docs?** Pointers to `requirements/`, `design/`,
   `docs/adr/` with one-line "read when…" cues.
4. **Non-obvious gotchas.** Per-project freezes, hidden invariants, in-progress
   refactors. Empty if none — do not pad.

Bad content for AGENTS.md: full requirements, full architecture, phase
history, old plans, narrative workflow explanations, anything derivable from
code.

The drafted file at `opus/AGENTS.md` is the canonical template.

## 6. Harness configuration (`settings.json`)

Wire via the `update-config` skill:

- **Stop hook** — print a one-line state cue (e.g. "`activeContext.md` last
  updated N turns ago; consider `/cycle-close`").
- **Context-threshold hook** — around 100k tokens warn "consider `/handoff`
  before context gets tight."
- **Permission allowlist** — read-only Bash + read-MCP via
  `/fewer-permission-prompts`.
- **MCP audit** — disable Gmail / Calendar / Drive (or any unused server) per
  project. Each adds tool schemas to every turn — the silent token killer.

## 7. Skill inventory

### Keep / use as-is

`grill-me`, `grill-with-docs`, `to-prd`, `to-issues`, `review`, `doc-update`,
`project-state`, `handoff`, `update-config`, `fewer-permission-prompts`.

### Custom skills in this folder

| Skill                 | Loop                   | Purpose                                         |
|-----------------------|------------------------|-------------------------------------------------|
| `session-open`        | Implementation (open)  | Fixed-cost session bootstrap, fixed read-order. |
| `next-slice`          | Implementation         | Pick the next atomic implementable step.        |
| `planning-capture`    | Planning               | Classify planning output into durable docs.     |
| `review-triage`       | Plan / code review     | Sort findings; implement only must-fix-now.     |
| `doc-update-lite`     | After implementation   | Selective durable-doc update; never internals.  |
| `cycle-close`         | Implementation (close) | Tick roadmap, append progress, refresh active.  |
| `session-close`       | Session end            | Handoff packet via doc-update-lite + template.  |

### Delete / don't build

- Custom `current-state` skill — replaced by `project-state` +
  `activeContext.md`.
- A `next-step` router skill — Claude already dispatches via skill
  descriptions; a router duplicates that and burns context. Sharpen existing
  skill descriptions instead.

## 8. Standard prompts (when not using a skill)

- **Planning:** "Use `planning-capture`. Capture only durable requirements,
  design decisions, roadmap changes, open questions, risks. No internals."
- **Implementation:** "Use `next-slice`. Determine and implement one atomic
  step from current state, roadmap, recent git, and code."
- **Doc update:** "Use `doc-update-lite`. Update only durable docs affected
  by this change. State which were updated and which were intentionally left."
- **Review:** "Use `review-triage`. Classify each finding. Implement only
  must-fix-now unless I say otherwise."
- **Session close:** "Use `session-close`. Minimal handoff, update durable
  docs only, identify the next atomic step."

## 9. Bootstrap checklist (once per project)

1. Drop in `AGENTS.md` (template at `opus/AGENTS.md`).
2. Create empty `activeContext.md`, `progress.md`, `roadmap.md` at repo root.
3. Move existing human-facing specs into `requirements/` and `design/`.
4. Extract non-obvious bits from any current internals docs into
   `docs/adr/` — *then* archive or delete the internals docs.
5. Audit MCP servers; disable unused ones.
6. Configure Stop + context-threshold hooks via `update-config`.
7. After two weeks: audit which skills you actually invoked. Delete the rest.

## 10. Open TODOs

- Pick a concrete `/handoff` trigger threshold (100k tokens recommended).
- Decide whether `activeContext.md` / `progress.md` / `roadmap.md` live at
  repo root or under `docs/`. Lean toward root for discoverability.
- Choose a commit-message convention for cycle-close commits, e.g.
  `chore(cycle): <phase> step <n> — <one-line>`.
- After two weeks of use, prune unused skills.

## 11. What changed across iterations

| Original instinct                            | After research / synthesis                   |
|----------------------------------------------|----------------------------------------------|
| Keep a thin internals layer                  | Delete entirely; ADRs absorb survivors       |
| Build a `next-step` router skill             | Don't — sharpen existing skill descriptions  |
| Document at 60k-80k tokens on the 200k baseline | Document inline via `activeContext.md`; compact around 120k tokens |
| Custom `current-state` skill                 | Replace with `project-state` + activeContext |
| AGENTS.md describes the project              | AGENTS.md is a router + workflow rules only  |
| Update all doc layers after each cycle       | Fast-churn inline; slow-churn rarely         |
| Single `current-state.md` for fast startup   | `activeContext.md` (inline) + `progress.md` (per cycle) |
| Review findings stored permanently           | Triage output only; reasoning preserved for rejected |
| Five-loop workflow as a mental model         | Same five loops, each mapped to one skill    |

## 12. Final operating principle

The goal is not less documentation — it's less *duplicated* documentation.

The most useful context for future coding agents is:

- what problem is being solved (`requirements/`)
- what behavior must be preserved (tests + `requirements/`)
- what decisions are already made (`design/`, `docs/adr/`)
- what phase the project is in (`roadmap.md`)
- what the next step is (`activeContext.md`)
- where the relevant code lives (the code itself)
- what invariants must not be broken (AGENTS.md gotchas + ADRs)

Everything else is discovered from code when needed.
