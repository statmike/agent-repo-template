# Project Name

<!-- ABOUT THIS TEMPLATE — for the GitHub landing page only. The agent replaces this entire file with project-specific docs during the Documentation Phase. -->

**AI-Native Project Harness** — a template for AI-assisted Python projects on GCP. It enforces clean, flat architecture, manages dependencies and environments with `uv`, authenticates via gcloud ADC (no JSON keys), and uses a single-source-of-truth directive (`AGENT.md`, symlinked to every agent's rules file) with a progressive-disclosure workflow that keeps the AI from scope-creeping.

### Three ways to start

Whichever you pick, you end at the same place — populate `IDEA.md` and prompt your agent. Full step-by-step for each is in **[GETTING_STARTED.md](GETTING_STARTED.md) → Quickstart**.

1. **New standalone repo** — click **"Use this template" → "Create a new repository"**, then clone it.
2. **Monorepo folder, agent files *not* tracked** — clone the template into a subfolder as *local* AI tooling (only `README.md` + your code get committed). Best for fast, single-player projects.
3. **Monorepo folder, agent files tracked** — same, but commit the AI harness too, so its guardrails are shared across the monorepo.

---

> 🧩 **This is an unstarted project from the AI-Native Project Harness template.**
> New here? Read **[GETTING_STARTED.md](GETTING_STARTED.md)** to set up your environment and kick off the workflow.
>
> _This README is a placeholder. During the Execution phase, the agent rewrites this file in place to document the actual project — its purpose, how to run it, and how to use it._

## Overview

_Describe what this project does once the design is approved and code exists._

## Status

Where this project stands and where it is going: **[STATUS.md](STATUS.md)**.

## Getting Started

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for prerequisites, environment setup (`uv` + gcloud ADC), and the AI agent workflow.
