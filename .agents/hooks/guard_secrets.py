#!/usr/bin/env python3
"""Polyglot PreToolUse guard blocking Service Account key files and flags.

Supports both Claude Code (.claude/settings.json) and Antigravity (.agents/hooks.json)
hook contracts. Enforces Application Default Credentials (ADC) instead of JSON key files.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

KEY_COMMAND_RE = re.compile(
    r"--key-file\b|activate-service-account\b|GOOGLE_APPLICATION_CREDENTIALS\s*="
)
SA_ACCOUNT_MARKER = "service_" + "account"
PRIVATE_KEY_MARKER = "private_" + "key"


def contains_sa_key_material(text: str) -> bool:
    """Return True if text appears to contain GCP Service Account JSON key material."""
    return SA_ACCOUNT_MARKER in text and PRIVATE_KEY_MARKER in text


def extract_invocation(payload: dict[str, Any]) -> tuple[bool, str, str, str, str]:
    """Return (is_antigravity, kind, command, file_path, written_text)."""
    if "toolCall" in payload:
        tool_call = payload.get("toolCall") or {}
        name = str(tool_call.get("name", ""))
        args = tool_call.get("args") or {}
        if name == "run_command":
            return True, "shell", str(args.get("CommandLine", "")), "", ""
        file_path = str(args.get("Path") or args.get("TargetFile") or "")
        chunks = [
            str(args.get("Content") or ""),
            str(args.get("Replacement") or ""),
            str(args.get("ReplacementContent") or ""),
            str(args.get("CodeContent") or ""),
        ]
        for chunk in args.get("ReplacementChunks") or []:
            if isinstance(chunk, dict):
                chunks.append(str(chunk.get("ReplacementContent") or ""))
        return True, "file", "", file_path, "\n".join(chunks)

    name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    if name == "Bash":
        return False, "shell", str(tool_input.get("command", "")), "", ""
    file_path = str(tool_input.get("file_path", ""))
    chunks = [
        str(tool_input.get("content") or ""),
        str(tool_input.get("new_string") or ""),
    ]
    for edit in tool_input.get("edits") or []:
        if isinstance(edit, dict):
            chunks.append(str(edit.get("new_string") or ""))
    return False, "file", "", file_path, "\n".join(chunks)


def respond(is_antigravity: bool, deny_reason: str | None) -> int:
    """Emit the protocol-appropriate allow/deny response and return exit code."""
    if is_antigravity:
        if deny_reason:
            print(json.dumps({"decision": "deny", "reason": deny_reason}))
        else:
            print('{"decision": "allow"}')
        return 0
    if deny_reason:
        print(f"BLOCKED: {deny_reason}", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    """Entry point for PreToolUse credential hygiene enforcement."""
    raw_stdin = sys.stdin.read()
    if not raw_stdin.strip():
        return 0
    try:
        payload = json.loads(raw_stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0

    is_antigravity, kind, command, file_path, written_text = extract_invocation(payload)
    reason: str | None = None
    if kind == "shell" and KEY_COMMAND_RE.search(command):
        reason = (
            "Commands referencing Service Account key files or setting "
            "GOOGLE_APPLICATION_CREDENTIALS are blocked. Use Application Default "
            "Credentials ('gcloud auth application-default login')."
        )
    elif kind == "file" and contains_sa_key_material(written_text):
        reason = (
            f"Writing a GCP Service Account JSON key file ({file_path}) is blocked. "
            "Authenticate via Application Default Credentials ('gcloud auth "
            "application-default login')."
        )
    return respond(is_antigravity, reason)


if __name__ == "__main__":
    raise SystemExit(main())
