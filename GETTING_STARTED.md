# Getting Started — Using This Template

This repository is an AI-assisted development harness. It is designed to enforce clean, flat Python architecture, manage GCP infrastructure via `uv`, and prevent AI scope-creep through progressive disclosure documentation.

This guide is for **humans bootstrapping a new project** from the template. It stays with the repo as a reference; the root `README.md` will be rewritten by the agent to describe your actual project.

## 🚀 Quickstart (For Humans)

This template supports **three ways to start**. Pick your scenario in **Step 1**, then **Steps 2–5 are identical** for all three — every path ends at the same place: populate `IDEA.md` and prompt the agent.

### Step 1 — Get the template in place (choose one)

#### A · New standalone repo

For a project that gets its own GitHub repository. Use either the GitHub UI or the `gh` CLI.

**Option 1 — GitHub UI**

1. On this template's GitHub page, click **"Use this template" → "Create a new repository"**.
2. Clone your new repo locally:
   ```bash
   git clone https://github.com/<you>/<your-new-repo>
   ```

**Option 2 — `gh` CLI** (creates the repo from the template and clones it in one step)

```bash
gh repo create <your-new-repo> --template statmike/agent-repo-template --private --clone
```

Either way, macOS/Linux recreate the agent symlinks automatically; Windows — see the note in [AI Agent Setup](#-ai-agent-setup).

Everything is tracked and CI runs on push. **Go to Step 2.**

#### B · Monorepo folder — agent files *not* tracked

A self-contained project folder inside a larger monorepo, where the AI harness is **local tooling only** (fast, single-player projects). Only `README.md` and your project code get committed.

1. Copy the template into your subfolder and drop its git history:
   ```bash
   git clone https://github.com/statmike/agent-repo-template <monorepo>/path/to/cell
   rm -rf <monorepo>/path/to/cell/.git
   ```
2. Remove the repo-only CI (a monorepo runs CI from its own root):
   ```bash
   rm -rf <monorepo>/path/to/cell/.github
   ```
   This also removes the cell's quality gate and Dependabot — rebuild both at the monorepo root: see [Monorepo cells: replace the CI you just deleted](#monorepo-cells-replace-the-ci-you-just-deleted).
3. Keep the harness untracked — append this to the cell's `.gitignore`:
   ```gitignore
   # Agent harness — local tooling, not tracked (README stays tracked)
   AGENT.md
   AGENTS.md
   CLAUDE.md
   .cursorrules
   .windsurfrules
   .claude/
   CODE_STANDARDS.md
   GETTING_STARTED.md
   IDEA.md
   DESIGN.md
   DEV_NOTES.md
   ROADMAP.md
   docs/monorepo-ci.yml.example
   ```

4. **Keep the tracked `README.md` self-contained.** It is the only doc your monorepo collaborators will see, so it must not link to harness files that aren't committed. The template's placeholder README links to `GETTING_STARTED.md` — replace those with a link to the template itself:
   ```markdown
   Built from the [AI-Native Project Harness](https://github.com/statmike/agent-repo-template).
   ```
   Then add a short **Setup** section inline (`uv sync`, plus `gcloud auth application-default login`) rather than pointing at the untracked guide. The agent follows the same rule when it rewrites the README — see `AGENT.md` → *Documentation Phase*.

The harness still works locally (hooks and symlinks run off the filesystem, not git), but it is **not shared** — enforcement and design history stay on your machine. **Go to Step 2.**

#### C · Monorepo folder — agent files tracked

A self-contained project folder inside a larger monorepo, with the AI harness **committed** so its guardrails are shared across the monorepo.

1. Copy the template into your subfolder and drop its git history:
   ```bash
   git clone https://github.com/statmike/agent-repo-template <monorepo>/path/to/cell
   rm -rf <monorepo>/path/to/cell/.git
   ```
2. Remove the repo-only CI (a monorepo runs CI from its own root):
   ```bash
   rm -rf <monorepo>/path/to/cell/.github
   ```
   This also removes the cell's quality gate and Dependabot — rebuild both at the monorepo root: see [Monorepo cells: replace the CI you just deleted](#monorepo-cells-replace-the-ci-you-just-deleted).
3. Commit the folder to your monorepo as-is — the harness comes along, and its guardrails apply to everyone.
   *(Windows collaborators: the committed symlinks need the setup in [AI Agent Setup](#-ai-agent-setup).)*

**Go to Step 2.**

#### Monorepo cells: replace the CI you just deleted

Applies to both **B** and **C**. Deleting `<cell>/.github` takes the cell's only automated check with it — ruff, format check, mypy, pytest — plus Dependabot. Put both back at the monorepo root:

- **CI** — copy [`docs/monorepo-ci.yml.example`](docs/monorepo-ci.yml.example) into `<monorepo>/.github/workflows/` (e.g. as `ci-<cell>.yml`), replace `path/to/cell`, and rename the job. It runs the same chain as the template's CI, scoped to the cell with a `paths:` filter and executed inside it via `defaults.run.working-directory`.
- **Dependabot** — add an entry to `<monorepo>/.github/dependabot.yml` with `package-ecosystem: "uv"` and `directory: "/path/to/cell"` (or `directory: "/"` if the cell is a `uv` workspace member — the root holds the lockfile).

#### Monorepo cells: always start your agent *inside* the cell

> ⚠️ Applies to both **B** and **C**, and it fails **silently** — so get this one right first.
>
> Agent config is discovered from the directory where the session starts, and the hooks in `.claude/settings.json` resolve their paths from it (`$CLAUDE_PROJECT_DIR/.claude/hooks/…`). Launching your agent at the **monorepo root** — the natural habit in a monorepo — means the cell's `.claude/settings.json` is never loaded: no pip block, no ADC-only guard, no attribution setting. Nothing errors; you simply have no guardrails.
>
> ```bash
> cd <monorepo>/path/to/cell   # ← then start the agent, from here
> claude
> ```
>
> **Verify once** after starting: run `/hooks` and confirm the two `PreToolUse` entries are listed, or ask the agent to run `pip --version` and check that it is blocked. If neither happens, you started from the wrong directory.
>
> Working from the monorepo root instead? Then the cell's guardrails cannot apply to that session — promote them to the monorepo's own root `.claude/settings.json` (they merge across levels; see [Environment vs. Project](#-environment-vs-project--what-this-template-owns)).

#### Monorepo cells: check for a uv workspace at the root

> ⚠️ Applies to both **B** and **C**, and it also fails **silently**.
>
> If an ancestor directory declares a `uv` **workspace** and your cell is one of its members, the cell stops being self-contained: `uv` resolves from the workspace root, so **both** of the template's pinning mechanisms are ignored. The symptoms, none of which raise an error:
>
> - **Wrong Python** — `uv run python -V` reports the *root's* interpreter (e.g. 3.13), not the 3.11 in the cell's `.python-version`.
> - **Dead lockfile** — `uv lock` writes `<monorepo>/uv.lock`; the cell's `uv.lock` is never read and quietly goes stale (and it stays tracked in both **B** and **C**).
> - **Venv in the wrong place** — `uv sync` creates `<monorepo>/.venv`, not `<cell>/.venv`, so an editor pointed at the cell's `.venv` finds nothing.
>
> **Check** the monorepo's root `pyproject.toml` — `uv` walks *up* from the cell, so check any `pyproject.toml` in between as well:
>
> ```bash
> grep -n "tool.uv.workspace" <monorepo>/pyproject.toml
> ```
>
> No match anywhere (or no root `pyproject.toml`) → nothing to do, the cell is already standalone. A match → check whether its `members` patterns cover your cell's path, and if they do, pick one:
>
> **(a) Keep the cell self-contained — recommended.** This is what the template promises: its own pinned interpreter, its own lockfile, its own venv. Add the cell to the workspace's `exclude` list in the root `pyproject.toml`. Paths are relative to the workspace root, and `exclude` wins over a `members` glob:
>
> ```toml
> [tool.uv.workspace]
> members = ["path/to/*"]
> exclude = ["path/to/cell"]
> ```
>
> Then re-run `uv sync` from inside the cell and confirm `<cell>/.venv` now exists and `uv run python -V` matches `.python-version`.
>
> **(b) Join the workspace.** Reasonable if the monorepo deliberately shares one resolution and one venv — but then stop pretending otherwise: **delete the cell's `uv.lock`** (the root's lockfile is the real one; the cell's is dead weight that will drift), and **delete the cell's `.python-version`** (or set it to the root's pin) so it isn't lying about the interpreter. If the shared interpreter differs, also update `[tool.ruff] target-version` and `[tool.mypy] python_version` in the cell's `pyproject.toml`, or you will lint for the wrong Python. Dependencies still belong in the cell's `pyproject.toml`, but a bare `uv sync` at the workspace root installs only the *root* package's dependencies — run `uv sync --all-groups` from inside the cell (it syncs the member's dependencies into the shared venv), or `uv sync --all-packages --all-groups` from the root. Point your editor at `<monorepo>/.venv`.

### Steps 2–5 — The same for every scenario

2. **Set up your environment** — see [Environment Setup](#-environment-setup) below (`uv sync` + gcloud ADC).
3. **Develop your brief** — this is the highest-leverage step, so invest in it. The quality of everything downstream (the design, the architecture, the code) is bounded by the quality of what you put in [`IDEA.md`](IDEA.md). Don't just jot a one-liner:
   - **Think it through deeply** — the problem you're solving, who it's for, constraints, success criteria, non-goals, and any GCP services or data sources you expect to involve.
   - **Use an AI thought-partner to go wide first** — take your raw notes into a conversational model (e.g. Claude or Gemini) and have it *research the space, challenge your assumptions, surface risks and alternatives, and canvas ideas* with you. Iterate until the concept is sharp.
   - **Distill, then paste** — consolidate that exploration into a coherent starting brief and paste the result into `IDEA.md`. The agent will turn this into a formal `DESIGN.md`, so the richer and clearer the brief, the better the design.
   - **Don't chase exact specifics** — focus on goals and intent. Package versions, API details, and feature availability go stale fast; before designing, the agent verifies them against the real packages and current docs, and proposes simpler up-to-date approaches where your assumptions have aged. It reports all of that in the *Research Findings* section of `DESIGN.md`, so **read that first at the approval gate** — you're approving the corrected plan, not your original brief.
4. **Open your AI agent in the project folder** — for a monorepo cell (B or C) you *must* `cd` into the cell first, or its guardrails silently never load; see [the warning above](#monorepo-cells-always-start-your-agent-inside-the-cell). Give it the starter prompt:
   > Read `AGENT.md`, then begin the **Design phase** from `IDEA.md`.
5. **Review the approval gate** — the agent will produce [`DESIGN.md`](DESIGN.md) (a PRD with architecture diagrams) and then **STOP**. Nothing gets built until you review and approve that design.

### ✅ First-run cleanup checklist

Right after setting up your project folder (any scenario above), do this one-time housekeeping so your project isn't wearing the template's clothes:

- [ ] **Rename the package** in [`pyproject.toml`](pyproject.toml) — set `name` and `description` to your project (the default is `agent-repo-template`).
- [ ] **Reset the version** to `0.1.0` if you changed anything (it ships at `0.1.0`).
- [ ] **Confirm the Python version** in [`.python-version`](.python-version) matches what you want (`uv` honors it — *unless* the cell sits inside a `uv` workspace; see [the workspace check](#monorepo-cells-check-for-a-uv-workspace-at-the-root)).
- [ ] **Lock dependencies** — run `uv sync` once so `uv.lock` reflects your machine.
- [ ] **Write your brief** in [`IDEA.md`](IDEA.md) (see step 3 above) — the template ships it empty.
- [ ] **Delete the example code** — `src/example.py` and `tests/test_example.py` are throwaway samples that demonstrate the flat-module + `tests/`-imports-`src/` pattern; in scenario A — and in B or C once you add the monorepo workflow — they also give you a green CI run out of the box. Remove them once your own modules exist.
- [ ] **Leave the guardrails** in [`.claude/`](.claude/) in place (pip block, ADC-only, no-attribution) unless you have a reason to change them — see *Environment vs. Project* below.
- [ ] The agent will **rewrite `README.md`** during the Documentation Phase — you don't need to touch it now.

## 🔧 Environment Setup

### Prerequisites

- [**uv**](https://docs.astral.sh/uv/) — the only supported package/environment manager (do not use `pip`).
- **Python 3.11** — pinned in [`.python-version`](.python-version); `uv` will fetch it if missing.
- [**Google Cloud CLI (`gcloud`)**](https://cloud.google.com/sdk/docs/install) — for GCP authentication.

### 1. Python environment

```bash
uv sync
```

This creates a local `.venv/` from [`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock). Point your editor / notebook kernel at this `.venv/`.

### 2. GCP authentication (ADC only)

This template **never uses Service Account JSON key files**. Local development authenticates via Application Default Credentials (ADC) managed by the `gcloud` CLI:

```bash
gcloud auth login                        # authenticate the CLI itself
gcloud auth application-default login     # write ADC for client libraries
gcloud config set project YOUR_PROJECT_ID
```

GCP client libraries then pick up these credentials automatically — locally via ADC, and in the cloud via the attached service account — with no code changes. See `CODE_STANDARDS.md` §4 for the full rule.

## 🤖 AI Agent Setup

This repo uses a **symlink strategy** so your agent of choice loads the right context automatically — no manual configuration:

| Agent | Rules file it reads | Symlinked to |
|-------|--------------------|--------------|
| Cursor | `.cursorrules` | → `AGENT.md` |
| Claude Code | `CLAUDE.md` | → `AGENT.md` |
| Windsurf | `.windsurfrules` | → `AGENT.md` |
| Antigravity 2.0 / `agy` CLI | `AGENTS.md` | → `AGENT.md` |

All of these point to a single source of truth, [`AGENT.md`](AGENT.md). Whichever tool you use picks up the same directives on its own. To adjust agent behavior, edit `AGENT.md` — never the symlinks.

> **⚠️ Windows & ZIP users:** These are real symlinks. They resolve correctly when you **`git clone`** on macOS/Linux or use GitHub's *"Use this template"*. On Windows, enable them with `git config --global core.symlinks true` plus Developer Mode (or an elevated shell); otherwise git checks them out as plain text stubs. Likewise, **clone the repo rather than "Download ZIP"** — ZIP extraction can flatten symlinks into stub files that break agent auto-loading.

## 🧭 Environment vs. Project — What This Template Owns

Agents rely on more than a directive: settings, skills, MCP servers, permissions, credentials. Most of that is **environment-level** — it's *yours*, and travels with you across every project — not something this template should ship.

Two questions tell them apart:

1. **Does it depend on *this* project's domain?** (or is it useful everywhere you code)
2. **Would another developer cloning this repo need the *identical* thing?** (or do they bring their own)

If either points to "general" or "mine," it's environment-level and does **not** belong in this repo.

| Environment-level (yours — not here) | Project-level (lives in this repo) |
|---|---|
| Personal/general MCP servers (filesystem, web search) | MCP servers intrinsic to this project — *declared here, credentials in your env* |
| Reusable skills ("write good commits", "run tests") | Skills for this project's domain (e.g. "deploy this service") |
| Global settings, editor prefs, permission allowlists you reuse everywhere | Hooks/permissions that enforce *this repo's* golden rules |
| API keys & credentials | *(never here — always your environment / ADC)* |

**Environment-level config → keep your own agent-config repo.** A personal "dotfiles for your agent" repo (your `~/.claude/` settings, personal skills, general MCP servers) lets you replicate your setup across every machine you work on. That's a pattern you can adopt separately — this template neither provides nor depends on it.

**Project-level config → this template carries a thin slice only:** enforcement of the golden rules (hooks/permissions) and *example declarations* of project-intrinsic MCP servers/skills. Credentials always stay in your environment (see [GCP authentication](#2-gcp-authentication-adc-only)).

Your personal `~/.claude` settings and this repo's committed `.claude/settings.json` are loaded together, not either/or. Additive resources — `permissions`, `hooks`, skills, MCP servers — **merge**, and a `deny` rule always wins. So wherever `.claude/` is tracked (scenario A or C), the guardrails this repo ships apply to everyone who clones it: your personal settings can *add* to them but cannot loosen them.

### What this template ships in `.claude/`

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Committed, shared enforcement: blocks direct `pip` (Golden Rule #3 — uv only) and Service Account key usage (CODE_STANDARDS §4 — ADC only), and keeps commits human-authored (no agent co-author/attribution trailers). |
| `.claude/hooks/block-pip.sh` | `PreToolUse` guard that inspects each Bash command and blocks `pip` / `pip3` / `python -m pip` while allowing `uv pip`. |
| `.claude/hooks/block-sa-keys.sh` | `PreToolUse` guard that blocks writing Service Account JSON keys or running commands that load them (`--key-file`, `activate-service-account`, `GOOGLE_APPLICATION_CREDENTIALS`). |
| `.claude/settings.local.json` | *Not shipped* — your personal, per-repo overrides. Git-ignored; create it if you need to tweak behavior locally without changing the shared config. |

Extend the shared config as your project grows (e.g. add a project-intrinsic MCP server via a root `.mcp.json`, keeping any credentials in your environment).

## 🚦 Workflow & Architecture

To prevent documentation drift, our canonical Ideation-to-Execution workflow and architectural standards are maintained centrally:

- **Workflow & Core Directives:** see [`AGENT.md`](AGENT.md).
- **Engineering & GCP Standards:** see [`CODE_STANDARDS.md`](CODE_STANDARDS.md).

Deeper architectural documentation lives in [`docs/`](docs/); ongoing decisions are logged in `DEV_NOTES.md`, and out-of-scope ideas are parked in `ROADMAP.md`.
