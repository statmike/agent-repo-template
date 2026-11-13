#!/usr/bin/env python3
"""Polyglot PreToolUse guard blocking Service Account key files and secret staging.

Supports both Claude Code (.claude/settings.json) and Antigravity (.agents/hooks.json)
hook contracts. Enforces Application Default Credentials (ADC) instead of JSON key files
and prevents force-staging gitignored secret files.
"""

from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import PurePath
from typing import Any

KEY_COMMAND_RE = re.compile(
    r"--key-file\b|activate-service-account\b|GOOGLE_APPLICATION_CREDENTIALS\s*="
)
SEGMENT_SPLIT_RE = re.compile(r"(?:&&|\|\||[;\n|])")
SA_ACCOUNT_MARKER = "service_" + "account"
PRIVATE_KEY_MARKER = "private_" + "key"
GIT_VALUE_FLAGS = frozenset({"-C", "-c", "--git-dir", "--work-tree"})
SENSITIVE_GLOBS = (
    ".env",
    ".env.*",
    "*-key.json",
    "*_key.json",
    "service-account*.json",
    "*credentials*.json",
    "gcp-*.json",
    "*.pem",
    "*.key",
)


def contains_sa_key_material(text: str) -> bool:
    """Return True if text appears to contain GCP Service Account JSON key material."""
    return SA_ACCOUNT_MARKER in text and PRIVATE_KEY_MARKER in text


def is_forced_git_add_of_secrets(command: str) -> bool:
    """Return True when a command runs `git add -f/--force` on secrets or wildcards."""
    for segment in SEGMENT_SPLIT_RE.split(command):
        raw_tokens = re.findall(r"""(?:"[^"]*"|'[^']*'|[^\s"']+)+""", segment)
        tokens = [token.strip("'\"") for token in raw_tokens if token.strip("'\"")]
        if not tokens:
            continue
        index = 0
        while index < len(tokens) and "=" in tokens[index] and not tokens[index].startswith("-"):
            index += 1
        if index >= len(tokens) or PurePath(tokens[index]).name != "git":
            continue
        index += 1
        while index < len(tokens) and tokens[index].startswith("-"):
            flag = tokens[index]
            index += 1
            if flag in GIT_VALUE_FLAGS and index < len(tokens):
                index += 1
        if index >= len(tokens) or tokens[index] != "add":
            continue

        add_args = tokens[index + 1 :]
        has_force = False
        has_all_flag = False
        targets: list[str] = []
        for arg in add_args:
            if arg == "--force":
                has_force = True
            elif arg == "--all":
                has_all_flag = True
            elif arg.startswith("-") and not arg.startswith("--"):
                if "f" in arg[1:]:
                    has_force = True
                if "A" in arg[1:] or "a" in arg[1:]:
                    has_all_flag = True
            elif not arg.startswith("-"):
                targets.append(arg)

        if not has_force:
            continue
        if has_all_flag or any(target in (".", "*", "./") for target in targets):
            return True
        for target in targets:
            basename = PurePath(target).name
            if (
                basename != ".env.template"
                and basename != ".env.example"
                and any(
                    fnmatch.fnmatch(basename.lower(), pattern.lower())
                    for pattern in SENSITIVE_GLOBS
                )
            ):
                return True
    return False


def check_shell_secrets(command: str) -> str | None:
    """Return a block reason if command loads SA keys or force-adds secret files."""
    if KEY_COMMAND_RE.search(command):
        return (
            "Commands referencing Service Account key files or setting "
            "GOOGLE_APPLICATION_CREDENTIALS are blocked. Use Application Default "
            "Credentials ('gcloud auth application-default login')."
        )
    if is_forced_git_add_of_secrets(command):
        return (
            "Forced 'git add' ('-f' / '--force') on '.env', credential files, or "
            "wildcard paths is blocked so gitignored secrets are never staged."
        )
    return None


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
    if kind == "shell":
        reason = check_shell_secrets(command)
    elif kind == "file" and contains_sa_key_material(written_text):
        reason = (
            f"Writing a GCP Service Account JSON key file ({file_path}) is blocked. "
            "Authenticate via Application Default Credentials ('gcloud auth "
            "application-default login')."
        )
    return respond(is_antigravity, reason)


if __name__ == "__main__":
    raise SystemExit(main())
