# Where `my-workflow` Sits on the Human–Agent Cooperation Spectrum

> **Assessment date:** 2026-08-04  
> **Scope:** the complete current repository, with archived versions used only
> as historical context.  
> **Model:** [The Human–Agent Cooperation Spectrum](research/human-agent-cooperation-spectrum.md)

![Coverage of the human–agent cooperation spectrum by my-workflow](assets/diag-my-workflow-cooperation-coverage.svg)

## Verdict

`my-workflow` is a **human-governed agentic coding workflow**.

It sits firmly in **agentic coding** for bounded implementation and review
tasks: an agent can inspect a repository, choose actions inside a confirmed
slice, edit files, run tools and tests, diagnose failures, and iterate toward a
result. The workflow deliberately moves back toward the human at consequential
boundaries: planning is interrogative, implementation slices require
confirmation, review findings require triage, commits are never automatic, and
the next cycle is explicitly selected.

It does **not** yet reach agentic system operation. There is no persistent
orchestrator that schedules work, launches and coordinates agents, enforces
policy, evaluates outcomes, or resumes workflows automatically. Cross-provider
review and handoff are procedural patterns executed by a human and cooperating
agents, not an automated multi-agent runtime.

The most accurate one-line position is:

> **Agentic execution inside human-controlled cycles, supported by an emerging
> agentic-engineering discipline.**

## How this assessment was made

The spectrum should not be applied as a single maturity score. Each workflow
phase was evaluated using six dimensions from the research model: scope,
duration, decision authority, tool authority, human checkpoints, and
coordination.

Evidence was weighted in this order:

1. executable behavior in `install-workflow.sh` and `hooks/context-zone.sh`;
2. active skill contracts under `skills/`;
3. routing rules in `AGENTS.md`;
4. current behavior documented in `README.md`, `WORKFLOW.md`, and
   `docs/PROBLEMS-AND-SOLUTIONS.md`;
5. archived drafts and transcripts, used only to understand evolution.

The audit covered every tracked file. Repeated historical copies and SVG assets
were checked for their role and references rather than treated as independent
current requirements. The new research note was also included. Shell syntax,
hook registration JSON, local diagram references, installer output, and
installer idempotence were checked. This is an architecture and workflow
assessment, not a longitudinal usability study; experiential performance claims
in the project docs were not independently reproduced.

## Coverage by workflow phase

| Phase | Spectrum position | What the agent can do | Human control point | Evidence |
| --- | --- | --- | --- | --- |
| **Research** | AI-assisted coding | Explore and distill material into a research summary | Human chooses inputs and decides when research is ready | `WORKFLOW.md` §3.1 |
| **Planning** | AI-assisted → bounded agentic | Interrogate assumptions, inspect the codebase, classify decisions, and produce durable plan artifacts | Human answers the design questions and must be able to defend the plan | `grill-me`, `grill-with-docs`, `planning-capture` |
| **Plan review** | Agentic coding | Cross-check requirements, design, ADRs, roadmap, and relevant code; write findings | A different-provider session is started manually; the original planner triages every finding | `plan-review`, `review-triage` |
| **Implementation** | Agentic coding | Select a candidate slice, then edit, run tools, test, diagnose, and iterate | `/next-slice` must print the slice and wait for confirmation; one slice per cycle | `next-slice`, `AGENTS.md` |
| **Documentation** | Bounded agentic | Inspect the diff and update only durable knowledge affected by it | Conflicts with standing decisions are surfaced instead of silently resolved | `doc-update`, `planning-capture` |
| **Code review** | Agentic coding | Review a defined diff against code and docs; produce evidence-backed findings | Range ambiguity stops the review; fixes happen only after human-mediated triage | `cross-review`, `review-triage` |
| **Session continuity** | Bounded agentic | Reconstruct orientation and write compact project state at close | Session transitions remain explicit; close does not start the next slice | `session-open`, `session-close` |
| **Git/PR/deployment** | Direct or AI-assisted | Inspect history and suggest commit boundaries/messages | The user must request commits and pushes; PR and deployment execution are outside the implemented workflow | `WORKFLOW.md` §7, `session-close` |
| **Multi-agent operation** | Designed/experimental, not implemented | Documentation proposes cross-model review and up to three parallel slice threads | The human launches sessions and transfers artifacts | `WORKFLOW.md` §§3.3–3.4; parallelism is marked experimental |

