# Customer Analytics Dashboard — Architecture Reference

## `config.py` — Global Configuration

| Variable | Type | Value / Purpose |
|---|---|---|
| `DB_PATH` | `str` | Path to `data/analytics.db` |
| `APP_TITLE` | `str` | `"Customer Analytics Dashboard"` |
| `SUPPORTED_FILE_TYPES` | `list[str]` | `["csv", "xlsx"]` |
| `DEFAULT_THEME` | `str` | `"seaborn-v0_8"` — Matplotlib style |
| `PAGE_ICON` | `str` | `":bar_chart:"` — Streamlit page icon |

---

## `database/schema.sql` — Table Definitions

### `customers`
| Column | Type | Constraints |
|---|---|---|
| customerNumber | INTEGER | PRIMARY KEY |
| customerName | TEXT | NOT NULL |
| contactLastName | TEXT | NOT NULL |
| contactFirstName | TEXT | NOT NULL |
| phone | TEXT | |
| addressLine1 | TEXT | |
| addressLine2 | TEXT | |
| city | TEXT | |
| state | TEXT | |
| postalCode | TEXT | |
| country | TEXT | |
| salesRepEmployeeNumber | REAL | |
| creditLimit | REAL | |

### `orders`
| Column | Type | Constraints |
|---|---|---|
| orderNumber | INTEGER | PRIMARY KEY |
| orderDate | TEXT | NOT NULL |
| requiredDate | TEXT | NOT NULL |
| shippedDate | TEXT | |
| status | TEXT | |
| comments | TEXT | |
| customerNumber | INTEGER | NOT NULL, FK → customers |

### `payments`
| Column | Type | Constraints |
|---|---|---|
| customerNumber | INTEGER | NOT NULL, FK → customers |
| checkNumber | TEXT | NOT NULL |
| paymentDate | TEXT | NOT NULL |
| amount | REAL | NOT NULL |
| — | — | PRIMARY KEY (customerNumber, checkNumber) |

---

## `database/db_manager.py` — Database Access Layer

### `get_connection()`
- **Signature:** `() -> Generator[sqlite3.Connection, None, None]`
- **Purpose:** Context manager that yields a connection to the SQLite DB at `DB_PATH`. Auto-commits on exit, rolls back on exception.

### `initialise_db()`
- **Signature:** `() -> None`
- **Purpose:** Reads `schema.sql` and executes `CREATE TABLE IF NOT EXISTS` for all three tables. Called once on app startup.

### `table_exists(table_name)`
- **Signature:** `(table_name: str) -> bool`
- **Purpose:** Returns `True` if a table with the given name exists in the database.

### `get_table_row_count(table_name)`
- **Signature:** `(table_name: str) -> int`
- **Purpose:** Returns the number of rows in the specified table. Returns 0 if the table is empty.

---

## `ingestion/file_parser.py` — File Reading

### `parse_file(file_path)`
- **Signature:** `(file_path: str | Path) -> pd.DataFrame`
- **Purpose:** Reads a CSV (`.csv`) or Excel (`.xls`, `.xlsx`) file from disk into a DataFrame. Raises `FileNotFoundError` or `ValueError` on unsupported types.

### `parse_file_bytes(buffer, filename)`
- **Signature:** `(buffer: object, filename: str) -> pd.DataFrame`
- **Purpose:** Reads CSV or Excel bytes from a file-like object (e.g. `BytesIO`). Uses the original filename to detect format. Explicit engine selection: `openpyxl` for `.xlsx`, `xlrd` for `.xls`.

---

## `ingestion/validator.py` — Schema & Data Validation

### Module-Level Constants
| Constant | Type | Purpose |
|---|---|---|
| `SCHEMAS` | `dict[str, dict[str, str]]` | Expected columns and their SQL types per table |
| `PRIMARY_KEYS` | `dict[str, list[str]]` | Primary key column(s) per table |
| `NUMERIC_COLUMNS` | `dict[str, list[str]]` | Columns that must be castable to numeric |
| `DATE_COLUMNS` | `dict[str, list[str]]` | Columns that must be `YYYY-MM-DD` |
| `DATE_PATTERN` | `re.Pattern` | Compiled regex for ISO date format |

### `validate_file(df, table_name)`
- **Signature:** `(df: pd.DataFrame, table_name: str) -> tuple[bool, list[str]]`
- **Purpose:** Main validation entry point. Runs all four checks in sequence, collects errors, returns `(is_valid, errors)`.

### `_check_required_columns(df, table_name)`
- **Signature:** `(df: pd.DataFrame, table_name: str) -> list[str]`
- **Purpose:** Verifies every column in `SCHEMAS` exists in the DataFrame.

