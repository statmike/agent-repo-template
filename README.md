# Project Name

<!-- ABOUT THIS TEMPLATE — for the GitHub landing page only. The agent replaces this entire file with project-specific docs during the Documentation Phase. -->

**AI-Native Project Harness** — a clean, portable project template and agent harness built for **Claude Code**, **Antigravity**, and `AGENTS.md`-compatible coding agents. Everything harness-owned (state, rules, skills, polyglot hooks, and quality gates) is encapsulated inside [`.agents/`](.agents/), keeping your project root clean whether you work in a standalone repository, a monorepo cell, or a plain local folder without Git.

### Four ways to start

Every scenario ends in the same place: paste your rough concept into [`.agents/idea.md`](.agents/idea.md) (or run `/bootstrap`), iterate with the agent on the verified plan in [`.agents/plan.md`](.agents/plan.md), and approve before building. Full instructions live in **[`.agents/README.md`](.agents/README.md)**.

1. **New standalone GitHub repo** — `gh repo create <repo> --template statmike/agent-repo-template --private --clone` (or **"Use this template"** on GitHub).
2. **Monorepo cell, harness untracked** — copy into a subfolder and ignore `.agents/`, `.claude/`, `AGENTS.md`, and `CLAUDE.md` (4 lines in `.gitignore`).
3. **Monorepo cell, harness tracked** — copy into a subfolder and commit `.agents/` + `.claude/` so guardrails are shared across the monorepo.
4. **Plain local folder (no Git required)** — `rsync -a --exclude=.git --exclude=.github` into any folder; all rules, skills, hooks, and `.agents/check.py` run directly off the filesystem.

---

> 🧩 **This is an unstarted project from the AI-Native Project Harness template.**
> Read **[`.agents/README.md`](.agents/README.md)** for setup, adding project/personal skills and rules, and the workflow loop.
>
> _During the Documentation Phase, the agent rewrites this `README.md` in place to document the actual project._

## Overview

_Describe what this project does once the design is approved and code exists._

## Status

Current increment state and roadmap live in **[`.agents/status.md`](.agents/status.md)**.

## Setup & Verification

```bash
uv sync
uv run python .agents/check.py
```
