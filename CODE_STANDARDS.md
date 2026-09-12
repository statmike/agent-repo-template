# **Code & Infrastructure Standards**

This document defines the strict engineering standards for this repository. The AI Agent must adhere to these rules at all times.

## **🐍 1. Python Architecture: Flat & Functional**

* **Single Responsibility:** Each `.py` file in `src/` should do exactly one thing (e.g., `bq_client.py`, `data_cleaner.py`).  
* **Avoid Deep OOP:** Do not create deep class hierarchies (e.g., `AbstractBaseDataProcessor`). Prefer procedural, functional programming with simple data structures (dataclasses, dicts).  
* **Human-Scannable:** A human developer should be able to open any module and understand its purpose top-to-bottom in under 30 seconds.  
* **Shallow Cross-References:** Understanding one module must not require opening a chain of others. If reading `a.py` sends the reader to `b.py` which sends them to `c.py`, collapse it — at most **one hop** to follow.  
* **Fewer, Fuller Modules:** Prefer a handful of well-named modules over many fragments. Split only for a genuinely distinct responsibility — never merely to shrink a file. Cohesion beats granularity; "single responsibility" is not a mandate to fragment.  
* **One-Way Dependencies:** No circular imports. Leaf modules (clients, I/O) must never import orchestration modules; calls flow down, data flows back up.  
* **No Grab-Bags:** Never create `utils.py`, `helpers.py`, or `common.py`. A little duplication is better than a shared-helper web that binds every module together.  
* **Type Hinting:** Use strict Python type hinting for all function signatures.

## **📦 2. Dependency Management: `uv`**

* We exclusively use `uv` for package and environment management.  
* All dependencies must be tracked in `pyproject.toml`.  
* Ensure `uv.lock` is updated whenever a package is added.  
* Do not generate `requirements.txt` unless specifically requested for a legacy system constraint.

## **📓 3. Jupyter Notebooks (The Runners)**

* Notebooks live in the `notebooks/` directory.  
* **Prohibition:** NEVER author core business logic, complex data transformations, or API integrations inside a notebook cell.  
* **Intended Use:** Notebooks are exclusively for narrative documentation, data exploration, and acting as "runners." They must `import` their capabilities from the `src/` directory.  
* The notebook kernel must be driven by the local `uv` environment.  
* **Outputs Are Committed On Purpose:** A notebook is an *illustration* — inline markdown plus the real results of calling `src/`. Its outputs are part of that illustration, so they are committed, never stripped. A reader must be able to see what the code produces without running it.  
* **Outputs Must Match The Code They Call:** That makes a stale output a lie about present behavior. When you change a module a notebook imports, **re-run the notebook top to bottom** and commit the refreshed outputs in the same change. A notebook showing results from an older `src/` is the same defect as a doc written in past tense (§5).  
* **Run In Order, Run Completely:** Ship notebooks that execute cleanly from a fresh kernel, cell 1 to cell N. No scattered execution counts from re-running one cell, no half-executed notebooks, no cells left erroring.

## **☁️ 4. GCP & Infrastructure**

* **Source of Truth:** The `pyproject.toml` and `uv.lock` files are the ultimate source of truth for cloud deployments.  
* **Custom Containers:** When generating Dockerfiles for GCP (Vertex AI, Cloud Run, Airflow, KFP), build them around the `uv` environment specification to ensure zero drift between local and cloud execution.  
* Keep cloud client instantiations isolated in their own modules so they can be easily mocked during local testing.
* **Authentication (ADC Only):** NEVER write code that loads explicit Service Account JSON keys. Local development must exclusively use Application Default Credentials (ADC) managed by the host machine (e.g., `gcloud auth application-default login`). All GCP client libraries must be initialized dynamically so they automatically inherit local ADC credentials or the attached cloud service account seamlessly. *(Enforced: `.claude/hooks/block-sa-keys.sh` blocks writing SA key files or loading them via `--key-file` / `GOOGLE_APPLICATION_CREDENTIALS`; `.gitignore` blocks committing them.)*

## **🧹 5. Current-State Hygiene**

The codebase describes what the system **is**, never how it got here. Iterative development leaves residue; removing it is part of finishing, not a separate cleanup project.

* **No Commented-Out Code:** Delete it. Git history is the archive. *(Enforced: ruff `ERA001`.)*  
* **No Inline Backlog:** No `TODO`, `FIXME`, `XXX`, or `HACK` comments. Work that must still happen goes in `STATUS.md` under *Now* or *Next*, where it is visible and tracked — not buried in a file nobody greps. *(Enforced: ruff `FIX`.)*  
* **No Change-Narration Comments:** Comments explain what the code does and why it is the way it is — never what it replaced. "Switched from pandas because…" is an ADR; put it in `DEV_NOTES.md`.  
* **No Orphans:** Remove unreachable functions, unused arguments, and flags left over from abandoned experiments. *(Enforced: ruff `ARG`, `F401`.)*  
* **No Design-Doc References:** Code and docs must never point at `DESIGN.md` or `IDEA.md`. Those are snapshots of intent at a moment; the code is now the specification. *(Enforced in CI.)*