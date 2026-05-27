# Final Workflow — Vibe Coding for Long-Running Projects

> Synthesized from this session's conversation + research pass. This is the
> "polish-from-here" baseline. Open questions tagged **TODO**.

## 1. Guiding principles

1. **Two audiences, two doc sets.** Humans get narrative requirements + design.
   Agents get a thin router + on-demand retrieval. Never merge them.
2. **Drift kills middle layers.** Code + tests are the truth. Keep durable
   *why/what* docs (requirements, ADRs). Drop the internals/implementation
   spec layer. Agents re-derive *how* from code on demand.
3. **Split docs by volatility, not abstraction.**
   - *Slow-churn:* `requirements/`, `design/`, `docs/adr/` (decisions, not
     implementations).
   - *Fast-churn:* `activeContext.md`, `progress.md` (append-as-you-work).
4. **Context budget is real.** Cap session work with both percent and
   k-tokens. On a 200k window, 40% = 80k and 60% = 120k; on 400k, 40% =
   160k and 60% = 240k; on 1M, 40% = 400k and 60% = 600k. System prompt +
   tools + MCP burn tokens before you type. Compact at ~60%, not 90%.
5. **Skills dispatch via description, not a router.** Many small skills with
   sharp frontmatter beats one big skill that decides what to do next.
6. **The honest test for any doc line / AGENTS.md line / skill:** would
   removing it cause the next session to make a *different and worse*
   decision? If not, delete it.

## 2. Doc layers — the final set

| Layer                | Audience    | Volatility | Update trigger                |
|----------------------|-------------|------------|-------------------------------|
| `requirements/*.md`  | Humans      | Low        | Scope changes only            |
| `design/*.md`        | Humans      | Low        | Architectural changes only    |
| `docs/adr/*.md`      | Both        | Append-only| Per non-obvious decision      |
| `activeContext.md`   | Agents      | High       | Inline, as the agent works    |
| `progress.md`        | Both        | High       | End of each cycle             |
| `roadmap.md`         | Both        | Medium     | Phase start / phase complete  |
| `AGENTS.md`          | Agents      | Low        | Workflow rule changes only    |
| `~/handoff-*.md`     | Agents      | Per-session| At `/handoff` invocation      |

**Killed:** internals / implementation / reference spec layer. Anything
genuinely worth saving from past internals docs becomes either (a) an ADR
under `docs/adr/`, or (b) a code comment at the surprise.

## 3. The workflow loop

### 3.1 Project bootstrap (once)

1. Drop in `AGENTS.md` (see file in this folder).
2. Create empty `activeContext.md`, `progress.md`, `roadmap.md`.
3. Move existing human-facing specs into `requirements/` and `design/`.
4. Archive or delete current internals docs. Extract non-obvious bits into
   ADRs first.
5. Audit MCP servers — disable any not actively in use this week.

### 3.2 Planning phase

1. External brainstorm or `/grill-me` for stress-testing.
2. `/to-prd` (or manual) → writes to `requirements/<feature>.md`.
3. Design pass → writes to `design/<feature>.md` and ADRs as decisions
   crystallize. **Skip if the feature is small enough that code is the
   design.**
4. `/to-issues` to break into phased issues, or write `roadmap.md` with phase
   checkboxes.
5. Second-agent plan review → markdown findings file → current agent triages
   (typically adopts 70-80%).

### 3.3 Implementation cycle (the inner loop)

For each phase step:

1. **Open session.** Agent reads `AGENTS.md` → `activeContext.md` →
   `roadmap.md`. No spec re-read by default.
2. **Confirm next step.** Either you say it, or invoke `/project-state`
   (replaces the old token-hungry `current-state` skill).
3. **Implement.** Agent appends meaningful state changes to
   `activeContext.md` as it goes — current hypothesis, what was tried, what's
   blocking — not a play-by-play.
4. **Review** (every few iterations, not every cycle): `/review` or dispatch
   a fresh agent → findings markdown → triage.
