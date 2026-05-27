#!/usr/bin/env bash
# context-zone-codex.sh — Codex Stop hook variant for context-zone nudges.
# Emits only a systemMessage because Codex rejects the richer Claude-style
# payload used by context-zone.sh.

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

msg=""
if [ "$approx_tokens" -lt "$WARN_TOKENS" ]; then
  exit 0
elif [ "$approx_tokens" -lt "$ASK_TOKENS" ]; then
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; smart-cap). After this step finishes, consider /session-close. Stay under 120k."
elif [ "$approx_tokens" -lt "$DUMB_TOKENS" ]; then
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; warn zone). Ask the user whether to run /session-close (SESSION mode) or /handoff now, BEFORE starting another code slice."
elif [ "$approx_tokens" -lt "$FORCE_TOKENS" ]; then
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; DUMB ZONE). Do not start new code changes. Run /session-close (SESSION mode) or /handoff now. Update activeContext.md so the next session can resume."
else
  msg="Context ~${approx_k}k tokens (~${ref_pct}% of ${pct_label}; FORCE-COMPACT). Run /compact or /handoff immediately. Do not continue this session."
fi

if command -v jq >/dev/null 2>&1; then
  printf '{"systemMessage":%s}\n' "$(jq -Rn --arg s "$msg" '$s')"
else
  escaped="$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  printf '{"systemMessage":"%s"}\n' "$escaped"
fi

exit 0
