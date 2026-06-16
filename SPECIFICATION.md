# Customer Analytics Dashboard — Project Specification

## 1. Project Overview

A local data analytics dashboard that allows a user to upload business data files (customers, orders, payments) in CSV/XLSX format, persist them to a local SQLite database, and explore them through an interactive EDA-driven Streamlit frontend with Matplotlib/Seaborn visualisations.

- **100% free, open-source stack**
- **Runs entirely on local machine — no cloud, no external services**
- **Target dataset size:** Medium (hundreds to a few thousand rows per table)
- **Target users:** Single user or small internal team

---

## 2. Confirmed Stack

| Layer | Technology | Version (minimum) |
|---|---|---|
| Language | Python | 3.10+ |
| Frontend / UI | Streamlit | 1.32+ |
| Database | SQLite | Built-in (Python `sqlite3`) |
| Data Layer | Pandas `.read_sql()` + `sqlite3` | Pandas 2.x |
| Analysis Engine | Pandas + NumPy | Latest stable |
| Visualisation | Matplotlib + Seaborn | Latest stable |
| File Parsing | Pandas (`read_csv`, `read_excel`) | — |
| Environment | Python `venv` | — |

---

## 3. Known Data Schema

### customers (confirmed from uploaded file)
| Column | Type | Notes |
|---|---|---|
| customerNumber | INTEGER | Primary Key |
| customerName | TEXT | |
| contactLastName | TEXT | |
| contactFirstName | TEXT | |
| phone | TEXT | |
| addressLine1 | TEXT | |
| addressLine2 | TEXT | Nullable |
| city | TEXT | |
| state | TEXT | Nullable |
| postalCode | TEXT | |
| country | TEXT | |
| salesRepEmployeeNumber | REAL | FK → employees (future) |
| creditLimit | REAL | |

### orders (expected schema — to be confirmed on upload)
| Column | Type | Notes |
|---|---|---|
| orderNumber | INTEGER | Primary Key |
| orderDate | TEXT | ISO date string |
| requiredDate | TEXT | |
| shippedDate | TEXT | Nullable |
| status | TEXT | e.g. Shipped, Cancelled |
| comments | TEXT | Nullable |
| customerNumber | INTEGER | FK → customers |

### payments (expected schema — to be confirmed on upload)
| Column | Type | Notes |
|---|---|---|
| customerNumber | INTEGER | FK → customers |
| checkNumber | TEXT | Primary Key |
| paymentDate | TEXT | ISO date string |
| amount | REAL | |

> **Note:** Schema validation should be performed at upload time. If uploaded files deviate from the expected schema, the app should surface clear error messages.

---

## 4. Project Structure

```
customer-analytics/
│
├── app.py                          # Streamlit entry point
│
├── config.py                       # Global config (DB path, app title, theme)
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py               # SQLite connection, table creation, upsert logic
│   └── schema.sql                  # SQL CREATE TABLE statements
│
├── ingestion/
│   ├── __init__.py
│   ├── file_parser.py              # Read CSV/XLSX → Pandas DataFrame
│   ├── validator.py                # Schema validation, type checks, null checks
│   └── loader.py                   # DataFrame → SQLite (with mode: replace / append)
│
├── analysis/
│   ├── __init__.py
│   ├── customer_analysis.py        # Customer-level EDA functions
│   ├── order_analysis.py           # Order-level EDA functions
│   ├── payment_analysis.py         # Payment-level EDA functions
│   └── summary_stats.py            # Cross-table KPIs and aggregations
│
├── visualisation/
│   ├── __init__.py
│   ├── charts.py                   # Reusable Matplotlib/Seaborn chart functions
│   └── kpi_cards.py                # Streamlit KPI card components
│
├── pages/
│   ├── 01_upload.py                # File upload page
│   ├── 02_overview.py              # Dashboard overview / KPI summary
│   ├── 03_customers.py             # Customer analysis page
│   ├── 04_orders.py                # Orders analysis page
│   └── 05_payments.py              # Payments analysis page
│
├── data/
│   └── analytics.db                # SQLite database file (auto-created, git-ignored)
│
├── assets/
│   └── style.css                   # Optional custom CSS for Streamlit
│
├── tests/
│   ├── test_validator.py
│   ├── test_loader.py
│   └── test_analysis.py
│
├── requirements.txt                # All pip dependencies
├── .gitignore                      # Ignore data/, __pycache__, .env, venv/
└── README.md                       # Setup and run instructions
```

