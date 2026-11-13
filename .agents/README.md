# AI Project Harness Guide (`.agents/`)

This directory holds the **AI-Native Project Harness** — the workflow state, modular rules, on-demand skills, and runtime guardrails that keep agentic development clean across **Claude Code**, **Antigravity** (`agy` / IDE), **Cursor**, **Windsurf**, and compatible agents.

Everything harness-owned lives inside `.agents/` (with thin symlinks for `CLAUDE.md` and `.claude/{rules,skills}`), keeping your project root clean and unambiguous.

---

## Quickstart: Four Ways to Start

Pick your workspace scenario in **Step 1**, then **Steps 2–4** are identical for all four.

### Step 1 — Put the harness in place

#### A · New standalone GitHub repository

```bash
gh repo create <your-new-repo> --template statmike/agent-repo-template --private --clone
cd <your-new-repo>
```
*(Or click **"Use this template" -> "Create a new repository"** on GitHub and `git clone` it.)*

#### B · Monorepo cell — harness *local only* (not committed)

Use when working inside a shared monorepo where only your application code and `README.md` should be committed:

```bash
git clone https://github.com/statmike/agent-repo-template <monorepo>/path/to/cell
rm -rf <monorepo>/path/to/cell/.git <monorepo>/path/to/cell/.github
```

Append 4 lines to `<monorepo>/path/to/cell/.gitignore`:

```gitignore
# Local-only AI harness
.agents/
.claude/
AGENTS.md
CLAUDE.md
```

Copy [`.agents/examples/monorepo-ci.yml`](examples/monorepo-ci.yml) into `<monorepo>/.github/workflows/ci-<cell>.yml` if you want per-cell CI at the monorepo root.

#### C · Monorepo cell — harness *tracked* (shared guardrails)

```bash
git clone https://github.com/statmike/agent-repo-template <monorepo>/path/to/cell
rm -rf <monorepo>/path/to/cell/.git <monorepo>/path/to/cell/.github
```

Copy [`.agents/examples/monorepo-ci.yml`](examples/monorepo-ci.yml) into `<monorepo>/.github/workflows/ci-<cell>.yml` and commit the cell as-is.

> **Monorepo cells (B & C) — two silent traps to avoid:**
> 1. **Always start your agent *inside* `<monorepo>/path/to/cell`** (`cd <monorepo>/path/to/cell` first). Agent hooks and `.agents/` / `.claude/` settings resolve from the session's workspace root; starting at the monorepo root skips cell-level hooks silently.
> 2. **Check for a root `[tool.uv.workspace]`** in `<monorepo>/pyproject.toml`. To keep the cell self-contained with its own `.venv`, `.python-version`, and `uv.lock`, add `"path/to/cell"` to the root workspace `exclude` list.

#### D · Plain local folder — *not* a Git repository

Use for local spikes, scratch tools, or folders outside version control. Copy with `-a` / `rsync -a` so symlinks (`CLAUDE.md`, `.claude/rules`, `.claude/skills`) stay intact:

```bash
rsync -a --exclude='.git' --exclude='.github' --exclude='.venv' \
  /path/to/agent-repo-template/ /path/to/your-project-folder/
cd /path/to/your-project-folder
```

*(Everything in the harness — `.agents/` discovery, polyglot hooks, skills, rules, and `uv run python .agents/check.py` — works off the filesystem with zero Git dependency.)*

---

### Steps 2–4 — Same for every scenario

2. **Initialize the project (`/bootstrap`):**
   Open your agent in the project folder and run `/bootstrap` (or say *"Bootstrap this project"*). The agent asks for your project name, one-line description, workspace mode, stack rules, and license choice (proposing defaults from your folder name and Git state), replaces the template `README.md`, runs `uv sync`, verifies `uv run python .agents/check.py`, and prompts you to populate [`.agents/idea.md`](idea.md).

3. **Paste your rough concept into [`.agents/idea.md`](idea.md):**
   Select-all and paste your brainstorm, rough notes, or distilled thought-partner conversation directly into [`.agents/idea.md`](idea.md) (or simply describe your idea in chat), then prompt your agent:
   > Read `.agents/idea.md`, verify current packages and docs, and create `.agents/plan.md`.

4. **Collaborate on & approve [`.agents/plan.md`](plan.md):**
   The agent verifies real package versions and current docs, writes `## Research Findings` and `## Design` (PRD + Mermaid diagrams) in [`.agents/plan.md`](plan.md), and **stops** at the Approval Gate so you can refine and approve the plan before any code is built.

> **Windows & ZIP note:** `CLAUDE.md`, `.claude/rules`, and `.claude/skills` are real symlinks. On Windows, enable `git config --global core.symlinks true` with Developer Mode, and always `git clone` or `rsync -a` / `cp -a` rather than extracting a GitHub "Download ZIP" archive.

---

## Harness Architecture & File Roles

