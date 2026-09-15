# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial project (see `README.md`) that teaches a PRD → `TASKS.md` → brainstorming → writing-plans → executing-plans → commit → push → review/merge → deploy workflow using Claude Code's Superpowers skills. The deliverable being built through that workflow is a Streamlit sales dashboard (`app.py` + `calculations.py`). Tutorial instructions live in `pre-work-setup.md` and `workshop-build-deploy.md`; `codex-companion.md` is an alternate-tool variant, not part of the app itself.

## Commands

```bash
source venv/bin/activate              # activate the venv (plain venv/requirements.txt, not uv/conda)
pip install -r requirements.txt

pytest -v                             # run the full test suite
pytest tests/test_calculations.py -v  # run just the calculations tests
pytest tests/test_calculations.py::test_compute_total_sales_sums_total_amount -v  # single test

streamlit run app.py --server.headless true   # run the dashboard (headless avoids the first-run
                                               # email prompt blocking a backgrounded shell)
```

There is no lint/format command configured in this repo.

## Architecture

**Two-file split, enforced deliberately:**
- `calculations.py` — all data loading and aggregation logic. **Zero Streamlit imports**, so every function is unit-testable in isolation with plain DataFrames. Each function takes a DataFrame and returns a DataFrame or scalar; none of them touch `st.*`.
- `app.py` — the Streamlit UI only. Imports from `calculations.py` and calls a function for every number and chart it renders; it never does its own pandas aggregation inline.

New dashboard features should follow this split: add the computation to `calculations.py` with a test in `tests/test_calculations.py`, then wire it into `app.py`.

**Data contract:** `data/sales-data.csv` has columns `date, order_id, product, category, region, quantity, unit_price, total_amount`. `load_data()` parses `date` and raises `FileNotFoundError` on a missing path — `app.py` catches that specific exception and shows a friendly `st.error()` + `st.stop()` rather than a raw traceback. There's no schema/row validation beyond what `pd.read_csv(..., parse_dates=[...])` does natively.

**Aggregation gotchas that aren't obvious from the column names alone:**
- `compute_total_orders` counts **unique** `order_id` values (`.nunique()`), not row count — one order can span multiple line-item rows.
- The trend chart aggregates by **month** (`monthly_sales_trend`), not day.
- `sales_by_category` / `sales_by_region` are intentionally near-duplicate groupby/sort functions rather than one parameterized helper — kept separate for independent testability and self-documenting call sites in `app.py`.

**Tests** live in `tests/test_calculations.py` and share a hand-built `sample_df` fixture (4 rows, round numbers) so each new aggregation function's expected value is easy to hand-verify. `pytest.ini` sets `pythonpath = .` so `calculations` imports directly without a package install.

## The planning workflow (Superpowers)

Work is driven by three documents, in this order:
1. `prd/ecommerce-analytics.md` — the requirements, including the Expected Output table (Total Sales ~$116,500, Total Orders 482, Top Category Electronics, Regions North/South/East/West) used to sanity-check implementation against real data.
2. `docs/superpowers/specs/*-design.md` — brainstorming output.
3. `docs/superpowers/plans/*.md` — the implementation plan, broken into small numbered tasks with explicit TDD steps (write failing test → verify it fails → implement → verify it passes → commit) and exact commit messages to use. **Read the relevant plan file before implementing a task** — it specifies exact function signatures, test expectations, and commit message text that this repo's history follows precisely.

`TASKS.md` is the tracking board, separate from the plan file: milestones (`TASK-1`, `TASK-2`, ...) move through `## To Do` → `## In Progress` → `## Done`. Its Definition of Done requires: acceptance criteria met, app runs locally, and changes committed with the milestone ID in the message. When a milestone is finalized, its entry gets Commit (the hash of the last *code* commit, not a board-only commit) and Notes (anything that went wrong or was changed, or "clean") lines added.

Per the plan's Global Constraints: work happens directly on the feature branch (no git worktree), and deployment to Streamlit Community Cloud is a manually-run, user-executed step from `main` after merge — not something to automate.

## Lessons

Distilled from the Notes lines recorded in `TASKS.md` while building this dashboard:

- **Stop the dev server with `pkill -f "streamlit run app.py"`, not `kill $(cat pid_file)`.** A PID captured from a backgrounded `&` job doesn't reliably map to the actual Streamlit process — killing it can leave orphaned servers running on 8501/8502 that then collide with the next run.
- **Verify a referenced plan/spec file path exists before using it.** A stale or mistyped date in a filename (e.g. copied from an earlier template) won't match what's actually in `docs/superpowers/plans/` or `docs/superpowers/specs/` — confirm the file first rather than assuming the name is current.
- **Cross-check task IDs within a single request before acting.** A templated request can name two different milestones across sentences (e.g. "verify TASK-N is committed... then update TASK-2..."). Flag the mismatch and confirm the intended target before implementing or finalizing either half.
- **Deployment (TASK-6) is user-executed, not automated.** It requires interactive GitHub sign-in in a browser at share.streamlit.io. Don't attempt it, and don't check off its board criterion or move TASK-6 to Done without the user confirming the deploy actually happened.
- **Subjective acceptance criteria (e.g. "professional appearance") can't be verified via logs, curl, or pytest.** Say so explicitly rather than marking them passed on the strength of an automated check that doesn't actually test them.

## Commit conventions

Commit messages are prefixed with the milestone ID, e.g. `TASK-2: add compute_total_sales with tests`. Code and `TASKS.md` board updates are typically committed separately (e.g. `TASK-2: render KPI scorecards` for the code, then `TASK-2: mark done on the board` for the tracking update).
