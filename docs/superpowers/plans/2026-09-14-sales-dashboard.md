# Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 ShopSmart sales dashboard: two KPI scorecards, a monthly sales trend chart, and category/region breakdown charts, reading from `data/sales-data.csv`.

**Architecture:** A two-file split. `calculations.py` holds all data loading and aggregation logic (no Streamlit imports, fully unit-testable). `app.py` holds the Streamlit UI and calls into `calculations.py` for every number and chart it renders.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly (`plotly.express`), pytest.

**Spec:** [docs/superpowers/specs/2026-09-14-sales-dashboard-design.md](../specs/2026-09-14-sales-dashboard-design.md)

## Global Constraints

- Work on the current feature branch (`feature/sales-dashboard`); no git worktree.
- Dependencies managed via a plain `venv/` virtual environment and `requirements.txt` — no uv or conda.
- All calculation logic lives in `calculations.py`, with zero Streamlit imports there, so it is unit-testable in isolation.
- Trend chart aggregates by **month**, not day.
- `compute_total_orders` counts **unique** `order_id` values (`nunique()`), not raw row count.
- A missing `data/sales-data.csv` must produce a plain-language `st.error()` message and `st.stop()` — never a raw traceback.
- No schema/row validation beyond what `pd.read_csv(..., parse_dates=[...])` does natively — the PRD's FR-5 doesn't ask for more.
- Deployment (Streamlit Community Cloud) is the final task, executed by the user from `main` after review and merge — not run by the implementing agent.

---

### Task 1: Project scaffold (TASK-1)

**Files:**
- Create: `requirements.txt`
- Create: `app.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: a runnable `app.py` shell later tasks extend; `requirements.txt` used by every later `pip install`

- [ ] **Step 1: Create `requirements.txt`**

```
streamlit
pandas
plotly
pytest
```

- [ ] **Step 2: Create the virtual environment and install dependencies**

Run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Expected: install completes with no errors. (`venv/` is already covered by `.gitignore`.)

- [ ] **Step 3: Create `app.py` with a title and page config**

```python
import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 4: Verify it runs**

Run: `streamlit run app.py`
Expected: browser opens showing the "ShopSmart Sales Dashboard" title, no errors in the terminal. Stop the server (Ctrl+C) when confirmed.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app.py
git commit -m "TASK-1: scaffold project with requirements.txt and app.py"
```

---

### Task 2: `load_data()` (TASK-1, TDD)

**Files:**
- Create: `calculations.py`
- Create: `tests/test_calculations.py`

**Interfaces:**
- Consumes: `data/sales-data.csv` (existing sample data)
- Produces: `load_data(path="data/sales-data.csv") -> pandas.DataFrame` with a `date` column parsed as datetime; raises `FileNotFoundError` on a missing path. Used by Task 3 (`app.py`) and every later calculation function.

- [ ] **Step 1: Write the failing tests**

```python
import pandas as pd
import pytest

from calculations import load_data


def test_load_data_reads_csv_and_parses_dates():
    df = load_data("data/sales-data.csv")
    assert "date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert len(df) == 482


def test_load_data_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("data/does-not-exist.csv")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'calculations'` (the module doesn't exist yet).

- [ ] **Step 3: Implement `calculations.py`**

```python
"""Data loading and aggregation functions for the sales dashboard."""
import pandas as pd


