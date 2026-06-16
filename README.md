# Customer Analytics Dashboard

A local data analytics dashboard that allows users to upload business data files (customers, orders, payments) in CSV/XLSX format, persist them to a local SQLite database, and explore them through an interactive Streamlit frontend with Matplotlib/Seaborn visualisations.

Built with a 100% free, open-source stack — no cloud services or external APIs required.

## Prerequisites

- Python 3.10 or higher

## Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

## Usage

1. Go to the **Upload** page and select a CSV or XLSX file
2. Choose the target table (customers, orders, payments)
3. Toggle persistence (SQLite vs in-memory)
4. After validation, confirm the load
5. Explore the data on the **Overview**, **Customers**, **Orders**, and **Payments** pages

## Folder Structure

```
customer-analytics/
  app.py                    # Streamlit entry point
  config.py                 # Global configuration
  database/                 # SQLite connection and schema
  ingestion/                # File parsing, validation, loading
  analysis/                 # Pure analysis functions
  visualisation/            # Charts and KPI card components
  pages/                    # Streamlit multi-page UI
  data/                     # SQLite database file (auto-created)
  tests/                    # Unit tests
```

## Running Tests

```bash
python -m unittest discover tests -v
```

## Known Limitations

- Single-user local tool only
- No authentication or user management
- No real-time data refresh
- No cloud deployment options
- No email or report export
- No REST API layer