## Coverage by delegation dimension

| Dimension | Current coverage | Assessment |
| --- | --- | --- |
| **Scope** | One atomic vertical slice, plan review, code review, or documentation pass | **Strong for bounded tasks.** The workflow intentionally prevents an agent from silently expanding into a full phase. |
| **Duration** | Several slices may share a session; durable state bridges sessions | **Moderate.** Resumable across sessions, but no unattended long-running execution or scheduler. |
| **Decision authority** | Agent chooses intermediate implementation actions after slice confirmation | **Moderate–high within a slice; low at boundaries.** This is the defining human-governed shape. |
| **Tool authority** | Inherited from the host coding agent; the workflow itself does not grant or restrict tools | **Externalized.** Advice exists to audit MCP servers and use a permission allowlist, but enforcement is not part of this repository. |
| **Human checkpoints** | Planning questions, slice confirmation, review triage, session close, explicit commits | **Strong and frequent.** Checkpoints are contractual in skills, though mostly instruction-enforced rather than runtime-enforced. |
| **Coordination** | Artifact-based cross-provider review and handoff | **Procedural, not orchestrated.** No agent registry, task scheduler, dependency runtime, or automatic fan-out/fan-in. |

## What the project already covers well

### 1. Goal and scope containment

`/next-slice` requires a small, dependency-free, independently verifiable slice,
prints its proposed scope, and waits for confirmation. It also forbids automatic
chaining into another slice. This is a strong boundary against accidental
task-level scope expansion.

### 2. Human understanding and intervention

The workflow treats planning as the most human-in-the-loop phase. Grilling,
plan review, and explicit triage keep important design decisions visible. The
human does not merely approve a final patch; they participate at different
levels of abstraction throughout the lifecycle.

### 3. Durable context and resumability

The separation of `activeContext.md`, `roadmap.md`, and `progress.md` from
requirements, design, ADRs, and code provides a coherent state model for fresh
sessions. `/session-open` reads narrowly; `/session-close` is the sole intended
writer of live state. This supports agentic work across sessions without
requiring the next agent to replay the transcript.

### 4. Evidence-producing review

Plan and code reviews produce files with defined tables, evidence, severity,
risk, value, and effort. The reviewing model cannot modify the subject of its
review, and the original agent validates findings against code before changes.
That separation is a meaningful review control, not merely a second prompt.

### 5. Context-budget controls

The context-zone Stop hook is the repository's only automatic runtime guard. It
prefers live or transcript token telemetry, falls back to an estimate, and emits
increasingly strong guidance at fixed thresholds. The hook is advisory—it
cannot block a tool call—but it operationalizes a failure boundary that would
otherwise depend entirely on memory.

### 6. Reproducible installation

The installer wires the router, canonical skills, tool-specific skill funnels,
the shared hook, and the documentation tree. A clean installation and a second
idempotence pass both completed successfully during this assessment. Existing
real files are preserved, differing symlinks require `--force`, and existing
Claude Stop hooks are merged rather than replaced.

### 7. Recovery and provenance

Git is treated as agent-readable evidence; review ranges begin from a known-good
commit, and automatic commits are prohibited. Session close records blockers,
open questions, and dead ends. `/handoff` supplies a separate path for
cross-tool transfer when native state is insufficient.

## Coverage that is partial or “soft solved”

### Instruction compliance

Most controls are written contracts in `AGENTS.md` and `SKILL.md`. They are
clear, but the runtime does not guarantee that a model reads the right skill,
waits for confirmation, updates state correctly, or stops after one slice. The
project itself acknowledges this distinction: hooks run automatically; skills
remain instructions.

### Permission boundaries

`WORKFLOW.md` recommends a permission allowlist and an MCP audit, but the
installer does not create a policy, capability profile, or per-action approval
gate. Effective authority depends on the host agent and project configuration.

### Verification quality

Slices must name a verification method, reviews require evidence, and skills
contain stop conditions. However, there is no shared evaluation harness that
tests whether the result satisfies acceptance criteria across agents and
projects. Verification remains project-specific and model-executed.

### Observability and audit

Diffs, commits, Markdown findings, state files, and host transcripts provide a
useful trail. They are distributed artifacts rather than a unified execution
trace. There is no structured record of every delegated goal, tool call,
approval, outcome, or policy decision.

### Recovery

