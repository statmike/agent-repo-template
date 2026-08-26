# AI-Native Project Harness

This repository is an AI-assisted development harness. It is designed to enforce clean, flat Python architecture, manage GCP infrastructure via `uv`, and prevent AI scope-creep through progressive disclosure documentation.

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

## 🚦 Workflow & Architecture

To prevent documentation drift, our canonical 4-step Ideation-to-Execution workflow and architectural standards are maintained centrally:

- **Workflow & Core Directives:** see [`AGENT.md`](AGENT.md).
- **Engineering & GCP Standards:** see [`CODE_STANDARDS.md`](CODE_STANDARDS.md).

Deeper architectural documentation lives in [`docs/`](docs/); ongoing decisions are logged in `DEV_NOTES.md`, and out-of-scope ideas are parked in `ROADMAP.md`.
