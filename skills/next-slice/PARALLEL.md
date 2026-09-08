# PARALLEL — fan-out dispatch

Loaded by [SKILL.md](SKILL.md) step 2 when the invocation carries `all` or `parallel`, and never otherwise. Replaces steps 3–6 of that skill for this invocation.

Read the `## Tracks — parallel` section of `roadmap.md`. If the roadmap has no such section, stop and say so: `/roadmap-split` produces it, and this skill never partitions.

## Print always, start only when told

Print the Plan block below on **every** invocation. Start agents only when the invocation asks for implementation in so many words — "and implement", "run them", "go". `/next-slice all` on its own prints and stops. There is no inferred authorization: a user who wanted work started says so, and the cost of guessing wrong is three agents writing code unattended.

```
Fan-out plan — <n> Tracks
  Track A — <name> | <n> runnable slices | Branch: track-a/<short-name>
                     Worktree: <path> | Files: <list>
  Track B — ...
Needs you: <n parked slices — the decisions these Tracks are not waiting for>
Barriers: <Track — the parked slice it stops at, or "none">
Roadmap commit: <sha — the revision workers branch from> | UNCOMMITTED — stop
Starting: <n agents, or "nothing — no implement instruction">
```

The `Needs you` line is not optional. A parked decision that sits unseen for weeks is the failure the parked list exists to prevent.

## Launch context — one per Track

Branch names alone do not isolate concurrent agents; two agents in one checkout share a working tree and overwrite each other. So, per Track, in this order:

1. **The partition must be committed first.** Workers branch from a revision, and a fresh worktree at HEAD silently omits an uncommitted roadmap — the workers would each partition-blind pick from the old roadmap. If `roadmap.md` is dirty, stop and ask the user to commit. Never commit on their behalf; this rule is not negotiable and has no fast path.
2. **Working directory:** one git worktree per Track, created by this dispatcher — `git worktree add <path> -b track-<letter>/<short-name>` from the commit above. Never two Tracks in one directory.
3. **Starting revision:** the commit holding the partition. Identical for every Track; Tracks are prerequisite-free by construction, so no worker waits on another's output and nothing else needs transferring.
4. **Ownership passed to the worker:** by the branch name. The worker's launch instruction names its Track letter and its worktree path, and `/session-open` recovers the same letter from the `track-<letter>/` branch prefix if the worker restarts cold. Nothing else tells a worker which slices are its own.
5. **Standing rules travel with the worker:** never commit automatically, never touch another Track's files, and `/session-close` still ends its session.

## Sequential execution inside a Track

`/next-slice` and `/session-close` each stop after one cycle by design, so neither can run a Track to its end. **This file owns the repetition**, and only under the implement instruction that started the fan-out:

- Repeat one-slice cycles: pick the next unchecked slice **in this Track's order** → open every doc it cites, plus ADRs those link, one hop → implement → verify → tick the slice.
- The fan-out implement instruction is the standing confirmation for slices inside this Track, and for nothing else. It does not authorize a slice from another Track, from `Needs you`, or from anywhere but the roadmap.
- The citation contract is unchanged and unweakened by running unattended. A cited link that resolves to nothing, or a behavior-changing slice claiming no doc governs it, stops the Track — it does not get waved through because no one is watching.

Stop the Track and report at the first of:

- a **Barrier** line, or a **HITL** slice reached in sequence — the remaining slices stay in place, unticked;
- the Track's slices are exhausted;
- a verification fails, or confidence in a slice is low;
- the context thresholds in `WORKFLOW.md` §6 are reached.

Then run `/session-close` for that worker. Do not re-partition, do not adopt another Track's remaining work, and do not merge — the user merges, submodule-first where one is involved.
