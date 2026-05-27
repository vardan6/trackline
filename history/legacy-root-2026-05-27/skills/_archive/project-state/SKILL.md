---
name: project-state
description: Infer current project state from docs, code, and recent activity.
---

Determine the real current state of the current project or subproject.

Goals:
- Maximize accuracy with minimal token usage.
- Prefer implementation reality over documentation.
- Build only enough context to determine the best next action.
- Prepare for likely follow-up: continue implementing the recommendation.

Keep inspection lightweight and local first.

Priority (stop when confidence is sufficient):

1. Current local context
- Current directory/subproject
- Nearby files
- Open/recently modified files if available

2. Implementation signals
- Existing functionality
- Partial implementations
- TODO/FIXME/HACK markers
- Current branch
- Uncommitted changes

3. Recent activity
- Recent commits
- Commit messages
- Recently touched files

4. Lightweight project context
- README / PLAN / ROADMAP / TODO only if needed
- Treat docs as lower trust than implementation

Infer:
- What was recently completed
- What is currently in progress
- What should logically happen next
- Best next implementation step

Output concisely:

## State
One short paragraph of the real current status.

## Recent
Recent completed work.

## Current
Current implementation phase. clearly mention what is done vs not done.

## Next
Single best next step.

## Continue Prompt
One short instruction for continuing immediately without re-analysis.

## Confidence
High / Medium / Low
