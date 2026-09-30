#!/usr/bin/env bash
# Compatibility entry point; automatic runtime selection is shared.
set -euo pipefail
exec bash "$(dirname "${BASH_SOURCE[0]}")/install-workflow.sh" "$@"
