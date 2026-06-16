# AGENTS.md — AI Coding Agent Instructions
## Customer Analytics Dashboard

This file instructs an AI coding agent (e.g. GitHub Copilot, Cursor, Claude Code) on how to generate, extend, and maintain this project. Read `SPECIFICATION.md` fully before writing any code.

---

## 1. Prime Directive

You are building a **local data analytics dashboard** in Python. Every decision must favour simplicity, readability, and correctness over cleverness. This is a single-user local tool — do not introduce unnecessary abstractions, premature optimisation, or external services.

---

## 2. Before You Write Any Code

- Read `SPECIFICATION.md` completely
- Understand the confirmed stack: Streamlit, SQLite, Pandas, NumPy, Matplotlib, Seaborn
- Understand the project folder structure defined in the spec — do not deviate from it
- Do not introduce any library not listed in `requirements.txt` without explicit instruction
- Do not use any cloud service, API, or paid tool

---

## 3. File Generation Order

Generate files in this exact order to avoid import errors:

1. `requirements.txt`
2. `config.py`
3. `database/schema.sql`
4. `database/db_manager.py`
5. `ingestion/file_parser.py`
6. `ingestion/validator.py`
7. `ingestion/loader.py`
8. `analysis/summary_stats.py`
9. `analysis/customer_analysis.py`
10. `analysis/order_analysis.py`
11. `analysis/payment_analysis.py`
12. `visualisation/charts.py`
13. `visualisation/kpi_cards.py`
14. `app.py`
15. `pages/01_upload.py`
16. `pages/02_overview.py`
17. `pages/03_customers.py`
18. `pages/04_orders.py`
19. `pages/05_payments.py`
20. `tests/test_validator.py`
21. `tests/test_loader.py`
22. `tests/test_analysis.py`
23. `.gitignore`
24. `README.md`

---

## 4. Layer Rules — Strict Separation

### `database/` layer
- Only responsible for SQLite connection management and schema creation
- Must use Python context managers for every connection (`with sqlite3.connect(...) as conn`)
- Must read DB path exclusively from `config.DB_PATH` — never hardcode paths
- Must expose functions: `get_connection()`, `initialise_db()`, `table_exists(table_name)`

### `ingestion/` layer
- `file_parser.py` reads a file path and returns a raw Pandas DataFrame — nothing else
- `validator.py` accepts a DataFrame and table name, returns a tuple `(is_valid: bool, errors: list[str])`
- `loader.py` accepts a validated DataFrame, table name, mode (`replace` or `append`), and writes to SQLite
- No Streamlit imports anywhere in the ingestion layer

### `analysis/` layer
- Every function accepts a SQLite connection or DataFrame as input
- Every function returns a Pandas DataFrame or a scalar value
- No Matplotlib, Seaborn, or Streamlit imports in this layer
- Functions must be pure and independently testable

### `visualisation/` layer
- Every chart function accepts a Pandas DataFrame as input
- Every chart function returns a Matplotlib `Figure` object
- Never call `plt.show()` — always return the figure for Streamlit to render
- Apply consistent styling using `config.DEFAULT_THEME` at the top of `charts.py`

### `pages/` layer
- Pages import from `analysis/` and `visualisation/` only
- No raw SQL strings in any page file
- No direct file I/O in any page file
- Each page is self-contained and independently renderable

---

## 5. Coding Standards

- Python 3.10+ syntax throughout
- Type hints on every function signature
- Docstring on every function and class explaining: what it does, parameters, return value
- Maximum function length: 40 lines — split longer functions
- No global mutable state outside of `config.py`
- All user-facing strings in plain English, sentence case
- Variable names: `snake_case`, descriptive, no single letters except loop counters

---

## 6. SQLite Rules

