# hooks/

Auto-nudges that enforce the workflow's context-budget rule (smart / warn /
dumb / force-compact zones) without you having to watch the `/context`
indicator.

## `context-zone.sh`

A **Stop hook** — fires after every assistant turn. Reads the session
transcript Claude Code writes to disk, prefers a live token count from the
hook payload when available, then falls back to transcript-embedded
`token_count` events using the latest `last_token_usage.input_tokens` value
when present, otherwise approximates tokens as
`bytes ÷ 4`, and emits a `systemMessage` the agent will see on the next turn.

### Thresholds are FIXED TOKEN AMOUNTS

The cliff lives at an absolute token count, not at a fraction of whatever
window the active model advertises. Empirically the 200k-era "50%" (≈100k
tokens) is where behavior starts to degrade; on Opus 4.7's 1M window that
same ~100k tokens is only 10% on the status line, but the cognitive
cliff is at the same absolute spot. In current Codex telemetry, ~100k is
about 39% of the effective 258.4k product window. The hook uses fixed-token
thresholds so Codex 258.4k, Sonnet 4.6 / Haiku 4.5 200k, and Opus 4.7 1M
sessions get nudged at the same actual context size.

### Zones (defaults)

| Tokens (approx) | Zone          | What the hook does                                                                            |
|-----------------|---------------|-----------------------------------------------------------------------------------------------|
| `< 80k`         | smart         | silent — no message                                                                           |
| `80k – 99k`     | warn (soft)   | "consider `/session-close` after this step. Stay under 120k."                                 |
| `100k – 119k`   | ask           | "ask the user whether to run `/session-close` (SESSION) or `/handoff` BEFORE the next slice." |
| `120k – 179k`   | dumb          | "DUMB ZONE — do not start new code changes. Run `/session-close` (SESSION) or `/handoff` now." |
| `≥ 180k`        | force-compact | "Run `/compact` or `/handoff` immediately. Do not continue this session."                     |

The message also includes a percentage. When the hook payload includes the
live model window, the hook uses that so the percentage matches the product
status line. When the payload does not include a window, it falls back to a
transcript-embedded model window if present, and only then to a
**reference window** (default 200k) so it can still speak the older
200k-era percentage vocabulary. This is presentation only — the cliff is the
token count.

### Same thresholds as a % of each product surface's effective window

(Reference only — for interpreting your status-line readout.)

| Product surface / model                          | Window | warn 80k | ask 100k | dumb 120k | force 180k |
|--------------------------------------------------|-------:|---------:|---------:|----------:|-----------:|
| Codex: GPT-5.2-Codex / GPT-5.3-Codex / GPT-5.4 / GPT-5.5 | 258.4k | 31% | 39% | 46% | 70% |
| Claude Code: Opus 4.7                            | 1,000k | 8% | 10% | 12% | 18% |
| Claude Code: Sonnet 4.6 / Haiku 4.5              | 200k | 40% | 50% | 60% | 90% |

A status-line "46%" on current Codex = ~120k tokens = **dumb zone**. A
status-line "12%" on Opus 4.7 means the same thing. Do not be
lulled by small percentages on 1M models or by API pages that advertise a
larger raw model window than the product surface exposes.

### Behavior

The message is injected as a `systemMessage`, so the **agent** acts on it
on the next turn. In the `ask` zone the agent confirms with you before
closing. In the `dumb` and `force-compact` zones it should refuse new code
work and close first.

### Install (both tools — use the installer)

`install-workflow.sh` wires this up for you: it creates the single in-project
link `.agents/hooks/context-zone.sh -> trackline/hooks/context-zone.sh`,
merges the Stop block into `.claude/settings.json`, and symlinks
`.codex/hooks.json`. Both tools then run the **same** script via the **same**
command string:

```sh
bash "$(git rev-parse --show-toplevel)/.agents/hooks/context-zone.sh"
```

The git-toplevel form resolves the project root from any subdirectory the hook
is launched in — this is what makes it robust across both tools.

**Manual Claude Code:** merge the `hooks` block from `settings.snippet.json`
into `.claude/settings.json` (project) or `~/.claude/settings.json` (global),
then restart Claude Code.

**Manual Codex:** symlink `codex.hooks.json` to `<project>/.codex/hooks.json`
and create the `.agents/hooks/context-zone.sh` link. Start Codex from anywhere
in the git worktree; approve the project hook once if prompted.

### Tested on

Claude Code and Codex (primary). Limited testing on OpenCode and Qwen Code —
both read `.agents/skills` and the `SKILL.md` standard, so the skills wire up,
but the context-zone hook has not been exercised there.

### Env-var overrides

All optional. The hook honors:

- `CONTEXT_WARN_TOKENS`   (default `80000`)
- `CONTEXT_ASK_TOKENS`    (default `100000`)
- `CONTEXT_DUMB_TOKENS`   (default `120000`)
- `CONTEXT_FORCE_TOKENS`  (default `180000`)
- `CONTEXT_REFERENCE_WINDOW` (default `200000`) — fallback display window
  used only when the hook payload does not include a live model window. It
  does **not** change when the hook fires. For Codex, the hook will prefer
  the live window from the payload when available.

The model's marketed API window is intentionally **not** a parameter. Larger
raw windows do not raise the cliff — they just make the same cliff look like
a smaller percentage. For Codex, use the effective window reported by the
Codex status/telemetry (`258400` in recent local sessions), not the larger
API model-page number.

### Dependencies

- `bash`, `wc`, `sed` — standard.
- `jq` — used to parse the hook payload. If absent, the hook silently exits
  (no nudge — falls back to manual `/session-close` discipline). Install
  with `apt install jq` / `brew install jq`.

### How it relates to the canonical skills

- `/session-close (STEP mode)` is still run by you (or the agent) after
  each roadmap step. The hook does not auto-run it.
- `/session-close (SESSION mode)` is what the hook escalates toward when
  context climbs.
- `/handoff` is the cross-tool alternative the hook also names.

The hook is **advisory**: it never blocks a tool call, it just makes sure
the agent sees the context budget at the right moment.
