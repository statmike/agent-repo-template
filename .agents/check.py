#!/usr/bin/env python3
"""Universal quality, guardrail self-test, and Current-State Doctrine gate.

Works identically in standalone Git repositories, monorepo cells, and plain
non-Git project folders. Run via: `uv run python .agents/check.py` (or `python3
.agents/check.py` for non-Python projects).
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = PROJECT_ROOT / ".agents" / "hooks"
TEMPLATE_README_MARKER = "ABOUT THIS TEMPLATE"
DOCTRINE_EXEMPT_MARKER = "doctrine-exempt"
SHIPPED_TARGETS = ("README.md", "docs", "src", "tests", "notebooks")
SCANNED_SUFFIXES = frozenset({".ipynb", ".md", ".py"})
IGNORED_DIR_NAMES = frozenset({"__pycache__", "node_modules"})
PYTEST_NO_TESTS_EXIT_CODE = 5

HISTORICAL_DOC_RE = re.compile(
    r"(?:\.agents/(?:idea|plan|decisions)\.md|\b(?:IDEA|DESIGN|DEV_NOTES)\.md\b)"
)


def load_hook_module(module_name: str, path: Path) -> ModuleType:
    """Load a hook script by file path without mutating sys.path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load hook module at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_harness_hooks() -> list[str]:
    """Run fast in-process self-tests against guard_uv.py and guard_secrets.py."""
    failures: list[str] = []
    guard_uv = load_hook_module("guard_uv", HOOKS_DIR / "guard_uv.py")
    guard_secrets = load_hook_module("guard_secrets", HOOKS_DIR / "guard_secrets.py")

    if (PROJECT_ROOT / "pyproject.toml").is_file():
        allowed_uv = (
            "uv sync",
            "uv run pytest",
            "uv pip list",
            'uv run python -c "import sys; print(sys.version)"',
            "uv export --no-hashes > requirements.txt",
        )
        for cmd in allowed_uv:
            if guard_uv.check_shell_command(cmd) is not None:
                failures.append(f"guard_uv unexpectedly blocked allowed command: {cmd}")

        blocked_uv = (
            "pip install httpx",
            ".venv/bin/pip install httpx",
            "uv pip list && pip install httpx",
            "env -u VIRTUAL_ENV pip install httpx",
            "sudo -E -u root pip install httpx",
            'echo "$(pip install httpx)"',
            "echo httpx > requirements.txt",
            "printf 'httpx\\n' | tee requirements-dev.txt",
            "python -m venv .venv",
            "pytest tests/",
            "python src/example.py",
        )
        for cmd in blocked_uv:
            if guard_uv.check_shell_command(cmd) is None:
                failures.append(f"guard_uv failed to block forbidden command: {cmd}")

        if guard_uv.check_file_target("__nonexistent_requirements_check__.txt") is None:
            pass  # Unmatched filename allowed
        if guard_uv.check_file_target("requirements-check-temp.txt") is None:
            failures.append("guard_uv failed to block creating requirements-check-temp.txt")

    sa_sample = json.dumps({"type": "service_" + "account", "private_key": "KEY_DATA"})
    if not guard_secrets.contains_sa_key_material(sa_sample):
        failures.append("guard_secrets failed to detect Service Account JSON key payload")

    allowed_sec = (
        "gcloud auth application-default login",
        "git add -A",
        "git add -f .env.template",
    )
    for cmd in allowed_sec:
        if guard_secrets.check_shell_secrets(cmd) is not None:
            failures.append(f"guard_secrets unexpectedly blocked allowed command: {cmd}")

    blocked_sec = (
        "gcloud auth activate-service-account --key-file=sa.json",
        "GOOGLE_APPLICATION_CREDENTIALS=sa.json uv run pytest",
        "git add -f .env",
        "git -C . add --force service-account-prod.json",
        "git add -Af",
    )
    for cmd in blocked_sec:
        if guard_secrets.check_shell_secrets(cmd) is None:
            failures.append(f"guard_secrets failed to block forbidden command: {cmd}")

    return failures


