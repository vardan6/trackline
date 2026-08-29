# Documentation Model Inquiry — ADRs, Layer Usage, and Information Flow

> **Status:** open inquiry thread — continued across sessions
> **Purpose:** preserve the questions, reasoning, evidence, and decisions behind
> Trackline's documentation model, so the thread can be resumed without
> re-deriving it. This is the *source record*; the resulting artifact is
> [document-lifecycle.md](../document-lifecycle.md), which this document links to
> rather than repeats.
> **Origin:** session of 2026-08-23, reference project `remote-rover`.
> **How to use:** each numbered thread below carries a status. Add new threads at
> the end; update statuses in place; move settled reasoning into `WORKFLOW.md` or
> `document-lifecycle.md` and leave a pointer here.

---

## 0. How this inquiry started

It did not start as a documentation question. It started with a **practical
failure** in the reference project, which is worth recording because it became
the strongest single piece of evidence in the whole thread.

Working on `feat/dock-chrome-and-widget-groups`, a Widget Group could only ever
display **one widget at a time as tabs** — you could not split widgets side by
side inside a Group, which was the entire point of the feature. Root cause: both
palettes called dockview's `addPanel` with no `position`, so every added widget
joined the active tab stack.

The relevant part: **the design doc had already diagnosed this exact defect**,
in writing, days earlier — naming the function, the missing argument, and the
consequence. It was rediscovered by reading code instead. That gap between
"documented" and "actually consulted" is what opened every question below.

---

## 1. Are ADRs an industry standard, or an artifact of LLM answers?

**Question (as asked).** The idea of ADRs came out of Opus model answers. Is this
an industry-standard programming documentation practice — decisions written down
during a specific process stage — or is it something the skills define, or
something we simply chose to adopt? What are ADRs in the world at large, in LLM
answers specifically, and in our workflow?

**Status:** ✅ settled.

**Answer.** Genuinely an industry practice, predating LLMs by roughly a decade:

| Item | Origin | Relevance |
|---|---|---|
| ADR concept + Context/Decision/Status/Consequences template | Michael Nygard, "Documenting Architecture Decisions," Nov 2011 | Trackline's template is this, near-verbatim |
| "Lightweight ADRs" → **Adopt** | ThoughtWorks Technology Radar, Nov 2016 | when it went mainstream |
| `adr-tools` CLI | Nat Pryce | source of the `0001-`, monotonic-numbering convention |
| MADR | arc42 orbit | competing, more structured template |
| Architecture rationale as a formal concept | ISO/IEC/IEEE 42010 | standards anchor |

**The LLM caveat is real but narrow.** Public repositories are saturated with
`docs/adr/0001-record-architecture-decisions.md`, so ADRs are over-represented in
training data relative to how often teams actually *sustain* the practice. Models
reach for them readily. The practice is genuine; the *reflex to propose it* is
amplified. Both things are true.

**In our workflow specifically:** nothing about ADRs comes from the skills as a
concept. The skills reference ADRs only as a routing destination — one line in
`planning-capture/SKILL.md`: *"ADR → non-obvious decision, rejected alternative,
unusual pattern."* That single line is the entire classifier. The template,
numbering, and supersession rules are defined per-project (in the reference
project, `docs/STYLE.md`).

---

## 2. Why does the ADR tier exist if the end state should be requirements + design?

**Question (as asked).** When everything is finished, having all the information
structured in requirements and design documents is what I want and what I prefer.
But during implementation, ADRs seem more convenient because they keep the scope
of what is currently being implemented. I want to make sure everything is covered
in requirements and design specs — yet a lot of important information appears to
live inside ADRs. Should it all fold into requirements and design?

**Status:** ✅ settled — the tier stays, with an explicit discriminator.

**Answer.** Requirements and design both describe states that **exist**;
an ADR is the only artifact that records states that were **rejected**. Rejected
alternatives are structurally homeless in the other two tiers — putting them in
design either bloats it with counterfactuals or loses them. So the tiers are
orthogonal, not redundant, and folding ADRs into design is lossy.

