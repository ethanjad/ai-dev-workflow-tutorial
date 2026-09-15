# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard.
Each milestone moves through To Do -> In Progress -> Done.

## Definition of Done (must hold before any milestone moves to Done)
- Acceptance criteria met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the message

## To Do
- [ ] **TASK-3: Sales trend chart**
  - [ ] Line chart of sales over time renders from the data, with interactive tooltips showing exact values
  - Commit:
- [ ] **TASK-4: Category breakdown**
  - [ ] Bar chart of sales by product category, sorted highest to lowest, with interactive tooltips
  - Commit:
- [ ] **TASK-5: Regional breakdown**
  - [ ] Bar chart of sales by region, sorted highest to lowest, with interactive tooltips
  - Commit:
- [ ] **TASK-6: Test and deploy**
  - [ ] Dashboard runs without errors, loads within 5 seconds, and matches the PRD's Expected Output values
  - [ ] Deployed to Streamlit Community Cloud and accessible via public URL
  - Commit:

## In Progress

## Done
- [x] **TASK-2: KPI scorecards**
  - [x] Total Sales and Total Orders displayed prominently, formatted as currency/numbers with separators
  - Commit: 730a17e
- [x] **TASK-1: Project setup and data loading**
  - [x] App runs with `streamlit run app.py` and shows a title
  - [x] Loads `data/sales-data.csv`; handles standard CSV formatting (date, numeric, categorical columns)
  - Commit: e2f4e37
  - Notes: Claude's `kill $(cat pid_file)` after backgrounding the dev server with `&` didn't fully stop it — two streamlit processes survived on ports 8501/8502 and had to be `pkill`ed manually before the next run. No code issues; implementation followed the plan as written.
/statusline show the current git branch, the folder, the model, the reasoning effort, and the context usage



