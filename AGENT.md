# **AI Agent Master Directive**

You are an expert AI developer and architect. You are operating within an AI-Native project harness. Your primary goal is to write clean, human-readable, flat Python code, and to strictly follow the progressive disclosure documentation model.

## **🚦 Core Workflow (Do Not Deviate)**

0. **Orientation Phase (every new session):** 🧭 **Assume you have no memory of this project.** Sessions are disposable and interchangeable — this one may be a fresh context, a different machine, or a different agent product than the one that did the last increment. The harness files are the only continuity. Before acting on the human's request, read in this order:
   * **`STATUS.md`** — where the project stands, what is in flight (*Now*), what comes next, and the known gaps. This is your primary handoff.
   * **`DEV_NOTES.md`** — the accumulated decisions and why they are what they are. Mandatory before refactoring or re-litigating an existing choice; this is where *"we already tried that"* lives.
   * **`CODE_STANDARDS.md`** — before writing any code.
   * **`IDEA.md` / `DESIGN.md`** — only when starting the project or opening a new increment. On an established project they are historical; the code is the spec.
   * **Reconcile with reality.** `STATUS.md` is a snapshot, and the previous session may have ended before Phase 7 ever ran. Check `git status` and recent `git log` for work the file does not mention. Where they disagree, **say so and correct `STATUS.md` first** — the repo is the authority on what exists, not the file's last optimistic update.

   Then **state your orientation back to the human in a few lines** — where the project stands, what *Now* claims, and what you propose to do — before taking action.
1. **Ideation Phase:** Read IDEA.md.  
2. **Research & Verification Phase:** 🛑 **Do not design from memory.** IDEA.md is a human brief written from recall — treat every specific in it (package versions, APIs, feature availability, service names, pricing/limits) as **unverified**, and treat your own training knowledge the same way. Before designing, establish ground truth:
   * **Inspect the real packages, not your memory of them** — for anything already in the local `uv` environment, read it directly (`uv tree`, `uv run python -c "import x; print(x.__version__)"`, and read the installed source/docstrings) rather than assuming an API shape.
   * **Not installed yet? Inspect it ephemerally.** Most dependencies won't exist locally during design. Pull a package into a throwaway environment to examine it *without* committing to it — `uv run --with <pkg> python -c "..."` (or `uvx <tool>`) resolves it on the fly and leaves `pyproject.toml`/`uv.lock` untouched. **Do not `uv add` anything before the Approval Gate**; dependencies are chosen in DESIGN.md and installed during Execution.
   * **Check current sources** — official docs and the package index for versions, deprecations, and features that shipped or vanished since the brief (or your training data) was written.
   * **Prefer the simpler current path.** If a goal in IDEA.md is now achievable with less machinery — a feature that became native, a library that replaces hand-rolled code, a service that subsumes a component — **propose the simplification** instead of faithfully building the stale plan.
3. **Design Phase:** Generate DESIGN.md from IDEA.md **as corrected by your research**. DESIGN.md must act as a formal Product Requirements Document (PRD) and include Mermaid.js architecture diagrams mapping out code and infrastructure (e.g., GCP services). It must also contain a **Research Findings** section recording what you verified, the versions/APIs you confirmed, anything in IDEA.md that proved stale, and every simplification or deviation you are proposing — with your reasoning.  
4. **Approval Gate:** **STOP.** You must wait for human approval on DESIGN.md before writing any code. Explicitly surface any deviation from IDEA.md here: the human approves the *corrected* plan, not the original brief.  
5. **Execution Phase:** Once approved, write code according to CODE_STANDARDS.md.  
6. **Documentation Phase:** After code exists, **rewrite `README.md` in place** so it documents *this project* — its purpose, how to run it, and how to use it — replacing the placeholder shipped with the template — including its `ABOUT THIS TEMPLATE` marker comment, whose absence is how CI knows the README is now project-owned. Keep `README.md` scannable; route deep docs to `docs/`. **Link to `STATUS.md`** from the README so a reader landing on the repo can find where the project stands. For environment/agent setup, **never link to a harness doc that isn't tracked in this repo** — check first (e.g. `git ls-files --error-unmatch GETTING_STARTED.md`):
   * **Tracked** (standalone repo, or monorepo cell with the harness committed) → don't duplicate it; link to `GETTING_STARTED.md` for prerequisites, `uv`, and gcloud ADC.
   * **Not tracked** (monorepo cell where the harness is local-only) → `README.md` is the only doc collaborators see, so make it self-contained: inline a short Setup section (`uv sync`, `gcloud auth application-default login`) and credit the template by URL instead of by relative link.
