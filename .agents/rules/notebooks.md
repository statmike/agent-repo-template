---
trigger: always_on
description: "Jupyter notebook runner standards: zero business logic in cells and fresh committed outputs."
---

# Jupyter Notebook Standards

Applies whenever `.ipynb` notebooks are used in `notebooks/`. Delete this rule file (and `notebooks/`) if the project does not use notebooks.

* **Zero Business Logic in Cells:** Never author core transformations, client logic, or reusable algorithms inside `.ipynb` cells. All core capabilities live in `src/` and are imported by the notebook.
* **Intended Role:** Notebooks live in `notebooks/` and act strictly as narrative walkthroughs, exploratory runners, and visual illustrations of `src/`, backed by the project's local `uv` `.venv` kernel.
* **Committed Outputs Are Current-State Claims:** Notebook cell outputs are committed intentionally so readers can inspect real results without executing code — never strip outputs globally.
* **Refresh Outputs Whenever `src/` Changes:** Whenever an increment modifies a `src/` module imported by a notebook, re-execute that notebook top-to-bottom (`1..N`) from a fresh kernel, verify zero leaked project IDs or secrets in cell outputs, and commit the refreshed notebook in the same change.
