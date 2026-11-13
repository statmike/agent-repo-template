---
trigger: always_on
description: "Jupyter notebook runner standards: numbered narrative walkthroughs, zero business logic in cells, and fresh committed outputs."
---

# Jupyter Notebook Standards

Applies whenever `.ipynb` notebooks are used in `notebooks/`. Delete this rule file (and `notebooks/`) if the project does not use notebooks.

* **Zero Business Logic in Cells:** Never author core transformations, client logic, modeling routines, or reusable algorithms inside `.ipynb` cells. All core capabilities live in `src/` and are imported by the notebook.
* **Clear Narrative Ordering:** Store notebooks in `notebooks/` using numbered, descriptive filenames when a sequence exists (`01_explore.ipynb`, `02_train_and_evaluate.ipynb`), backed by the project's local `uv` `.venv` kernel.
* **Committed Outputs Are Current-State Claims:** Notebook cell outputs are committed intentionally so readers can inspect real results, tables, and plots without executing code — never strip outputs globally.
* **Refresh Outputs Whenever `src/` Changes:** Whenever an increment modifies a `src/` module imported by a notebook, re-execute that notebook top-to-bottom (`1..N`) from a fresh kernel, verify zero leaked project IDs or secrets in cell outputs, and commit the refreshed notebook in the same change.
