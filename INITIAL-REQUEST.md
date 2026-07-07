# Initial Request — The Problems Behind My Workflow

> This is the record of *why* the workflow exists: the real pain points I hit
> doing long-running AI-assisted coding, and how I now understand solving each
> one. It is actual experience, not theory. Numbers are personal operating
> heuristics from months of real projects, never measured constants. It is
> structured to match the topic ordering used across the rest of the workflow
> docs (see [FINAL-WORKFLOW.md](FINAL-WORKFLOW.md)).

## Framing: engineer the workflow, not just the prompt

After several months of AI-assisted development, I noticed that most of my
problems were not coming from the model. They were coming from my own workflow.
My early approach was close to vibe-coding: it worked for small tasks, but it did
not scale to projects that run for weeks or months. So I started treating the
workflow as an engineering problem in its own right — specified, pressure-tested,
and refined against real work.

The recurring failures were almost never "the AI is not smart enough." They were
context-engineering problems, documentation problems, and orientation problems —
and all three turned out to be addressable. The pain points below are those
problems, in priority order, each paired with how I now understand solving it.

## 1. Staying on track — developer awareness and project alignment

**Pain.** On a months-long build it is easy to stay busy while slowly drifting
from the original problem. The agent makes lower- and medium-level decisions that
I only notice a week later, by which point the direction is wrong and the work
needs restructuring. The risk is becoming disconnected from what the agent is
actually doing while still feeling productive.

**Direction.** Plan by being challenged: before any code, a long grill-me session
where the agent interrogates the plan branch by branch until weak assumptions
surface. Planning is not done when the agent understands the task — it is done
when I can defend the task and its boundaries too. Keep project alignment in an
always-current roadmap / progress / activeContext trio, and enforce mode
discipline so the agent and I always know whether we are planning, implementing,
reviewing, or closing.

## 2. Context budget — smart zone vs. dumb zone

**Pain.** The biggest bottleneck is the active context window. Modern models
advertise huge windows, but the reliable "smart zone" is much smaller. Past it,
in the "dumb zone," the agent misses information already in context, loses focus
on the original goal, confuses similar files and functions, hallucinates details,
makes unnecessary changes, and spins anywhere from 20 to 60 minutes without solving the problem —
burning a large part of the usage limit and sometimes breaking the project. I
also tried to cap context as a percentage of the window, but the percentage is
misleading: the same degradation threshold is a much smaller percentage on a
large window.

**Direction.** Treat context as a *budget, not a window*. The degradation
threshold is an absolute token count, not a fraction of the advertised window. As
personal heuristics: keep working while load stays low, begin wrapping up the
current step around ~100k tokens, and stop adding new work around ~120k, closing
the session cleanly. Research supports this as model- and task-dependent:
degradation reliably starts well before the window is full — *lost in the middle*
(Liu et al.) and *context rot* (Chroma Research) — and while it is gradual in
aggregate, a given model on a given task can degrade abruptly once it passes its
effective context length. Every
loaded token competes for the model's attention, so a lean context is a quality
decision first and a cost decision second.

## 3. Documentation — layers, single source of truth, and drift

**Pain.** I kept three spec layers: requirements (what), design (why), and
internals (how the code works). The internals layer was meant to help the agent
orient quickly, but after enough planning-to-implementation round-trips the code
moved on and the document did not. It became a second source of truth that
quietly disagreed with the code — and with agents that is worse than with humans,
because the agent trusts the stale document completely. Updating all layers after
every change was friction I kept forgetting, and asking the agent to refresh them
burned tokens. I also never had a precise system for what to document, when, or
which layer should receive which information.

**Direction.** *Code is the truth*: re-derive how something works from the code,
and drop the internals layer — keep only durable invariants and genuine gotchas
that cannot be recovered by reading the code. Give every fact one canonical home
and point to it instead of copying it. Apply the deletion test: would removing
this make a future session decide worse? If not, delete it. Documentation is
agent-first and human-second, because a correct source of truth lets
human-readable summaries be generated on demand. Status never enters requirements
or design.

## 4. Sessions — externalized state and the save/restore cost

**Pain.** Every new session re-derived the project state from scratch: the same
files loaded, reasoned over, and discarded when the session ended, then paid for
again next time in tokens and quality. I never knew exactly what a handoff saved,
what it *should* save, or whether I needed it at all. Session end is
unpredictable — context creeps upward and I rarely know which step is the last —
so I could not plan handoff timing.