### `_check_primary_key_null(df, table_name)`
- **Signature:** `(df: pd.DataFrame, table_name: str) -> list[str]`
- **Purpose:** Checks that primary key columns have no null values.

### `_check_numeric_columns(df, table_name)`
- **Signature:** `(df: pd.DataFrame, table_name: str) -> list[str]`
- **Purpose:** Checks that numeric columns can be cast via `pd.to_numeric`.

### `_check_date_columns(df, table_name)`
- **Signature:** `(df: pd.DataFrame, table_name: str) -> list[str]`
- **Purpose:** Validates date columns match `YYYY-MM-DD` format using regex + `datetime.strptime` fallback.

---

## `ingestion/loader.py` — Database Writer

### `load_dataframe(df, table_name, mode)`
- **Signature:** `(df: pd.DataFrame, table_name: str, mode: str = "replace") -> None`
- **Purpose:** Writes a validated DataFrame to SQLite. `mode="replace"` drops and recreates the table; `mode="append"` inserts new rows.
- **Raises:** `ValueError` if mode is not `"replace"` or `"append"`.

---

## `analysis/summary_stats.py` — Cross-Table KPIs

| Function | Signature | Returns | Purpose |
|---|---|---|---|
| `total_customers` | `(conn: sqlite3.Connection) -> int` | `int` | Count of all customers |
| `total_orders` | `(conn: sqlite3.Connection) -> int` | `int` | Count of all orders |
| `total_revenue` | `(conn: sqlite3.Connection) -> float` | `float` | Sum of all payment amounts |
| `avg_credit_limit` | `(conn: sqlite3.Connection) -> float` | `float` | Average credit limit across customers |
| `customers_by_country` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Customer count grouped by country |
| `revenue_over_time` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Monthly payment totals |
| `top_customers_by_credit` | `(conn: sqlite3.Connection, n: int = 10) -> pd.DataFrame` | DataFrame | Top N customers by credit limit |

---

## `analysis/customer_analysis.py` — Customer-Level EDA

| Function | Signature | Returns | Purpose |
|---|---|---|---|
| `credit_limit_distribution` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | All credit limit values |
| `customers_by_country` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Customer count per country |
| `top_cities` | `(conn: sqlite3.Connection, n: int = 10) -> pd.DataFrame` | DataFrame | Top N cities by customer count |
| `sales_rep_workload` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Customers per sales rep |
| `filtered_customers` | `(conn, country=None, sales_rep=None) -> pd.DataFrame` | DataFrame | Filtered customer list |
| `distinct_countries` | `(conn: sqlite3.Connection) -> list[str]` | `list[str]` | Sorted unique country names |
| `distinct_sales_reps` | `(conn: sqlite3.Connection) -> list[float]` | `list[float]` | Sorted unique sales rep IDs |

---

## `analysis/order_analysis.py` — Order-Level EDA

| Function | Signature | Returns | Purpose |
|---|---|---|---|
| `orders_over_time` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Monthly order counts |
| `order_status_breakdown` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Count per order status |
| `avg_order_value_trend` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Monthly avg payment amount |
| `top_customers_by_order_count` | `(conn, n=10) -> pd.DataFrame` | DataFrame | Top N customers by order volume |
| `filtered_orders` | `(conn, start_date, end_date, status) -> pd.DataFrame` | DataFrame | Filtered order list |
| `distinct_order_statuses` | `(conn: sqlite3.Connection) -> list[str]` | `list[str]` | Sorted unique statuses |

---

## `analysis/payment_analysis.py` — Payment-Level EDA

| Function | Signature | Returns | Purpose |
|---|---|---|---|
| `payments_over_time` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Monthly payment totals |
| `payment_amount_distribution` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | All payment amounts |
| `credit_vs_payments` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Customer credit vs total payments |
| `late_payments` | `(conn: sqlite3.Connection) -> pd.DataFrame` | DataFrame | Orders shipped after required date |
| `filtered_payments` | `(conn, start_date, end_date, customer_number) -> pd.DataFrame` | DataFrame | Filtered payment list |
| `distinct_customer_numbers` | `(conn: sqlite3.Connection) -> list[int]` | `list[int]` | Sorted unique customer numbers with payments |

---

## `visualisation/charts.py` — Chart Builders

Configuration: `plt.style.use("seaborn-v0_8")`

