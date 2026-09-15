# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard.
Each milestone moves through To Do -> In Progress -> Done.

## Definition of Done (must hold before any milestone moves to Done)
- Acceptance criteria met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the message

## To Do
- [ ] **TASK-5: Regional breakdown**
  - [ ] Bar chart of sales by region, sorted highest to lowest, with interactive tooltips
  - Commit:
- [ ] **TASK-6: Test and deploy**
  - [ ] Dashboard runs without errors, loads within 5 seconds, and matches the PRD's Expected Output values
  - [ ] Deployed to Streamlit Community Cloud and accessible via public URL
  - Commit:

## In Progress

## Done
- [x] **TASK-4: Category breakdown**
  - [x] Bar chart of sales by product category, sorted highest to lowest, with interactive tooltips
  - Commit: 91b0c5a
  - Notes: Clean — implementation followed the plan as written; sorted descending, top category Electronics ($42,683.67), matching the PRD's expected output. Same recurring template mismatch (TASK-2 named in the finalize sentence) — treated as TASK-4 throughout per the pattern you confirmed on TASK-3.
- [x] **TASK-3: Sales trend chart**
  - [x] Line chart of sales over time renders from the data, with interactive tooltips showing exact values
  - Commit: beb6531
  - Notes: Clean — implementation followed the plan as written; 12 months, chronologically sorted, monthly totals sum to the same $116,500 as TASK-2. (Minor: your request named TASK-3 in the first sentence but TASK-2 in the finalize sentence — flagged it and confirmed you meant TASK-3 throughout before starting.)
- [x] **TASK-2: KPI scorecards**
  - [x] Total Sales and Total Orders displayed prominently, formatted as currency/numbers with separators
  - Commit: 730a17e
  - Notes: Clean — implementation followed the plan as written; computed values matched the PRD's expected output ($116,500 / 482 orders) on the first run. (Minor: the plan path you gave, 2026-09-08-sales-dashboard.md, doesn't exist — used the 2026-09-14 file instead, per your confirmation.)
- [x] **TASK-1: Project setup and data loading**
  - [x] App runs with `streamlit run app.py` and shows a title
  - [x] Loads `data/sales-data.csv`; handles standard CSV formatting (date, numeric, categorical columns)
  - Commit: e2f4e37
  - Notes: Claude's `kill $(cat pid_file)` after backgrounding the dev server with `&` didn't fully stop it — two streamlit processes survived on ports 8501/8502 and had to be `pkill`ed manually before the next run. No code issues; implementation followed the plan as written.
/statusline show the current git branch, the folder, the model, the reasoning effort, and the context usage