def load_data(path="data/sales-data.csv"):
    return pd.read_csv(path, parse_dates=["date"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-1: add load_data with tests"
```

---

### Task 3: Wire data loading into app.py, with error handling (TASK-1)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `load_data` from `calculations.py` (Task 2)
- Produces: an `app.py`-level `df` variable every later rendering task uses

- [ ] **Step 1: Update `app.py`**

```python
import streamlit as st

from calculations import load_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Could not find data/sales-data.csv. Make sure the file exists "
        "before running the dashboard."
    )
    st.stop()
```

- [ ] **Step 2: Verify the happy path**

Run: `streamlit run app.py`
Expected: title loads, no error shown (the real CSV is present). Stop the server when confirmed.

- [ ] **Step 3: Verify the missing-file path**

Run:
```bash
mv data/sales-data.csv data/sales-data.csv.bak
streamlit run app.py
```
Expected: page shows the friendly error message, not a traceback. Then restore the file:
```bash
mv data/sales-data.csv.bak data/sales-data.csv
```
Stop the server when confirmed.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-1: load data into app.py with friendly error handling"
```

---

### Task 4: `compute_total_sales()` (TASK-2, TDD)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: a DataFrame with a `total_amount` column
- Produces: `compute_total_sales(df) -> float`; also introduces the `sample_df` pytest fixture reused by Tasks 5, 7, 9, 11

- [ ] **Step 1: Write the failing test (and the shared fixture)**

Add to `tests/test_calculations.py`, replacing the existing import line with:

```python
import pandas as pd
import pytest

from calculations import load_data, compute_total_sales
```

Add the fixture and test (after the imports, before the existing `load_data` tests):

```python
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime([
            "2024-01-05", "2024-01-15", "2024-02-10", "2024-02-20",
        ]),
        "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004"],
        "product": ["Widget A", "Widget B", "Gadget A", "Gadget B"],
        "category": ["Electronics", "Accessories", "Electronics", "Accessories"],
        "region": ["North", "South", "North", "South"],
        "quantity": [1, 2, 1, 3],
        "unit_price": [100.0, 25.0, 200.0, 10.0],
        "total_amount": [100.0, 50.0, 200.0, 30.0],
    })


def test_compute_total_sales_sums_total_amount(sample_df):
    assert compute_total_sales(sample_df) == 380.0
```

- [ ] **Step 2: Run tests to verify the new test fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_total_sales'`.

- [ ] **Step 3: Implement `compute_total_sales`**

Add to `calculations.py`:

```python
def compute_total_sales(df):
    return df["total_amount"].sum()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-2: add compute_total_sales with tests"
```

---

### Task 5: `compute_total_orders()` (TASK-2, TDD)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: a DataFrame with an `order_id` column; reuses `sample_df` fixture from Task 4
- Produces: `compute_total_orders(df) -> int`

- [ ] **Step 1: Write the failing test**

Update the import line in `tests/test_calculations.py`:

```python
from calculations import load_data, compute_total_sales, compute_total_orders
```

Add below the `compute_total_sales` test:

```python
def test_compute_total_orders_counts_unique_order_ids(sample_df):
    assert compute_total_orders(sample_df) == 4
```

- [ ] **Step 2: Run tests to verify it fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_total_orders'`.

- [ ] **Step 3: Implement `compute_total_orders`**

Add to `calculations.py`:

```python
def compute_total_orders(df):
    return df["order_id"].nunique()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-2: add compute_total_orders with tests"
```

---

### Task 6: Render KPI scorecards (TASK-2)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `compute_total_sales`, `compute_total_orders` from `calculations.py`
- Produces: nothing further tasks depend on (leaf UI rendering)

- [ ] **Step 1: Update `app.py`**

Update the import line:

```python
from calculations import load_data, compute_total_sales, compute_total_orders
```

Add after the `try/except` data-loading block:

```python
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Sales", f"${compute_total_sales(df):,.0f}")
with col2:
    st.metric("Total Orders", f"{compute_total_orders(df):,}")
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: two metric cards showing Total Sales (formatted as `$XXX,XXX`) and Total Orders (formatted with thousands separators, e.g. `482`). Stop the server when confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-2: render KPI scorecards"
```

---

### Task 7: `monthly_sales_trend()` (TASK-3, TDD)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: a DataFrame with `date` and `total_amount` columns; reuses `sample_df` fixture from Task 4
- Produces: `monthly_sales_trend(df) -> pandas.DataFrame` with columns `month_label` (str, e.g. `"Jan 2024"`) and `total_amount` (float), sorted chronologically

- [ ] **Step 1: Write the failing test**

Update the import line:

```python
from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
)
```

Add:

```python
def test_monthly_sales_trend_aggregates_by_month(sample_df):
    result = monthly_sales_trend(sample_df)
    assert list(result["month_label"]) == ["Jan 2024", "Feb 2024"]
    assert list(result["total_amount"]) == [150.0, 230.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ImportError: cannot import name 'monthly_sales_trend'`.

- [ ] **Step 3: Implement `monthly_sales_trend`**

Add to `calculations.py`:

```python
def monthly_sales_trend(df):
    monthly = df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M")
    result = monthly.groupby("month")["total_amount"].sum().reset_index()
    result = result.sort_values("month")
    result["month_label"] = result["month"].dt.strftime("%b %Y")
    return result[["month_label", "total_amount"]].reset_index(drop=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculations.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-3: add monthly_sales_trend with tests"
```

---

### Task 8: Render the sales trend chart (TASK-3)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `monthly_sales_trend` from `calculations.py`; `plotly.express`
- Produces: nothing further tasks depend on

- [ ] **Step 1: Update `app.py`**

Add `import plotly.express as px` near the top (after `import streamlit as st`), update the calculations import:

```python
import plotly.express as px
import streamlit as st

from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
)
```

Add after the KPI columns block:

```python
st.subheader("Sales Trend Over Time")
trend_df = monthly_sales_trend(df)
fig_trend = px.line(trend_df, x="month_label", y="total_amount", markers=True)
fig_trend.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(fig_trend, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: a line chart below the KPIs showing monthly sales across the 12 months in the data, with hover tooltips showing exact values. Stop the server when confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: render sales trend chart"
```

---

### Task 9: `sales_by_category()` (TASK-4, TDD)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: a DataFrame with `category` and `total_amount` columns; reuses `sample_df` fixture from Task 4
- Produces: `sales_by_category(df) -> pandas.DataFrame` with columns `category`, `total_amount`, sorted descending by `total_amount`

- [ ] **Step 1: Write the failing test**

Update the import line:

```python
from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
    sales_by_category,
)
```

Add:

```python
def test_sales_by_category_sorted_descending(sample_df):
    result = sales_by_category(sample_df)
    assert list(result["category"]) == ["Electronics", "Accessories"]
    assert list(result["total_amount"]) == [300.0, 80.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ImportError: cannot import name 'sales_by_category'`.

- [ ] **Step 3: Implement `sales_by_category`**

Add to `calculations.py`:

```python
def sales_by_category(df):
    result = df.groupby("category")["total_amount"].sum().reset_index()
    return result.sort_values("total_amount", ascending=False).reset_index(drop=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculations.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-4: add sales_by_category with tests"
```

---

### Task 10: Render the category breakdown chart (TASK-4)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by_category` from `calculations.py`
- Produces: the `col3`, `col4` two-column row that Task 12 (region chart) fills in

- [ ] **Step 1: Update `app.py`**

Update the calculations import:

```python
from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
    sales_by_category,
)
```

Add after the trend chart block:

```python
col3, col4 = st.columns(2)
with col3:
    st.subheader("Sales by Category")
    category_df = sales_by_category(df)
    fig_cat = px.bar(category_df, x="category", y="total_amount")
    fig_cat.update_layout(xaxis_title="Category", yaxis_title="Sales ($)")
    st.plotly_chart(fig_cat, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: a bar chart in the left column showing sales by category, sorted highest to lowest, with hover tooltips. The right column is empty for now (filled in by Task 12). Stop the server when confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-4: render category breakdown chart"
```

---

### Task 11: `sales_by_region()` (TASK-5, TDD)

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`

**Interfaces:**
- Consumes: a DataFrame with `region` and `total_amount` columns; reuses `sample_df` fixture from Task 4
- Produces: `sales_by_region(df) -> pandas.DataFrame` with columns `region`, `total_amount`, sorted descending by `total_amount`

- [ ] **Step 1: Write the failing test**

Update the import line:

```python
from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
    sales_by_category,
    sales_by_region,
)
```

Add:

```python
def test_sales_by_region_sorted_descending(sample_df):
    result = sales_by_region(sample_df)
    assert list(result["region"]) == ["North", "South"]
    assert list(result["total_amount"]) == [300.0, 80.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL — `ImportError: cannot import name 'sales_by_region'`.

- [ ] **Step 3: Implement `sales_by_region`**

Add to `calculations.py`:

```python
def sales_by_region(df):
    result = df.groupby("region")["total_amount"].sum().reset_index()
    return result.sort_values("total_amount", ascending=False).reset_index(drop=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculations.py -v`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add calculations.py tests/test_calculations.py
git commit -m "TASK-5: add sales_by_region with tests"
```

---

### Task 12: Render the region breakdown chart (TASK-5)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by_region` from `calculations.py`; the `col4` column created in Task 10
- Produces: nothing further tasks depend on

- [ ] **Step 1: Update `app.py`**

Update the calculations import:

```python
from calculations import (
    load_data,
    compute_total_sales,
    compute_total_orders,
    monthly_sales_trend,
    sales_by_category,
    sales_by_region,
)
```

Add the `with col4:` block directly after the existing `with col3:` block (same `col3, col4 = st.columns(2)` line from Task 10, not duplicated):

```python
with col4:
    st.subheader("Sales by Region")
    region_df = sales_by_region(df)
    fig_reg = px.bar(region_df, x="region", y="total_amount")
    fig_reg.update_layout(xaxis_title="Region", yaxis_title="Sales ($)")
    st.plotly_chart(fig_reg, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: both category (left) and region (right) bar charts render side by side, each sorted highest to lowest, with hover tooltips. Stop the server when confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-5: render region breakdown chart"
```

---

### Task 13: Full verification against the PRD (TASK-6)

**Files:** none (verification only; fix-and-recommit if something fails)

**Interfaces:**
- Consumes: the complete `app.py` and `calculations.py` from Tasks 1-12
- Produces: nothing further tasks depend on

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all tests PASS (7 tests: 2 for `load_data`, 1 each for `compute_total_sales`, `compute_total_orders`, `monthly_sales_trend`, `sales_by_category`, `sales_by_region`).

- [ ] **Step 2: Run the app and check it against the PRD's Acceptance Criteria**

Run: `streamlit run app.py`

Check each item from `prd/ecommerce-analytics.md`'s Acceptance Criteria section against the running page:
- [ ] KPIs visible: Total Sales and Total Orders displayed prominently
- [ ] Trend chart works: line chart shows sales over time with correct data
- [ ] Category chart works: bar chart shows sales by category, sorted by value
- [ ] Region chart works: bar chart shows sales by region, sorted by value
- [ ] Data loads correctly: values match the PRD's Expected Output table (Total Sales ~$116,500; Total Orders 482; Top Category Electronics; Regions shown North/South/East/West)
- [ ] No errors: dashboard runs without errors or warnings
- [ ] Professional appearance: suitable for an executive presentation

Stop the server when confirmed.

- [ ] **Step 3: If anything fails, fix it and commit**

If any acceptance criterion above doesn't hold, fix the responsible code in `app.py` or `calculations.py`, rerun `pytest -v` and the manual check, then:

```bash
git add app.py calculations.py
git commit -m "TASK-6: fix acceptance criteria gap found in verification"
```

If everything already passes, there is nothing to commit for this step.

---

### Task 14: Deploy to Streamlit Community Cloud (TASK-6 — user-executed)

**This task is executed by you, not by the implementing agent.** It runs after the branch is reviewed and merged into `main` (per the project's ground rules), so it is out of scope for `executing-plans`/`subagent-driven-development` to run automatically. It's recorded here so the plan covers every `TASKS.md` milestone end to end.

- [ ] Merge `feature/sales-dashboard` into `main` and push `main` to GitHub (covered by the tutorial's own merge step, not by this plan)
- [ ] Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
- [ ] Click "New app", select this repository, branch `main`, and main file path `app.py`
- [ ] Click "Deploy" and wait for the build to finish
- [ ] Open the resulting public URL and re-check it against the PRD's Acceptance Criteria (same checklist as Task 13, Step 2)
- [ ] Record the public URL wherever `TASKS.md`'s TASK-6 Notes line expects it
