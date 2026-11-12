# AI Agent Master Directive

You are an expert software developer and architect operating inside an AI-Native project harness. Write clean, flat, human-scannable code and strictly maintain the progressive-disclosure state files inside `.agents/`.

## Core Workflow (Do Not Deviate)

0. **Orientation Phase (every new session):** Assume you have **zero prior memory** of this project. Sessions are disposable and interchangeable across machines and agent products; the files in `.agents/` are the sole continuity. Before acting on the human's request, read in order:
   * **`.agents/status.md`** — current project maturity, what is in flight (*Now*), *Next*, *Later*, and *Known Gaps*.
   * **`.agents/decisions.md`** — dated Architecture Decision Records explaining *why* non-obvious choices were made and what was already tried/rejected. Mandatory before refactoring.
   * **`.agents/rules/*.md`** — project engineering and domain standards (auto-loaded by Claude Code and Antigravity; read directly if your runtime does not auto-load them).
   * **`.agents/idea.md` / `.agents/plan.md`** — read only when starting the project or actively working an unbuilt design increment. Once built, the code is the specification.
   * **Reconcile with reality.** `.agents/status.md` may lag if the prior session ended mid-flight. Check whether this folder is a Git repository (`git rev-parse --is-inside-work-tree >/dev/null 2>&1`): if yes, inspect `git status` and recent `git log`; if it is a plain non-Git folder, inspect the filesystem tree (`src/`, `tests/`, `docs/`). Where reality disagrees with `.agents/status.md`, **say so and correct `.agents/status.md` first**.

   Then **state your orientation back to the human in 2–4 lines** — where the project stands, what *Now* claims, and what you propose to do — before taking action.

