# Customer Analytics Dashboard — Project Summary

## What It Is

A local, single-user data analytics dashboard. Upload business data files (customers, orders, payments) in CSV or XLSX format, persist them to a local SQLite database, and explore them through an interactive web UI with charts and KPI cards.

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Frontend | Streamlit 1.32+ |
| Database | SQLite (via `sqlite3`) |
| Data | Pandas, NumPy |
| Charts | Matplotlib, Seaborn |
| Linting | Ruff |
| Type-checking | Mypy |
| Tests | `unittest` (built-in) |

## Features

### Upload Page
- File picker for `.csv` / `.xlsx`
- Dropdown to target table: customers, orders, payments
- Persistence toggle: SQLite (permanent) or in-memory (session only)
- Schema validation with error messages
- Data preview (first 5 rows)
- Confirm-and-load workflow
- Row counts per table, clear-all button

### Overview Page
- 4 KPI cards: Total Customers, Total Orders, Total Revenue, Avg Credit Limit
- Customers by Country bar chart
- Revenue Over Time line chart
- Top 10 Customers by Credit Limit horizontal bar chart

### Customers Page
- Credit Limit Distribution histogram
- Customers by Country pie/bar chart
- Top 10 Cities horizontal bar chart
- Sales Rep Workload horizontal bar chart
- Sidebar filters: country, sales rep
- Sortable, filterable data table

### Orders Page
- Orders Over Time line chart
- Order Status Breakdown pie chart
- Average Order Value Trend line chart
- Top Customers by Order Count bar chart
- Sidebar filters: date range, status
- Sortable data table

### Payments Page
- Payments Over Time line chart
- Payment Amount Distribution histogram
- Credit Limit vs Total Payments comparison
- Late Payments indicator (shippedDate > requiredDate)
- Sidebar filters: date range, customer
- Sortable data table

## Project Structure

```
chinu_project/
  app.py                     # Entry point — page config + DB init
  config.py                  # Global constants
  launcher.py                # Opens Streamlit in Chrome
  pyproject.toml             # Ruff + Mypy config
  requirements.txt           # Dependencies
  .gitignore                 # Git ignore rules
  AGENTS.md                  # AI agent instructions
  SPECIFICATION.md           # Original spec
  README.md                  # Setup & usage guide
  database/
    __init__.py
    db_manager.py            # DB connection, init, helpers
    schema.sql               # CREATE TABLE statements
  ingestion/
    __init__.py
    file_parser.py           # Read CSV/XLSX → DataFrame
    validator.py             # Schema & type validation
    loader.py                # DataFrame → SQLite writer
  analysis/
    __init__.py
    summary_stats.py         # Cross-table KPIs
    customer_analysis.py     # Customer-level EDA
    order_analysis.py        # Order-level EDA
    payment_analysis.py      # Payment-level EDA
  visualisation/
    __init__.py
    charts.py                # Matplotlib chart builders
    kpi_cards.py             # Streamlit KPI components
  pages/
    01_upload.py             # Upload workflow
    02_overview.py           # Dashboard overview
    03_customers.py          # Customer analysis
    04_orders.py             # Orders analysis
    05_payments.py           # Payments analysis
  tests/
    test_validator.py        # 10 validation tests
    test_loader.py           # 3 loader tests
    test_analysis.py         # 14 analysis tests
  data/                      # SQLite DB auto-created here
  assets/                    # Optional custom CSS
  document/
    summary.md               # This file
    architecture.md          # Function-level reference
```

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python launcher.py           # Opens http://localhost:8501
```

## Quality Checks

```bash
ruff check .                 # Lint
mypy . --ignore-missing-imports  # Type check
python -m unittest discover tests -v  # Run tests
```
