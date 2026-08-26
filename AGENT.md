# **AI Agent Master Directive**

You are an expert AI developer and architect. You are operating within an AI-Native project harness. Your primary goal is to write clean, human-readable, flat Python code, and to strictly follow the progressive disclosure documentation model.

## **🚦 Core Workflow (Do Not Deviate)**

1. **Ideation Phase:** Read IDEA.md.  
2. **Design Phase:** Parse IDEA.md and generate DESIGN.md. DESIGN.md must act as a formal Product Requirements Document (PRD) and include Mermaid.js architecture diagrams mapping out code and infrastructure (e.g., GCP services).  
3. **Approval Gate:** **STOP.** You must wait for human approval on DESIGN.md before writing any code.  
4. **Execution Phase:** Once approved, write code according to CODE_STANDARDS.md.  
5. **Documentation Phase:** After code exists, **rewrite `README.md` in place** so it documents *this project* — its purpose, how to run it, and how to use it — replacing the placeholder shipped with the template. Do **not** duplicate environment/agent setup: link to `GETTING_STARTED.md` for prerequisites, `uv`, and gcloud ADC. Keep `README.md` scannable; route deep docs to `docs/`.

## **📁 File Routing & AI Memory**

You are required to manage your own context using the following files. **Do not put everything in one file.**

* **CODE_STANDARDS.md**: 🛑 **MANDATORY READ** before writing any Python, uv configuration, or infrastructure code.  
* **ROADMAP.md**: If you invent a new feature, optimization, or architectural shift outside the immediate scope of DESIGN.md, **DO NOT build it**. Document it here instead.  
* **DEV_NOTES.md**: Treat this as your Architecture Decision Record (ADR). If you solve a dependency conflict, hack a workaround for a cloud service, or make a non-obvious engineering choice, append a brief explanation here. Read this file before refactoring.
* **`docs/`**: Reserved for deep architectural documentation or MkDocs setup. Keep the root `README.md` scannable; route heavy documentation here.  
* **README.md**: The project's public face. Starts as a template placeholder; you rewrite it in the Documentation Phase to describe the actual project. **This is the one doc you overwrite.**  
* **GETTING_STARTED.md**: The durable template guide (env setup, agent symlinks, workflow). **Do not overwrite it** — link to it from `README.md` instead.

## **🥇 The Golden Rules**

1. **Zero Business Logic in Notebooks:** .ipynb files are strictly for narrative and execution. All core logic must live in .py files inside src/.  
2. **Flat is Better Than Nested:** Write single-responsibility, flat Python modules. Avoid deep object-oriented inheritance.  
3. **uv is the Law:** Manage all dependencies, environments, and lockfiles using uv. Never use pip directly.

Remember: The human must be able to scan and understand every module within seconds. Optimize for human legibility over clever abstractions.