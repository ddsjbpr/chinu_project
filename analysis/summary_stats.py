import sqlite3

import pandas as pd


def total_customers(conn: sqlite3.Connection) -> int:
    """Return the total number of customers in the database.

    Args:
        conn: SQLite connection object.

    Returns:
        Total customer count.
    """
    result = pd.read_sql("SELECT COUNT(*) as count FROM customers", conn)
    return int(result["count"].iloc[0])


def total_orders(conn: sqlite3.Connection) -> int:
    """Return the total number of orders in the database.

    Args:
        conn: SQLite connection object.

    Returns:
        Total order count.
    """
    result = pd.read_sql("SELECT COUNT(*) as count FROM orders", conn)
    return int(result["count"].iloc[0])


def total_revenue(conn: sqlite3.Connection) -> float:
    """Return the sum of all payment amounts.

    Args:
        conn: SQLite connection object.

    Returns:
        Total revenue as a float. Returns 0.0 if no payments exist.
    """
    result = pd.read_sql("SELECT SUM(amount) as revenue FROM payments", conn)
    val = result["revenue"].iloc[0]
    return 0.0 if val is None else float(val)


def avg_credit_limit(conn: sqlite3.Connection) -> float:
    """Return the average credit limit across all customers.

    Args:
        conn: SQLite connection object.

    Returns:
        Average credit limit. Returns 0.0 if no customers exist.
    """
    result = pd.read_sql(
        "SELECT AVG(creditLimit) as avg_limit FROM customers", conn
    )
    val = result["avg_limit"].iloc[0]
    return 0.0 if val is None else float(val)


def customers_by_country(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return customer count grouped by country.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'country' and 'count'.
    """
    return pd.read_sql(
        "SELECT country, COUNT(*) as count FROM customers "
        "GROUP BY country ORDER BY count DESC",
        conn,
    )


def revenue_over_time(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return total payments aggregated by month.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'month' and 'revenue'.
    """
    return pd.read_sql(
        "SELECT SUBSTR(paymentDate, 1, 7) as month, "
        "SUM(amount) as revenue "
        "FROM payments GROUP BY month ORDER BY month",
        conn,
    )


def top_customers_by_credit(conn: sqlite3.Connection, n: int = 10) -> pd.DataFrame:
    """Return the top N customers by credit limit.

    Args:
        conn: SQLite connection object.
        n: Number of top customers to return.

    Returns:
        DataFrame with columns 'customerName' and 'creditLimit'.
    """
    return pd.read_sql(
        "SELECT customerName, creditLimit FROM customers "
        "ORDER BY creditLimit DESC LIMIT ?",
        conn,
        params=(n,),
    )
