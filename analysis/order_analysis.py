import sqlite3

import pandas as pd


def orders_over_time(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return order count grouped by month.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'month' and 'order_count'.
    """
    return pd.read_sql(
        "SELECT SUBSTR(orderDate, 1, 7) as month, "
        "COUNT(*) as order_count "
        "FROM orders GROUP BY month ORDER BY month",
        conn,
    )


def order_status_breakdown(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return order count grouped by status.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'status' and 'count'.
    """
    return pd.read_sql(
        "SELECT status, COUNT(*) as count FROM orders "
        "GROUP BY status ORDER BY count DESC",
        conn,
    )


def avg_order_value_trend(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return average order value by month based on payment amounts.

    Notes:
        Uses payments table mapped to orders via customerNumber.
        Assumes a loose coupling — one payment ≈ one order period.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'month' and 'avg_value'.
    """
    return pd.read_sql(
        "SELECT SUBSTR(p.paymentDate, 1, 7) as month, "
        "AVG(p.amount) as avg_value "
        "FROM payments p GROUP BY month ORDER BY month",
        conn,
    )


def top_customers_by_order_count(
    conn: sqlite3.Connection, n: int = 10
) -> pd.DataFrame:
    """Return the top N customers by number of orders.

    Args:
        conn: SQLite connection object.
        n: Number of top customers to return.

    Returns:
        DataFrame with columns 'customerNumber' and 'order_count'.
    """
    return pd.read_sql(
        "SELECT customerNumber, COUNT(*) as order_count "
        "FROM orders GROUP BY customerNumber "
        "ORDER BY order_count DESC LIMIT ?",
        conn,
        params=(n,),
    )


def filtered_orders(
    conn: sqlite3.Connection,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
) -> pd.DataFrame:
    """Return orders filtered by optional date range and status.

    Args:
        conn: SQLite connection object.
        start_date: ISO date string for lower bound (inclusive).
        end_date: ISO date string for upper bound (inclusive).
        status: Order status filter.

    Returns:
        DataFrame of matching orders.
    """
    query = "SELECT * FROM orders WHERE 1=1"
    params: list[str | float] = []

    if start_date:
        query += " AND orderDate >= ?"
        params.append(start_date)
    if end_date:
        query += " AND orderDate <= ?"
        params.append(end_date)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY orderDate DESC"
    return pd.read_sql(query, conn, params=params)


def distinct_order_statuses(conn: sqlite3.Connection) -> list[str]:
    """Return a sorted list of distinct order statuses.

    Args:
        conn: SQLite connection object.

    Returns:
        Sorted list of status strings.
    """
    result = pd.read_sql(
        "SELECT DISTINCT status FROM orders "
        "WHERE status IS NOT NULL ORDER BY status",
        conn,
    )
    return list(result["status"])
