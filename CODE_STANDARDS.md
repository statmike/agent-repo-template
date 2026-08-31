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

## **☁️ 4. GCP & Infrastructure**

* **Source of Truth:** The `pyproject.toml` and `uv.lock` files are the ultimate source of truth for cloud deployments.  
* **Custom Containers:** When generating Dockerfiles for GCP (Vertex AI, Cloud Run, Airflow, KFP), build them around the `uv` environment specification to ensure zero drift between local and cloud execution.  
* Keep cloud client instantiations isolated in their own modules so they can be easily mocked during local testing.
* **Authentication (ADC Only):** NEVER write code that loads explicit Service Account JSON keys. Local development must exclusively use Application Default Credentials (ADC) managed by the host machine (e.g., `gcloud auth application-default login`). All GCP client libraries must be initialized dynamically so they automatically inherit local ADC credentials or the attached cloud service account seamlessly. *(Enforced: `.claude/hooks/block-sa-keys.sh` blocks writing SA key files or loading them via `--key-file` / `GOOGLE_APPLICATION_CREDENTIALS`; `.gitignore` blocks committing them.)*