**Direction.** Externalize state into a few small, curated live-state files —
activeContext (now + the exact next step), roadmap (phases + what is done),
progress (append-only log of finished work) — so each session opens already
oriented from a cheap summary instead of the full history. Keep status out of
requirements and design so moving the work forward never means editing four
documents. Two cautions learned in practice: externalizing state is not free
either, since save and restore also cost tokens, so the files must stay small;
and the close must be cheap and routine, or an unpredictable session end will
make me skip it and lose the thread.

## 5. Repeating prompts — the need for skills

**Pain.** I kept retyping the same long prompts: update the documentation after a
step, write a complete handoff for the next session, review the recent work,
choose the next implementation slice, read the project and figure out what is
next. I had no reusable text for these, sometimes saving ad-hoc prompts in
project files, which was not a structured workflow. My one custom skill consumed
too many tokens.

**Direction.** Move the repeated prompts into named skills that guide the workflow
and manage its flow — what comes first, what is next, how to finish a step, how
to close a session and set up the next one. Skills (session-open, next-slice,
doc-update, review-triage, planning-capture, session-close, plus grill-me /
grill-with-docs / handoff) replace the retyping and keep each stage consistent.

## 6. Small, reviewable slices

**Pain.** Large changes are hard to review and understand, and they force the
agent to hold too much of the project in working memory at once — which feeds
straight back into the context and orientation problems above.

**Direction.** Implement one atomic vertical slice at a time, finished and
verified on its own, so I can review and understand each change and the agent
never needs the whole project in working memory.

## 7. Cross-model code review

**Pain.** I needed a structured way to review the agent's work, and I wanted to
use leftover usage productively — for example, when I still had a large share of
the limit but only 10–20 minutes before it reset.

**Direction.** Hand the work to a second, ideally stronger, and always different
model. It writes findings into a Markdown file — one entry per finding with a
severity guess — scoped to the diff since the last known-good commit. The
findings go back to the original agent, which validates each one against the
actual code before anything changes; in my experience roughly 70–80% survive,
triaged into must-fix-now, before-phase-complete, backlog, or invalid. Two
independent models usually agree on the important findings, and that agreement is
signal. The review discussion itself is disposable — only validated findings and
the resulting changes are kept.

## 8. Thin instruction files and exact names

**Pain.** `AGENTS.md` / `CLAUDE.md` are useful but loaded into every session, so
every line is comparatively expensive. Mine grew line by line — the agent appends
a note, I add a rule — until the file was a half-stale encyclopedia. For small,
focused tasks like bug fixes, a minimal or even absent instruction file often
worked better. Vague requests ("the settings page") also made the agent guess and
quietly bake wrong context into the diff.

**Direction.** Keep the instruction file a thin router: where things are, which
file owns which kind of fact, what the workflow expects. Everything loaded
competes for the model's attention — instructions and even tool schemas, not just
code — so more is not better. A minimal or even absent instruction file is the
right general default for small, focused tasks; this workflow is the deliberate
exception, because its `AGENTS.md` is load-bearing — it declares the mode, names
the next step, and points at the docs — so here it is mandatory rather than
optional. Name things exactly (page, widget, file, function,
path/XPath) so the agent fetches the right context itself, which is what lets the
context stay thin.

## 9. Version control — git as agent fuel

**Pain.** Coding agents rely on version-control state. When asked to review, an
agent often compares only the uncommitted diff against the last commit, not the
whole project — easy to miss, so I would think it reviewed everything while it
reviewed one slice. A messy history of "wip" and "fix" also removes a signal the
agent uses to orient itself.

**Direction.** Commit only working code, create clean checkpoints after each
meaningful step, and keep small commits that map to reviewable slices with
meaningful messages. The agent reads history (`git log`, `git diff`, `git blame`)
to understand what changed and why, so clean history is fuel, not just hygiene; it
also keeps review scope honest and lets me roll back to known-good states. What
began as the least-finished area has since settled into a practiced flow —
short-lived topic branches when work switches to a larger topic, commits a few
times a day as recoverable save points, a cross-model review before each pull
request, then merge (the operating detail lives in
[FINAL-WORKFLOW.md](FINAL-WORKFLOW.md) §7). The anchoring principle:
conversation provides reasoning, project files preserve decisions, and Git
preserves change.

## Desired outcome

A clearer personal workflow for long-running AI-assisted coding projects that:

- keeps the agent inside the smart zone for reliable, precise behavior
- preserves the useful parts of my process while cutting what does not earn its place
- reduces repeated prompts through reusable skills
- avoids stale, duplicated documentation and keeps one source of truth
- defines what to document, when, and in which layer
- externalizes just enough state for clean session open, close, and handoff
- makes future sessions quickly understand the current state and next step
- treats the workflow itself as something specified, pressure-tested, and improvable
