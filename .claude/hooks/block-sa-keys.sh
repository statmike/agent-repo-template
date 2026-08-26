#!/usr/bin/env bash
# PreToolUse guard — enforces CODE_STANDARDS §4: "Authentication (ADC Only)."
#
# This project authenticates to GCP via Application Default Credentials, never
# via Service Account JSON key files. This hook blocks two ways such keys sneak in:
#   1. Writing/editing a file whose content is a Service Account key
#      (JSON containing "type": "service_account" and a "private_key").
#   2. Bash commands that consume a key file (gcloud ... --key-file,
#      activate-service-account, or GOOGLE_APPLICATION_CREDENTIALS=...json).
#
# Contract: reads the PreToolUse payload as JSON on stdin; exits 2 (message on
# stderr) to block. Any other exit code allows the call. All detection is done in
# one Python pass to stay robust to command quoting and whitespace.

set -euo pipefail

payload="$(cat)"

# Python inspects the payload and prints "OK" or "DENY:<reason>".
result="$(printf '%s' "$payload" | python3 -c '
import sys, json, re
try:
    d = json.load(sys.stdin)
except Exception:
    print("OK"); sys.exit(0)

tool = d.get("tool_name", "")
ti = d.get("tool_input", {}) or {}
cmd = ti.get("command", "") or ""
blob = (ti.get("content", "") or "") + (ti.get("new_string", "") or "")
fp = ti.get("file_path", "") or ""

# 1. Writing Service Account key material to a file.
if tool in ("Write", "Edit") and "service_account" in blob and "private_key" in blob:
    print(f"DENY:attempt to write a Service Account JSON key file ({fp}).")
    sys.exit(0)

# 2. Bash commands that load a key file.
if tool == "Bash" and re.search(r"--key-file|activate-service-account|GOOGLE_APPLICATION_CREDENTIALS=", cmd):
    print("DENY:command references a Service Account key file.")
    sys.exit(0)

print("OK")
' 2>/dev/null || echo "OK")"

if [[ "$result" == DENY:* ]]; then
  echo "BLOCKED: ${result#DENY:}" >&2
  echo "This project is ADC-only (CODE_STANDARDS §4). Use 'gcloud auth application-default login' — never Service Account JSON keys." >&2
  exit 2
fi

exit 0
