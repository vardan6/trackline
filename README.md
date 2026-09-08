# Trackline

**Engineer the workflow, not just the prompt.**

Trackline is a session-based workflow for building long-running projects with
AI coding agents. Tested on **Claude Code and Codex**, refined against months of
real work.

## The problem

Vibe-coding works for a day-long task. Once a project runs longer than a
week — many sessions, several rounds of planning and implementation — two
problems dominate:

1. **The human loses track.** The agent is faster than your understanding:
   each step looks reasonable, and a week later you discover the medium-level
   decisions it quietly made. You no longer know what was built or how to
   proceed — the moment many people quit coding agents.
2. **The agent leaves its smart zone.** The reliable context zone is far
   smaller than the advertised window. Past it, the agent misses information
   already in context, confuses similar files, and spins for an hour burning
   your usage limits. Context must be managed as a budget.

Both are amplified by a third: **project knowledge has no reliable home.**
Every new session re-derives state from scratch, status is buried inside
design documents, and stale documentation gets trusted completely — the same
bug was "fixed" four times because a leftover doc kept re-teaching the buggy
behavior as intended.

None of these are model problems. They need a *defined process* — specified,
pressure-tested, and refined against real work, like any other engineering
artifact. The full analysis of all nine failure modes is in [WHY.md](WHY.md).

## The idea

Work happens in three **self-contained cycles** — *plan*, *implement*,
*review* — each run when needed, each ended with `/session-close`, the standard
close-out step that synchronizes the project's live state. The next session
opens from a few small state files instead of a long transcript.

The discipline connects four recurring needs:

| Need | Practice | Read more |
|---|---|---|
| Keep the developer aligned | Challenge the plan, capture the decisions, and work in independently verifiable slices. | [Planning](WORKFLOW.md#32-grill-me-and-grill-with-docs--plan-by-being-challenged) |
| Preserve knowledge | Give each fact one home; keep current state separate from agreed behavior and design. | [Document roles](WORKFLOW.md#4-the-state-files-and-the-docs-tree) |
| Sustain work across sessions | Load only relevant context, close deliberately, and resume from small state files. | [Session close](WORKFLOW.md#310-session-close--the-non-optional-close) |
| Check and recover work | Review plans and code with another provider, validate findings, and keep meaningful Git history. | [Review](WORKFLOW.md#39-cross-review-and-review-triage--cross-model-code-review) |

This is a reader's overview of the practices, not another numbered principle
list. The [design statements](WORKFLOW.md#2-operating-principles) explain the
rules behind them; [WHY.md](WHY.md) connects the observed failures to the
responses.

## Quick start

```sh
./install-workflow.sh /path/to/your/project
```

Idempotent — re-run any time to reconcile. It links `AGENTS.md` (and
`CLAUDE.md` → `AGENTS.md`), wires the skills into `.agents/`, `.claude/`, and
`.codex/`, registers the context-zone hook for both tools, and scaffolds the
`docs/` tree. Flags: `-n` preview, `-f` repair links, `--with-external` pin
third-party skills per-project. Git and `jq` are prerequisites; without `jq`,
the installer leaves the Claude hook unregistered. See the
[hook dependencies](hooks/README.md#dependencies) for setup details.

Seed one unchecked step in `roadmap.md`:

```md
# Roadmap
## Phase 1 - First useful outcome
- [ ] Describe the first small result to implement.
```

Then open your coding agent and run `/next-slice` — or `/session-open` first if
you are resuming and need orientation. State files (`activeContext.md`,
`progress.md`) are created by the workflow as it runs.

## The loop

![Workflow overview](docs/assets/diag-workflow-overview.svg)

The most-used move is `/next-slice` — in practice the most reliable prompt is
literally *"find the next slice and implement it."* Take another slice while
context stays light; close the session as you approach the warn zone. The full
graph with every node's inputs, checks, and outputs is in
[workflow graph](WORKFLOW.md#11-the-workflow-graph).

Commits are user-controlled checkpoints. The skills do not commit; the branch
must be committed before its PR. See [version control](WORKFLOW.md#7-version-control)
for the checkpoint and review flow.

## The context budget

![Fuel gauge](docs/assets/diag-fuel-gauge.svg)

Long-context degradation starts well before the window is full
([Lost in the Middle](https://arxiv.org/abs/2307.03172),
[Context Rot](https://www.trychroma.com/research/context-rot)). The thresholds
are **fixed token amounts** — "12%" on a 1M-window model and "60%" on a 200k
model are the same ~120k tokens. One rule to remember: **start closing at
100k, stop coding at 120k.** An optional [Stop hook](hooks/README.md) watches
the count after every turn and nudges at the right moment — because what must
happen every time cannot depend on the model remembering.

## The skills

| Skill | Mode | Use it when |
| --- | --- | --- |
| `/grill-me` · `/grill-with-docs` | plan | Building the plan by being challenged, question by question. |
| `/planning-capture` | plan | Writing the agreed plan into durable docs and a vertically sliced roadmap. |
| `/plan-review` | plan review | Reviewing the captured plan as the other provider's strongest model. |
| `/next-slice` | implement | Picking the next small, verifiable vertical slice. |
| `/doc-update` | implement | Syncing durable docs to what actually changed (git diff, decision table). |
| `/cross-review` | review | Reviewing the diff since the last known-good commit against the docs. |
| `/review-triage` | review | Validating findings and sorting them by risk, effort, and value. |
| `/session-open` | any | Recovering orientation on an ambiguous resume. |
| `/session-close` | any | Ending a step (STEP) or session (SESSION) and synchronizing live state. |
| `/handoff` | any | Writing a standalone `handoff-*.md` packet for a tool or model that does not know this workflow. |

`grill-me`, `grill-with-docs`, and `handoff` are vendored from
[Matt Pocock's skills](https://github.com/mattpocock/skills) under MIT — see
[CREDITS.md](CREDITS.md).

## Project files

Three root files preserve live state: `activeContext.md` names now and next,
`roadmap.md` holds scheduled slices, and `progress.md` records completed work.
Durable knowledge lives under `docs/`.

See [document roles and the installed tree](WORKFLOW.md#4-the-state-files-and-the-docs-tree)
for where each kind of fact belongs, and the
[document lifecycle](docs/document-lifecycle.md) for its producers and consumers.

Installed third-party skills also expect files such as `CONTEXT.md`. Check the
[external document contracts](WORKFLOW.md#documents-this-workflow-does-not-define)
before treating an unfamiliar file as drift.

## Going deeper

| Read | For |
| --- | --- |
| [WORKFLOW.md](WORKFLOW.md) | The operating manual — every step, its inputs, outputs, and the workflow graph. |
| [WHY.md](WHY.md) | The why — nine real failure modes and the mechanism answering each. |
| [AGENTS.md](AGENTS.md) | The thin router template every project links. |
| [hooks/README.md](hooks/README.md) | Context-zone hook thresholds and setup. |

Honest limitations: the token thresholds are calibrated heuristics, not
guarantees; slice sizing still takes judgment; and the branch/PR flow is the
youngest part and will keep evolving.
