#!/usr/bin/env bash
set -euo pipefail

# install-workflow.sh — wire the my-workflow shared workflow into a project.
#
# Idempotent and re-runnable: run it again any time to reconcile a project to
# the current canonical state (repairs drifted or broken links). The workflow
# repository is the single source of truth; a project holds only symlinks plus
# the minimum tool-specific registration each tool requires.
#
# Layout it produces in <project>:
#   AGENTS.md                     -> <workflow>/AGENTS.md      (absolute)
#   CLAUDE.md                     -> AGENTS.md                 (relative)
#   .agents/skills/<s>            -> <workflow>/skills/<s>     (absolute; canonical)
#   .claude/skills/<s>            -> ../../.agents/skills/<s>  (relative; funnels)
#   .codex/skills/<s>             -> ../../.agents/skills/<s>  (relative; funnels)
#   .agents/hooks/context-zone.sh -> <workflow>/hooks/context-zone.sh
#   .codex/hooks.json             -> <workflow>/hooks/codex.hooks.json
#   .claude/settings.json          : Stop hook appended (existing hooks/keys preserved)
#
# Both tools run the SAME hook script via the SAME command string:
#   bash "$(git rev-parse --show-toplevel)/.agents/hooks/context-zone.sh"

WORKFLOW="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# My skills — always installed into a project.
SKILLS=(cross-review doc-update next-slice plan-review planning-capture review-triage session-close session-open)
# Third-party skills — live in user scope by default; not installed per-project
# unless --with-external is given.
EXTERNAL_SKILLS=(grill-me grill-with-docs handoff)
# Tool skill directories that funnel through .agents/skills.
FUNNEL_DIRS=(.claude/skills .codex/skills)
# Docs subdirectories to scaffold (created if missing; content files are left
# to the workflow — activeContext.md is auto-created by /session-close, and
# roadmap.md is seeded by you).
DOCS_DIRS=(requirements design adr reviews research archive)

HOOK_CMD='bash "$(git rev-parse --show-toplevel)/.agents/hooks/context-zone.sh"'

usage() {
  cat <<EOF
Usage: install-workflow.sh [OPTIONS] [project-dir]

Wire the my-workflow workflow into a project via symlinks (idempotent).

  project-dir         Target project root (default: current directory)

Options:
  -n, --dry-run       Show what would change; make no changes
  -f, --force         Replace links/files that point somewhere else
      --with-external Also install the third-party skills (${EXTERNAL_SKILLS[*]})
                      per-project instead of relying on user scope
  -h, --help          Show this help
EOF
}

DRY_RUN=false
FORCE=false
WITH_EXTERNAL=false
TARGET=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--dry-run)    DRY_RUN=true; shift ;;
    -f|--force)      FORCE=true; shift ;;
    --with-external) WITH_EXTERNAL=true; shift ;;
    -h|--help)       usage; exit 0 ;;
    -*)              echo "Unknown option: $1" >&2; usage; exit 1 ;;
    *)               TARGET=$1; shift ;;
  esac
done

TARGET=$(realpath "${TARGET:-.}")
[[ -d "$TARGET" ]] || { echo "error: '$TARGET' is not a directory." >&2; exit 1; }

if [[ ! -d "$TARGET/.git" ]]; then
  printf "warning: '%s' is not a git repo root (the hook uses git rev-parse). Continue? [y/N] " "$TARGET" >&2
  read -r reply
  [[ "$reply" =~ ^[Yy]$ ]] || exit 1
fi

$DRY_RUN && echo "(dry run — no changes will be made)"
echo "Workflow: $WORKFLOW"
echo "Target:   $TARGET"
echo ""

created=0 updated=0 skipped=0 conflict=0
# Items the workflow wanted to write but skipped because something else is
# already there and doesn't match. Collected and reported verbatim at the end
# so nothing has to be hunted for in the log. Nothing here is ever overwritten.
ATTENTION=()