def iter_shipped_files(root: Path) -> list[Path]:
    """Collect shipped prose, code, and notebook files subject to doctrine checks."""
    files: list[Path] = []
    for rel_name in SHIPPED_TARGETS:
        target = root / rel_name
        if not target.exists():
            continue
        if target.is_file():
            if rel_name == "README.md":
                text = target.read_text(encoding="utf-8", errors="ignore")
                if TEMPLATE_README_MARKER in text:
                    continue
            files.append(target)
            continue
        for child in sorted(target.rglob("*")):
            if not child.is_file() or child.suffix not in SCANNED_SUFFIXES:
                continue
            parent_parts = child.relative_to(target).parts[:-1]
            if any(part.startswith(".") or part in IGNORED_DIR_NAMES for part in parent_parts):
                continue
            files.append(child)
    return files


def check_current_state_doctrine(root: Path) -> list[str]:
    """Verify shipped artifacts never reference historical planning/ADR files."""
    violations: list[str] = []
    for file_path in iter_shipped_files(root):
        rel_display = file_path.relative_to(root).as_posix()
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if DOCTRINE_EXEMPT_MARKER in line:
                continue
            match = HISTORICAL_DOC_RE.search(line)
            if match:
                violations.append(
                    f"{rel_display}:{line_number}: references '{match.group(0)}' "
                    f"(move historical rationale to .agents/decisions.md or .agents/status.md)"
                )
    return violations


def run_step(
    label: str, command: list[str], allow_exit_codes: frozenset[int] = frozenset({0})
) -> bool:
    """Execute a check command at PROJECT_ROOT and print a clear status banner."""
    print(f"==> {label}: {' '.join(command)}")
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if completed.returncode in allow_exit_codes:
        if completed.returncode == PYTEST_NO_TESTS_EXIT_CODE:
            print("    (no tests collected yet — skipping)")
        return True
    print(f"FAILED: {label} (exit {completed.returncode})", file=sys.stderr)
    return False


def has_python_files(directory: Path) -> bool:
    """Return True when directory exists and contains at least one .py file."""
    return directory.is_dir() and any(directory.rglob("*.py"))


def main() -> int:
    """Run all applicable hook self-tests, doctrine, lint, format, type, and test gates."""
    print("==> Harness guardrail self-test")
    hook_failures = check_harness_hooks()
    if hook_failures:
        for failure in hook_failures:
            print(f"  ERROR: {failure}", file=sys.stderr)
        return 1
    print("    OK: guard_uv.py and guard_secrets.py passed all self-checks.")

    print("==> Current-state doctrine check")
    violations = check_current_state_doctrine(PROJECT_ROOT)
    if violations:
        for violation in violations:
            print(f"  ERROR: {violation}", file=sys.stderr)
        return 1
    print("    OK: zero historical harness references in shipped artifacts.")

    if not (PROJECT_ROOT / "pyproject.toml").is_file():
        print("==> No pyproject.toml present — Python gates skipped.")
        return 0

    ok = True
    ok = run_step("Lint (ruff)", ["uv", "run", "ruff", "check", "."]) and ok
    ok = run_step("Format check (ruff)", ["uv", "run", "ruff", "format", "--check", "."]) and ok

    mypy_targets: list[str] = [".agents"]
    if has_python_files(PROJECT_ROOT / "src"):
        mypy_targets.insert(0, "src")
    ok = run_step("Type check (mypy)", ["uv", "run", "mypy", *mypy_targets]) and ok

    ok = (
        run_step(
            "Tests (pytest)",
            ["uv", "run", "pytest"],
            allow_exit_codes=frozenset({0, PYTEST_NO_TESTS_EXIT_CODE}),
        )
        and ok
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
