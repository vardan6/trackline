# Session Transcript — Workflow Rethink

> Raw record of the back-and-forth that produced the final workflow. Lightly
> reflowed for readability; substance unchanged.

---

## Turn 1 — Do I need the internals layer?

**Me:** *(see 00-initial-request.md §1 for the full original question)*

**Opus:**

You're identifying the real tradeoff correctly: internals docs are the layer
most prone to drift because they live closest to code, which is exactly the
layer code-reading can reconstruct cheapest. I'd drop internals as a standing
layer and keep only requirements + design as durable docs (the "why" and "what"
that code can't tell you), then let agents re-derive implementation details
from code on demand — with one narrow exception: keep an internals note only
for genuinely non-obvious mechanics (hidden invariants, ordering constraints,
why an unusual pattern was chosen), which is the same rule your memory system
already uses.

The honest test for whether an internals doc earns its keep: if a fresh agent
reading the code would arrive at the same understanding within a few minutes,
the doc is duplication and will drift; if they'd miss something important,
that something is what belongs in the doc — not the whole walkthrough.

---

## Turn 2 — Define my personal workflow

**Me:** *(see 00-initial-request.md §2 for the full original question)*

**Opus:**

Before going wide on research, let me reflect back what I think your actual gap
is, because I suspect it's smaller than it looks.

You already own most of this workflow as skills. Look at what's loaded:
`grill-me` / `grill-with-docs` (planning), `to-prd` (capture requirements from
conversation), `to-issues` (break plan into phases), `review` (code review
pass), `doc-update` (update docs after code), `project-state` (infer current
state — likely cheaper than your custom one), `handoff` (compact for next
session). The thing you're missing is not skills — it's **triggers and
sequencing**: knowing which skill to fire at which transition, and a tiny
"router" that picks the next step so you stop typing the same prompts.

On the drift problem: docs can't fix it; only tests + code-derivable structure
can. Every doc layer you maintain is a liability proportional to how often it
changes. The industry direction (spec-driven dev à la Kiro / Spec Kit,
Anthropic's own guidance, the Aider/Cline patterns) is converging on: keep
durable why/what docs (requirements + design / ADRs), let agents re-derive
*how* from code on demand, and use tests as the executable specification that
catches drift the moment it happens. Your instinct to drop the internals layer
aligns with this.

**Concrete proposal — three additions, no more:**

1. **`next-step` skill** (cheap replacement for current-state-as-router):
   reads roadmap + last commit + uncommitted diff, outputs one sentence:
   "next step is phase X.Y: do Z" or "next step is review/document." Single-
   purpose, ~5k tokens, replaces the prompt you keep retyping.
2. **Session-budget trigger, not a skill:** a hook in `settings.json` that
   warns around 100k tokens with "consider /handoff." You said you never know
   when a session will end — make the harness tell you. (`update-config`
   skill earns its keep here.)
3. **`cycle-close` skill:** at the end of each implementation cycle, runs
   the deterministic close sequence — update roadmap status, run `doc-update`
   only on the requirements/design layer, suggest commit. Stops you from
   forgetting and stops the agent from rewriting internals docs you no longer
   want.

**Recommendation order:** delete the internals layer first (one cleanup pass),
then build `next-step`, then add the context-threshold hook, then `cycle-close`.
Don't build all four before testing one — your workflow drifts too, and you
want to feel each piece before committing to the next.

---

## Turn 3 — What goes in AGENTS.md? Two audiences?

**Me:** *(see 00-initial-request.md §3 + §4)*

**Opus:**

Two audiences, two different needs — and conflating them is what makes
AGENTS.md grow into a hassle.

**For humans:** requirements + design docs are real artifacts. Narrative,
motivation, tradeoffs, who-said-what. They earn their keep at review time,
onboarding, stakeholder conversations.

**For agents:** the docs are mostly retrieval targets, not required reading.
An agent at session start does not need to ingest your spec pack — it needs
to know where to look when it gets stuck and what the workflow rules are.
Loading specs preemptively burns context for information the agent often
doesn't need.

**AGENTS.md as a router, not a knowledge base.** Target <80 lines. It should
answer four questions and nothing else:

1. **Where am I right now?** → one line pointing at `roadmap.md` or
   equivalent, with the convention that the current phase is marked there.
   Not the content — the pointer.
2. **What's the workflow?** → 5-10 lines of rules, not narrative. "After
   implementing a step, update roadmap status. Do not update internals docs.
   Run `/handoff` when context is around 100k tokens." This is the part you keep re-typing in
   prompts — putting it here is the actual win.
3. **Where are the canonical docs if I need them?** → pointers to
   `requirements/`, `design/`, with one sentence each on when to consult.
4. **What are the non-obvious gotchas?** → things code can't tell you. Hidden
   invariants, "don't refactor X yet because Y is pending," current freeze
   rules.

That's it. Architecture descriptions, file maps, tech stack — all derivable
and will drift. Leave them out.

**How many layers does an agent need at session start?** Zero, by default. It
needs the router (AGENTS.md) and a "next step" answer. Specs get pulled in
only when the task requires them — grilling, cross-cutting design, or when a
step explicitly says "implement per `design.md` §3." Same logic as the memory
system: load on relevance, not on principle.

The honest test for any line in AGENTS.md: would removing it cause the next
session to make a *different and worse* decision? If not, delete it. Most
content in AGENTS.md fails this test and just inflates every conversation.

---

## Turn 4 — Research pass

**Me:** Please go do the research and bring back best practices.

**Opus (after dispatching a research subagent):**

**Confirmed:**

- **Drop internals layer.** Cline, Kiro, BCMS, Augment all converge:
  requirements + ADRs hold up; the middle/internals layer is what drifts. Code
  + tests *are* the design doc.
- **AGENTS.md as a router.** Consensus cap is **<300 lines / ~2K tokens** —
  every line competes with working memory. Frontier models reliably attend to
  ~150-200 instructions before signal degrades.
- **Your context ceiling is correct, not paranoid:** system prompt + tools
  + MCP + CLAUDE.md eat 30-40k tokens before you type; performance often
  degrades around the 100k-150k working range, before the model's full window.
- **Phased plans + second-agent review + selective adoption** matches what
  Simon Willison calls "vibe engineering."

**Updated my view — I was wrong about the router skill.** Community consensus
(anthropics/skills, 320+ skill libraries surveyed) is **many granular skills
with sharp description frontmatter, not a router skill**. Claude already
dispatches by reading every `SKILL.md` description; an explicit router is
redundant and consumes context. Practitioners report deleting router skills
once they trusted native dispatch. **Scratch the earlier `next-step` skill
suggestion** — invest instead in tightening descriptions on existing skills
(`project-state`, `handoff`, `doc-update`) so they fire automatically at the
right moments.

**New, non-obvious findings worth adopting:**

1. **Split docs by volatility, not abstraction.** Cline's pattern:
   - *Long-term* = `projectbrief.md` / `systemPatterns.md` / `techContext.md`
     (principles only, ADR-flavored, slow churn).
   - *Short-term* = `activeContext.md` + `progress.md` — the agent appends to
     these inline as it works, no separate "document everything" step at end
     of session.
   - This collapses the expensive `current-state` skill into "just read
     `activeContext.md`."
2. **Handoff template should include a "Discarded as noise" section** —
   failed hypotheses, dead ends. Most templates omit this; it's what stops
   the next session from re-litigating the same wrong paths.
3. **Compact around 120k tokens, not near the model limit** — late
   compaction loses fidelity. Your 60k-80k trigger for *documentation* is
   fine; don't conflate it with `/compact`.
4. **MCP server count is the silent token killer** — each server adds tool
   schemas to every turn. Audit what's enabled.

**Revised concrete proposal:**

- Delete internals docs layer. Move surviving "why we did it this way" notes
  into per-feature ADRs.
- Add `activeContext.md` + `progress.md` to the project root. Update AGENTS.md
  with one rule: "Append to `activeContext.md` as you work. Read it at session
  start instead of regenerating state."
- Drop the custom `current-state` skill; lean on `project-state` +
  `activeContext.md`.
- When you next run `/handoff`, add "Discarded as noise" to the output
  template.
- Audit MCP servers; disable any you don't actively use.