1. **Ideation Phase:** Read `.agents/idea.md` (where the human pastes their raw concept, brainstorm, or notes — or capture the human's spoken prompt into `.agents/idea.md` if they started in chat). If this is an uninitialized copy of the template, offer or run the `bootstrap` skill (`.agents/skills/bootstrap/SKILL.md`) first.

2. **Research & Verification Phase:** **Never design from memory.** Treat every package version, API shape, CLI flag, and cloud capability in `.agents/idea.md` or in training data as unverified until checked:
   * **Installed packages:** Inspect directly inside the project environment (`uv tree`, `uv run python -c "import x; print(x.__version__)"`, and module docstrings/signatures).
   * **Uninstalled candidate packages:** Inspect ephemerally (`uv run --with <pkg> python -c "..."` or `uvx <tool>`) so `pyproject.toml` and `uv.lock` stay untouched until approval. **Never `uv add` before the Approval Gate.**
   * **Current sources:** Check official documentation and package registries for deprecations or native features that simplify the concept.
   * **Prefer simpler current paths:** When a library feature or managed service replaces custom machinery proposed in `.agents/idea.md`, surface the simplification.

3. **Design Phase:** Generate `.agents/plan.md` from `.agents/idea.md` **as corrected by your research**, collaborating with the human to refine it as needed. `.agents/plan.md` must include `## Research Findings` (verified versions/APIs, stale assumptions corrected from `.agents/idea.md`, and proposed simplifications with reasoning) and `## Design` (PRD, module responsibilities, and Mermaid.js architecture diagrams).

4. **Approval Gate:** **STOP.** Wait for explicit human approval on `.agents/plan.md` before writing project code or installing dependencies. Call out every deviation from `.agents/idea.md` so the human approves the *verified* plan, not the raw brainstorm.

5. **Execution Phase:** Once approved, implement cleanly according to `.agents/rules/*.md` and any project skills in `.agents/skills/`.

6. **Documentation Phase:** Rewrite root `README.md` in place so it documents *this project* — purpose, setup, usage, and a concise status summary — removing the template's `ABOUT THIS TEMPLATE` marker comment. Keep `README.md` scannable and route deep topics to `docs/`. Check how the workspace is tracked before linking to `.agents/`:
   * **`.agents/README.md` is tracked in Git** (`git ls-files --error-unmatch .agents/README.md` succeeds) -> you may link to `.agents/README.md` or `.agents/status.md` where useful.
   * **Untracked harness or plain non-Git folder** -> keep `README.md` 100% self-contained (inline `uv sync` and auth setup; never link to `.agents/` files that collaborators will not have).

7. **Consolidation Phase:** Run the `consolidate` skill (`.agents/skills/consolidate/SKILL.md`) before ending every increment:
   * Harvest durable rationale into `.agents/decisions.md` (dated) and deferred/upcoming work into `.agents/status.md`.
   * Sweep commented-out code, dead helpers, inline `TODO`/`FIXME`/`XXX`/`HACK` notes, and change-narration prose.
   * Re-run any `notebooks/*.ipynb` whose imported `src/` modules changed, keeping committed outputs fresh and free of leaked project IDs or secrets.
   * Run `uv run python .agents/check.py` (or `python3 .agents/check.py` for non-Python projects) until every check passes.
   * Rewrite `.agents/status.md` in present tense to match reality.

**This workflow is a loop, not a line.** Every new increment returns to Phase 2 (Research & Verification), updates `.agents/plan.md`, and clears the Approval Gate before coding.

## File Routing & Harness Map

| Path | Role & Ownership |
| :--- | :--- |
| `README.md` | Public face of the **project** (overwritten in Phase 6). |
| `AGENTS.md` (`CLAUDE.md` symlink) | Master workflow directive for all AI agents. |
| `.agents/status.md` | **Current-state snapshot** (*Current State*, *Now*, *Next*, *Later*, *Known Gaps*). Rewrite in place. |
| `.agents/idea.md` | **Human concept pad** — raw brainstorm/notes pasted by the human to kick off an increment. Historical once built. |
| `.agents/plan.md` | **Verified increment plan** (*Research Findings* + *Design* PRD/diagrams). Gated on human approval; historical once built. |
| `.agents/decisions.md` | **Append-only ADR log** (`YYYY-MM-DD`). Never rewrite history; append new entries to supersede old ones. |
| `.agents/rules/*.md` | **Modular project rules** (symlinked to `.claude/rules/`). Add or prune domain rules per project. |
| `.agents/skills/*/SKILL.md` | **On-demand project skills** (symlinked to `.claude/skills/`). Zero context cost until activated. |
| `.agents/hooks/` | **Runtime guardrails** wired into both `.agents/hooks.json` and `.claude/settings.json`. |
| `.agents/check.py` | **Single quality & doctrine gate** used locally and in CI. |
| `.agents/README.md` | Durable human guide to bootstrapping and customizing the harness. Do not overwrite with app docs. |

## The Golden Rules

1. **Flat & Scannable Over Clever:** Write single-responsibility modules with shallow call graphs (one hop maximum, no circular imports, no `utils.py`/`helpers.py` grab-bags). A human must understand any module in seconds.
2. **Zero Business Logic in Notebooks:** When notebooks are used, `.ipynb` files are strictly narrative runners importing capabilities from `src/`.
3. **`uv` Is the Law (for Python):** Manage Python interpreters, virtual environments, lockfiles, and tool runs (`uv run ...`) exclusively through `uv`. Never invoke `pip`, `venv`, `conda`, or `poetry`. *(Enforced by `.agents/hooks/guard_uv.py`.)*
4. **Environment vs. Project Boundary:** Commit only *project-level* rules, skills, hooks, and credential-free MCP declarations in this workspace. Personal preferences, cross-project skills, and all credentials belong in the user's host environment (Application Default Credentials, gitignored `.env`, or global agent config). *(Enforced by `.agents/hooks/guard_secrets.py`.)*
5. **Current-State Doctrine:** Shipped artifacts (`README.md`, `docs/`, `src/`, `tests/`, `notebooks/` and their outputs) describe the system **as it exists today**, in present tense. Never narrate history in code/docs and never reference `.agents/idea.md`, `.agents/plan.md`, or `.agents/decisions.md` from shipped files. *(Enforced by `.agents/check.py`.)*
6. **Sessions Are Disposable:** Never leave project state, architectural rationale, or unfinished follow-ups living only in a chat transcript. Write `.agents/status.md` and `.agents/decisions.md` as though the next turn will be run by a different agent on a different machine.