---

## 5. Feature Specification

### 5.1 Upload Page (`pages/01_upload.py`)
- File uploader widget accepting `.csv` and `.xlsx`
- Dropdown to select which table the file maps to: `customers`, `orders`, `payments`
- **Persistence toggle:** `Load to SQLite (persistent)` vs `Load in memory (session only)`
- On upload: validate schema → show preview (first 5 rows) → confirm → save
- Show currently loaded tables with row counts
- Option to clear/reset a specific table or all tables

### 5.2 Overview Page (`pages/02_overview.py`)
- KPI cards: Total Customers, Total Orders, Total Revenue, Avg Credit Limit
- Customers by Country (bar chart)
- Revenue trend over time (line chart, if orders loaded)
- Top 10 customers by credit limit (horizontal bar)

### 5.3 Customers Page (`pages/03_customers.py`)
- Credit limit distribution (histogram)
- Customers by country (pie + bar)
- Customers by city (top 10 bar)
- Sales rep workload (customers per rep)
- Filter sidebar: by country, by sales rep
- Sortable data table

### 5.4 Orders Page (`pages/04_orders.py`)
- Orders over time (line chart by month)
- Order status breakdown (pie chart)
- Average order value trend
- Top customers by order count
- Filter by date range, status

### 5.5 Payments Page (`pages/05_payments.py`)
- Total payments over time
- Payment amount distribution (histogram)
- Customers with highest outstanding credit vs payments
- Late payment indicators (if shippedDate > requiredDate)
- Filter by date range, customer

---

## 6. Database Behaviour

- SQLite database file stored at `data/analytics.db`
- Tables created automatically on first run via `schema.sql`
- Upload modes:
  - **Replace:** Drops and recreates the table (full refresh)
  - **Append:** Inserts new rows, skips duplicates by primary key
- `db_manager.py` handles all connections using Python context managers (`with sqlite3.connect(...)`)
- `pandas.read_sql()` used for all SELECT queries returning DataFrames

---

## 7. Validation Rules

| Rule | Applies To |
|---|---|
| Required columns must be present | All tables |
| Primary key column must not be null | All tables |
| Numeric columns must be castable to float/int | creditLimit, amount, orderNumber |
| Date columns must match ISO format (YYYY-MM-DD) | orderDate, paymentDate |
| Foreign key values should exist in parent table (warn, not block) | customerNumber in orders/payments |

---

## 8. Configuration (`config.py`)

```
DB_PATH = "data/analytics.db"
APP_TITLE = "Customer Analytics Dashboard"
SUPPORTED_FILE_TYPES = ["csv", "xlsx"]
DEFAULT_THEME = "seaborn"  # Matplotlib style
PAGE_ICON = "📊"
```

---

## 9. Dependencies (`requirements.txt`)

```
streamlit
pandas
numpy
matplotlib
seaborn
openpyxl
xlrd
```

---

## 10. Setup Instructions

```bash
# 1. Clone or create project folder
mkdir customer-analytics && cd customer-analytics

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## 11. Coding Conventions

- All functions must have docstrings
- Analysis functions return Pandas DataFrames or scalar values only — no UI logic
- Visualisation functions accept a DataFrame and return a Matplotlib `Figure` object
- Streamlit pages import from `analysis/` and `visualisation/` — no raw SQL in pages
- All DB connections opened and closed within context managers
- No hardcoded file paths — always use `config.py` constants
- Type hints on all function signatures

---

## 12. Out of Scope (v1)

- User authentication
- Multi-user concurrent access
- Cloud deployment
- Real-time data refresh
- Email/export reports
- REST API layer
