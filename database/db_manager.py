import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from config import DB_PATH


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Provide a database connection as a context manager.

    Yields a sqlite3.Connection object that auto-commits and closes on exit.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialise_db() -> None:
    """Create database tables if they do not already exist.

    Reads and executes the SQL statements from schema.sql to create the
    customers, orders, and payments tables.
    """
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema_sql)


def table_exists(table_name: str) -> bool:
    """Check whether a table exists in the database.

    Args:
        table_name: Name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None


def get_table_row_count(table_name: str) -> int:
    """Return the number of rows in a given table.

    Args:
        table_name: Name of the table.

    Returns:
        Row count as an integer.
    """
    with get_connection() as conn:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        row = cursor.fetchone()
        return int(row[0]) if row else 0
