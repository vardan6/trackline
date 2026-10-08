# PARALLEL — fan-out dispatch

Loaded by [SKILL.md](SKILL.md) step 2 for `all` or `parallel`, never otherwise; replaces its steps 3–6.

Read the `## Tracks — parallel` section of `roadmap.md`. No such section → stop and say so: `/roadmap-split` produces it; this skill never partitions.

A Track that already has a `Worktree:` line is in flight or finished but unmerged. Never launch a second worktree for it: check its branch, then resume its worker or run [Finish](#finish--merge-back-and-cleanup). The roadmap alone lets a session that never saw the launch recover.

## Print always, start only when told

Print the Plan block on **every** invocation. Start agents only when the invocation asks for implementation in so many words — "and implement", "run them", "go". `/next-slice all` alone prints and stops. Never infer authorization: guessing wrong means three agents writing code unattended.

```
Fan-out plan — <n> Tracks
  Track A — <name> | <n> runnable slices | Branch: track-a/<short-name> | Base: <branch>
                     Worktree: <path> | Files: <list>
  Track B — ...
Needs you: <n parked slices — the decisions these Tracks are not waiting for>
Barriers: <Track — the parked slice it stops at, or "none">
Placeholders: <Track — items still marked "split again when selected"; a Track stops there, or "none">
Roadmap commit: <sha — the revision workers branch from> | UNCOMMITTED — stop
Starting: <n agents, or "nothing — no implement instruction">
```

The `Needs you` line is mandatory: a parked decision left unseen for weeks is the failure the parked list exists to prevent.

## Launch

Branch names alone do not isolate concurrent agents: two agents in one checkout overwrite each other's working tree. In this order:

1. **The partition must be committed first.** A fresh worktree omits uncommitted changes, so workers would pick from the old roadmap. If `roadmap.md` holds changes this dispatcher did not write, stop and ask the user to commit. Never commit the user's changes — no exceptions, no fast path.
2. **Write launch lines before any worktree exists.** Base is the branch checked out in the dispatcher's checkout; a Track merges back into it and nowhere else. Under each Track write `Base: <branch> | Worktree: <absolute path>`; once above the Tracks, the merge-back rule: *"On finish the dispatcher merges each Track branch into its Base, verifies, removes the worktree and deletes the branch; a Track that cannot finish keeps both and is reported with its remaining slices."* Under the implement instruction, commit `roadmap.md` with only these lines — the one commit authorized before work starts. It is the starting revision for every Track; Tracks are prerequisite-free, so nothing else needs transferring.
3. **One worktree per Track**, never two Tracks in one directory: `git worktree add <path> -b track-<letter>/<short-name>` from the starting revision. Then run `PROJECT.md` §Worktree setup in it, if present (dependency links, environment paths, ignore entries): a worktree that cannot run the project's tests cannot verify a slice.
4. **Fixed worker brief, never improvised:** Track letter, worktree path, branch and Base; the Track's `Files:` line as the only files it may change, docs included; the project's verification commands; the rules below; and, when the skill files are not tracked in the repo, absolute paths to this file and `SKILL.md` — the worktree has no copy. Nothing else tells a worker which slices are its own; if it restarts cold, `/session-open` recovers the letter from the `track-<letter>/` branch prefix.
5. **Standing rules for every worker:** commit each verified slice on the Track branch; never push, never merge, never touch another Track's files. Tick slices only in its own Track section. Never edit `activeContext.md` or `progress.md` — two Tracks editing them conflict on every merge; the report carries that content instead.

## Sequential execution inside a Track

`/next-slice` and `/session-close` each stop after one cycle by design, so neither can run a Track to its end. **This file owns the repetition**, only under the implement instruction that started the fan-out. Tracks run side by side; workers within a Track run one after another in the same worktree.

Worker cycle: take the next unchecked slice **in this Track's order** → confirm it is atomic → open every doc it cites, plus ADRs those link, one hop → implement → verify → tick → commit on the Track branch. Continue to the next slice only under the [SKILL.md](SKILL.md) stop condition (same files and cited docs, context below ~100k); otherwise report and exit, and the dispatcher launches a fresh worker for the next slice.

- The implement instruction confirms slices inside this Track and nothing else — not another Track's, not `Needs you`, nothing outside the roadmap.
- **A placeholder is not a slice.** An item marked "split again when selected" (or otherwise flagged for a split) is parked planning. Never run it whole or re-split it unattended; splitting is for `/planning-capture` with the user. Fan-out incident 2026-09-08 (`progress.md`): two such items ran whole for ~146K and ~232K tokens.
- Running unattended does not weaken the citation contract: a cited link that resolves to nothing, or a behavior-changing slice claiming no doc governs it, stops the Track.

Stop the Track and report at the first of:

- a **Barrier** line, a **HITL** slice, or an unsplit placeholder reached in sequence — remaining slices stay in place, unticked;
- the Track's slices are exhausted;
- a verification fails, or confidence in a slice is low;
- a slice is still unverified past ~120k context — it was not atomic.

Keep the worker report short; the dispatcher's context grows with every report: stop reason, slices ticked, slices remaining and why, files changed, verification commands with pass/fail counts, open questions, and the state-file lines it would have written. Workers never re-partition, adopt another Track's work, or merge.

## Finish — merge-back and cleanup

Dispatcher only, one Track at a time as reports arrive, never two merges at once.

**A Track finished** when its last worker stopped on exhausted slices or a designed gate (Barrier, HITL, placeholder), and every ticked slice is committed and verified. In the dispatcher's checkout:

1. The checkout must be on the Track's Base and clean; otherwise stop and report. Never stash or switch branches over the user's work.
2. `git merge --no-ff track-<letter>/<short-name>`, submodule-first where one is involved. Conflicts only in roadmap ticks of different Track sections → keep both sides. Any other conflict → `git merge --abort`, keep the worktree, report.
3. Run the project's verification on the merged result. Fails → `git reset --hard ORIG_HEAD` (only on the merge commit just made) and report.
4. `git worktree remove <path>`, then `git branch -d track-<letter>/<short-name>`. Never `-D` or `--force`: a refusal means uncommitted or unmerged work — report it.
5. Remove the Track's launch line; leave its ticked slices for `/session-close` to archive. Write the state files once from the Track's reports, then commit.

**Any other stop reason** means the Track did not finish: do not merge. Keep worktree, branch and launch line, and report the stop reason, the remaining slices, and the one action that unblocks it. The launch line is the resume pointer for a later session.

When every launched Track is finished or reported, print the summary, then run `/session-close` STEP mode once for the fan-out.

```
Fan-out result
  Track A — merged into <base> @ <sha> | worktree removed | <n> slices
  Track B — NOT FINISHED: <stop reason> | remaining: <slices> | unblock: <action>
Needs you: <parked slices + new questions from reports>
```
