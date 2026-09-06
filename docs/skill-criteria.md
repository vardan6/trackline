# What Makes a Good Skill

> Design criteria for every skill in this workflow. Apply them when writing a
> new skill or reviewing an existing one. The six-section skeleton and line
> budget live in [WORKFLOW.md](../WORKFLOW.md) §8; this document is the *why*
> behind that shape. Criteria marked *(external)* are corroborated by
> Anthropic's skill-authoring guidance and field-tested skill libraries — see
> [Sources](#sources).

A skill has two audiences with opposite needs:

- **The router** sees only the `description` — in *every* session, whether the
  skill runs or not. Description tokens are rent paid always.
- **The executor** sees the body — only when the skill is invoked. Body tokens
  are paid on demand, so completeness there is cheap.

Quality is serving each audience without taxing the other.

"Cheap on demand" is not free, and how cheap depends on *when* the skill fires:
a body loaded at the close of a session is paid once, the same body loaded in
the middle is paid on every turn that follows. The Edit criteria (21–25) turn
that into the pricing rule for changing a skill.

## Description criteria (always loaded)

1. **Trigger-complete, content-free.** The description answers one question:
   *should this skill fire now?* Trigger conditions and the slash name —
   never a summary of what the body does. This is not just economy: a
   description that summarizes the procedure becomes a shortcut — the model
   follows the one-line summary instead of reading the body *(external:
   observed in practice; an agent ran one review instead of two because the
   description mentioned the review step)*.
2. **Discriminating.** It must make choosing the wrong sibling impossible:
   plan review vs code review vs triage must be separable from the
   descriptions alone.
3. **Searchable by the words the moment produces.** *(external)* Include the
   phrases a user or session would actually emit at trigger time — user
   wording, symptoms, error messages, file types — not abstractions. Written
   in third person (it lands in the system prompt; mixed point-of-view hurts
   discovery). Err slightly pushy: models under-trigger skills more often
   than they over-trigger.
4. **Named by the job, verb-first.** *(external)* The name is part of the
   trigger surface. `plan-review`, `session-close` — an action or gerund
   naming the one job. Never vague (`helper`, `utils`) and consistent in
   pattern across the collection, so siblings read as a system.

## Body criteria (loaded on invocation)

5. **Deterministic shape.** Same skeleton every time — *When to use · Do NOT
   use when · Inputs (read order) · Steps · Output · Stop conditions*. The
   reader (model or human) always knows where to look.
6. **One mode, one job.** A skill belongs to exactly one workflow mode and
   does one thing. Two jobs means an ambiguous trigger and an unpredictable
   output.
7. **Explicit negative space.** "Do NOT use when" and stop conditions matter
   as much as steps. A skill that cannot stop, or hand off to the right
   sibling, causes mode bleed. For rules the executor will be tempted to
   bend under pressure, close the loophole in the text — name the
   rationalization and refuse it; a soft "prefer X" reopens negotiation
   *(external)*.
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
13. **Self-contained body.** The body carries everything needed to execute
    correctly on its own. Repeating a rule that also lives in `AGENTS.md` is
    correct, not waste: the router is the always-loaded skeleton that carries
    the process and guards direct (non-skill) work; the skill is the complete
    procedure when invoked. Body tokens cost only on execution — never thin a
    skill by delegating its rules to the router.
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

21. **Price a body by where it loads, not by how long it is.** Context is
    resent on every turn, so the real unit is *token-turns* — tokens × the
    turns they stay resident. The same 1,000-token body costs ~2,000
    token-turns when a terminal skill loads it at the end of a session, and
    ~25,000 when something loads it in the middle. Consequences: growth in a
    closing skill (`/session-close`, `/handoff`) is nearly free and is the
    right place to spend for quality, while growth in a skill that can fire
    mid-session (`/doc-update`, `/next-slice`) is paid for every remaining
    turn. Establish where a body loads before optimizing its size.
22. **Price invocation frequency before word count.** An edit that adds a
    trigger, or moves a call earlier in the session, changes cost far more
    than the words it adds. Price the two terms separately with criterion
    21's turn counts (`end ≈ 2`, `middle ≈ 25`): the prose costs
    `tokens × turns_resident`, the relocation costs
    `body_tokens × (turns_after − turns_before)`. Worked case — ~170 tokens
    of prose that causes an ~1,100-token skill to load mid-session rather
    than at close: relocation is 1,100 × 23 ≈ 25,300 token-turns, while the
    prose is 4,250 if it rides in the relocated body and 340 if it sits in a
    closing skill — so the relocation costs ~6× to ~74× the prose, depending
    on where the prose itself lands. Do not carry a single ratio; the point
    is the ordering, not the constant. When an edit changes *when* or *how
    often* a skill fires, price that first; word count measures the wrong
    term.
23. **Every added sentence earns its tokens or leaves.** Judge each addition
    by what it changes: does the executor decide differently because of it?
    Instruction earns its place; persuasion, restatement, and background do
    not. If a passage changes no decision, cut it — and if it must exist for
    human readers, move it to a file nothing loads. `WORKFLOW.md` and the
    docs tree cost zero context; skill bodies do not. Keep only the *why*
    criterion 16 requires — the reason that lets the executor generalize —
    and put the rest where it is free.
24. **Compress as a separate pass, with the strongest model available.** Once
    the content is right, run an explicit compression pass: ask the best
    model to cut tokens, words, and characters as far as they go *without
    dropping a single decision, condition, threshold, trigger, stop
    condition, or output field*. Treat the result as a proposal — diff it
    against the original and confirm nothing load-bearing vanished.
    Authoring and compressing in one motion loses rules quietly.
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

A good skill **encodes a decision already made**, so no session re-litigates
it. If executing the skill still requires judgment calls the body does not
resolve, it is a reminder, not a skill. The lifecycle criteria are this same
rule applied to the skill itself: what it must say is decided by an observed
failure, not by taste.

## Sources

External criteria synthesized from:

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic platform docs
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Anthropic engineering blog
- [obra/superpowers · writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) — field-tested skill library (description-shortcut failure, rationalization-closing, test-first skills)
- [anthropics/claude-code · plugin-dev skill-development](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md) — Claude Code's own skill-authoring skill