# link <target-of-link> <link-path> : ensure <link-path> is a symlink to <target>.
link() {
  local src=$1 dst=$2 rel
  rel=${dst#"$TARGET"/}
  if [[ -L "$dst" ]]; then
    local cur; cur=$(readlink "$dst")
    if [[ "$cur" == "$src" ]]; then
      printf "  ok      %s\n" "$rel"; ((skipped++)) || true; return
    fi
    if $FORCE; then
      $DRY_RUN || { rm -f "$dst"; ln -s "$src" "$dst"; }
      printf "  repair  %s -> %s (was %s)\n" "$rel" "$src" "$cur"; ((updated++)) || true; return
    fi
    printf "  DIFFER  %s -> %s (want %s; use --force)\n" "$rel" "$cur" "$src"; ((conflict++)) || true
    ATTENTION+=("DIFFER  $rel — symlink points to '$cur'; workflow wants '$src' (kept yours; --force to repair)"); return
  fi
  if [[ -e "$dst" ]]; then
    printf "  EXISTS  %s (real file/dir, not touched)\n" "$rel"; ((conflict++)) || true
    ATTENTION+=("EXISTS  $rel — real file/dir already here; workflow wanted a symlink to '$src' (kept yours)"); return
  fi
  $DRY_RUN || { mkdir -p "$(dirname "$dst")"; ln -s "$src" "$dst"; }
  printf "  create  %s -> %s\n" "$rel" "$src"; ((created++)) || true
}

install_skill() {
  local s=$1 d
  link "$WORKFLOW/skills/$s" "$TARGET/.agents/skills/$s"
  for d in "${FUNNEL_DIRS[@]}"; do
    link "../../.agents/skills/$s" "$TARGET/$d/$s"
  done
}

echo "Project files:"
link "$WORKFLOW/AGENTS.md" "$TARGET/AGENTS.md"
link "AGENTS.md"           "$TARGET/CLAUDE.md"

echo ""
echo "Skills (mine):"
for s in "${SKILLS[@]}"; do install_skill "$s"; done

echo ""
echo "Skills (third-party):"
for s in "${EXTERNAL_SKILLS[@]}"; do
  if $WITH_EXTERNAL; then
    install_skill "$s"
  elif [[ -e "$HOME/.agents/skills/$s" ]]; then
    printf "  user    %s — available via user scope (~/.agents/skills), skipping project install\n" "$s"
    ((skipped++)) || true
  else
    printf "  omit    %s — not installed (pass --with-external to pin it per-project)\n" "$s"
  fi
done

echo ""
echo "Hooks:"
link "$WORKFLOW/hooks/context-zone.sh"  "$TARGET/.agents/hooks/context-zone.sh"
link "$WORKFLOW/hooks/codex.hooks.json" "$TARGET/.codex/hooks.json"

# Prune legacy artifacts from the old two-script layout (per-tool hook script).
if [[ -L "$TARGET/.codex/hooks/context-zone.sh" ]]; then
  $DRY_RUN || rm -f "$TARGET/.codex/hooks/context-zone.sh"
  printf "  prune   .codex/hooks/context-zone.sh (legacy)\n"; ((updated++)) || true
  $DRY_RUN || rmdir "$TARGET/.codex/hooks" 2>/dev/null || true
fi

# Claude Stop hook: add ours without clobbering existing hooks. We append our
# entry to .hooks.Stop rather than replacing it, so any Stop hooks the project
# already defined are preserved. Re-running is a no-op once ours is present.
settings="$TARGET/.claude/settings.json"
if ! command -v jq >/dev/null 2>&1; then
  printf "  WARN    .claude/settings.json — jq not found; add the Stop hook manually (see hooks/settings.snippet.json)\n"
  ((conflict++)) || true
  ATTENTION+=("WARN    .claude/settings.json — jq not found; Stop hook NOT added (add manually from hooks/settings.snippet.json)")
else
  entry_json="$(jq -cn --arg cmd "$HOOK_CMD" '{hooks:[{type:"command",command:$cmd}]}')"
  mkdir -p "$TARGET/.claude"
  if [[ -f "$settings" ]]; then
    if jq -e --arg cmd "$HOOK_CMD" 'any(.hooks.Stop[]?.hooks[]?; .command == $cmd)' "$settings" >/dev/null; then
      printf "  ok      .claude/settings.json (Stop hook present)\n"; ((skipped++)) || true
    else
      had=$(jq -r '(.hooks.Stop // []) | length' "$settings")
      $DRY_RUN || { tmp=$(mktemp); jq --argjson entry "$entry_json" '.hooks.Stop = ((.hooks.Stop // []) + [$entry])' "$settings" > "$tmp" && mv "$tmp" "$settings"; }
      if [[ "$had" == "0" ]]; then
        printf "  add     .claude/settings.json (set Stop hook)\n"
      else
        printf "  merge   .claude/settings.json (appended Stop hook; existing preserved)\n"
      fi
      ((updated++)) || true
    fi
  else
    $DRY_RUN || jq -n --argjson entry "$entry_json" '{hooks:{Stop:[$entry]}}' > "$settings"
    printf "  create  .claude/settings.json (with Stop hook)\n"; ((created++)) || true
  fi
fi

echo ""
echo "Docs structure:"
for d in "${DOCS_DIRS[@]}"; do
  dir="$TARGET/docs/$d"
  if [[ -d "$dir" ]]; then
    printf "  ok      docs/%s\n" "$d"; ((skipped++)) || true
  else
    $DRY_RUN || mkdir -p "$dir"
    printf "  create  docs/%s/\n" "$d"; ((created++)) || true
  fi
done

echo ""
echo "Done: $created created, $updated updated, $skipped ok/skipped, $conflict need attention."
if [[ ${#ATTENTION[@]} -gt 0 ]]; then
  echo ""
  echo "Needs attention — present already and left untouched (nothing above was overwritten):"
  for a in "${ATTENTION[@]}"; do
    printf "  - %s\n" "$a"
  done
  echo ""
  echo "Reconcile each by hand, or re-run with --force to repair the DIFFER symlinks"
  echo "(--force still never touches real files marked EXISTS)."
fi
