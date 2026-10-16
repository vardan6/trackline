# Windows launcher: same inputs, matching, and decision as harness-guard.sh.
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$harnesses = '^(claude|claude-code|codex|gemini|gemini-cli|cursor-agent|aider|opencode|opencode-ai|qwen|qwen-code|amp|crush|droid|copilot)$'
$wrappers = '^(sudo|exec|nohup|time|command|builtin|nice|xargs|npx|bunx|dlx|rtk|proxy|run|start|call|wsl|wsl\.exe|env|timeout)$'
$shells = '^(bash|sh|zsh|dash|fish|pwsh|pwsh\.exe|powershell|powershell\.exe|cmd|cmd\.exe)$'
# Wrapper options whose value is a separate word, so it is not taken for the
# command. Options whose value is itself a command (bash -c, env -S, -File)
# are left out on purpose. PowerShell options are matched lowercase.
$operands = @{
    timeout = '-s|--signal|-k|--kill-after'
    sudo = '-u|--user|-g|--group|-U|--other-user|-C|--close-from|-D|--chdir|-p|--prompt|-r|--role|-t|--type|-T|--command-timeout|--host'
    env = '-u|--unset|-C|--chdir'
    nice = '-n|--adjustment'
    xargs = '-a|--arg-file|-d|--delimiter|-E|-I|-L|--max-lines|-n|--max-args|-P|--max-procs|-s|--max-chars'
    wsl = '-d|--distribution|-u|--user|--cd'; 'wsl.exe' = '-d|--distribution|-u|--user|--cd'
    pwsh = '-executionpolicy|-ep|-windowstyle|-workingdirectory|-wd|-configurationname|-inputformat|-outputformat'; 'pwsh.exe' = '-executionpolicy|-ep|-windowstyle|-workingdirectory|-wd|-configurationname|-inputformat|-outputformat'; powershell = '-executionpolicy|-ep|-windowstyle|-workingdirectory|-wd|-configurationname|-inputformat|-outputformat'; 'powershell.exe' = '-executionpolicy|-ep|-windowstyle|-workingdirectory|-wd|-configurationname|-inputformat|-outputformat'
}

$raw = [Console]::In.ReadToEnd()
function Strings($value) {
    if ($null -eq $value) { return }
    if ($value -is [string]) { $value; return }
    if ($value -is [Collections.IEnumerable]) { foreach ($item in $value) { Strings $item }; return }
    if ($value -is [PSCustomObject]) { foreach ($p in $value.PSObject.Properties) { Strings $p.Value } }
}
function Calls([string]$script) {
    # Keep cmd strings in any JS literal form: double, single, or backtick quotes.
    $found = [regex]::Matches($script, '(?:cmd|command)["'']?\s*:\s*(?:"((?:\\.|[^"\\])*)"|''((?:\\.|[^''\\])*)''|`((?:\\.|[^`\\])*)`)') |
        ForEach-Object { $g = $_.Groups; (1..3 | ForEach-Object { $g[$_] } | Where-Object Success)[0].Value }
    if ($found) { return ($found -join "`n") }
    if ($script -match 'apply_patch|\*\*\* Begin Patch') { return '' }
    return $script
}
try {
    $payload = $raw | ConvertFrom-Json
    $tool = ([string]$payload.tool_name).ToLowerInvariant()
    if ($tool -match '^(apply_patch|edit|multiedit|write|notebookedit|read|grep|glob|webfetch|websearch)$') { exit 0 }
    $t = $payload.tool_input
    $direct = @()
    if ($t -is [PSCustomObject]) {
        foreach ($name in 'command', 'cmd') {
            $value = $t.$name
            if ($null -ne $value) { $direct += ((@($value) | ForEach-Object { [string]$_ }) -join ' ') }
        }
    }
    if ($direct.Count) { $text = $direct -join "`n" }
    elseif ($tool -match 'bash|shell|exec|powershell|^$') { $text = Calls ((@(Strings $t)) -join "`n") }
    else { $text = '' }
} catch {
    # Unparseable payload: scan it raw, with JSON quotes and punctuation as
    # separators so a property name cannot shield the command; over-matching
    # beats silent bypass.
    if ($raw -match '"tool_name"\s*:\s*"([^"]*)"' -and
        $Matches[1].ToLowerInvariant() -match '^(apply_patch|edit|multiedit|write|notebookedit|read|grep|glob|webfetch|websearch)$') { exit 0 }
    $text = $raw -replace '[":,\[\]]', "`n"
}

$found = ''
$segments = ($text -replace '\\n', "`n" -replace '\$\(', "`n" -replace '[;&|(){}`]', "`n") -split "`n"
foreach ($segment in $segments) {
    $words = @($segment -split '\s+' | Where-Object { $_ -ne '' })
    $i = 0
    while ($i -lt $words.Count) {
        # Keep backslashes until the basename split: C:\Tools\x.exe is a path.
        $word = $words[$i] -replace '^cmd:', '' -replace '^command:', '' -replace '["'']', '' -replace '\\+$', ''
        if (-not $word) { $i++; continue }
        $lower = $word.ToLowerInvariant()
        $base = ($lower -split '[/\\]')[-1]
        if ($word -match '^[A-Za-z_][A-Za-z0-9_]*=') { $i++ }
        elseif ($base -match $shells -or $base -match $wrappers) {
            $i++
            # Skip the wrapper's options and their values, and timeout's duration operand.
            if ($base -eq 'command' -and $i -lt $words.Count -and $words[$i] -cmatch '^-[vV]$') { break }
            $takes = $operands[$base]
            while ($i -lt $words.Count -and $words[$i] -match '^(-|/[A-Za-z]$)') {
                $opt = $words[$i]
                if ($base -match '^(pwsh|powershell)') { $opt = $opt.ToLowerInvariant() }
                $i++
                if ($takes -and $opt -cmatch "^($takes)$") { $i++ }
            }
            if ($base -eq 'timeout' -and $i -lt $words.Count -and $words[$i] -match '^[0-9]') { $i++ }
        }
        elseif ($lower -match '^(npm|pnpm|yarn)$') { $i++ }
        else {
            # npx @scope/pkg@ver, paths, and Windows extensions reduce to the name.
            $name = $base -replace '@[^@]*$', ''
            if (-not $name) { $name = $base }
            $name = $name -replace '\.(exe|cmd|ps1|bat|js)$', ''
            if ($name -match $harnesses) { $found = $name }
            break
        }
    }
    if ($found) { break }
}
if (-not $found) { exit 0 }

$reason = "Trackline harness-guard: launching another coding agent harness ($found) from an agent session is blocked; it spends the user's paid quota for that tool. Do not retry or work around this. For /cross-review or /plan-review, tell the user to run the skill in a session of the other provider that they open themselves. If this command only mentions $found as text, rephrase it so the name does not start a command segment."
@{ hookSpecificOutput = [ordered]@{ hookEventName = 'PreToolUse'; permissionDecision = 'deny'; permissionDecisionReason = $reason } } |
    ConvertTo-Json -Compress
exit 0
