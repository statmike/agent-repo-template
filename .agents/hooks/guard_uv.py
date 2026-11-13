#!/usr/bin/env python3
"""Polyglot PreToolUse guard enforcing uv for Python environments and packages.

Supports both Claude Code (.claude/settings.json) and Antigravity (.agents/hooks.json)
stdin/stdout hook contracts from a single stdlib-only script. Automatically acts
as a no-op when no pyproject.toml exists at the project root.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_UV_BINARIES = frozenset({"uv", "uvx"})
BANNED_ENV_MANAGERS = frozenset(
    {"conda", "mamba", "micromamba", "pdm", "pipenv", "poetry", "virtualenv"}
)
BANNED_PYTHON_MODULES = frozenset({"ensurepip", "pip", "venv", "virtualenv"})
PROJECT_RUNNER_TOOLS = frozenset({"jupyter", "mypy", "pytest", "ruff"})
COMMAND_WRAPPERS = frozenset({"command", "env", "nohup", "sudo", "time"})
WRAPPER_VALUE_FLAGS = frozenset({"-C", "-S", "-g", "-u"})
BANNED_MANIFEST_NAMES = frozenset(
    {
        "conda.yaml",
        "conda.yml",
        "environment.yaml",
        "environment.yml",
        "pipfile",
        "pipfile.lock",
        "poetry.lock",
        "requirements.txt",
    }
)
PIP_BINARY_RE = re.compile(r"^pip(?:\d+(?:\.\d+)*)?$")
PYTHON_BINARY_RE = re.compile(r"^python(?:\d+(?:\.\d+)*)?$")
ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
REQUIREMENTS_FILE_RE = re.compile(r"^requirements[-_].+\.(?:txt|in)$")
SHELL_REDIRECT_RE = re.compile(r"(?:>>?|[12]>)\s*([^\s;|&]+)")


def split_shell_segments(command: str) -> list[str]:
    """Split a shell command string on control operators and active subshells."""
    segments: list[str] = []
    current: list[str] = []
    quote_char: str | None = None
    escaped = False
    index = 0
    length = len(command)

    while index < length:
        char = command[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\" and quote_char != "'":
            current.append(char)
            escaped = True
            index += 1
            continue
        if quote_char == "'":
            if char == "'":
                quote_char = None
            current.append(char)
            index += 1
            continue
        if quote_char == '"':
            if char == '"':
                quote_char = None
                current.append(char)
                index += 1
                continue
            if char == "`":
                segments.append("".join(current).strip())
                current = []
                index += 1
                continue
            if char == "$" and index + 1 < length and command[index + 1] == "(":
                segments.append("".join(current).strip())
                current = []
                index += 2
                continue
            current.append(char)
            index += 1
            continue
        if char in ("'", '"'):
            quote_char = char
            current.append(char)
            index += 1
            continue
        if char == "$" and index + 1 < length and command[index + 1] == "(":
            segments.append("".join(current).strip())
            current = []
            index += 2
            continue
        if char in (";", "\n", "|", "(", ")", "`"):
            segments.append("".join(current).strip())
            current = []
            index += 1
            continue
        if char == "&":
            step = 2 if (index + 1 < length and command[index + 1] == "&") else 1
            segments.append("".join(current).strip())
            current = []
            index += step
            continue
        current.append(char)
        index += 1

    tail = "".join(current).strip()
    if tail:
        segments.append(tail)
    return [segment for segment in segments if segment]


def tokenize_segment(segment: str) -> list[str]:
    """Tokenize a single shell segment while stripping env assignments and wrappers."""
    raw_tokens = re.findall(r"""(?:"[^"]*"|'[^']*'|[^\s"']+)+""", segment)
    tokens = [token.strip("'\"") for token in raw_tokens if token.strip("'\"")]
    while tokens:
        head = tokens[0]
        if ENV_ASSIGNMENT_RE.match(head):
            tokens.pop(0)
            continue
        if head in COMMAND_WRAPPERS:
            tokens.pop(0)
            while tokens and tokens[0].startswith("-"):
                flag = tokens.pop(0)
                if flag == "--":
                    break
                if flag in WRAPPER_VALUE_FLAGS and tokens:
                    tokens.pop(0)
            continue
        break
    return tokens


def is_external_script_target(arguments: list[str]) -> bool:
    """Return True when python invokes an absolute or home script outside root."""
    index = 0
    while index < len(arguments):
        arg = arguments[index]
        if arg in ("-c", "-m"):
            return False
        if arg in ("-W", "-X") and index + 1 < len(arguments):
            index += 2
            continue
        if arg.startswith("-"):
            index += 1
            continue
        expanded = Path(arg).expanduser()
        resolved = (
            expanded.resolve() if expanded.is_absolute() else (PROJECT_ROOT / expanded).resolve()
        )
        return not resolved.is_relative_to(PROJECT_ROOT)
    return False