7. **Consolidation Phase:** 🧹 An iteration is **not done** until the repo describes only its present state. Development is iterative — you chased ideas, abandoned some, and left notes — and this phase collects that residue so the repo stays near-shareable at all times.
   * **Harvest, don't delete.** Nothing of value is lost, it is *relocated*: non-obvious decisions and rejected approaches → `DEV_NOTES.md` (dated); deferred ideas → `STATUS.md` → *Later*; work that must still happen → `STATUS.md` → *Now*/*Next*. Once a thing has a home, remove it from the code.
   * **Sweep the code.** Delete commented-out blocks, dead branches, unreachable helpers, flags for abandoned experiments, and inline `TODO`/`FIXME`/`XXX`/`HACK` notes. *(Enforced: ruff `ERA`/`FIX`/`ARG` in CI.)*
   * **Refresh the notebooks.** Notebooks illustrate `src/` by calling it, and their committed outputs are part of that illustration — **never strip them**. But an output generated by code you have since changed is a stale claim about present behavior. If this iteration touched a module any notebook imports, re-run that notebook top to bottom from a fresh kernel and commit the new outputs. *(Not machine-checkable — executing notebooks in CI would need live GCP credentials, which CODE_STANDARDS §4 forbids. This one is on you.)*
   * **Sweep the docs.** Rewrite to present tense. Strip change-narration — "previously", "we switched to", "note that this used to", "as decided in the design". A reader must never need the project's history to understand its behavior.
   * **Update `STATUS.md`** so *Current State*, *Now*, *Next*, and *Known Gaps* match reality.

**This workflow is a loop, not a line.** The next increment returns to Phase 2 (Research & Verification) — re-verify, extend `DESIGN.md`, and pass the Approval Gate again before building.

## **📁 File Routing & AI Memory**

You are required to manage your own context using the following files. **Do not put everything in one file.**

* **CODE_STANDARDS.md**: 🛑 **MANDATORY READ** before writing any Python, uv configuration, or infrastructure code.  
* **STATUS.md** *(current-state)*: The single answer to "where is this at, where is it going." Holds *Current State*, *Now*, *Next*, *Later*, and *Known Gaps*. **Rewrite it in place** — it is a snapshot, never a log. If you invent a feature, optimization, or architectural shift outside the scope of DESIGN.md, **DO NOT build it**; park it under *Later*.  
* **DEV_NOTES.md** *(stream)*: Treat this as your Architecture Decision Record (ADR). If you solve a dependency conflict, hack a workaround for a cloud service, or make a non-obvious engineering choice, **append** a brief dated explanation here. This is the one file that accumulates — never rewrite history, supersede it. Read this file before refactoring.
* **`docs/`**: Reserved for deep architectural documentation or MkDocs setup. Keep the root `README.md` scannable; route heavy documentation here.  
* **README.md**: The project's public face. Starts as a template placeholder; you rewrite it in the Documentation Phase to describe the actual project. **This is the one doc you overwrite.**  
* **GETTING_STARTED.md**: The durable template guide (env setup, agent symlinks, workflow). **Do not overwrite it** — link to it from `README.md` instead, but only when it is tracked in this repo (see Documentation Phase).

## **🥇 The Golden Rules**

1. **Zero Business Logic in Notebooks:** .ipynb files are strictly for narrative and execution. All core logic must live in .py files inside src/.  
2. **Flat is Better Than Nested:** Write single-responsibility, flat Python modules. Avoid deep object-oriented inheritance.  
3. **No Spider Webs:** Single-responsibility is *not* a mandate to fragment. Prefer fewer, fuller modules; reading one must never require chasing a chain of others (**one hop maximum**). No circular imports, and no `utils.py`/`helpers.py` grab-bags — a little duplication beats a web of shared helpers. *(Details: CODE_STANDARDS.md §1.)*  
4. **uv is the Law:** Manage all dependencies, environments, and lockfiles using uv. Never use pip directly. *(Enforced: a `PreToolUse` hook in `.claude/settings.json` blocks `pip`/`pip3`/`python -m pip`; use `uv add`, `uv sync`, `uv run`, or `uv pip`.)*  
5. **Environment vs. Project Boundary:** Only *project-level* agent artifacts belong in this repo — enforcement of these rules (hooks/permissions, shipped in `.claude/settings.json`) and declarations of project-intrinsic MCP servers/skills. **Never create or commit environment-level agent config** (personal settings, general-purpose skills, or any credentials); those live in the user's own environment. See `GETTING_STARTED.md` → *Environment vs. Project* for how the levels merge at runtime.

6. **Current-State Doctrine:** Shipped artifacts — `README.md`, `docs/`, `STATUS.md`, code and its comments, and notebooks **including their committed outputs** — describe the system **as it is now**, in present tense. They are a garden to be continuously re-pruned, not a diary. If a sentence only makes sense as a narrative of what happened ("previously", "we changed", "this used to"), it belongs in `DEV_NOTES.md`. **`IDEA.md` and `DESIGN.md` are historical artifacts of a moment — once built, the code is the spec.** No shipped artifact may reference them. *(Enforced: CI rejects `DESIGN.md`/`IDEA.md` references in `README.md`, `STATUS.md`, `docs/`, `src/`, `tests/`, and `notebooks/` — the template's placeholder README is exempt until you rewrite it.)*

7. **Sessions Are Disposable:** Nothing survives a session — not the transcript, not your reasoning, not the plan you were holding in your head. The harness carries it instead: `STATUS.md` for where things stand, `DEV_NOTES.md` for why they stand that way. Write to both as though the next session will be a **different agent on a different machine**, because it may be. Never end an increment with state living only in the conversation. *(Corollary: the human is free to switch agent products mid-project — the symlinked directive and these two files are what make that a non-event.)*

Remember: The human must be able to scan and understand every module within seconds. Optimize for human legibility over clever abstractions.