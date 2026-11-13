---
name: bootstrap
description: >-
  Initializes a newly cloned or copied project from the agent-repo-template harness.
  Use when setting up a brand-new repository, monorepo cell, or standalone non-Git
  folder from the template to collect project name and details, configure workspace
  mode and optional domain rules (GCP, notebooks, Python), verify a clean baseline,
  and guide the user into populating .agents/idea.md.
---

# Bootstrap Project From Harness Template

Run this interactive setup once when starting a new project from `agent-repo-template`.

## Step 1: Inspect Folder & Ask the Human for Project Details

First, inspect the current directory (`basename "$PWD"`, whether `.git` exists, and whether `.agents/idea.md` already has content beyond its HTML comment) so you can propose smart defaults.

Unless the human already provided all answers in their prompt, **ask concisely in one turn and wait for their reply** before deleting or rewriting files:

1. **Project name & one-line description** *(propose the current folder/repo name as the default slug for `pyproject.toml` and `README.md`)*.
2. **Workspace mode** *(propose the detected mode as default)*:
   * **A · Standalone Git repository** (everything tracked; GitHub Actions CI active)
   * **B · Monorepo cell — harness untracked** (local-only `.agents/` + `.claude/`; only project code & `README.md` committed)
   * **C · Monorepo cell — harness tracked** (shared guardrails in monorepo)
   * **D · Plain local folder — not a Git repository** (standalone local directory, no VCS)
3. **Stack & license options:**
   * Keep **Python (`uv`)**, **Google Cloud rules** (`.agents/rules/gcp.md`), and **Jupyter notebooks** (`.agents/rules/notebooks.md` + `notebooks/`), or prune any unused ones?
   * Keep the **Apache 2.0 `LICENSE`** (updating the copyright holder if desired), replace it, or remove `LICENSE` (common for private/internal projects)?

## Step 2: Apply Mode-Specific Cleanup

* **Mode A (Standalone Git repo):** Keep `.git/` and `.github/`.
* **Mode B (Monorepo cell — untracked harness):**
  1. Remove `.git/` (if cloned directly into the cell) and `.github/` (mention `.agents/examples/monorepo-ci.yml` if they want cell CI at the monorepo root).
  2. Append the 4-line harness ignore block to the cell's `.gitignore`:
     ```gitignore
     # Local-only AI harness
     .agents/
     .claude/
     AGENTS.md
     CLAUDE.md
     ```
  3. Check ancestor directories for `[tool.uv.workspace]` in `pyproject.toml` and warn the human if the cell should be added to `exclude`.
* **Mode C (Monorepo cell — tracked harness):**
  1. Remove `.git/` (if present inside the cell) and `.github/` (mention `.agents/examples/monorepo-ci.yml`).
  2. Check ancestor directories for `[tool.uv.workspace]` collisions.
* **Mode D (Plain non-Git folder):**
  1. Remove `.git/` (if present) and `.github/`.

## Step 3: Configure Project Metadata, Starter `README.md` & Domain Rules

* **Replace the template `README.md`:** If `README.md` still contains the `<!-- ABOUT THIS TEMPLATE` marker, rewrite it into a clean starter `README.md` titled `# <Project Name>` with the human's one-line description and setup commands (only linking to `.agents/` files when `.agents/README.md` is tracked in Git).
* **Apply `LICENSE` choice:** Keep/update `LICENSE` or remove it per Step 1.
* **If Python is used:**
  1. Set `[project] name` and `description` in `pyproject.toml` (keep `version = "0.1.0"`).
  2. Confirm `.python-version` matches the desired interpreter.
  3. Run `uv sync` to initialize `.venv/` and update `uv.lock`.
* **If Python is NOT used:**
  1. Remove `pyproject.toml`, `uv.lock`, `.python-version`, `src/example.py`, `tests/test_example.py`, and `.agents/rules/python.md`.
* **Optional domain cleanup:**
  * Delete `.agents/rules/gcp.md` if the project will not touch Google Cloud.
  * Delete `.agents/rules/notebooks.md` and `notebooks/` if Jupyter notebooks are not needed.

## Step 4: Verify Baseline & Guide Into `.agents/idea.md` -> `.agents/plan.md`

1. Run the quality gate and confirm everything passes:
   * Python project: `uv run python .agents/check.py`
   * Non-Python project: `python3 .agents/check.py`
2. Rewrite `.agents/status.md` so *Current State* reflects the initialized `<Project Name>` scaffold.
3. **Hand off to Ideation & Planning:**
   * **If `.agents/idea.md` only has its template comment:** Explicitly remind the human to paste their rough concept, goals, constraints, or brainstorm notes into `.agents/idea.md` (or describe them right in chat so you can write `.agents/idea.md` for them), and let them know that once `.agents/idea.md` is ready you will research current packages/docs and iterate with them on `.agents/plan.md` before building.
   * **If `.agents/idea.md` already contains the human's notes:** Confirm you see their concept in `.agents/idea.md` and ask if they want you to start Phase 2 (Research & Verification) and draft `.agents/plan.md` now.
