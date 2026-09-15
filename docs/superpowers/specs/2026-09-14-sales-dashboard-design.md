# Design: E-Commerce Sales Dashboard

**Status:** Approved
**Source PRD:** [prd/ecommerce-analytics.md](../../../prd/ecommerce-analytics.md)
**Task board:** [TASKS.md](../../../TASKS.md)
**Date:** 2026-09-14

## Summary

A single-page Streamlit dashboard reading `data/sales-data.csv` and
showing two KPI scorecards (Total Sales, Total Orders), a monthly sales
trend line chart, and two sorted bar charts (sales by category, sales
by region). This covers Phase 1 of the PRD only; Phase 2 items
(auth, database integration, exports, filtering, etc.) are explicitly
out of scope.

## Ground rules

- Work on the current feature branch (`feature/sales-dashboard`); no git worktree.
- Plain Python virtual environment in `venv/`, dependencies pinned in `requirements.txt` (no uv or conda).
- Data calculations live in their own module with pytest tests.
- Code stays simple and readable.
- Deployment (Streamlit Community Cloud) is the final plan step, executed by the user from `main` after merge — not part of the automated build.

## Architecture

```
app.py                      Streamlit UI: page config, layout, calls
                             into calculations.py, renders KPIs/charts
calculations.py             load_data(), compute_total_sales(),
                             compute_total_orders(), monthly_sales_trend(),
                             sales_by_category(), sales_by_region()
tests/test_calculations.py  pytest tests for every function above
data/sales-data.csv         existing sample data, unchanged
requirements.txt            streamlit, pandas, plotly, pytest
venv/                       local virtual environment (gitignored)
```

`calculations.py` has no Streamlit imports and no UI code — every
function takes a DataFrame (or, for `load_data`, a file path) and
returns a plain value or DataFrame. That boundary is what makes the
module unit-testable without starting the app, and is the "own module
with pytest tests" ground rule made concrete.

## Data layer (`calculations.py`)

| Function | Behavior |
|---|---|
| `load_data(path="data/sales-data.csv")` | Reads the CSV with pandas, parses `date` as a datetime column. Raises `FileNotFoundError` on a missing file — caught by the caller (`app.py`), not here. |
| `compute_total_sales(df)` | `df['total_amount'].sum()` |
| `compute_total_orders(df)` | `df['order_id'].nunique()` (protects against accidental duplicate rows, vs. `len(df)`) |
| `monthly_sales_trend(df)` | Groups by `df['date'].dt.to_period('M')`, sums `total_amount`, returns a chronologically sorted DataFrame with a readable month label (e.g. "Jan 2024") for the x-axis |
| `sales_by_category(df)` | Groups by `category`, sums `total_amount`, sorted descending |
| `sales_by_region(df)` | Groups by `region`, sums `total_amount`, sorted descending |

**Trend granularity:** monthly (not daily). With 482 records over 12
months, monthly aggregation gives a smoother, more readable trend line
for an executive-meeting audience (PRD user story: Finance Manager
Sarah, CEO David) and matches the PRD's own mockup (`Jan Feb Mar Apr
...` axis labels).

## UI layer (`app.py`)

- `st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")`.
- Title header, then `load_data()` wrapped in `try/except FileNotFoundError`.
- Two `st.columns(2)` with `st.metric()` for Total Sales (formatted `$X,XXX,XXX`) and Total Orders (formatted with thousands separators).
- `st.plotly_chart()` for the monthly trend line, full width, with interactive tooltips.
- Two more `st.columns(2)` below it: category bar chart and region bar chart (Plotly, hover tooltips, sorted descending — sort order comes from the data layer, not re-applied in the UI).

## Error handling

**Missing or unreadable data file:** `app.py` catches
`FileNotFoundError` from `load_data()`, shows a plain-language message
via `st.error()` (e.g. "Could not find data/sales-data.csv. Make sure
the file exists before running the dashboard.") instead of a raw
traceback, then calls `st.stop()` so no chart code runs against
missing data. This satisfies NFR-2 ("no training required for basic
usage") for the one failure mode the PRD's acceptance criteria and
FR-5 call out.

**Malformed rows:** The PRD's FR-5 asks only that the app "handle
standard CSV formatting" — it does not ask for schema validation
beyond what pandas' `parse_dates` naturally enforces. No additional
validation logic is added; doing so would be scope the PRD doesn't
require.

## Testing

`tests/test_calculations.py` covers every function in
`calculations.py` using small, hand-built DataFrames (a few rows
spanning at least 2 categories, regions, and months), asserting exact
expected sums, counts, and sort order. This is the TDD-flagged part of
the build: a failing test is written first, then the function that
makes it pass.

`app.py` is not unit tested. Streamlit UI code and chart rendering
aren't meaningfully testable this way; verification is manual (running
`streamlit run app.py` and checking against the PRD's Acceptance
Criteria and Expected Output table).

## Deployment (out of scope for the implementation plan)

The plan's final step names the deployment task (Streamlit Community
Cloud, per NFR-5) but marks it as user-executed: the user runs it
themselves from `main`, after review and merge. No deployment
automation is part of this build.

## Milestone mapping

This design covers all of `TASKS.md`:

- **TASK-1** (setup + data loading) → `load_data()`, `requirements.txt`, `venv/`, app skeleton with title and error handling.
- **TASK-2** (KPI scorecards) → `compute_total_sales()`, `compute_total_orders()`, the two `st.metric()` cards.
- **TASK-3** (sales trend chart) → `monthly_sales_trend()`, the Plotly line chart.
- **TASK-4** (category breakdown) → `sales_by_category()`, the Plotly bar chart.
- **TASK-5** (regional breakdown) → `sales_by_region()`, the Plotly bar chart.
- **TASK-6** (test and deploy) → full test suite run, manual verification against PRD Acceptance Criteria/Expected Output, then user-executed deployment.
