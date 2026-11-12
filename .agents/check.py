#!/usr/bin/env python3
"""Universal quality and Current-State Doctrine gate for local runs and CI.

Works identically in standalone Git repositories, monorepo cells, and plain
non-Git project folders. Run via: `uv run python .agents/check.py` (or `python3
.agents/check.py` for non-Python projects).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_README_MARKER = "ABOUT THIS TEMPLATE"
DOCTRINE_EXEMPT_MARKER = "doctrine-exempt"
SHIPPED_TARGETS = ("README.md", "docs", "src", "tests", "notebooks")
SCANNED_SUFFIXES = frozenset({".ipynb", ".md", ".py"})
PYTEST_NO_TESTS_EXIT_CODE = 5

HISTORICAL_DOC_RE = re.compile(
    r"(?:\.agents/(?:idea|plan|decisions)\.md|\b(?:IDEA|DESIGN|DEV_NOTES)\.md\b)"
)


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
            if child.is_file() and child.suffix in SCANNED_SUFFIXES:
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
    """Run all applicable doctrine, lint, format, type, and unit test gates."""
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
