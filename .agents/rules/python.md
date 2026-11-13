---
trigger: always_on
description: "Python architecture, naming, folder layout, unit testing, uv management, and code evolution standards."
---

# Python, Testing & Code Management Standards

Applies whenever this project includes Python code (`pyproject.toml` / `src/`). Remove this file if bootstrapping a pure non-Python project.

## 1. Well-Structured Folders & Simple Naming

* **Predictable Top-Level Layout:**
  * `src/` — all reusable code, transformations, models, and client modules.
  * `tests/` — automated `pytest` suite mirroring `src/` (`src/features.py` -> `tests/test_features.py`).
  * `notebooks/` — optional numbered narrative runners (`01_explore.ipynb`, `02_evaluate.ipynb`).
  * `docs/` — deeper architecture or user documentation beyond `README.md`.
  * `data/`, `artifacts/`, `outputs/` — local-only datasets, model weights, and scratch outputs (gitignored at root; never commit raw data dumps or fitted binaries).
* **One Capability Per File:** Name each module after the single capability or pipeline stage it owns (`ingest.py`, `clean.py`, `features.py`, `train.py`, `evaluate.py`) — never vague buckets (`manager.py`, `handler.py`, `processor.py`, `utils.py`, `helpers.py`, `common.py`).
* **Plain, Descriptive Identifiers:** Use clear verbs for functions (`load_records`, `score_predictions`) and full domain nouns for variables (`horizon_days`, `validation_rows`, `feature_columns`). Avoid cryptic single-letter names (`X2`, `df2`) or vowel-stripped abbreviations (`trn_cfg`, `val_res`).
* **Never Shadow Python Stdlib Names:** With `pythonpath = ["src"]`, never name bare files in `src/` after standard library modules (`io.py`, `types.py`, `logging.py`, `statistics.py`, `math.py`, `code.py`). When packaging an installable library or when `src/` outgrows ~8–10 flat files, group modules into a single flat package `src/<project_name>/` (still one level deep — never nested `src/pkg/core/services/`).

## 2. Flat, Human-Scannable Code Design

* **30-Second Legibility:** A human must be able to read any module top-to-bottom and understand its job in under 30 seconds.
* **Functions + Simple Data Structures Over Deep OOP:** Never build abstract inheritance hierarchies (`AbstractBaseRunner`). Prefer flat functions operating on standard types or `dataclass` configs.
* **One Hop Maximum & One-Way Dependencies:** Reading `a.py` must never require chasing `a.py` -> `b.py` -> `c.py`. Leaf modules (I/O, storage, clients) never import orchestration modules; calls flow down, data flows back up. Zero circular imports.
* **Separate I/O From Pure Logic:** Keep external reads/writes (files, tables, APIs) at thin module boundaries, and write transformations, feature logic, modeling, and evaluation as pure **data-in -> data-out** functions.
* **Explicit Parameters & Reproducibility:** Surface thresholds, hyperparameters, random seeds, and paths as explicit arguments, module-level constants, or a flat `dataclass` — never bury magic numbers (`0.8`, `42`, `1e-4`), hidden global state, or hardcoded machine paths inside functions.
* **Modern Type Annotations:** Annotate every function parameter and return type using modern syntax (`X | None`, built-in `list`/`dict`/`tuple`/`frozenset`, `collections.abc`). Reserve `typing.Any` strictly for untyped third-party boundaries.

## 3. Unit Testing Standards (`pytest`)

* **Test Behavior on Small Synthetic Inputs:** Import the capability from `src/`, pass tiny deterministic in-memory inputs (a handful of rows, fixed seeds, plus boundary cases like empty inputs, nulls, zeros, and shape mismatches), and assert concrete outputs and invariants.
* **Never Re-Implement Logic or Over-Mock:** Tests verify `src/`, never duplicate its formulas. Mock only external boundaries (network, cloud SDKs, clocks); never mock your own pure functions. Use `tmp_path` for local file I/O tests.
* **Flat Test Functions:** Write plain `def test_<capability>_<scenario>():` functions rather than `unittest.TestCase` classes or deep `conftest.py` fixture chains.
* **Fast Offline Default vs. `@pytest.mark.integration`:** Bare `uv run pytest` must run fast and offline without credentials. Mark live external/cloud smoke tests with `@pytest.mark.integration` and skip them automatically when unauthenticated in CI.

## 4. Managing Code Over Time & `uv` Hygiene

* **Evolve In Place (Zero `_v2` Clones):** Modify modules and functions directly in place — never leave `features_v2.py`, `train_new.py`, or `evaluate_old()` alongside superseded code. Git and `.agents/decisions.md` hold history.
* **`uv` Exclusively:** Manage Python, virtual environments, dependencies (`pyproject.toml` + `uv.lock`), and tool execution (`uv run pytest`, `uv run ruff`, `uv run mypy`, `uv run python ...`) exclusively through `uv`. Never invoke `pip`, `venv`, `conda`, or `poetry`, and never generate `requirements.txt` unless an external legacy target requires `uv export`. *(Enforced by `.agents/hooks/guard_uv.py`.)*
* **Current-State Hygiene:** Delete commented-out code (`ERA001`), never leave `TODO`/`FIXME`/`XXX`/`HACK` comments in code (`FIX` — track in `.agents/status.md`), avoid change-narration comments (log in `.agents/decisions.md`), remove unused arguments/imports (`ARG`, `F401`), and never reference `.agents/idea.md`, `.agents/plan.md`, or `.agents/decisions.md` from shipped files. *(Enforced by `.agents/check.py`.)*