The discriminator now lives in
[document-lifecycle.md §6](../document-lifecycle.md). The two tests:

- **Forward test.** *Why is it this way and not an obvious alternative?* → ADR.
  *How does it currently work?* → design. *What must the product do?* →
  requirements. *What next?* → roadmap.
- **Inverse test, for auditing.** No reader should ever need an ADR to understand
  **how the system works** — that content belongs in design. They should need it
  only to understand **why it isn't different**.

**On the "ADRs conveniently scope current implementation" observation:** that
convenience is a **misuse signal**, not a feature. An ADR is not a scope
container; roadmap slices are. In the reference project, ADR 0033 was doing double
duty — carrying both the decision and the slice plan — and the two drifted apart
during implementation. Keep scope in `roadmap.md`; keep only the decision and
rejected alternatives in the ADR.

**Concrete evidence the tier earns its keep:** ADR 0033's rejected-alternatives
list is what has repeatedly stopped vertical tab bars being re-proposed for the
same chrome problem. No requirements or design doc would have produced that.

---

## 3. Do we actually use all the documentation layers during development?

**Question (as asked).** Walk the real pipeline: prompts, then possibly existing
docs, then a grilling session, then `/planning-capture` producing requirements,
design, ADRs, roadmap and activeContext. Then implementation happens in separate
sessions. Does the coding agent really use the existing requirement and design
specs? Or does it use an ADR only when it happens to be referenced? Or does it
just discover everything from the code unless the roadmap explicitly says to read
some documentation? Do we genuinely use all the layers, or do we only keep the
status files current and never actually consume the rest during development?

**Status:** ✅ settled — with a correction recorded in thread 4.

**Answer.** The layers are **written fully and read partially**. During the
implementation step specifically, the working set is
`roadmap.md` + `activeContext.md` + **code**. Design is read occasionally;
requirements and ADRs are close to cold.

Why, mechanically:

- Every skill's read-order list has an escape hatch. `next-slice/SKILL.md:19`:
  *"Inputs (read order, **stop when confident**)"* — with requirements/design/ADR
  at position **3**, after state files and git. Confidence almost always arrives
  at step 1–2, because roadmap lines are written to be self-sufficient.
- `session-open/SKILL.md:29` explicitly **forbids** reading the deep layers.
- `AGENTS.md` gates them on subjective triggers (*"code looks surprising"*).
- Reading code is always cheaper and always available: it is precise, current, and
  needs no navigation guess. The cheap path wins every time it is permitted, and
  it is always permitted.

**The layers do reach implementation — but by a different route than designed.**
`roadmap.md` carries 14 doc citations and `activeContext.md` 7, in the reference
project. Design content arrives as **summaries pre-copied into the roadmap during
planning**, not by the agent opening the design doc.

**Which exposes the real defect.** The fact that diagnosed the Widget Group bug
was recorded in **two** places — `roadmap.md` and the design doc — and they had
drifted (design posed an open question; implementation shipped a third option
neither had described). This duplication is structural: the roadmap must
duplicate design *because* nobody opens design during implementation.

---

## 4. If we almost never use the documents, why write them?

**Question (as asked).** So if we almost never use any type of document, why did
we decide to write them?

**Status:** ✅ settled — and it corrected an over-claim from thread 3.

**Answer.** The premise is wrong in two places, and the correction matters.

**First:** `roadmap.md` and `activeContext.md` *are* documents, and they are read
every single session. The narrow true claim is that the **deep layers are cold
during the implementation step specifically** — one consumer out of five.

**Second:** thread 3 under-counted the consumers. The deep layers feed:

| Consumer | Evidence | Reads |
|---|---|---|
| `/plan-review` | `SKILL.md:23` — input **#1** is requirements/design/adr | deep layers, directly |
| `/cross-review` | `SKILL.md:31` — validates code against docs **bidirectionally** | deep layers, directly |
| **RAG retrieval** | `rag_service/ingest.py --docs-dir`, `search_project_docs` | `docs/` **is the corpus** |
| `/doc-update`, `/planning-capture` | read before writing, to avoid contradiction | deep layers |
| `/next-slice` | "stop when confident" | rarely |

