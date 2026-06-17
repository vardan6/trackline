## Planning and Initial Research

For planning, I often start with a voice chat, for example with ChatGPT. I ask questions about the essential parts of the project, such as:

* What proof of concept is possible?
* What already exists, and what does not?
* Which technologies, programming languages, libraries, and protocols are most suitable?
* What technical options are available?
* What numbers, limits, or benchmarks should be checked first?

A common approach is to start with a large initial prompt, explore the topic through questions, and continue clarifying until the project details become clear enough for implementation planning. A structured questioning approach, such as using the grill-me skill, can be useful because it helps challenge assumptions, identify missing requirements, and uncover technical details that might otherwise be overlooked before implementation begins.

Any subsequent smaller planning tasks can also start with a grill-me session when the planning prompt is prepared or provided through the grill-me skill. A grill-me session is a major factor in keeping the developer actively involved in both design and implementation details, because it is possible to spend hours answering dozens or sometimes around a hundred structured questions that are then documented as ADRs or other project documentation. When needed, lower-level technical questions can be delegated to an AI agent, which typically suggests an answer based on best practices, while the developer remains focused on the higher-level decisions.

## Context Engineering

For context engineering, I usually keep all project documentation inside the project directory. The project directory is also the repository, and version control is typically managed with GitHub or another Git-based system.

Version control is technically optional, for small projects, but mandatory for long projects. Coding agents work much better when the project has clear version history, clean commits, and a structured repository.

Based on my experience, project files such as `AGENTS.md` or `CLAUDE.md` are useful but not always necessary. They can provide persistent instructions and reduce repeated prompting, but I have often found that smaller—or even absent—instruction files work better for focused tasks. In several projects, keeping these files minimal helped the coding agent retrieve context more efficiently, use fewer tokens, and stay within a more effective active context. This has been especially noticeable during bug fixes and other well-defined tasks, where extra persistent instructions can add more overhead than value.

What matters is whether a file has a specific reason to be there. If it does, it is worth keeping; if not, I would lean toward not having it, since I am not sure whether it actually helps or just adds overhead and token usage. For this workflow specifically, those files are needed for the guidance to work properly—the workflow relies on them to declare mode, name the next step, and keep durable state out of the live transcript—so I do not see a conflict here.

When giving instructions, I try to use exact names such as page names, widget names, paths (XPaths), file names, function names, or other unique technical terms. This helps the coding agent find the correct context and avoid mixing unrelated parts of the project.

## Context Management and the Active Context Window

For AI coding agents, the biggest bottleneck is the active context window. Modern LLMs may support very large context windows, sometimes even millions of tokens, but the effective “smart zone” is usually much smaller.

In practice the reliable “smart zone” is comfortably under ~50K tokens for most models, though many keep working well up to ~75–100K. The less reliable “dumb zone” — where quality is clearly worse — sits above ~100–150K. These are two different thresholds, not one line: between them is a model-dependent transition band tens of thousands of tokens wide, not a single switch. How that transition behaves also varies — across many models and tasks it is a gradual decline that begins well before the window is full, but for a given model on a given task it can be abrupt, holding up and then falling off sharply once it passes that model’s effective context length. Smaller or weaker models tend to degrade earlier. In the dumb zone, problems become more likely, such as:

* **Common large-context problems**

  * Missing or overlooking information that is already available
  * Losing focus on the original goal or implementation plan
  * Confusing similar files, functions, or requirements
  * Hallucinating details or making incorrect assumptions
  * Spending too much time searching or reasoning instead of progressing
  * Making unnecessary changes to unrelated code or documentation

---

### Addendum: Large Context Window Effects

* **Information retrieval and attention problems**

  * Context dilution
  * Lost-in-the-middle effect
  * Attention decay
  * Retrieval failures

* **Instruction and planning degradation**

  * Reduced instruction fidelity
  * Plan drift
  * Higher susceptibility to distraction by low-priority details

* **Reasoning and accuracy issues**

  * Confusing semantically similar entities
  * Hallucinating implementation details
  * Context contamination
  * Accumulation of small errors across long reasoning chains

