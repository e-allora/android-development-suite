#!/usr/bin/env bash
# harness.sh — thin shell wrapper around harness.py.
# Lets you run `harness <cmd>` from anywhere with the project root auto-detected.

set -euo pipefail
SUITE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "${SUITE_ROOT}/harness/harness.py" "$@"
