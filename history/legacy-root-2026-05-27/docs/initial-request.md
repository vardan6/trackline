# Initial Request

## Context

I have been doing AI-assisted coding, sometimes close to "vibe coding", while also trying to learn and improve my long-running project workflow. Over time I created an idea of having three layers of specifications:

- Requirement specifications
- Design specifications
- Internals, implementation, or reference specifications

I am now rethinking whether the third layer is actually useful.

## Current Concern

When I plan with a coding agent, I often do brainstorming, small research sessions, questioning sessions such as `grill-me`, or other planning techniques. After that, we agree on higher-level behavior, technologies, functionality, and constraints.

The stable planning result can be stored in requirements and design specifications. But I am unsure whether implementation or internals specifications should also exist.

The concern is that internals documentation can become equivalent to code. If the code is easier and more reliable for an agent to inspect, then the internals document becomes a second source of truth. Over time, code changes and older internals documentation can drift away from reality.

This creates several problems:

- Every update may require updating code, requirements, design docs, and internals docs.
- I can forget to update one of the layers.
- Updating all documentation layers costs tokens.
- The lower-level docs may become stale after many planning and implementation iterations.
- The value of internals docs is unclear if the code already contains the authoritative implementation.

## Why I Wanted Lower-Level Documentation

I mostly wanted lower-level documentation so that future sessions and future agents could quickly understand:

- how something works
- where important logic lives
- what has already been implemented
- how to continue the next task with fewer mistakes
- what the current state of the project is

However, after months of work and many planning-to-implementation round trips per day, this documentation becomes hard to maintain.

## Current Workflow

My current workflow usually looks like this:

1. I start with planning, brainstorming, research, or an externally prepared prompt/document.
2. I may run a `grill-me` session or ask the agent to plan based on existing documentation or a long prompt.
3. I ask the coding agent to document the result, but historically I did not specify whether it should be documented as requirements, design, implementation notes, or current state.
4. Sometimes another coding agent reviews the plan and writes review findings into a markdown file.
5. I ask the current coding agent to evaluate that review. Usually about 70-80% of the points are accepted and implemented, while the rest are lower priority or not worth doing immediately.
6. The final plan is often phase-based, with several phases and subphases.
7. In a later coding session, I ask what is next and then ask the agent to implement the next step.
8. When context becomes too large, I ask the agent to save enough information to continue in the next session. The old phrasing was "around 30-40%," but the better way to state it is both percent and token count: on a 200k model, 30-40% is 60k-80k; on a 400k model, 30-40% is 120k-160k; on a 1M model, 30-40% is 300k-400k.
9. In the next session, I spend tokens again discovering what is next and what the current state is.
10. After a few iterations, I ask for code review and then triage the review findings.
11. I periodically ask agents to update documentation according to current implementation, but I am not always sure what they update or where.

## Main Problems

I keep too much of the workflow in my head. I repeat the same prompts often. I do not have a precise system for:

- what should be documented
- when it should be documented
- which document layer should receive which information
- when to create a handoff
- how to start the next session efficiently
- how to avoid stale implementation documentation
- how to keep context under a reliable model-aware budget, stated as both percent and k-tokens rather than a misleading raw percentage
- how to make coding agents always know whether they are planning, implementing, reviewing, or closing a session

## Questions

The main questions are:

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

## Desired Outcome

I want a clearer personal workflow for long-running AI-assisted coding projects. The workflow should:

- preserve the useful parts of my current process
- reduce repeated prompts
- reduce token usage
- avoid stale duplicated documentation
- define when and where to document things
- define reusable skills for common workflow steps
- support clean session handoffs
- keep context small enough for reliable coding work
- make future sessions quickly understand the current state and next step
