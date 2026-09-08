---
name: roadmap-split
description: Partition roadmap slices into independent Tracks for parallel work.
---

## Not this skill

- Picking one slice to implement → `/next-slice`; dispatching an existing partition → `/next-slice all`.

## Inputs (read order)

1. `roadmap.md` — only the section named, else the current phase. Reuse if already read.
2. Slice text and the doc *paths* each slice cites. Do not open those docs; this skill never implements.
3. `rg` — only where a slice's file set is vague (tier 1), or a Track holds a code slice (tier 1.5).
4. [DEEP-SPLIT.md](DEEP-SPLIT.md) — only when step 4 escalates.

## Steps

1. Stop if `roadmap.md` holds uncommitted changes this session did not write; report and let the user commit first. Never commit. Three Tracks unless the user asks for another count; leave sections naming another repository alone unless the user names one.
2. **Tier 0 — roadmap text only.** Build the prerequisite graph. Give every slice exactly one of **AFK**/**HITL**: propose a mark for unmarked slices and show it for approval, and stop if the text cannot support a guess — never default silently. Park **HITL** slices under "Needs you".
3. **Tier 1 — file-disjointness** from slice text and cited paths, `rg` only where the text is vague. Then **tier 1.5 — symbol overlap**, mandatory whenever a Track holds a code slice: `rg` the symbols each Track's files define and reference, and split Tracks that overlap. Tier 1.5 is not skippable — a moved signature under three running agents is a defect, not a cosmetic loss. Partition along module or feature verticals, one Track per directory or module; layer splits (API vs data layer) are maximum coupling by construction.
4. Count Tracks **after tier 1.5**, never after tier 1 alone. Short of the requested count → read `DEEP-SPLIT.md`. At the count with no empty Track → stop escalating: balance is cosmetic, and a 5/3/1 split of genuinely independent work beats paying for tier 2.
5. **No two Tracks may change one file, at any tier** — a hard blocker, not a risk to argue away. Tier 2 can only prove tier 1 read a file set wrongly, never that sharing a file is harmless. Where a file set is not cheaply determinable, write `Files: undetermined` and send that slice to "Unthreaded"; it cannot claim disjointness.
6. Rewrite the section in place, in the format below. Idempotent: recompute over an existing partition, never nest a second one. Keep no copy of the previous shape — git is the history. Then print the Output and stop.

### Track format

```markdown
## Tracks — parallel, <YYYY-MM-DD>
Prerequisite-free and file-disjoint; the three state files are excluded.

### Track A — <name>
Files: <paths, or "undetermined">
Branch: track-a/<short-name>
- [ ] <slice> … **AFK**
- [ ] **Barrier** — waiting on "<parked slice>" under Needs you; Track A stops here
- [ ] <slice that needed the parked one> … **AFK**

### Needs you — parked, not blocking
- [ ] <slice> … **HITL**

### Unthreaded
- [ ] <slice> — <why it could not join a Track>
```

A **Barrier** appears only where an **AFK** slice needs a parked one; it stops its own Track and no other, and the parked slice's text stays canonical under "Needs you" rather than being duplicated into the Track. A **HITL** slice nothing depends on parks with no barrier.

## Output

```
Tracks: <n> requested, <n> created
  Track A — <name> | <n> slices | Files: <list or "undetermined">
                     Branch: track-a/<short-name>
Needs you: <n slices, or "none">
Barriers: <Track — the parked slice it waits on, or "none">
Unthreaded: <slice — reason, or "none">
Depth used: tier 1 | tier 1.5 | tier 2 — <why it escalated>
Roadmap: written | not written — <reason>
Next: /next-slice all
```

## Stop conditions

- Uncommitted roadmap changes this skill did not write → stop before writing anything.
- A slice's **AFK**/**HITL** mark cannot be guessed from its text → stop and ask; never default.
- The requested count is unreachable — including fewer open **AFK** slices than Tracks requested → propose the single reorder or split that would free a Track; failing that, write the best valid partition and name the slices that blocked it.
- After Output, stop. This skill never implements and never starts an agent — fan-out is `/next-slice all`, a separate and explicit act.