5. **Close the cycle:** `/cycle-close` (see skill in this folder) — updates
   `progress.md` + `roadmap.md` checkbox, suggests commit.
6. **Watch the context meter.** At ~50% the harness should warn you (hook,
   see §5) and include k-tokens: 100k on 200k, 200k on 400k, 500k on 1M.
   Don't push to 90%.

### 3.4 Session end

- Triggered by context warning, end of phase, or end of day.
- Invoke `/handoff` → writes `~/handoff-YYYY-MM-DD-HHMM.md` with the
  template in §4 (including "Discarded as noise").
- `activeContext.md` continues to live in the repo; the handoff file captures
  *this session's* loose ends.

### 3.5 Next session start

- Agent reads, in order: `AGENTS.md`, `activeContext.md`, latest
  `handoff-*.md` (if any), `roadmap.md`.
- Total cost: small. No spec re-ingestion.
- If a task explicitly needs a spec, the agent fetches it on demand.

## 4. Handoff template

```
# Handoff — <date> <time>

## Where we are
<one paragraph; current phase + the literal next step>

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
- Outstanding question for the human: <if any>
```

## 5. Harness configuration (settings.json)

**TODO:** wire these via the `update-config` skill.

- **Stop hook** that prints a one-line state cue ("activeContext.md last
  updated <N> turns ago; consider /cycle-close").
- **Context-threshold hook:** at ~50% warn "consider /handoff before context
  gets tight" and include k-tokens: 100k on 200k, 200k on 400k, 500k on 1M.
- **Permission allowlist:** read-only Bash + read-MCP via
  `/fewer-permission-prompts` skill.
- **MCP audit:** disable Gmail / Calendar / Drive MCP servers unless this
  project actively uses them. Each one adds tool schemas to every turn.

## 6. Skills inventory

### Keep as-is
`grill-me`, `grill-with-docs`, `to-prd`, `to-issues`, `review`, `doc-update`,
`project-state`, `handoff`, `update-config`, `fewer-permission-prompts`.

### Delete
- Custom `current-state` skill — replaced by `project-state` +
  `activeContext.md`.

### New (drafted in `./skills/`)
- `cycle-close` — deterministic end-of-cycle close (progress.md + roadmap
  checkbox + commit suggestion).
- `session-open` — the read-order at session start (AGENTS.md →
  activeContext → handoff → roadmap), in one skill so it dispatches
  automatically when the user says "let's continue" or starts blank.

### Reconsidered (do NOT build)
- `next-step` router skill — Claude already dispatches via skill descriptions;
  a router would duplicate that and burn context. Sharpen descriptions on
  existing skills instead.

## 7. Open questions / TODOs

- **TODO:** Decide whether `progress.md` and `activeContext.md` live at repo
  root or under `docs/`. Lean toward root for discoverability.
- **TODO:** Configure the context-threshold and Stop hooks via
  `update-config`. Pick a concrete trigger %.
- **TODO:** First cleanup pass — delete or archive existing internals docs.
  Extract anything non-obvious into ADRs *before* deleting.
- **TODO:** After two weeks of using this, audit which skills you actually
  invoke. Delete ones you don't.
- **TODO:** Decide on a commit-message convention for cycle-close commits
  (e.g. `chore(cycle): <phase> step <n> — <one-line>`).

## 8. What changed from my original instinct

| Original thought                            | After research                              |
|---------------------------------------------|---------------------------------------------|
| Maybe keep internals as a thin layer        | Delete entirely; ADRs absorb the survivors  |
| Build a `next-step` router skill            | Don't — sharpen existing skill descriptions |
| Document at 30-40% context                  | State both percent and tokens: 60k-80k on 200k, 120k-160k on 400k, 300k-400k on 1M; document inline via `activeContext.md`; compact at ~60% |
| Custom `current-state` skill                | Replace with `project-state` + active doc   |
| AGENTS.md should describe the project       | AGENTS.md is a router + workflow rules only |
| Update all doc layers after each cycle      | Update fast-churn only; slow-churn rarely   |