| Function | Signature | Returns | Purpose |
|---|---|---|---|
| `bar_chart` | `(df, x_col, y_col, title, xlabel, ylabel, horizontal, top_n) -> Figure` | `Figure` | Vertical bar chart (rotates labels if >5 categories) |
| `line_chart` | `(df, x_col, y_col, title, xlabel, ylabel, marker) -> Figure` | `Figure` | Line chart with markers |
| `histogram` | `(df, col, title, xlabel, bins) -> Figure` | `Figure` | Histogram with KDE overlay |
| `pie_chart` | `(df, label_col, value_col, title) -> Figure` | `Figure` | Pie chart with percentage labels |
| `horizontal_bar_chart` | `(df, label_col, value_col, title, xlabel, ylabel, top_n) -> Figure` | `Figure` | Horizontal bar chart for ranked data |

---

## `visualisation/kpi_cards.py` — KPI Display

### `kpi_card(label, value, delta)`
- **Signature:** `(label: str, value: str, delta: str | None = None) -> None`
- **Purpose:** Renders a single Streamlit metric card. Wraps `st.metric()`.

---

## `app.py` — Entry Point

- Sets Streamlit page config (`wide` layout, custom title/icon)
- Calls `initialise_db()` on every start
- Renders sidebar with app title
- Navigation is auto-generated by Streamlit from the `pages/` directory

---

## `pages/01_upload.py` — Upload Page

- File uploader widget (`.csv`, `.xlsx`)
- Dropdown to select target table
- Persistence toggle checkbox
- On file selection: parses bytes → validates schema → shows preview
- "Confirm & Load" button writes to SQLite or stores in `st.session_state`
- Shows current row counts per table peristence/in-memory
- Clear All Tables button

---

## `pages/02_overview.py` — Dashboard Overview

- 4 KPI cards from `summary_stats`
- Customers by Country bar chart
- Revenue Over Time line chart
- Top 10 Customers by Credit Limit horizontal bar
- Early exit with info message if no data loaded
- All figures rendered via `st.pyplot(fig)` with `plt.close(fig)` cleanup

---

## `pages/03_customers.py` — Customer Analysis Page

- Sidebar filters: country dropdown, sales rep dropdown
- 4 charts: credit limit histogram, country distribution (pie if <7, else bar), top 10 cities, sales rep workload
- Sortable data table with applied filters
- Row count indicator

---

## `pages/04_orders.py` — Orders Analysis Page

- Sidebar filters: date range pickers, status dropdown
- 4 charts: orders over time, status breakdown, avg value trend, top customers
- Sortable filtered data table

---

## `pages/05_payments.py` — Payments Analysis Page

- Sidebar filters: date range pickers, customer number dropdown
- 2 charts: payments over time, amount distribution
- Credit vs payments comparison section
- Late payments table (if orders data available)
- Sortable filtered data table

---

## `launcher.py` — Browser Launcher

### `main()`
- **Signature:** `() -> None`
- **Purpose:** Spawns `streamlit run app.py` as a subprocess, waits 3 seconds, then opens `http://localhost:8501` in Google Chrome (falls back to default browser). Streams app output to the terminal.
- **Usage:** `python launcher.py`

---

## `tests/` — Test Coverage

### `tests/test_validator.py` (10 tests)
| Test | What It Checks |
|---|---|
| `test_valid_customers_passes` | Complete valid customers DataFrame passes |
| `test_missing_required_column_fails` | Missing column detected |
| `test_primary_key_null_fails` | Null in primary key detected |
| `test_non_numeric_credit_limit_fails` | Non-numeric in numeric column detected |
| `test_invalid_date_format_fails` | Bad date format in orders detected |
| `test_valid_orders_passes` | Complete valid orders DataFrame passes |
| `test_unknown_table_name_fails` | Unknown table name returns error |
| `test_payments_valid_passes` | Complete valid payments DataFrame passes |
| `test_payments_primary_key_null_fails` | Null in payments composite PK detected |

### `tests/test_loader.py` (3 tests)
| Test | What It Checks |
|---|---|
| `test_load_dataframe_replace` | Replace mode writes correctly to in-memory SQLite |
| `test_load_dataframe_append` | Append mode adds rows without duplication |
| `test_invalid_mode_raises` | Invalid mode string raises `ValueError` |

### `tests/test_analysis.py` (14 tests)
| Test Class | Tests | What It Checks |
|---|---|---|
| `TestSummaryStats` | 11 | All summary/analysis functions with populated data |
| `TestEmptyDataFrames` | 3 | Empty table edge cases (returns 0 / empty DataFrame) |

---

## `pyproject.toml` — Tool Configuration

- **Ruff:** line-length 88, target Python 3.10, rules E/F/W/I
- **Mypy:** Python 3.10, strict mode, ignore missing imports

---

## `requirements.txt` — Dependencies

```
streamlit, pandas, numpy, matplotlib, seaborn,
openpyxl, xlrd, ruff, mypy, types-python-dateutil,
types-requests
```
