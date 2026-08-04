# Slide source: Human-governed agentic coding

> **Use:** source copy and speaker notes for one presentation slide.  
> **Primary visual:** [Project coverage SVG](assets/diag-my-workflow-cooperation-coverage.svg)  
> **General model:** [Human–agent cooperation spectrum](research/human-agent-cooperation-spectrum.md)  
> **Evidence:** [`my-workflow` assessment](my-workflow-human-agent-cooperation-assessment.md)

## Recommended slide

### Title

**Where `my-workflow` sits: human-governed agentic coding**

### Main statement

> Agents execute bounded coding and review loops; humans govern goals,
> boundaries, consequential decisions, and progression between loops.

### Three supporting points

- **Delegated:** repository inspection, planning support, implementation within
  a confirmed slice, testing, documentation updates, and evidence-based review.
- **Human-controlled:** planning decisions, slice confirmation, review triage,
  scope changes, commits and pushes, and movement into the next cycle.
- **Not yet covered:** autonomous scheduling, enforceable permission policy,
  shared evaluations, automatic multi-agent coordination, and deployment
  governance.

### Footer

**Current position:** agentic coding—not agentic system operation.  
**Engineering strength:** context, state, checkpoints, review, and recovery
artifacts.

## Speaker notes

The diagram is a delegation spectrum, not a maturity ladder. `my-workflow`
does not occupy one fixed point: planning is strongly human-led, while bounded
implementation and review are agentic. The workflow's distinctive choice is to
delegate execution inside small cycles and return control to the human at the
boundaries.

This makes the project more rigorous than vibe coding, because agents operate
against durable requirements, explicit slices, tests, diffs, and review
artifacts. But it is not an autonomous agent platform: people still launch the
sessions, choose the next cycle, coordinate providers, accept findings, and
authorize Git actions.

The lower band in the visual is important. Agentic engineering is not a final
stage after agentic coding; it is the discipline that makes delegation safe.
The workflow already has strong context engineering, state continuity, and
review boundaries. Its main gaps are enforceable permissions, common
evaluations, unified traces, and automated coordination.

## Optional shorter slide copy

**Headline:** Bounded autonomy, explicit human control.

**Body:** `my-workflow` delegates implementation and review to agents one
verified slice at a time. Humans retain control of plans, scope, findings,
commits, and lifecycle transitions.

**Callout:** The next frontier is not “more agents”; it is enforceable controls
and better evidence.

