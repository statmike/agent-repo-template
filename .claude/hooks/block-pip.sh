#!/usr/bin/env bash
# PreToolUse (Bash) guard — enforces Golden Rule #4: "uv is the Law."
#
# Blocks direct pip usage (pip, pip3, python -m pip) because this project manages
# all dependencies and environments with uv. `uv pip ...` is explicitly allowed,
# since that is uv's own pip-compatible interface.
#
# Contract: reads the PreToolUse payload as JSON on stdin, inspects
# tool_input.command, and exits 2 (with a message on stderr) to block the call.
# Any other exit code allows it.

set -euo pipefail

payload="$(cat)"

# Extract the command string from the JSON payload (python3 is guaranteed on a uv project).
command="$(printf '%s' "$payload" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null || true)"

# Nothing to inspect — allow.
[ -z "$command" ] && exit 0

# Does the command invoke pip directly (pip, pip3, pipX.Y, or python[3] -m pip)?
if printf '%s' "$command" | grep -Eq '(^|[;&|`(]|[[:space:]])(pip[0-9.]*|python[0-9.]*[[:space:]]+-m[[:space:]]+pip)([[:space:]]|$)'; then
  # ...but allow uv's own pip interface (uv pip ...).
  if printf '%s' "$command" | grep -Eq '(^|[;&|`(]|[[:space:]])uv[[:space:]]+pip'; then
    exit 0
  fi
  echo "BLOCKED: direct pip use is not allowed in this project (Golden Rule #4: 'uv is the Law')." >&2
  echo "Use uv instead — e.g. 'uv add <pkg>', 'uv sync', 'uv run ...', or 'uv pip ...'." >&2
  exit 2
fi

exit 0
