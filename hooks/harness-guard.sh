#!/usr/bin/env bash
# harness-guard.sh — PreToolUse hook (Claude Code and Codex).
#
# Denies shell commands that launch another coding agent harness (claude,
# codex, gemini, ...): a nested harness bills the user's quota for that tool.
# Local model runners (ollama, llama.cpp, ...) are not on the list.
#
# A harness counts only in command position — after a separator or a wrapper
# such as `bash -c`, `timeout 30s`, `env X=1`, `npx`, or `rtk proxy` — so
# `rg claude` or `which codex` pass. Splitting ignores quoting, so a quoted
# string that starts a segment with a harness name is also denied; rephrase it.

HARNESSES='claude|claude-code|codex|gemini|gemini-cli|cursor-agent|aider|opencode|opencode-ai|qwen|qwen-code|amp|crush|droid|copilot'
WRAPPERS='sudo|exec|nohup|time|command|builtin|nice|xargs|npx|bunx|dlx|rtk|proxy|run|start|call|wsl|wsl.exe'
SHELLS='bash|sh|zsh|dash|fish|pwsh|pwsh.exe|powershell|powershell.exe|cmd|cmd.exe'

# Wrapper options whose value is a separate word, so it is not taken for the
# command. Options whose value is itself a command (bash -c, env -S, -File)
# are left out on purpose. PowerShell options are matched lowercase.
operands() {
  case $1 in
    timeout) echo '-s|--signal|-k|--kill-after' ;;
    sudo) echo '-u|--user|-g|--group|-U|--other-user|-C|--close-from|-D|--chdir|-p|--prompt|-r|--role|-t|--type|-T|--command-timeout|--host' ;;
    env) echo '-u|--unset|-C|--chdir' ;;
    nice) echo '-n|--adjustment' ;;
    xargs) echo '-a|--arg-file|-d|--delimiter|-E|-I|-L|--max-lines|-n|--max-args|-P|--max-procs|-s|--max-chars' ;;
    wsl|wsl.exe) echo '-d|--distribution|-u|--user|--cd' ;;
    pwsh|pwsh.exe|powershell|powershell.exe) echo '-executionpolicy|-ep|-windowstyle|-workingdirectory|-wd|-configurationname|-inputformat|-outputformat' ;;
  esac
}

input=$(cat)

# Shell-capable tools only; edit tools carry file text, not commands.
if command -v jq >/dev/null 2>&1; then
  tool=$(printf '%s' "$input" | jq -r '.tool_name // ""' 2>/dev/null)
elif [[ $input =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"([^\"]*)\" ]]; then
  tool=${BASH_REMATCH[1]}
fi
case "${tool,,}" in
  apply_patch|edit|multiedit|write|notebookedit|read|grep|glob|webfetch|websearch) exit 0 ;;
esac

raw=''
if command -v jq >/dev/null 2>&1; then
  text=$(printf '%s' "$input" | jq -r --arg tool "${tool,,}" '
    def flat: if type == "array" then map(tostring) | join(" ") elif type == "string" then . else empty end;
    # Code-mode tools (Codex `exec`) carry script text: keep its cmd strings
    # in any JS literal form (double, single, or backtick quotes); a script
    # without them is checked whole unless it is only a patch.
    def calls: ([scan("(?:cmd|command)[\"\\x27]?\\s*:\\s*(?:\"((?:\\\\.|[^\"\\\\])*)\"|\\x27((?:\\\\.|[^\\x27\\\\])*)\\x27|`((?:\\\\.|[^`\\\\])*)`)")
        | map(select(. != null)) | .[0]] | join("\n")) as $c
      | if $c != "" then $c elif test("apply_patch|\\*\\*\\* Begin Patch") then "" else . end;
    .tool_input as $t
    | if ($t | type) == "object" and (($t.command // $t.cmd) != null) then
        [$t.command, $t.cmd] | map(select(. != null) | flat) | join("\n")
      elif ($tool | test("bash|shell|exec|powershell|^$")) then [$t | .. | strings] | join("\n") | calls
      else "" end' 2>/dev/null) || raw=1
else
  raw=1
fi
# Without jq, scan the raw payload with JSON quotes and punctuation as
# separators, so a property name cannot shield the command: over-matching
# beats silent bypass.
[ -n "$raw" ] && text=$(printf '%s' "$input" | sed -e 's/[":,[]/\n/g' -e 's/]/\n/g')

found=''
segments=$(printf '%s' "$text" | sed -e 's/\\n/\n/g' -e 's/\$(/\n/g' -e 's/[;&|(){}`]/\n/g')
while IFS= read -r segment; do
  words=()
  read -r -a words <<<"$segment"
  i=0
  while [ "$i" -lt "${#words[@]}" ]; do
    word=${words[$i]}
    word=${word#cmd:}; word=${word#command:}
    # Keep backslashes until the basename split: C:\Tools\x.exe is a path.
    word=${word//[\"\']/}
    while [[ $word == *\\ ]]; do word=${word%\\}; done
    [ -z "$word" ] && { i=$((i + 1)); continue; }
    lower=${word,,}
    base=${lower##*[/\\]}
    if [[ $word =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
      i=$((i + 1))
    elif [[ $base =~ ^($SHELLS)$ || $base =~ ^($WRAPPERS)$ || $base == env || $base == timeout ]]; then
      i=$((i + 1))
      # Skip the wrapper's options and their values, and timeout's duration operand.
      [ "$base" = command ] && [[ ${words[$i]} =~ ^-[vV]$ ]] && break  # lookup, not a launch
      takes=$(operands "$base")
      while [ "$i" -lt "${#words[@]}" ] && [[ ${words[$i]} =~ ^(-|/[A-Za-z]$) ]]; do
        opt=${words[$i]}; [[ $base == pwsh* || $base == powershell* ]] && opt=${opt,,}
        i=$((i + 1))
        [[ -n $takes && $opt =~ ^($takes)$ ]] && i=$((i + 1))
      done
      if [ "$base" = timeout ] && [[ ${words[$i]} =~ ^[0-9] ]]; then i=$((i + 1)); fi
    elif [[ $lower =~ ^(npm|pnpm|yarn)$ ]]; then
      i=$((i + 1))
    else
      # npx @scope/pkg@ver, paths, and Windows extensions reduce to the name.
      name=${base%@*}; [ -z "$name" ] && name=$base
      name=${name%.exe}; name=${name%.cmd}; name=${name%.ps1}; name=${name%.bat}; name=${name%.js}
      if [[ $name =~ ^($HARNESSES)$ ]]; then found=$name; fi
      break
    fi
  done
  [ -n "$found" ] && break
done <<<"$segments"

[ -z "$found" ] && exit 0

reason="Trackline harness-guard: launching another coding agent harness ($found) from an agent session is blocked; it spends the user's paid quota for that tool. Do not retry or work around this. For /cross-review or /plan-review, tell the user to run the skill in a session of the other provider that they open themselves. If this command only mentions $found as text, rephrase it so the name does not start a command segment."
jq -n --arg reason "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}' 2>/dev/null ||
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
exit 0
