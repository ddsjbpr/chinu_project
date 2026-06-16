import pandas as pd

from database.db_manager import get_connection


def load_dataframe(
    df: pd.DataFrame,
    table_name: str,
    mode: str = "replace",
) -> None:
    """Write a validated DataFrame to the SQLite database.

    Args:
        df: The DataFrame to write.
        table_name: Target table name (customers, orders, payments).
        mode: 'replace' to drop and recreate the table, 'append' to add rows.

    Raises:
        ValueError: If mode is not 'replace' or 'append'.
    """
    if mode not in ("replace", "append"):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'replace' or 'append'.")

    if_exists = "replace" if mode == "replace" else "append"

    with get_connection() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
