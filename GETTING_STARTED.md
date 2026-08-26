# Getting Started — Using This Template

This repository is an AI-assisted development harness. It is designed to enforce clean, flat Python architecture, manage GCP infrastructure via `uv`, and prevent AI scope-creep through progressive disclosure documentation.

This guide is for **humans bootstrapping a new project** from the template. It stays with the repo as a reference; the root `README.md` will be rewritten by the agent to describe your actual project.

## 🚀 Quickstart (For Humans)

Start a new project in five steps:

1. **Create a repo from this template** — click *"Use this template"* on GitHub (or clone it).
2. **Set up your local environment** — see [Environment Setup](#-environment-setup) below.
3. **Develop your brief** — this is the highest-leverage step, so invest in it. The quality of everything downstream (the design, the architecture, the code) is bounded by the quality of what you put in [`IDEA.md`](IDEA.md). Don't just jot a one-liner:
   - **Think it through deeply** — the problem you're solving, who it's for, constraints, success criteria, non-goals, and any GCP services or data sources you expect to involve.
   - **Use an AI thought-partner to go wide first** — take your raw notes into a conversational model (e.g. Claude or Gemini) and have it *research the space, challenge your assumptions, surface risks and alternatives, and canvas ideas* with you. Iterate until the concept is sharp.
   - **Distill, then paste** — consolidate that exploration into a coherent starting brief and paste the result into `IDEA.md`. The agent will turn this into a formal `DESIGN.md`, so the richer and clearer the brief, the better the design.
4. **Open your AI agent in this folder** and give it the starter prompt:
   > Read `AGENT.md`, then begin the **Design phase** from `IDEA.md`.
5. **Review the approval gate** — the agent will produce [`DESIGN.md`](DESIGN.md) (a PRD with architecture diagrams) and then **STOP**. Nothing gets built until you review and approve that design.

### ✅ First-run cleanup checklist

Right after creating your repo from the template, do this one-time housekeeping so your project isn't wearing the template's clothes:

- [ ] **Rename the package** in [`pyproject.toml`](pyproject.toml) — set `name` and `description` to your project (the default is `agent-repo-template`).
- [ ] **Reset the version** to `0.1.0` if you changed anything (it ships at `0.1.0`).
- [ ] **Confirm the Python version** in [`.python-version`](.python-version) matches what you want (`uv` honors it).
- [ ] **Lock dependencies** — run `uv sync` once so `uv.lock` reflects your machine.
- [ ] **Write your brief** in [`IDEA.md`](IDEA.md) (see step 3 above) — the template ships it empty.
- [ ] **Delete the example code** — `src/example.py` and `tests/test_example.py` are throwaway samples that demonstrate the flat-module + `tests/`-imports-`src/` pattern and give you a green CI run out of the box. Remove them once your own modules exist.
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

### How the two levels combine at runtime

The two levels are not either/or — Claude Code **loads every level and combines them** on each run. It uses two different rules depending on the kind of setting:

- **Override** — for single scalar values (`model`, `theme`, `effortLevel`), the most specific level that sets it wins.
- **Merge (union)** — for additive resources, every level's contributions apply *together*: `permissions` (allow/deny/ask), `hooks`, `skills`, `agents`, MCP servers (`.mcp.json`), and `CLAUDE.md` memory files.

**Precedence (highest → lowest)** — when a scalar is set at more than one level, higher wins:

| # | Level | Path |
|---|-------|------|
| 1 | Enterprise / managed policy | `/etc/claude-code/managed-settings.json` (Linux) · `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS) |
| 2 | Command-line flag | `claude --settings '{…}'` |
| 3 | Project-local (personal, per-repo) | `<repo>/.claude/settings.local.json` *(git-ignored)* |
| 4 | **Project-shared (this template)** | `<repo>/.claude/settings.json` *(committed)* |
| 5 | User / environment (yours) | `~/.claude/settings.json` |

The practical upshot for this template: because `permissions` and `hooks` **merge** and a `deny` rule **always wins regardless of level**, the guardrails this repo ships in `.claude/settings.json` apply to everyone who clones it — and a developer's personal `~/.claude` settings can add to them but cannot loosen them. Your personal conveniences and the repo's non-negotiable rules run side by side.

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