- All table names must match exactly: `customers`, `orders`, `payments`
- Always use parameterised queries — never f-string or `.format()` SQL
- `replace` mode: use `df.to_sql(name, conn, if_exists='replace', index=False)`
- `append` mode: use `df.to_sql(name, conn, if_exists='append', index=False)`
- Use `pd.read_sql(query, conn)` for all SELECT operations returning DataFrames
- Initialise DB and create tables on app startup via `db_manager.initialise_db()`

---

## 7. Streamlit Rules

- Entry point is `app.py` — it sets page config and renders the sidebar navigation
- Multi-page routing uses Streamlit's native `pages/` directory convention
- Page files are prefixed with numbers for ordering: `01_upload.py`, `02_overview.py`, etc.
- Use `st.session_state` to store in-memory DataFrames when persistence mode is off
- Use `st.cache_data` on expensive data loading functions
- Use `st.pyplot(fig)` to render all Matplotlib/Seaborn figures
- Always call `plt.close(fig)` after `st.pyplot(fig)` to prevent memory leaks
- Show `st.spinner()` during file upload and DB operations
- Show `st.error()` for validation failures with the full error list
- Show `st.success()` after successful upload

---

## 8. Validation Requirements

When validating an uploaded file, check in this order and collect all errors before returning:

1. Required columns are present (compare against expected schema per table)
2. Primary key column has no null values
3. Numeric columns can be cast without error
4. Date columns match `YYYY-MM-DD` format where applicable
5. Warn (do not block) if foreign key values don't exist in the parent table

Return all errors as a list — never raise exceptions for validation failures, always return them gracefully.

---

## 9. Chart Styling Rules

- Apply `plt.style.use(config.DEFAULT_THEME)` once at the top of `charts.py`
- Every chart must have: a title, labelled axes, and readable font sizes
- Use `figure, ax = plt.subplots(figsize=(10, 5))` as the default figure size
- Horizontal bar charts for ranked/categorical data with long labels
- Line charts for time series data
- Histograms for numeric distributions
- Pie charts only when there are fewer than 7 categories
- Rotate x-axis labels 45° when there are more than 5 categories
- Always return `figure`, never `ax`

---

## 10. Error Handling

- Wrap all file read operations in `try/except` and surface errors via `st.error()`
- Wrap all DB operations in `try/except` and log errors to console with `print()`
- Never use bare `except:` — always catch specific exceptions
- If the database file does not exist, create it automatically — never crash on first run
- If an analysis function receives an empty DataFrame, return an empty DataFrame with correct columns rather than raising an error

---

## 11. What NOT to Do

- Do not use `st.experimental_rerun()` — use `st.rerun()` (Streamlit 1.27+)
- Do not use `@st.cache` (deprecated) — use `@st.cache_data` or `@st.cache_resource`
- Do not use `plt.show()` anywhere
- Do not write SQL strings directly in page files
- Do not import Streamlit in analysis or database modules
- Do not use any ORM (SQLAlchemy, Peewee, etc.)
- Do not add authentication, login screens, or user management
- Do not connect to any external API or internet service
- Do not use `f-strings` to build SQL queries

---

## 12. Testing Instructions

- Tests live in `tests/` and use Python's built-in `unittest` module (no pytest required)
- Each test file covers one module only
- Use in-memory SQLite (`:memory:`) for all DB tests — never touch `data/analytics.db` in tests
- Use small hardcoded DataFrames as test fixtures — do not read from disk in tests
- Test both the happy path and at least one failure case per function

---

## 13. Lint & Typecheck

Run these three commands **after every file edit** and fix all issues before moving on:

```bash
ruff check .
mypy . --ignore-missing-imports
python -m unittest discover tests -v
```

Configuration lives in `pyproject.toml` — do not modify without reason.

---

## 14. README Requirements

The generated `README.md` must include:
- Project description (2–3 sentences)
- Prerequisites (Python version)
- Setup steps (venv, pip install, run)
- How to upload data files
- Folder structure summary
- How to run tests
- Known limitations
