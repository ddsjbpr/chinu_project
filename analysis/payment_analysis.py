import sqlite3

import pandas as pd


def payments_over_time(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return total payment amount grouped by month.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'month' and 'total'.
    """
    return pd.read_sql(
        "SELECT SUBSTR(paymentDate, 1, 7) as month, "
        "SUM(amount) as total "
        "FROM payments GROUP BY month ORDER BY month",
        conn,
    )


def payment_amount_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return all payment amounts for distribution analysis.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with a single column 'amount'.
    """
    return pd.read_sql("SELECT amount FROM payments", conn)


def credit_vs_payments(conn: sqlite3.Connection) -> pd.DataFrame:
    """Compare each customer's credit limit to their total payments.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'customerName', 'creditLimit', 'total_payments'.
    """
    return pd.read_sql(
        "SELECT c.customerName, c.creditLimit, "
        "COALESCE(SUM(p.amount), 0) as total_payments "
        "FROM customers c "
        "LEFT JOIN payments p ON c.customerNumber = p.customerNumber "
        "GROUP BY c.customerNumber ORDER BY c.customerName",
        conn,
    )


def late_payments(conn: sqlite3.Connection) -> pd.DataFrame:
    """Identify orders where shippedDate exceeds requiredDate.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'orderNumber', 'orderDate', 'requiredDate',
        'shippedDate', 'customerNumber', 'days_late'.
    """
    return pd.read_sql(
        "SELECT orderNumber, orderDate, requiredDate, shippedDate, "
        "customerNumber, "
        "JULIANDAY(shippedDate) - JULIANDAY(requiredDate) as days_late "
        "FROM orders "
        "WHERE shippedDate IS NOT NULL "
        "AND shippedDate > requiredDate "
        "ORDER BY days_late DESC",
        conn,
    )


def filtered_payments(
    conn: sqlite3.Connection,
    start_date: str | None = None,
    end_date: str | None = None,
    customer_number: int | None = None,
) -> pd.DataFrame:
    """Return payments filtered by optional date range and customer.

    Args:
        conn: SQLite connection object.
        start_date: ISO date string for lower bound (inclusive).
        end_date: ISO date string for upper bound (inclusive).
        customer_number: Specific customer number filter.

    Returns:
        DataFrame of matching payments.
    """
    query = "SELECT * FROM payments WHERE 1=1"
    params: list[str | int] = []

    if start_date:
        query += " AND paymentDate >= ?"
        params.append(start_date)
    if end_date:
        query += " AND paymentDate <= ?"
        params.append(end_date)
    if customer_number is not None:
        query += " AND customerNumber = ?"
        params.append(customer_number)

    query += " ORDER BY paymentDate DESC"
    return pd.read_sql(query, conn, params=params)


def distinct_customer_numbers(conn: sqlite3.Connection) -> list[int]:
    """Return a sorted list of distinct customer numbers with payments.

    Args:
        conn: SQLite connection object.

    Returns:
        Sorted list of customer numbers.
    """
    result = pd.read_sql(
        "SELECT DISTINCT customerNumber FROM payments "
        "WHERE customerNumber IS NOT NULL ORDER BY customerNumber",
        conn,
    )
    return [int(x) for x in result["customerNumber"]]
