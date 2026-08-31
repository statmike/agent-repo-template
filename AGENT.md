# **AI Agent Master Directive**

You are an expert AI developer and architect. You are operating within an AI-Native project harness. Your primary goal is to write clean, human-readable, flat Python code, and to strictly follow the progressive disclosure documentation model.

## **🚦 Core Workflow (Do Not Deviate)**

1. **Ideation Phase:** Read IDEA.md.  
2. **Research & Verification Phase:** 🛑 **Do not design from memory.** IDEA.md is a human brief written from recall — treat every specific in it (package versions, APIs, feature availability, service names, pricing/limits) as **unverified**, and treat your own training knowledge the same way. Before designing, establish ground truth:
   * **Inspect the real packages, not your memory of them** — for anything already in the local `uv` environment, read it directly (`uv tree`, `uv run python -c "import x; print(x.__version__)"`, and read the installed source/docstrings) rather than assuming an API shape.
   * **Not installed yet? Inspect it ephemerally.** Most dependencies won't exist locally during design. Pull a package into a throwaway environment to examine it *without* committing to it — `uv run --with <pkg> python -c "..."` (or `uvx <tool>`) resolves it on the fly and leaves `pyproject.toml`/`uv.lock` untouched. **Do not `uv add` anything before the Approval Gate**; dependencies are chosen in DESIGN.md and installed during Execution.
   * **Check current sources** — official docs and the package index for versions, deprecations, and features that shipped or vanished since the brief (or your training data) was written.
   * **Prefer the simpler current path.** If a goal in IDEA.md is now achievable with less machinery — a feature that became native, a library that replaces hand-rolled code, a service that subsumes a component — **propose the simplification** instead of faithfully building the stale plan.
3. **Design Phase:** Generate DESIGN.md from IDEA.md **as corrected by your research**. DESIGN.md must act as a formal Product Requirements Document (PRD) and include Mermaid.js architecture diagrams mapping out code and infrastructure (e.g., GCP services). It must also contain a **Research Findings** section recording what you verified, the versions/APIs you confirmed, anything in IDEA.md that proved stale, and every simplification or deviation you are proposing — with your reasoning.  
4. **Approval Gate:** **STOP.** You must wait for human approval on DESIGN.md before writing any code. Explicitly surface any deviation from IDEA.md here: the human approves the *corrected* plan, not the original brief.  
5. **Execution Phase:** Once approved, write code according to CODE_STANDARDS.md.  
6. **Documentation Phase:** After code exists, **rewrite `README.md` in place** so it documents *this project* — its purpose, how to run it, and how to use it — replacing the placeholder shipped with the template. Keep `README.md` scannable; route deep docs to `docs/`. For environment/agent setup, **never link to a harness doc that isn't tracked in this repo** — check first (e.g. `git ls-files --error-unmatch GETTING_STARTED.md`):
   * **Tracked** (standalone repo, or monorepo cell with the harness committed) → don't duplicate it; link to `GETTING_STARTED.md` for prerequisites, `uv`, and gcloud ADC.
   * **Not tracked** (monorepo cell where the harness is local-only) → `README.md` is the only doc collaborators see, so make it self-contained: inline a short Setup section (`uv sync`, `gcloud auth application-default login`) and credit the template by URL instead of by relative link.

## **📁 File Routing & AI Memory**

You are required to manage your own context using the following files. **Do not put everything in one file.**

* **CODE_STANDARDS.md**: 🛑 **MANDATORY READ** before writing any Python, uv configuration, or infrastructure code.  
* **ROADMAP.md**: If you invent a new feature, optimization, or architectural shift outside the immediate scope of DESIGN.md, **DO NOT build it**. Document it here instead.  
* **DEV_NOTES.md**: Treat this as your Architecture Decision Record (ADR). If you solve a dependency conflict, hack a workaround for a cloud service, or make a non-obvious engineering choice, append a brief explanation here. Read this file before refactoring.
* **`docs/`**: Reserved for deep architectural documentation or MkDocs setup. Keep the root `README.md` scannable; route heavy documentation here.  
* **README.md**: The project's public face. Starts as a template placeholder; you rewrite it in the Documentation Phase to describe the actual project. **This is the one doc you overwrite.**  
* **GETTING_STARTED.md**: The durable template guide (env setup, agent symlinks, workflow). **Do not overwrite it** — link to it from `README.md` instead, but only when it is tracked in this repo (see Documentation Phase).

## **🥇 The Golden Rules**

1. **Zero Business Logic in Notebooks:** .ipynb files are strictly for narrative and execution. All core logic must live in .py files inside src/.  
2. **Flat is Better Than Nested:** Write single-responsibility, flat Python modules. Avoid deep object-oriented inheritance.  
3. **No Spider Webs:** Single-responsibility is *not* a mandate to fragment. Prefer fewer, fuller modules; reading one must never require chasing a chain of others (**one hop maximum**). No circular imports, and no `utils.py`/`helpers.py` grab-bags — a little duplication beats a web of shared helpers. *(Details: CODE_STANDARDS.md §1.)*  
4. **uv is the Law:** Manage all dependencies, environments, and lockfiles using uv. Never use pip directly. *(Enforced: a `PreToolUse` hook in `.claude/settings.json` blocks `pip`/`pip3`/`python -m pip`; use `uv add`, `uv sync`, `uv run`, or `uv pip`.)*  
5. **Environment vs. Project Boundary:** Only *project-level* agent artifacts belong in this repo — enforcement of these rules (hooks/permissions, shipped in `.claude/settings.json`) and declarations of project-intrinsic MCP servers/skills. **Never create or commit environment-level agent config** (personal settings, general-purpose skills, or any credentials); those live in the user's own environment. See `GETTING_STARTED.md` → *Environment vs. Project* for how the levels merge at runtime.

Remember: The human must be able to scan and understand every module within seconds. Optimize for human legibility over clever abstractions.