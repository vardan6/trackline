#!/usr/bin/env bash
# context-zone.sh — Stop-hook that classifies the session into
# smart / warn / dumb / force-compact zones based on approximate token usage,
# and nudges the agent toward /session-close or /handoff.
#
# Thresholds are FIXED TOKEN AMOUNTS, not fractions of any model window.
# They are empirical behavior cliffs calibrated on the Claude 200k era.
# Same absolute token counts apply on Codex 258.4k, Claude Code 200k
# (Sonnet 4.6 / Haiku 4.5), and Opus 4.7 1M windows.
#
# Wire via .claude/settings.json:
#   {
#     "hooks": {
#       "Stop": [
#         { "command": "/abs/path/to/my-workflow/hooks/context-zone.sh" }
#       ]
#     }
#   }
#
# The hook reads the JSON payload Claude Code provides on stdin:
#   { "session_id": "...", "transcript_path": "/path/to/session.jsonl", ... }
# If the payload includes a live token count, prefer that. Otherwise estimate
# tokens by transcript-bytes / 4. Emits a systemMessage that the next turn
# will see.
#
# Zones (token amounts, configurable via env):
#   <  WARN_TOKENS  (default  80,000) -> silent (smart zone, incl. calm < 60k)
#   >= WARN_TOKENS, < ASK_TOKENS      -> soft nudge: "consider /session-close soon"
#   >= ASK_TOKENS,  < DUMB_TOKENS     -> ask: "run /session-close (SESSION) or /handoff now?"
#   >= DUMB_TOKENS, < FORCE_TOKENS    -> strong: "dumb zone — stop new code"
#   >= FORCE_TOKENS                   -> force: "/compact or /handoff immediately"
#
# Defaults (anchored on the 200k-era cliff):
#   WARN_TOKENS=80000       (smart-cap; warn coming up)
#   ASK_TOKENS=100000       (warn; ask user how to close)
#   DUMB_TOKENS=120000      (dumb; no new code)
#   FORCE_TOKENS=180000     (force-compact)
#
# Override per project by setting CONTEXT_{WARN,ASK,DUMB,FORCE}_TOKENS in the
# settings env block. The model's marketed/API window does NOT enter the
# threshold math.
#
# Display percentage:
# - If the hook payload includes the live model window, use that so the
#   percentage matches the product status line.
# - Otherwise fall back to REFERENCE_WINDOW (default 200000), which preserves
#   the older 200k-era percentage vocabulary.

set -u

WARN_TOKENS="${CONTEXT_WARN_TOKENS:-80000}"
ASK_TOKENS="${CONTEXT_ASK_TOKENS:-100000}"
DUMB_TOKENS="${CONTEXT_DUMB_TOKENS:-120000}"
FORCE_TOKENS="${CONTEXT_FORCE_TOKENS:-180000}"
REFERENCE_WINDOW="${CONTEXT_REFERENCE_WINDOW:-200000}"

payload="$(cat || true)"
transcript=""
display_window=""
payload_tokens=""
transcript_tokens=""
transcript_window=""
if command -v jq >/dev/null 2>&1; then
  transcript="$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
  display_window="$(printf '%s' "$payload" | jq -r '
    .model_context_window
    // .context_window
    // .workspace_context.model_context_window
    // .workspace_context.context_window
    // .hook_event.model_context_window
    // .hook_event.context_window
    // empty
  ' 2>/dev/null || true)"
  payload_tokens="$(printf '%s' "$payload" | jq -r '
    .total_tokens
    // .context_tokens
    // .transcript_tokens
    // .transcript_token_count
    // .token_count
    // .token_usage.total_tokens
    // .usage.total_tokens
    // .usage.input_tokens
    // .workspace_context.total_tokens
    // .workspace_context.context_tokens
    // .hook_event.total_tokens
    // .hook_event.context_tokens
    // empty
  ' 2>/dev/null || true)"
fi

if [ -z "$transcript" ] || [ ! -f "$transcript" ]; then
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  transcript_tokens="$(jq -rs '
    map(
      select(
        .type == "event_msg"
        and .payload.type == "token_count"
        and (.payload.info.last_token_usage.input_tokens // 0) > 0
      )
      | .payload.info.last_token_usage.input_tokens
    )
    | last // empty
  ' "$transcript" 2>/dev/null || true)"
  transcript_window="$(jq -rs '
    map(
      select(
        .type == "event_msg"
        and .payload.type == "token_count"
        and (.payload.info.model_context_window // 0) > 0
      )
      | .payload.info.model_context_window
    )
    | last // empty
  ' "$transcript" 2>/dev/null || true)"
fi

if [ -n "$payload_tokens" ] && [ "$payload_tokens" -gt 0 ] 2>/dev/null; then
  approx_tokens="$payload_tokens"
elif [ -n "$transcript_tokens" ] && [ "$transcript_tokens" -gt 0 ] 2>/dev/null; then
  approx_tokens="$transcript_tokens"
else
  # Approximate token count: total bytes of transcript / 4.
  bytes="$(wc -c < "$transcript" 2>/dev/null || echo 0)"
  approx_tokens=$(( bytes / 4 ))
fi
approx_k=$(( (approx_tokens + 500) / 1000 ))
if [ -z "$display_window" ] || ! [ "$display_window" -gt 0 ] 2>/dev/null; then
  if [ -n "$transcript_window" ] && [ "$transcript_window" -gt 0 ] 2>/dev/null; then
    display_window="$transcript_window"
  fi
fi
if [ -z "$display_window" ] || ! [ "$display_window" -gt 0 ] 2>/dev/null; then
  display_window="$REFERENCE_WINDOW"
  pct_label="${REFERENCE_WINDOW} baseline"
else
  pct_label="${display_window} window"
fi
ref_pct=$(( approx_tokens * 100 / display_window ))

zone=""
msg=""
if [ "$approx_tokens" -lt "$WARN_TOKENS" ]; then
  exit 0
elif [ "$approx_tokens" -lt "$ASK_TOKENS" ]; then
  zone="warn"
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; smart-cap). After this step finishes, consider /session-close. Stay under 120k."
elif [ "$approx_tokens" -lt "$DUMB_TOKENS" ]; then
  zone="ask"
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; warn zone). Ask the user whether to run /session-close (SESSION mode) or /handoff now, BEFORE starting another code slice."
elif [ "$approx_tokens" -lt "$FORCE_TOKENS" ]; then
  zone="dumb"
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; DUMB ZONE). Do not start new code changes. Run /session-close (SESSION mode) — or /handoff for cross-tool transfer — now. Update activeContext.md so the next session can resume."
else
  zone="force"
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; FORCE-COMPACT). Run /compact or /handoff immediately. Do not continue this session."
fi

# Emit a systemMessage the agent will see on the next turn.
# Stop hooks only support top-level fields; hookSpecificOutput is not valid for Stop.
printf '{"systemMessage":"%s"}\n' \
  "$(printf '%s' "$msg" | sed 's/"/\\"/g')"

exit 0
