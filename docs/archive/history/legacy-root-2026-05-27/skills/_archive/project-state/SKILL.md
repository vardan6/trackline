---
name: project-state
description: Use when the user asks for current status, where work stands, what was last done, or what should happen next. Keywords: continue, resume, pick up, where were we, current state, status, progress, what's next.
---

Infer the real current state of the current project or subproject.

Keep it lightweight.

- Prefer code and recent activity over stale docs.
- Read only enough local context to answer confidently.
- Aim to identify: current state, recent work, and the next sensible step.

Common trigger phrases:

- "where are we?"
- "where were we?"
- "what's the current state?"
- "what did we finish?"
- "what's next?"
- "continue"
- "resume"
- "pick this up"
- "status"
- "progress"

Suggested lookup order, stopping early when confidence is high:

1. Current directory and nearby files
2. Existing implementation and uncommitted changes
3. Recent commits or recently touched files
4. Lightweight roadmap or TODO docs if needed

Reply concisely with the current state, what appears recently completed, and the best next step. Include confidence when uncertain.
