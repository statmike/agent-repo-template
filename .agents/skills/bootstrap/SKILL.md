---
name: bootstrap
description: >-
  Initializes a newly cloned or copied project from the agent-repo-template harness.
  Use when setting up a brand-new repository, monorepo cell, or standalone non-Git
  folder from the template to configure workspace mode, project metadata, optional
  domain rules (GCP, notebooks, Python), and verify a clean baseline.
---

# Bootstrap Project From Harness Template

Run this workflow once when starting a new project from `agent-repo-template`.

## Step 1: Confirm Workspace Mode & Stack

If the human has not already specified them, ask concisely:

1. **Workspace mode:**
   * **A · Standalone Git repository** (everything tracked; GitHub Actions CI active)
   * **B · Monorepo cell — harness untracked** (local-only `.agents/` + `.claude/`; only project code & `README.md` committed)
   * **C · Monorepo cell — harness tracked** (shared guardrails in monorepo)
   * **D · Plain local folder — not a Git repository** (standalone local directory, no VCS)
2. **Project name & one-line description** (for `pyproject.toml` / `README.md`).
3. **Stack pruning:** Keep Python (`uv`), Google Cloud rules (`.agents/rules/gcp.md`), and Jupyter notebooks (`.agents/rules/notebooks.md` + `notebooks/`), or remove any unused ones?

## Step 2: Apply Mode-Specific Cleanup

* **Mode A (Standalone Git repo):** Keep `.git/` and `.github/`.
* **Mode B (Monorepo cell — untracked harness):**
  1. Remove `.git/` (if cloned directly into the cell) and `.github/` (copy `.agents/examples/monorepo-ci.yml` to the monorepo root `.github/workflows/` if desired).
  2. Append the 4-line harness ignore block to the cell's `.gitignore`:
     ```gitignore
     # Local-only AI harness
     .agents/
     .claude/
     AGENTS.md
     CLAUDE.md
     ```
  3. Check ancestor directories for `[tool.uv.workspace]` in `pyproject.toml` and warn the human if the cell needs to be added to `exclude`.
* **Mode C (Monorepo cell — tracked harness):**
  1. Remove `.git/` (if present inside the cell) and `.github/` (point the human to `.agents/examples/monorepo-ci.yml`).
  2. Check ancestor directories for `[tool.uv.workspace]` collisions.
* **Mode D (Plain non-Git folder):**
  1. Remove `.git/` (if present) and `.github/`.

## Step 3: Configure Stack & Domain Rules

* **If Python is used:**
  1. Update `[project] name` and `description` in `pyproject.toml` (keep `version = "0.1.0"`).
  2. Confirm `.python-version` matches the desired interpreter.
  3. Run `uv sync` to initialize `.venv/` and refresh `uv.lock`.
* **If Python is NOT used:**
  1. Remove `pyproject.toml`, `uv.lock`, `.python-version`, `src/example.py`, `tests/test_example.py`, and `.agents/rules/python.md`.
* **Optional domain cleanup:**
  * Delete `.agents/rules/gcp.md` if the project will never use Google Cloud.
  * Delete `.agents/rules/notebooks.md` and `notebooks/` if Jupyter notebooks are not needed.

## Step 4: Verify Baseline & Hand Off to Planning

1. Run the quality gate:
   * Python project: `uv run python .agents/check.py`
   * Non-Python project: `python3 .agents/check.py`
2. Update `.agents/status.md` so *Current State* reflects the initialized project scaffold.
3. Prompt the human to paste their rough concept into `.agents/idea.md` (or share it in chat) to begin Phase 2 (Research & Verification) -> `.agents/plan.md`.
