from pathlib import Path

_DB_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = str(_DB_DIR / "analytics.db")
APP_TITLE = "Customer Analytics Dashboard"
SUPPORTED_FILE_TYPES = ["csv", "xlsx"]
DEFAULT_THEME = "seaborn-v0_8"
PAGE_ICON = ":bar_chart:"
