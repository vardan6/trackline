# What Makes a Good Skill

> Design criteria for every skill in this workflow. Apply them when writing a
> new skill or reviewing an existing one. The five-section skeleton and line
> budget live in [WORKFLOW.md](../WORKFLOW.md) §8; this document is the *why*
> behind that shape. Optimize descriptions first, bodies second. External
> guidance informs these criteria; local conventions are not platform requirements.
> See [Sources](#sources) for evidence and its limits.

A skill has two audiences with opposite needs:

- **The router** sees the name and description before selection (and, in some
  hosts, the path). This metadata competes with every other advertised skill.
- **The executor** sees the body — only when the skill is invoked. Body tokens
  are paid on demand; preserve necessary instructions without treating space as free.

Quality is serving each audience without taxing the other.

The split has a consequence worth stating outright, because it is easy to
violate by habit: **content only the router can act on does not belong in the
body.** By the time the executor reads a line, the skill has already been
chosen — so a body section listing trigger phrases addresses an audience that
has left the room, and it duplicates the description word for word. What *does*
belong in the body is the inverse: the conditions under which this skill,
already invoked, should hand off to a sibling instead of proceeding.

Metadata exposure and body retention depend on the host. Explicit-only skills,
catalog truncation, caching, and compaction make "always loaded" and "paid once"
approximations, not billing rules. See criteria 21–22.

## Description criteria (before selection)

1. **Minimum sufficient routing information.** State the capability and only
   the context needed to select it: **job + distinguishing condition**, often
   in one clause. Put the distinguishing words first. A capability summary is
   useful; procedure, step order, tool commands, output paths, and rationale
   belong in the body unless they distinguish the requested service.
   This follows the [Agent Skills specification](https://agentskills.io/specification#description-field)
   and [OpenAI guidance](https://learn.chatgpt.com/docs/build-skills).
2. **Discriminating among installed siblings.** Make plan review, code review,
   and findings triage separable using their names and descriptions. Add an
   exclusion only for a plausible collision that positive wording does not
   resolve. Optimize both missed selections and unwanted selections; neither
   exhaustive trigger lists nor "pushy" wording is a default quality improvement.
3. **No redundant invocation wording.** Omit "Use this skill", "when called",
   and repetitions of `/skill-name` or `$skill-name` when the host already
   resolves explicit invocation. Keep a distinct alias only if routing actually
   depends on it. "Use when" is optional grammar, not a required prefix; keep
   the condition if it adds information. Do not infer explicit-only policy
   from a user invoking a skill manually: automatic discovery is a separate
   setting. Preserve the intended invocation policy; use the host's supported
   control when changing it is requested, rather than relying on prose alone.
4. **Concrete, compact language.** Use familiar task words and a specific
   object; include file types, symptoms, or synonyms only when they help select
   this skill. Avoid first/second-person introductions, marketing adjectives,
   keyword catalogs, and unnatural abbreviations. Keep names specific and
   consistent (`plan-review`, `session-close`); do not rename working skills
   merely to impose verb-first grammar.

### Description acceptance check

The local optimization target is **the fewest tokens that preserve routing
quality**, not a universal word count. Start with one short clause; add a
condition only when necessary. The specification's 1,024-character maximum is
a format ceiling, not a target or an optimal length. Count tokens with the
target model's tokenizer when reporting token savings; words and characters
are only proxies.

- Test the candidate with the actual sibling catalog: intended requests,
  natural paraphrases, close sibling requests, and unrelated requests sharing
  a keyword. Include explicit invocation separately from automatic selection.
- Delete each extra phrase in turn. Restore it only if its removal loses a
  required distinction or worsens observed routing. Compare against the current
  description on the same requests; keep some requests out of the editing loop
  to check generalization. Repeat ambiguous cases on the intended host/models.
- Check actual selection and body loading, not just whether the text reads
  well. A manual wording review is not a behavioral test; record untested
  routing as unverified. No description makes model errors impossible.
- Before growing a description, identify the missed or incorrect selection
  the added words address. Do not change descriptions incidentally while
  editing a body, or copy a body's new implementation details into metadata.

Illustrative compression patterns, not tested replacements for installed skills:

| Redundant wording | Compact candidate |
| --- | --- |
| Review a captured plan. Use when asked to review a plan or when `/plan-review` is invoked. | Review captured implementation plans. |
| Use this skill to triage review findings when the user provides review findings or calls `/review-triage`. | Triage review findings. |
| Use when the user wants to resume a project, continue work, or invokes `/session-open`. | Recover project state for ambiguous continuation. |

Retain qualifications such as "cross-model" when they separate real alternatives.
These examples remove repeated invocation language, not meaningful scope.

## Body criteria (loaded on invocation)

5. **Deterministic shape.** Same skeleton every time — *Not this skill ·
   Inputs (read order) · Steps · Output · Stop conditions*. The reader (model
   or human) always knows where to look. No *When to use* section: triggers
   are the description's job (criterion 1), and repeating them in the body
   pays rent for a decision already made. A skill needing one more section
   ahead of Inputs may add exactly one, named for the decision it settles
   (`session-close` has *Mode*) — a section the executor acts on, never a
   restatement of when to fire. When removing a trigger section, move only
   missing selection distinctions into the description; do not transplant the
   list. This skeleton is a local convention, not an Agent Skills requirement.
6. **One mode, one job.** A skill belongs to exactly one workflow mode and
   does one thing. Two jobs means an ambiguous trigger and an unpredictable
   output.
7. **Explicit negative space.** "Not this skill" and stop conditions matter
   as much as steps. A skill that cannot stop, or hand off to the right
   sibling, causes mode bleed. For rules the executor will be tempted to
   bend under pressure, close the loophole in the text — name the
   rationalization and refuse it; a soft "prefer X" reopens negotiation
   *(external)*. "Not this skill" is the one section that must sit **before**
   Steps: it is a bail-out for a skill invoked on a mis-read, and an executor
   that reads it only after the procedure has already run gets no benefit
   from it. Each bullet names the sibling to go to, so bailing out routes
   rather than merely refuses. Preconditions the executor can check itself
   belong here too (`/cross-review` running in the implementer's own
   provider) — they read as triggers but resolve after invocation.
8. **Bounded inputs with read order.** Name what to read, in what order, and
   when to stop reading. An unbounded "gather context" step blows the budget
   the workflow exists to protect.
9. **Contract-shaped output.** A fixed output block makes the skill
   verifiable at a glance and composable — the next skill knows what it
   receives. Keep field labels stable and machine-scannable.
10. **Freedom matched to fragility.** *(external)* Calibrate how prescriptive
    each step is. Where many paths succeed (judgment, review, synthesis),
    give direction and heuristics — over-specifying wastes lines and fights
    the model. Where exactly one path is safe (a fragile sequence, an exact
    command), give the exact text and forbid variation. One skill can mix
    both; the failure is prescribing at the wrong level.
11. **One default, not a menu.** *(external)* Where a choice exists, the
    skill states the chosen default and at most one escape hatch with its
    condition. Listing alternatives re-litigates a decision the skill exists
    to have made.
12. **Verifiable steps close their own loop.** *(external)* A step whose
    output can be checked names the check and the rule: verify → if it
    fails, fix and re-verify → proceed only on pass. "Then validate" without
    a loop is how half-done output escapes.
13. **Complete execution contract, explicit dependencies.** Keep skill-specific
    decisions in the body or bundled references. Do not copy rules guaranteed
    by the target environment merely for completeness. If standalone execution
    needs a rule otherwise supplied by `AGENTS.md`, include the minimum rule
    or make the dependency explicit; never assume an unavailable router.
14. **Assume a smart executor.** *(external)* Only include what the model
    does not already know: this workflow's decisions, orderings, contracts,
    and thresholds. Never explain what a tool is, what a common format
    means, or why testing matters — each such line is a token that displaces
    a decision.
15. **Stable vocabulary, no expiry dates.** *(external)* One term per
    concept, used identically in description and body — synonyms read as
    distinctions. No content that a calendar invalidates; when a rule
    changes, replace it rather than layering "as of…" history.
16. **Deletion test, applied internally.** Cut a body line only if removing
    it changes no future decision — merged duplicate steps, intros restating
    the description, stale references. Precision beats brevity; brevity
    beats internal redundancy. Where a rule must survive pressure, state the
    *why* in the same breath — the reason is what lets the executor
    generalize to the case the skill did not spell out *(external)*.
17. **Rare-path content externalized.** Templates and formats needed only on
    a branch (e.g. a handoff template) live in a sibling file inside the
    skill directory, loaded only when that branch is taken. The installer
    links skill directories whole, so sibling files always travel with the
    skill. Sibling files link from SKILL.md directly — one level deep, never
    chained — and a sibling long enough to be read partially opens with its
    own table of contents *(external)*.

## Lifecycle criteria (how a skill earns its place)

18. **Born from an observed failure.** *(external)* A skill exists because a
    session without it went wrong in a specific, reproducible way — not
    because a failure was imagined. The observed failure is the skill's
    test: it defines what the body must prevent and nothing more.
19. **Tested by watching, not by rereading.** *(external)* The check is a
    fresh session running the skill on a real task: does it fire when it
    should (and not when it shouldn't), read the inputs in order, produce
    the output block, stop at the stop conditions? Where the executor
    deviates is where the body is weak — fix the observed deviation, not the
    imagined one.
20. **Revised against behavior, not taste.** *(external)* Edits cite what a
    session actually did — skipped a step, missed a sibling file, re-derived
    a decided question. Style-only rewrites churn a body that was working.

## Edit criteria (what a change to a skill costs)

The body criteria say what a skill should contain. These say how to price a
change to one — applied on *every* edit to a description or body, before the
edit lands.

21. **Measure exposure, not assumed billing.** `tokens × model calls retaining
    them` estimates repeated context exposure, not money or quality. Retention,
    compaction, and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
    affect the real cost. Use measured calls when available; do not assume
    closing bodies are nearly free or impose fixed end/middle turn counts.
22. **Include selection effects in the cost.** A longer description may avoid
    loading the wrong body; a shorter but broader one may increase total work.
    Compare metadata size, invocation frequency, loaded references, and retries.
    Preserve required workflow timing; token savings alone do not justify
    delaying a necessary check.
23. **Every added sentence earns its tokens or leaves.** Judge each addition
    by what it changes: does the executor decide differently because of it?
    Instruction earns its place; persuasion, restatement, and background do
    not. If a passage changes no decision, cut it — and if it must exist for
    human readers, move it to a file nothing loads. `WORKFLOW.md` and the
    docs tree cost no context until read. Keep only the *why*
    criterion 16 requires — the reason that lets the executor generalize —
    and put the rest where it is free.
24. **Compress as a separate pass; verify on the intended model.** Once
    the content is right, cut unnecessary tokens *without
    dropping a single decision, condition, threshold, trigger, stop
    condition, or output field*. Treat the result as a proposal — diff it
    against the original and confirm nothing load-bearing vanished.
    Check affected behavior as well as the diff. A stronger editing model
    does not establish that the target executor can follow the compressed text.
25. **Delegate the branch; do not inline the sibling.** When a skill needs
    another skill's content, carry only the *test* that decides whether the
    branch is taken and invoke the sibling when it fires. Quoting the
    sibling's table or steps duplicates a canonical fact and invites drift;
    pointing at a shared file breaks installation, because the installer
    links skill directories individually and nothing outside a skill
    directory reaches the project. A cheap in-body test that usually answers
    "no" keeps the expensive body unloaded in the common case — which is the
    saving, not the shorter text.

## The meta-criterion

A good skill **preserves settled decisions and guides necessary judgment**.
State criteria where the answer depends on task evidence; do not invent rigid
rules to eliminate judgment. Optimize for correct selection and execution per
token, not brevity alone.

## Sources

Primary references for the description update:

- [Agent Skills specification](https://agentskills.io/specification) — description
  semantics and format limits; it does not establish an optimal token count.
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) — explicit
  versus implicit selection, concise boundaries, and front-loading key terms
  because hosts may shorten the advertised descriptions.
- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
  — capability plus context, concrete vocabulary, progressive disclosure, and
  evaluation on intended models. Third-person wording is Anthropic guidance,
  not a universal format constraint.
- [OpenAI: Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
  — why repeated context exposure is not equivalent to uncached billing.

The deletion check and no-redundant-invocation rule are local design conclusions
from those mechanisms, not published benchmark results. The description
examples have not been tested against this workflow's installed catalog.

Additional sources behind the existing body and lifecycle criteria:

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic platform docs
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Anthropic engineering blog
- [obra/superpowers · writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) — first-hand report of a procedural description bypassing the full workflow; evidence against procedure summaries, not proof that capability summaries are harmful or that every skill needs its testing ritual.
- [anthropics/claude-code · plugin-dev skill-development](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md) — Claude Code's own skill-authoring skill
