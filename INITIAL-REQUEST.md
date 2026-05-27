# Initial Request — Rethinking My Vibe-Coding Workflow

> Merged from the conversational opus version and the formal docs version.
> Nothing from either is dropped. Captures the questions, motivations, and
> specifics brought into the design session before any research or answers.

## Context

I have been doing AI-assisted coding, sometimes close to "vibe coding," while
trying to learn and improve my long-running project workflow. Over time I
landed on three layers of specifications:

1. **Requirements spec** — what the system must do.
2. **Design spec** — how it's shaped at a high level.
3. **Internals / implementation / reference spec** — low-level mechanics.

I'm rethinking the third layer.

## 1. Do I need three layers of specs?

Reasoning behind dropping the third layer:

- After planning sessions (`grill-me`, research, Q&A) we agree on technologies
  and higher-level behavior. That naturally belongs in requirements + design.
- Internals docs are essentially equivalent to code. A coding agent can
  re-derive them from the source faster and more reliably than from a stale
  doc.
- After many round-trips between planning and implementation, the code drifts
  and the internals docs lag behind. They become a *second source of truth*
  that silently disagrees with the code.
- Updating all three layers after every change is friction I forget — and
  even when I remember, asking the agent to refresh all three burns tokens I
  don't want to spend.
- I mainly wanted the lower layer so the next task could quickly find "how it
  works." But if the agent can read code just as quickly, the internals layer
  is pure overhead.

Problems this creates concretely:

- Every update may require updating code + requirements + design + internals.
- I forget to update one of the layers.
- Updating all layers costs tokens.
- Lower-level docs become stale after many planning↔implementation iterations.
- The value of internals docs is unclear if the code already contains the
  authoritative implementation.

### Why I wanted lower-level documentation in the first place

So future sessions and agents could quickly understand:

- how something works
- where important logic lives
- what has already been implemented
- how to continue the next task with fewer mistakes
- what the current state of the project is

After months of work and many planning-to-implementation round trips per day,
this documentation became hard to maintain.

**Question:** do I drop the internals layer entirely, or keep a narrow
version for non-obvious mechanics only?

## 2. Define my actual workflow

I want to formalize my workflow instead of holding it in my head. Today it
looks roughly like this:

1. **Planning / brainstorm / research** — sometimes external, sometimes via
   `grill-me`, sometimes a long prompt with attached docs.
2. **Capture plan** — ask the agent to save it. In the past I never told it
   *which* spec layer to save into; from now on I think I should be explicit
   ("save this as requirements" vs "as design").
3. **Plan review** — have a second agent review and write findings to a
   markdown file. The current agent then checks those findings; usually
   **70-80%** are adopted into the plan or implemented when appropriate, the
   rest are valid but lower priority.
4. **Phase out the plan** — typically 6-10 phases, sometimes with sub-phases.
5. **Implementation cycles** — each cycle: ask "what's next?", implement,
   repeat.
6. **Mid-session documentation** — when active context reaches roughly
   **100k-120k tokens**, ask the agent to document or prepare continuation
   state. That is about **39-46%** of Codex's current 258.4k effective
   window, **50-60%** of Sonnet 4.6 / Haiku 4.5's 200k window, or
   **10-12%** of Opus 4.7's 1M window. I'm not sure exactly what it
   documents or where, and I'm not even sure I need all of it.
7. **Code review cycle** — every few iterations, ask the same or another
   agent to review. Usually ~10 findings, **70-80%** get implemented (high
   priority, low risk).
8. **Doc refresh** — every few iterations, ask to update docs to match code.
   Mechanics unclear to me.
9. **Session end / handoff** — when context gets high, ask the agent to save
   state so the next session can continue. I don't know what it actually
   saves, what it *should* save, or whether I need it at all.
10. **Next session start** — spend tokens re-orienting before the next
    "what's next?" prompt.

### Problems I notice

- I keep retyping the same prompts.
- I have no skill for session-close or session-open handoffs.
- My one custom skill (`current-state`) consumes too many tokens; I wanted
  something simpler.
- I never know in advance when a session will end — context creep is
  unpredictable, so I can't plan handoff timing.
- I try to keep active context under a model-aware working budget rather than
  a raw percentage. The old **30-40%** habit meant **60k-80k** on a 200k
  model. On current Codex, local telemetry reports a **258.4k effective
  context window** for recent GPT-5.* Codex models, so **100k-120k** is
  about **39-46%**. On Opus 4.7 it is only **10-12%**; on Sonnet 4.6 and
  Haiku 4.5 it is **50-60%**. The useful threshold should be recorded as
  both percentage and k-tokens for the active product surface.
- **240k is not 100% for the models I care about**; it is about **93%** of
  Codex's current 258.4k effective window, **24%** of Opus 4.7's 1M window,
  and **120%** of Sonnet 4.6 / Haiku 4.5's 200k window.
- I keep too much of the workflow in my head.

### What I do not have a precise system for

- what should be documented
- when it should be documented
- which document layer should receive which information
- when to create a handoff
- how to start the next session efficiently
- how to avoid stale implementation documentation
- how to keep active context under a reliable token budget instead of relying
  on a misleading percentage of the model's maximum context window
- how to make coding agents always know whether they are planning,
  implementing, reviewing, or closing a session

## 3. What goes in AGENTS.md?

I want any agent starting a session to know:

- What it is doing.
- What the workflow is.
- How we manage context.
- When and how to interrupt for handoff.
- How to start the next session efficiently.

Every time I add content to AGENTS.md it adds hassle. Large instructions seem
worse than absent ones. **Conciseness feels right, but I need confirmation
and a principle for what earns its place.**

## 4. Two audiences, one set of docs?

Requirements + design docs are real artifacts **for humans** — presenting the
project, onboarding, stakeholder review. Worth it.

But **for the coding agent**, how much of that does it actually need? Does
it need all three layers at session start? Does it need any? My current habit
is to ask it to "check documentation" before each step, which is expensive
and maybe unnecessary.

I want this redefined.

## 5. The ask

Research the best vibe-coding / spec-driven workflows for long-running
projects. Compare against my workflow. I'd prefer to keep mine if it's
actually token-efficient. Help me:

- Decide the doc layers I really need.
- Define skills to stop me repeating prompts.
- Cover session start, session close, and the handoff in between.
- Land on something I can polish further on my own.

## Questions to answer

- Do I really need an internals specification layer?
- If yes, what should it contain?
- If no, what replaces it?
- How much documentation is useful for coding agents?
- How much documentation is useful for humans?
- What should go into `AGENTS.md`?
- What should be moved into skills instead of always-loaded instructions?
- What skills should exist for my repeated workflow?
- How should I start and end sessions efficiently?
- How can I reduce token use while improving reliability?

## Desired outcome

A clearer personal workflow for long-running AI-assisted coding projects
that:

- preserves the useful parts of my current process
- reduces repeated prompts
- reduces token usage
- avoids stale duplicated documentation
- defines when and where to document things
- defines reusable skills for common workflow steps
- supports clean session handoffs
- keeps context small enough for reliable coding work
- makes future sessions quickly understand the current state and next step
