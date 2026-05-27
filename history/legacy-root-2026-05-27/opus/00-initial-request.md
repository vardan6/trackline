# Initial Request — Rethinking My Vibe-Coding Workflow

> Cleaned-up, deduplicated version of my original prompts. Captures the questions
> and motivations I brought into this session, before any research or answers.

## 1. Do I need three layers of specs?

While vibe coding and learning on this project, I landed on three layers of
specifications:

1. **Requirements spec** — what the system must do.
2. **Design spec** — how it's shaped at a high level.
3. **Internals / implementation / reference spec** — low-level mechanics.

I'm now rethinking the third layer. Reasoning:

- After planning sessions (grill-me, research, Q&A) we agree on technologies and
  higher-level behavior. That naturally belongs in the requirements + design
  layers.
- Internals docs are essentially equivalent to code. A coding agent can re-derive
  them from the source faster and more reliably than from a stale doc.
- After many round-trips between planning and implementation, the code drifts
  and the internals docs lag behind. They become a *second source of truth* that
  silently disagrees with the code.
- Updating all three layers after every change is friction I forget — and even
  when I remember, asking the agent to refresh all three burns tokens I don't
  want to spend.
- I mainly wanted the lower layer so that the next task could quickly find "how
  it works." But if the agent can read code just as quickly, the internals layer
  is pure overhead.

**Question:** do I drop the internals layer entirely, or keep a narrow version
of it for non-obvious mechanics only?

## 2. Define my actual workflow

I want to formalize my workflow instead of holding it in my head. Today it looks
roughly like this:

1. **Planning / brainstorm / research** — sometimes external, sometimes via the
   `grill-me` skill, sometimes a long prompt with attached docs.
2. **Capture plan** — ask the agent to save it. In the past I never told it
   *which* spec layer to save into; from now on I think I should be explicit
   ("save this as requirements" vs "as design").
3. **Plan review** — have a second agent review the plan and write findings to a
   markdown file. The current agent then checks those findings; usually 70-80%
   are adopted, the rest are valid but lower priority.
4. **Phase out the plan** — typically 6-10 phases, sometimes with sub-phases.
5. **Implementation cycles** — each cycle: ask "what's next?", implement, repeat.
6. **Mid-session documentation** — when context hits a model-aware threshold,
   ask the agent to document. The old shorthand was ~30-40%; stated precisely,
   that is 60k-80k on a 200k model, 120k-160k on a 400k model, and 300k-400k
   on a 1M model. I'm not sure exactly what it documents or where, and I'm not
   even sure I need all of it.
7. **Code review cycle** — every few iterations, ask the same or another agent
   to review. Usually 10 findings, ~70-80% get implemented (high priority, low
   risk).
8. **Doc refresh** — every few iterations, ask to update docs to match code.
   Mechanics unclear to me.
9. **Session end / handoff** — when context gets high, ask the agent to save
   state so the next session can continue. I don't know what it actually saves,
   what it *should* save, or whether I need it at all.
10. **Next session start** — spend tokens re-orienting before the next "what's
    next?" prompt.

Problems I notice:

- I keep retyping the same prompts.
- I have no skill for session-close or session-open handoffs.
- My one custom skill (`current-state`) consumes too many tokens; I wanted
  something simpler.
- I never know in advance when a session will end — context creep is
  unpredictable, so I can't plan handoff timing.
- I try to keep context under a model-aware working budget because the agent
  works cleanly there. The old 40% shorthand means 80k on a 200k model, 160k
  on a 400k model, and 400k on a 1M model. Above the useful working budget,
  regressions appear even if the advertised maximum context window is larger.

## 3. What goes in AGENTS.md?

I want any agent starting a session to know:

- What it is doing.
- What the workflow is.
- How we manage context.
- When and how to interrupt for handoff.
- How to start the next session efficiently.

But every time I add content to AGENTS.md, it adds hassle. Large instructions
seem worse than absent ones. **Conciseness feels right, but I need confirmation
and a principle for what earns its place.**

## 4. Two audiences, one set of docs?

Requirements + design docs are real artifacts **for humans** — presenting the
project, onboarding, stakeholder review. Worth it.

But **for the coding agent**, how much of that does it actually need? Does it
need all three layers at session start? Does it need any? My current habit is
to ask it to "check documentation" before each step, which is expensive and
maybe unnecessary.

I want this redefined.

## 5. The ask

Research the best vibe-coding / spec-driven workflows for long-running projects.
Compare against my workflow. I'd prefer to keep mine if it's actually
token-efficient. Help me:

- Decide the doc layers I really need.
- Define skills to stop me repeating prompts.
- Cover session start, session close, and the handoff in between.
- Land on something I can polish further on my own.