The workflow supports session recovery and clean Git checkpoints, but does not
define transactional rollback, compensation for external side effects, retry
budgets, or automatic escalation after repeated failure.

### Parallel work

Independent parallel slice threads appear in the planning guidance as an
experiment. There is no implemented mechanism to prove file independence,
spawn workers, merge their results, resolve conflicts, or aggregate evidence.

## Areas not covered

- autonomous scheduling or unattended continuation;
- automatic multi-agent orchestration and work allocation;
- enforceable least-privilege permissions supplied by this project;
- deployment, production operations, or external-action governance;
- centralized traces, cost accounting, and outcome metrics;
- repeatable agent-behavior evaluations or regression tests for skills;
- machine-enforced approval gates for high-impact actions;
- automatic rollback or compensation after partial failure;
- organizational roles, compliance policy, or responsibility assignment.

These are not all defects. Several are sensible non-goals for a personal coding
workflow. They define the boundary between the project's current focus and a
full agent operating platform.

## The agentic-engineering layer

The project covers the discipline around delegated coding unevenly but
substantially:

| Engineering control | Coverage | Mechanism |
| --- | --- | --- |
| Goal and acceptance framing | **Strong** | grilling, requirements, vertical slices, verification field |
| Context and knowledge | **Strong** | state triad, docs routing, one source of truth, context budget |
| Checkpoints and approvals | **Strong but mostly advisory** | slice confirmation, triage, explicit commits, stop conditions |
| Evaluation | **Partial** | project tests/checks and cross-model review; no common eval harness |
| Observability | **Partial** | diffs, Git, findings, state files, transcripts |
| Permissions and policy | **Weak/external** | host configuration recommendations only |
| Recovery | **Moderate for coding state** | Git checkpoints, session close/open, handoff |
| Multi-agent coordination | **Early/experimental** | manual cross-provider loop; parallel-thread planning note |

## What would move it further right

Moving right is not automatically desirable. If the goal is greater safe
delegation, the next useful steps would be:

1. **Create an evaluation contract for every slice.** Store machine-checkable
   success criteria and require a result artifact before a slice can close.
2. **Make approvals enforceable.** Map action classes—read, local write, command,
   commit, push, deploy, external communication—to host-level permission gates.
3. **Add structured execution records.** Capture goal, scope, agent, tool
   authority, checks, approvals, result, and failure state in a compact format.
4. **Test the skills behaviorally.** Run repeatable scenario fixtures that
   detect failure to trigger, over-reading, skipped confirmation, mode bleed,
   or malformed outputs.
5. **Prototype one orchestrated parallel wave.** Start with two proven
   conflict-free slices and explicit fan-out/fan-in checks before generalizing.
6. **Define failure policy.** Set retry limits, escalation conditions, rollback
   behavior, and the point at which an agent must stop rather than improvise.

The first four improve trustworthiness without requiring more autonomy. Only
the fifth materially moves the project toward agentic system operation.

## Recommended positioning language

For the README or a presentation:

> `my-workflow` is a human-governed agentic coding workflow for long-running
> projects. It delegates bounded implementation and review loops to coding
> agents while keeping planning, scope changes, findings triage, commits, and
> session progression under explicit human control.

Avoid describing it as a multi-agent orchestration platform or autonomous
software factory. The repository coordinates agents through people and durable
artifacts; it does not operate them autonomously.

## Evidence index

- [`AGENTS.md`](../AGENTS.md): routing, one-slice rule, context thresholds, and
  documentation authority.
- [`README.md`](../README.md): project goals, operating principles, skill map,
  and stated limitations.
- [`WORKFLOW.md`](../WORKFLOW.md): phase contracts, state model, Git policy,
  experimental parallelism, and environment recommendations.
- [`docs/PROBLEMS-AND-SOLUTIONS.md`](PROBLEMS-AND-SOLUTIONS.md): problem model,
  intended safeguards, and explicit “soft solved” limitations.
- [`skills/`](../skills): executable instruction contracts and their stop
  conditions.
- [`install-workflow.sh`](../install-workflow.sh): actual installation and
  reconciliation behavior.
- [`hooks/context-zone.sh`](../hooks/context-zone.sh) and
  [`hooks/README.md`](../hooks/README.md): the automatic context guard and its
  advisory boundary.
- [`docs/archive/`](archive): historical evolution; not current authority.