| Path | Kind | Purpose |
| :--- | :--- | :--- |
| [`AGENTS.md`](../AGENTS.md) (`CLAUDE.md` -> `AGENTS.md`) | Directive | Universal workflow & golden rules auto-loaded by Claude Code, Antigravity, Cursor, Windsurf, and Codex. |
| [`.agents/status.md`](status.md) | Snapshot | Evergreen session handoff (*Current State*, *Now*, *Next*, *Later*, *Known Gaps*). Rewritten in place. |
| [`.agents/idea.md`](idea.md) | Concept Pad | Human paste-zone for raw ideas, rough notes, or brainstorms that kick off an increment. |
| [`.agents/plan.md`](plan.md) | Plan / PRD | Agent-researched `Research Findings` + `Design` built from `idea.md` and gated on approval. |
| [`.agents/decisions.md`](decisions.md) | ADR Stream | Append-only dated engineering decisions and rejected alternatives (`YYYY-MM-DD`). |
| [`.agents/check.py`](check.py) | Gate | Single local & CI runner for Current-State Doctrine, `ruff`, `mypy`, and `pytest`. |
| [`.agents/rules/`](rules/) (`.claude/rules` symlink) | Rules | Modular always-on project rules (`python.md`, `gcp.md`, `notebooks.md`, plus your own). |
| [`.agents/skills/`](skills/) (`.claude/skills` symlink) | Skills | Progressive-disclosure runbooks (`bootstrap`, `consolidate`, plus project-specific skills). |
| [`.agents/hooks/`](hooks/) | Guardrails | Polyglot `PreToolUse` Python scripts wired into both [`.agents/hooks.json`](hooks.json) and [`.claude/settings.json`](../.claude/settings.json). |

---

## Adding Rules & Skills

### 1. Adding a Project Rule (`.agents/rules/<name>.md`)

Drop a Markdown file into `.agents/rules/` **with YAML frontmatter**. Because `.claude/rules` symlinks to `.agents/rules`, both Antigravity and Claude Code load it automatically:

```markdown
---
trigger: always_on
description: "API design and pagination rules for FastAPI endpoints."
---

# FastAPI Endpoint Rules

* Return typed Pydantic response models on every route.
* Require cursor pagination on list endpoints.
```

> **Important:** Always include `trigger: always_on` and `description:` in the frontmatter. Antigravity requires `trigger: always_on` to load `.agents/rules/*.md` files (files without frontmatter are skipped silently), while Claude Code loads all `.claude/rules/*.md` files and ignores unknown frontmatter keys.

*Need a rule scoped to a single subdirectory (for example `frontend/` or `src/pipelines/`)?* Place a local `AGENTS.md` (plus `CLAUDE.md -> AGENTS.md` symlink) inside that subdirectory.

### 2. Adding a Project Skill (`.agents/skills/<skill-name>/SKILL.md`)

Use a **Skill** instead of an always-on rule for multi-step workflows, deployment runbooks, or domain scripts (`0` tokens in context until relevant or invoked via `/skill-name`):

```text
.agents/skills/deploy-cloud-run/
├── SKILL.md
└── scripts/
    └── verify_service.py
```

```markdown
---
name: deploy-cloud-run
description: >-
  Builds, deploys, and smoke-tests the Cloud Run service. Use when asked to
  deploy a staging or production revision.
---

# Deploy Cloud Run Service

1. Run `uv run python .agents/check.py`.
2. Deploy from source and run `scripts/verify_service.py`.
```

Because `.claude/skills` symlinks to `.agents/skills`, every skill created here works identically in Claude Code and Antigravity.

---

## Personal Skills & Personal Rules (Host Environment)

Keep cross-project habits, personal productivity skills, and personal safety rails in your **host environment** — never committed into individual project repos:

| Scope | Antigravity Global Path | Claude Code Global Path |
| :--- | :--- | :--- |
| **Personal Skills** | `~/.gemini/config/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` |
| **Personal Rules** | `~/.gemini/config/rules/<name>.md` | `~/.claude/rules/<name>.md` |

### Share One Canonical Personal Toolkit Across Both Agents

Maintain your personal `skills/` and `rules/` in one place (for example inside a personal `~/Git/agent-personal-config` dotfiles repo, or directly in `~/.gemini/config/`) and symlink the other agent to it once per machine:

```bash
mkdir -p ~/.gemini/config/skills ~/.gemini/config/rules ~/.claude
ln -sfn ~/.gemini/config/skills ~/.claude/skills
ln -sfn ~/.gemini/config/rules  ~/.claude/rules
```

Include `trigger: always_on` + `description:` frontmatter in your personal `rules/*.md` files so both agents load them seamlessly. At runtime, personal rules and skills merge with `.agents/{rules,skills}`, and project-level skills take precedence on name collisions.

---

## Runtime Enforcement (`uv` & Credential Hygiene)

Two fast stdlib-only Python hooks run automatically before tool calls in both **Claude Code** (via [`.claude/settings.json`](../.claude/settings.json)) and **Antigravity** (via [`.agents/hooks.json`](hooks.json)):

* **[`guard_uv.py`](hooks/guard_uv.py)** *(active whenever `pyproject.toml` exists)*:
  * Splits compound shell commands (`&&`, `;`, `|`, subshells) and blocks direct `pip` / `pip3` / `.venv/bin/pip`, `python -m pip`, `python -m venv`, `virtualenv`, `conda`, `mamba`, `poetry`, `pipenv`, and `pdm` while allowing `uv` and `uvx`.
  * Blocks bare `pytest`, `ruff`, `mypy`, `jupyter`, and project-local `python` invocations unless run via `uv run ...` (external absolute helper scripts outside the project root remain allowed).
  * Blocks creating legacy manifest files (`requirements.txt`, `Pipfile`, `poetry.lock`, `environment.yml`) inside the project.
* **[`guard_secrets.py`](hooks/guard_secrets.py)**:
  * Blocks writing GCP Service Account JSON key material to files and blocks `--key-file`, `activate-service-account`, and `GOOGLE_APPLICATION_CREDENTIALS=` shell flags, enforcing Application Default Credentials (`gcloud auth application-default login`).

Run all static, type, test, and Current-State Doctrine checks locally at any time with:

```bash
uv run python .agents/check.py
```
