# hooks/

Auto-nudges that enforce the workflow's context-budget rule (smart / warn /
dumb / force-compact zones) without you having to watch the `/context`
indicator.
`harness-guard.sh` blocks agents from launching other coding agent harnesses
(see its section below).

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

## `harness-guard.sh`

A **PreToolUse hook**: it runs before every tool call and denies shell
commands that launch another coding agent harness: `claude`, `codex`,
`gemini`, `cursor-agent`, `aider`, `opencode`, `qwen`, `amp`, `crush`,
`droid`, `copilot`. A nested harness bills the user's quota for that tool. On
2026-10-14 Codex started `claude -p --effort max` for a `/cross-review` and
used 77% of a 5-hour Claude window in 30 minutes. Cross-provider work runs in
a session the user opens; the deny reason tells the agent to say so.

- **Command position only.** A name counts when it starts a command segment
  (after `;`, `&&`, `|`, `$(`, a backtick, or a newline) or follows a wrapper:
  `bash -c`, `sh -lc`, `powershell -Command`, `timeout 30s`, `env X=1`,
  `sudo`, `npx`/`bunx`/`npm exec`, `rtk proxy`. Paths, `.exe`, and npm package
  names (`@anthropic-ai/claude-code`) reduce to the harness name. `rg claude`,
  `which codex`, and `command -v claude` pass.
- **Known false positive.** Splitting ignores quoting, so a quoted argument
  with a separator before a harness name is denied
  (`git commit -m "a; claude b"`). The reason tells the agent to rephrase.
- **Tools.** Shell tools (`Bash`, `PowerShell`, Codex `exec_command`, `shell`)
  are checked through `command` / `cmd`. For Codex code-mode `exec`, only the
  `cmd` strings of its script are checked, in any quote form (`"…"`, `'…'`,
  `` `…` ``). Edit and patch tools are never checked, so editing docs that
  mention these commands works.
- **Not covered.** Local model runners (`ollama`, `llama.cpp`, …) are not on
  the list. There is no allow switch: to permit nesting, remove the
  `PreToolUse` registration.
- **Without jq** the hook still skips edit tools by `tool_name`, then scans
  the raw payload with JSON quotes and punctuation as separators; it
  over-matches rather than failing open. `harness-guard.ps1` is the native
  Windows Codex equivalent; `tests/test_harness_guard.py` runs one case table
  against both.

### Install (both tools — use the installer)

`install-workflow.sh` registers both Bash hooks for Linux/WSL and adds
equivalent PowerShell launchers for native Windows Codex in a shared
Windows-drive project. Hooks link to the canonical Trackline source; project
JSON registration preserves other hooks and settings. Reinstallation does not
duplicate registrations or rewrite unchanged settings.

Bash command:

```sh
bash "$(git rev-parse --show-toplevel)/.agents/hooks/context-zone.sh"
```

The Windows command also resolves the Git root at runtime before invoking
`.agents/hooks/context-zone.ps1`, so moving the project or launching from a
subdirectory does not require rewriting registration.

Native Windows Claude Code uses the Bash launcher and requires **Git Bash and
jq in its Bash environment**. A WSL jq installation does not satisfy that
Windows dependency. The installer reports this requirement; verify it in the
shell Claude uses before relying on its hook.

**Manual Claude Code:** merge the `hooks` block from `settings.snippet.json`
into `.claude/settings.json` (project) or `~/.claude/settings.json` (global),
then restart Claude Code.

**Manual Codex:** merge the `hooks` block from `codex.hooks.json` into
`<project>/.codex/hooks.json` (do not symlink it; the installer migrates such a
link) and create the `.agents/hooks/context-zone.sh` and `harness-guard.sh` links. Native Windows Codex
needs `commandWindows` entries for the `.ps1` launchers and Git for Windows on the
Windows PATH; let the installer write it. Start Codex from anywhere
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

The context-zone hook is **advisory**: it never blocks a tool call, it just
makes sure the agent sees the context budget at the right moment.
harness-guard is the only hook that blocks.