* **Efficiency and implementation risks**

  * Increased reasoning latency
  * Unnecessary modifications
  * Greater computational cost and token consumption

The purpose of this workflow is to keep the coding agent inside the smart zone. The goal is not only to reduce token usage, but also to get cleaner, more precise, and more reliable behavior.

In my experience, when the active context became too large, the agent could spend 20–30 minutes without solving the problem, consume a large part of the usage limit, and sometimes even break the project.

After I started keeping the active context smaller and slicing tasks better, I rarely noticed this strange behavior. The agent became more precise, more reliable, and usually stopped after completing a clean, well-defined task.

## Documentation Purpose and Priority

For documentation, I see two main purposes.

The first purpose is to provide the coding agent with a clear implementation reference. Documentation acts as the final communication contract between planning and implementation. It defines what was agreed, what should be implemented, and how the implementation should match the project design.

The second purpose is human understanding and presentation. This is still important, but I now consider it the second priority.

Previously, I was thinking about whether documentation should mainly help me present the project or help the coding agent implement correctly. I realized that most people will not read very detailed documentation, especially if there is too much of it. Coding agents can generate human-readable summaries on demand if the correct source of truth exists.

Therefore, the priority should be to maintain useful source-of-truth documentation. This source of truth may exist in the code, requirements, design documents, or other selected documentation layers. The documentation does not need to describe every detail, but it must contain the important decisions and implementation contracts needed for accurate coding-agent work.

## Repeating Prompts and the Need for Skills

Another problem was repeating the same prompts again and again.

After each implementation step, especially when the active context reached around 40% (roughly 80K tokens in the 200K-era baseline) or more, I often asked the coding agent to update documentation. Usually, I tried to explain things like:

* Update the relevant documentation.
* Document what you think is important.
* Check against existing documentation.
* Update whatever is necessary.
* Keep the documentation accurate and consistent.
* Be concise, but do not skip important details.

The problem was that I did not have a clear reusable prompt for this. Sometimes I saved temporary prompts in project files, but this was not a structured workflow.

The same issue happened during handoff between sessions. I would ask the agent to write the necessary current-session information for the next session, so the next agent could continue from the correct state. Again, I had to repeat instructions like:

* Write a concise but complete handoff.
* Include what was done.
* Include what is next.
* Include important files, decisions, and risks.
* Do not skip necessary details.

Similar repeating prompts were also needed for code review, documentation updates after research, planning the next implementation slice, and asking the agent to understand the project before continuing.

This showed a clear need for reusable skills and workflow-stage definitions. Skills help avoid repeating the same long prompts and make the workflow more consistent.

## Code Review Workflow

For code review, I sometimes switch to a larger or stronger model, especially when I still have a significant amount of usage left before the usage window resets. For example, if I have more than 20% usage left and only 10–20 minutes before the limit resets, I may use that remaining capacity for a review.

The review process can work like this:

1. Ask a stronger model or another coding agent to review the recent implementation.
2. Ask it to write the findings into a Markdown review document.
3. Give that review document back to the original coding agent.
4. Ask the original agent to evaluate whether the review findings are valid and worth implementing.
5. Implement the confirmed review items.

In my experience, around 70–80% of the review findings are usually useful. Some are high or critical priority, some are medium priority, and a few may be lower quality or unnecessary.

Often, two different coding agents agree on most of the important points. This cross-review process helps catch missed issues, bugs, mismatches with documentation, and possible improvements.

## Version Control and Coding Agents

Version control is very important when working with coding agents.

Coding agents often rely on the version control state. For example, when you ask for a review, the agent may only compare the current uncommitted changes against the last commit. It may not review the entire project unless you explicitly ask for that.

This can be easy to miss. You may think the agent reviewed the full project, while in reality it only reviewed the latest diff.

A good Git workflow makes cooperation with coding agents much easier:

* Commit only working code.
* Create clear checkpoints after each meaningful implementation step.
* Use code reviews before or after commits.
* Keep commit messages meaningful.
* Use commit history as a reference for future debugging and investigation.
* Roll back safely when something goes wrong.
* Cross-check changes against previous known-good states.

Good commit points and clear commit messages are especially useful because coding agents can inspect commit history and use it as an additional source of context.
