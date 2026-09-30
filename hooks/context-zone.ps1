# Windows launcher: equivalent inputs, thresholds, and messages to context-zone.sh.
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
try { $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { exit 0 }
if (-not $payload) { exit 0 }
function PositiveNumber($value) {
    $number = 0L
    if ([long]::TryParse([string]$value, [ref]$number) -and $number -gt 0) { return $number }
    return 0L
}
function Threshold([string]$name, [long]$fallback) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if ($value -notmatch '^[0-9]+$') { return $fallback }
    $number = PositiveNumber $value
    if ($number) { return $number }
    return $fallback
}
function FirstValue($values) {
    foreach ($value in $values) {
        if ($null -ne $value -and $value -isnot [bool]) { return $value }
        if ($value -is [bool] -and $value) { return $value }
    }
    return $null
}
$warn = Threshold 'CONTEXT_WARN_TOKENS' 80000
$ask = Threshold 'CONTEXT_ASK_TOKENS' 100000
$dumb = Threshold 'CONTEXT_DUMB_TOKENS' 120000
$force = Threshold 'CONTEXT_FORCE_TOKENS' 180000
$baseline = Threshold 'CONTEXT_REFERENCE_WINDOW' 200000
$transcript = [string]$payload.transcript_path
# Preserve the Bash hook's requirement for an existing transcript.
if (-not $transcript -or -not [IO.File]::Exists($transcript)) { exit 0 }
$window = PositiveNumber (FirstValue @(
    $payload.model_context_window, $payload.context_window,
    $payload.workspace_context.model_context_window, $payload.workspace_context.context_window,
    $payload.hook_event.model_context_window, $payload.hook_event.context_window))
$tokens = PositiveNumber (FirstValue @(
    $payload.total_tokens, $payload.context_tokens, $payload.transcript_tokens,
    $payload.transcript_token_count, $payload.token_count, $payload.token_usage.total_tokens,
    $payload.usage.total_tokens, $payload.usage.input_tokens,
    $payload.workspace_context.total_tokens, $payload.workspace_context.context_tokens,
    $payload.hook_event.total_tokens, $payload.hook_event.context_tokens))
$transcriptTokens = 0L
$transcriptWindow = 0L
try {
    foreach ($line in [IO.File]::ReadLines($transcript, [Text.Encoding]::UTF8)) {
        try {
            $event = $line | ConvertFrom-Json
            if ($event.type -eq 'event_msg' -and $event.payload.type -eq 'token_count') {
                $count = PositiveNumber $event.payload.info.last_token_usage.input_tokens
                if ($count) { $transcriptTokens = $count }
                $size = PositiveNumber $event.payload.info.model_context_window
                if ($size) { $transcriptWindow = $size }
            }
        } catch {
            # Bash's jq parser rejects a malformed JSONL stream as a whole.
            $transcriptTokens = 0L; $transcriptWindow = 0L; break
        }
    }
    if (-not $tokens) { $tokens = $transcriptTokens }
    if (-not $tokens) { $tokens = [long][math]::Floor((Get-Item -LiteralPath $transcript).Length / 4) }
} catch { exit 0 }
if (-not $window) { $window = $transcriptWindow }
if ($window) { $label = "$window window" }
else { $window = $baseline; $label = "$window baseline" }
if (-not $tokens -or $tokens -lt $warn) { exit 0 }
$approx = [long][math]::Floor(($tokens + 500) / 1000)
$percent = [long][math]::Floor($tokens * 100 / $window)
if ($tokens -lt $ask) {
    $message = "Context ~${approx}k tokens (~${percent}% of $label; smart-cap). After this step finishes, consider /session-close. Stay under 120k."
} elseif ($tokens -lt $dumb) {
    $message = "Context ~${approx}k tokens (~${percent}% of $label; warn zone). Ask the user whether to run /session-close (SESSION mode) or /handoff now, BEFORE starting another code slice."
} elseif ($tokens -lt $force) {
    $dash = [char]0x2014
    $message = "Context ~${approx}k tokens (~${percent}% of $label; DUMB ZONE). Do not start new code changes. Run /session-close (SESSION mode) $dash or /handoff for cross-tool transfer $dash now. Update activeContext.md so the next session can resume."
} else {
    $message = "Context ~${approx}k tokens (~${percent}% of $label; FORCE-COMPACT). Run /compact or /handoff immediately. Do not continue this session."
}
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
@{ systemMessage = $message } | ConvertTo-Json -Compress
