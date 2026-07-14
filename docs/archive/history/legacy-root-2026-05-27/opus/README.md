# opus/ — Workflow Session Output

Outputs from the Opus session on rethinking my vibe-coding workflow.

## Files

- **`00-initial-request.md`** — my original prompts, cleaned of spelling,
  dedup'd, lightly structured. The questions I brought in.
- **`01-session-transcript.md`** — back-and-forth that produced the answers.
- **`02-final-workflow.md`** — the synthesized final workflow + open TODOs.
  Polish from here.
- **`AGENTS.md`** — drafted router file to drop into a project root.
- **`skills/cycle-close/SKILL.md`** — new skill: end-of-cycle close.
- **`skills/session-open/SKILL.md`** — new skill: cheap session bootstrap.

## Read order

If you only read one file: `02-final-workflow.md`.
If you want the reasoning: `00` → `01` → `02`.

## What was killed

- The internals / implementation / reference spec layer.
- The custom `current-state` skill (replaced by `project-state` +
  `activeContext.md`).
- The earlier proposal for a `next-step` router skill (research showed it
  duplicates Claude's native skill dispatch).