def check_file_target(file_path_str: str) -> str | None:
    """Block creating legacy dependency manifests inside a uv project."""
    if not file_path_str:
        return None
    candidate = Path(file_path_str).expanduser()
    resolved = (
        candidate.resolve() if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()
    )
    if not resolved.is_relative_to(PROJECT_ROOT) or resolved.exists():
        return None
    lower_name = resolved.name.lower()
    if lower_name in BANNED_MANIFEST_NAMES or REQUIREMENTS_FILE_RE.match(lower_name):
        return (
            f"Creating '{resolved.name}' is blocked ('uv is the Law'). "
            "Declare dependencies in pyproject.toml via 'uv add <pkg>'."
        )
    return None


def check_segment_redirects(segment: str, tokens: list[str]) -> str | None:
    """Block shell redirection or tee writes that create banned manifest files."""
    for match in SHELL_REDIRECT_RE.finditer(segment):
        target = match.group(1).strip("'\"")
        reason = check_file_target(target)
        if reason:
            return reason
    if tokens and PurePath(tokens[0]).name.lower() == "tee":
        for arg in tokens[1:]:
            if not arg.startswith("-"):
                reason = check_file_target(arg)
                if reason:
                    return reason
    return None


def check_shell_command(command: str) -> str | None:
    """Inspect a shell command and return a block reason, or None if allowed."""
    for segment in split_shell_segments(command):
        tokens = tokenize_segment(segment)
        if not tokens:
            continue
        binary_name = PurePath(tokens[0]).name.lower()
        if binary_name in ALLOWED_UV_BINARIES:
            continue
        redirect_reason = check_segment_redirects(segment, tokens)
        if redirect_reason:
            return redirect_reason
        if PIP_BINARY_RE.match(binary_name):
            return (
                "Direct pip usage is blocked ('uv is the Law'). "
                "Use 'uv add <pkg>', 'uv sync', 'uv run ...', or 'uv pip ...'."
            )
        if binary_name in BANNED_ENV_MANAGERS:
            return (
                f"'{binary_name}' is blocked in this project. "
                "Manage environments and dependencies exclusively with 'uv'."
            )
        if binary_name in PROJECT_RUNNER_TOOLS:
            return (
                f"Run '{binary_name}' inside the project environment via "
                f"'uv run {binary_name} ...' instead of invoking '{binary_name}' directly."
            )
        if PYTHON_BINARY_RE.match(binary_name):
            rest = tokens[1:]
            for idx, arg in enumerate(rest):
                if arg == "-m" and idx + 1 < len(rest):
                    module_name = rest[idx + 1].lower()
                    if module_name in BANNED_PYTHON_MODULES:
                        return (
                            f"'python -m {module_name}' is blocked ('uv is the Law'). "
                            "Use 'uv add <pkg>', 'uv sync', or 'uv pip ...'."
                        )
            if is_external_script_target(rest):
                continue
            return (
                "Bare 'python' invocations are blocked in uv projects so commands "
                "never hit the wrong interpreter. Use 'uv run python ...'."
            )
    return None


def extract_invocation(payload: dict[str, Any]) -> tuple[bool, str, str, str]:
    """Return (is_antigravity_protocol, kind, command, file_path)."""
    if "toolCall" in payload:
        tool_call = payload.get("toolCall") or {}
        name = str(tool_call.get("name", ""))
        args = tool_call.get("args") or {}
        if name == "run_command":
            return True, "shell", str(args.get("CommandLine", "")), ""
        file_path = str(args.get("Path") or args.get("TargetFile") or "")
        return True, "file", "", file_path

    name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    if name == "Bash":
        return False, "shell", str(tool_input.get("command", "")), ""
    return False, "file", "", str(tool_input.get("file_path", ""))


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
    """Entry point for PreToolUse uv enforcement."""
    raw_stdin = sys.stdin.read()
    if not raw_stdin.strip():
        return 0
    try:
        payload = json.loads(raw_stdin)
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0

    is_antigravity, kind, command, file_path = extract_invocation(payload)
    if not (PROJECT_ROOT / "pyproject.toml").is_file():
        return respond(is_antigravity, None)

    reason = check_shell_command(command) if kind == "shell" else check_file_target(file_path)
    return respond(is_antigravity, reason)


if __name__ == "__main__":
    raise SystemExit(main())
