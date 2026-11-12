---
name: consolidate
description: >-
  Executes Phase 7 (Consolidation Phase) at the end of an increment to harvest
  decisions, sweep code and documentation residue, refresh affected notebooks,
  run the quality and Current-State Doctrine gates, and update .agents/status.md.
  Use before finishing any implementation increment or committing work.
---

# Consolidate Increment (Phase 7)

An increment is not complete until every shipped artifact describes only present behavior and all automated gates pass.

## Step 1: Harvest Decisions & Backlog

1. **Architectural choices & workarounds** -> append a brief dated entry (`## YYYY-MM-DD — Title`) to `.agents/decisions.md` explaining what was chosen, why, and what alternatives were rejected.
2. **Deferred ideas & out-of-scope improvements** -> move to `.agents/status.md` under `## Later`.
3. **Remaining committed tasks** -> record in `.agents/status.md` under `## Now` or `## Next`.

## Step 2: Sweep Code & Shipped Docs

1. Remove commented-out blocks, unreachable helpers, unused flags/arguments, and any inline `TODO`/`FIXME`/`XXX`/`HACK` comments from `src/` and `tests/`.
2. Delete placeholder template samples (`src/example.py`, `tests/test_example.py`) once real project modules and tests exist.
3. Audit `README.md` and `docs/` so every sentence is written in **present tense** without change-narration ("previously", "we switched to", "used to") and without references to `.agents/idea.md`, `.agents/plan.md`, or `.agents/decisions.md`.

## Step 3: Refresh Affected Notebooks

If `notebooks/*.ipynb` exist and any imported `src/` module changed during this increment:
1. Re-execute affected notebooks top-to-bottom (`1..N`) from a fresh `uv` kernel.
2. Inspect committed cell outputs to confirm zero hardcoded real GCP project IDs, emails, or credentials leaked into output cells.

## Step 4: Run Quality & Hygiene Gates

1. Run the project gate and fix every failure:
   ```bash
   uv run python .agents/check.py
   ```
   *(Or `python3 .agents/check.py` for non-Python projects.)*
2. If operating in a Git repository, check `git status` and `git diff` to verify zero untracked scratch artifacts or accidental secret files.

## Step 5: Rewrite `.agents/status.md`

Rewrite `.agents/status.md` in place so *Current State*, *Now*, *Next*, *Later*, and *Known Gaps & Caveats* accurately match the codebase as it stands right now, enabling the next session (in any agent tool) to pick up cold.
