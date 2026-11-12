---
trigger: always_on
description: "Core Python architecture, uv dependency management, strict typing, and current-state code hygiene standards."
---

# Python & `uv` Engineering Standards

Applies whenever this project includes Python code (`pyproject.toml` / `src/`). Remove this file if bootstrapping a pure non-Python project.

## 1. Flat, Human-Scannable Architecture

* **Single Responsibility:** Each `.py` module in `src/` owns one clear capability (for example `bq_client.py`, `data_cleaner.py`).
* **Avoid Deep OOP:** Do not build abstract class hierarchies (`AbstractBaseProcessor`). Prefer flat functions with simple data structures (`dataclass`, typed dicts, tuples).
* **30-Second Legibility:** A human reader must be able to scan any module top-to-bottom and understand its responsibility in under 30 seconds.
* **One Hop Maximum:** Understanding `a.py` must never require chasing `a.py` -> `b.py` -> `c.py`. Collapse deep internal chains.
* **Fewer, Fuller Modules:** Cohesion beats fragmentation. Split a module only for a genuinely distinct responsibility, never merely to shrink line count.
* **One-Way Dependencies:** Zero circular imports. Leaf modules (clients, I/O) never import orchestration modules; calls flow down, data flows back up.
* **No Grab-Bags:** Never create `utils.py`, `helpers.py`, or `common.py`. Small local duplication beats a web of shared helpers.
* **Strict Type Annotations:** Annotate every function signature using modern Python syntax (`X | None`, built-in `list`/`dict`/`tuple`/`frozenset`, `collections.abc`).

## 2. Dependency & Environment Management (`uv` Only)

* **`uv` Is the Law:** Manage Python interpreters, virtual environments, dependencies, and execution exclusively with `uv` (`uv sync`, `uv add`, `uv lock`, `uv run`).
* **Never Invoke Rival Managers or Bare Runners:** Never run `pip`, `python -m venv`, `virtualenv`, `conda`, or `poetry`, and always execute project tools via `uv run` (`uv run pytest`, `uv run ruff`, `uv run mypy`, `uv run python ...`). *(Enforced by `.agents/hooks/guard_uv.py`.)*
* **Manifest Hygiene:** Declare dependencies in `pyproject.toml` (with public PyPI pinned as the default index) and keep `uv.lock` synchronized. Never generate `requirements.txt` unless an external legacy target explicitly requires `uv export`.

## 3. Current-State Code Hygiene

* **No Commented-Out Code:** Delete dead code blocks rather than commenting them out. *(Enforced: ruff `ERA001`.)*
* **No Inline Backlog:** Never leave `TODO`, `FIXME`, `XXX`, or `HACK` comments in code. Track remaining work in `.agents/status.md` under *Now* or *Next*. *(Enforced: ruff `FIX`.)*
* **No Change-Narration Comments:** Comments explain present behavior and invariants, never historical evolution ("switched from X"). Log historical rationale in `.agents/decisions.md`.
* **No Orphans or Plan References:** Remove unused arguments, imports, and abandoned flags (`ARG`, `F401`), and never reference `.agents/idea.md`, `.agents/plan.md`, or `.agents/decisions.md` from shipped code or docs. *(Enforced by `.agents/check.py`.)*