So `docs/` is not write-only — it is the input to the entire **review and
retrieval half** of the system. Implementation is precisely the one stage that
*should not* need it, because there code is truth.

**Every layer earned its keep in the single session that raised the question:**

- **requirements** — one sentence ("a Group holds several widgets visible at
  once") is what established that the **code was wrong and the doc was right**,
  rather than treating tab-stacking as intended. Without it the bug report was
  ambiguous.
- **design** — had already diagnosed the exact defect.
- **ADR 0033** — its rejected list is why vertical tabs stay rejected.
- **roadmap** — carried the fact into the first tool call of the session.

**The real answer to "why write them":** because neither the human nor the agent
has cross-session memory. Docs are consumed **upstream of implementation**, and
implementation reads the compressed output. That is the pipeline working, not
failing. The thing worth fixing is that the compression step is **lossy and
manual**, not the decision to write the source.

**Genuine waste identified** (~5% of the corpus, all mechanical drift):

1. roadmap items summarizing design prose → two homes, observed drift;
2. empty decoy directories teaching agents the deep layers are empty;
3. orphaned ADRs with zero inbound links.

---

## 5. Map the whole documentation flow

**Question (as asked).** I want one large picture: a graph or map of the
documentation structure across the development timeline, left to right. It should
show the development stages — research, planning, implementation, review — and for
each, what it takes as input and what it outputs; what turns into what; which
documents each stage consumes. If a node is a leaf, that tells us nothing consumes
it anymore. Suggest anything else worth including. A larger picture is fine;
missing nodes or missing connections are the real problem.

**Status:** ✅ delivered → [document-lifecycle.md](../document-lifecycle.md),
linked from `WORKFLOW.md §4`.

**Framing that made it work.** `WORKFLOW.md §1.1` already graphs the workflow,
but **skill-centric**: nodes are actions, artifacts are edge labels. The new
document **inverts** it — documents are nodes, skills are the transforming edges.
The two are complements, not rivals.

**Sections delivered:** six-stage timeline · information-flow graph ·
per-document contracts (producer / consumers / cardinality / lifetime /
mutability) · terminal-node analysis · compression ladder · ADR discriminator ·
two tree shapes · cross-cutting axes · health checks.

**Additions volunteered beyond the request:**

- **Mutability axis** — frozen / living / append-only / ephemeral. Editing a
  frozen doc is always a mistake; supersede instead.
- **Retrieval-path ranking** — the five ways a fact reaches an agent, by
  reliability. Roadmap citation is the weak link; RAG is the only path that
  reaches an otherwise-terminal doc.
- **Compression ladder** — what each stage discards. Key result:
  **conversation → captured docs is the highest-loss step in the pipeline.**
  Everything `/planning-capture` fails to classify dies with the session — which
  is the load-bearing justification for the planning-capture gate in
  `/session-close (SESSION)`.
- **Health checks** — six mechanical greps, each mapped to a defect.

**Structural result worth remembering:** knowledge flows **left to right and never
back — except through review**, the only mechanism that corrects an upstream
artifact from downstream evidence. That is why both review stages exist, and why
skipping one lets an error propagate to the end of the pipeline unchallenged.

---

## 6. Evidence appendix

Measured in the reference project on 2026-08-23. Recorded so future sessions do
not re-derive them; re-measure before relying on any of it.

**Empty decoy directories — four.** `docs/requirements/`, `docs/design/`,
`docs/adr/`, `docs/research/` all exist and are **completely empty**, created
Jul 4. Real content lives at `docs/components/<name>/{requirements,design}.md`,
`docs/cross-cutting/decisions/`, and `docs/cross-cutting/research/` (17 files).
The skills, `AGENTS.md`, and `install-workflow.sh` all name the *flat* paths.

*Diagnostic value:* a layer that is genuinely consumed **cannot** have an empty
decoy at its documented address for seven weeks unnoticed. This is the single
hardest piece of evidence in the whole inquiry.

**State file sizes.**

| File | Size | Note |
|---|---:|---|
| `activeContext.md` | 7.8 KB | target: tiny |
| `roadmap.md` | 11.1 KB | checklist-first |
| `progress.md` | **101.7 KB** | 13× activeContext; append-only; effectively never read |
| `docs/future-plans.md` | 36.8 KB | |
| `docs/glossary.md` | 15.6 KB | |

`progress.md` is terminal **and** unbounded — suggested rotation into
`docs/archive/` past ~50 KB.

**ADR set.** 29 active records, `0001`–`0033`, with intentional gaps (supersession
deletes rather than tombstones — numbering monotonic, never reused). **Two
orphans** with zero inbound links from any live doc: `0026` (replay logging /
scrubbing ships, full replay deferred) and `0027` (soft-constraint route scoring).
Every other ADR has at least one inbound link.

**Doc citations in state files.** `roadmap.md`: 14. `activeContext.md`: 7.

**Skill installation.** 8 of 11 skills are symlinked into the reference project;
`grill-me`, `grill-with-docs`, and `handoff` stay in user scope by design
(`WORKFLOW.md §8`), which is why `AGENTS.md` references `/handoff` with no local
skill directory. Not a defect — worth not re-investigating.

**Template drift.** `STYLE.md` specifies `# <number>. <Title>` with
`## Alternatives Considered`. The newest ADR (0033) uses `# ADR 0033 — <Title>`
with `## Rationale` + `## Alternatives rejected`. Cosmetic, but it indicates the
template is not read at authoring time.

---

## 7. Open threads

Numbered for resumption. None are started.

| # | Item | Scope | Rationale |
|---|---|---|---|
| O1 | Remove the four empty decoy directories; empty `DOCS_DIRS` for component-scoped projects | installer + reference project | The only defect that can cause a *wrong action* — an agent creating `docs/adr/` and writing there |
| O2 | Override doc paths in the reference project's `AGENTS.md` §Docs block | reference project | Router currently points at emptiness |
| O3 | Make `/next-slice` **open the doc sections its slice cites** | `next-slice/SKILL.md` | Converts "load when you judge it needed" (skipped in practice) into "load what the slice names" (deterministic). The highest-leverage change in the list |
| O4 | Stop copying design prose into roadmap items; cite sections instead | convention + `planning-capture` | Only safe once O3 lands |
| O5 | Fold the ADR discriminator into `planning-capture/SKILL.md` | skill | Needs compressing to ~6 table rows — skills have a 60-line hard cap |
| O6 | Close the two orphan ADRs by linking them from the design sections they govern | reference project | Restores reachability of their rejected-alternatives lists |
| O7 | Rotate `progress.md` into `docs/archive/` past ~50 KB | convention | Terminal + unbounded |
| O8 | Reconcile ADR template drift, or update `STYLE.md` to match practice | reference project | Decide which is canonical rather than letting both run |
| O9 | Render and validate the mermaid graph in `document-lifecycle.md` | workflow | Written to spec, not yet executed |

**Sequencing note:** O3 is the one that changes agent behavior; O1/O2 are
prerequisites for it being meaningful (no point opening cited paths while the
router points at empty directories). O4 depends on O3. The rest are independent.

---

## 8. Standing conclusions

Short claims this inquiry established, worth not re-arguing:

1. ADRs are a real practice, over-represented in LLM output, and correctly adopted
   here. The tier is **not** redundant with design.
2. The end state of "everything in requirements and design" is achievable for the
   *what* and *how*, but **not** for the *why-not-otherwise*. That last part needs
   the ADR tier permanently.
3. Documentation is not write-only; it feeds review and RAG. Implementation is the
   one stage that legitimately runs on code + state files.
4. The weak link is the **design → implementation** path, which today depends on a
   manual summarization step performed during planning.
5. Fix the retrieval path before writing more documentation. Volume is not the
   problem; reachability is.
