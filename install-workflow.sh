#!/usr/bin/env bash
set -euo pipefail
installer_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo 'error: python3 is required by the installer.' >&2; exit 1; }
exec python3 "$installer_dir/hooks/install-workflow.py" --installer-dir "$installer_dir" "$@"
