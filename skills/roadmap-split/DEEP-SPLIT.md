# DEEP-SPLIT — tier 2 interface analysis

Loaded by [SKILL.md](SKILL.md) step 4 and never on the common path. Everything here costs real reading; do not run it to tidy a partition that already meets its count.

## When tier 2 runs

Exactly one trigger: **the partition remaining after tiers 1 and 1.5 holds fewer Tracks than requested.** Measure after 1.5, not after 1 — tier 1.5 is mandatory when code is involved and can merge two Tracks that tier 1 had separated, and that loss is a legitimate escalation route. A count reached at tier 1 and still standing after 1.5 never escalates.

Do not run tier 2 to balance Track sizes. Balance is cosmetic and may be given up freely.

## What tier 2 may conclude

Tier 2 **overturns tier 1's conservative verdict with evidence**. It does not relax the rules to find Tracks. Two admissible conclusions:

1. **The file set was wrong.** Tier 1 attributed a file to a slice that does not in fact change it — the slice reads it, names it in passing, or touches a sibling. Correct the set; the overlap disappears and the Tracks separate.
2. **One slice is the whole obstruction.** Name the single slice whose reordering into another Track, or splitting in two, frees the requested count. Propose it; do not perform it silently.

**Not admissible: permitting two Tracks to change one file.** Append-only files, non-interacting functions in one file, and "it will merge fine" are all rejected. File-disjointness is a hard blocker in the [independence contract](SKILL.md), and a whole-file rewrite — a `Write`, a formatter, a codegen pass — loses the other Track's work with no error and no conflict marker. The emitted partition is always literally file-disjoint, at every tier.

## The analysis

Interface-disjointness is the real test: **no Track modifies a symbol, schema, or contract another Track reads.** File-disjointness is a cheap proxy for it. Work outward from the contested slices only — never the whole tree:

1. For each slice in the contested pair, resolve its true file set: `rg` the identifiers the slice names, and read the definition sites, not the whole file.
2. For each symbol a slice *modifies*, `rg` its references across the other Track's file set. A reference the other Track reads is a genuine coupling; the Tracks stay merged.
3. Check the four couplings that survive file-disjointness and are invisible to `rg` on symbols alone: shared registration points (one index, router table, or array both append to), migration or fixture ordinals, manifests and lockfiles, and a shared test run one Track can redden for the other. Any of these keeps the Tracks together.
4. Semantic drift — same signature, changed meaning — has no reliable catcher. Where a slice changes what a function *means*, treat the Tracks as coupled; do not certify a split on signature stability alone.

## Reporting

Report through SKILL.md's Output block. `Depth used: tier 2` must name the reason it escalated and what the evidence changed — which file set was corrected, or which slice was proposed for reorder. If tier 2 finds nothing, say so and return the tier 1.5 partition; an escalation that changes nothing is a legitimate and reportable outcome, not a failure to try harder.
