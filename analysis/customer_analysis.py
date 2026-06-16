import sqlite3

import pandas as pd


def credit_limit_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return credit limit values for all customers.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with a single column 'creditLimit'.
    """
    return pd.read_sql("SELECT creditLimit FROM customers", conn)


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


def top_cities(conn: sqlite3.Connection, n: int = 10) -> pd.DataFrame:
    """Return the top N cities by customer count.

    Args:
        conn: SQLite connection object.
        n: Number of top cities to return.

    Returns:
        DataFrame with columns 'city' and 'count'.
    """
    return pd.read_sql(
        "SELECT city, COUNT(*) as count FROM customers "
        "WHERE city IS NOT NULL AND city != '' "
        "GROUP BY city ORDER BY count DESC LIMIT ?",
        conn,
        params=(n,),
    )


def sales_rep_workload(conn: sqlite3.Connection) -> pd.DataFrame:
    """Return number of customers per sales representative.

    Args:
        conn: SQLite connection object.

    Returns:
        DataFrame with columns 'salesRepEmployeeNumber' and 'customer_count'.
    """
    return pd.read_sql(
        "SELECT salesRepEmployeeNumber, COUNT(*) as customer_count "
        "FROM customers WHERE salesRepEmployeeNumber IS NOT NULL "
        "GROUP BY salesRepEmployeeNumber ORDER BY customer_count DESC",
        conn,
    )


def filtered_customers(
    conn: sqlite3.Connection,
    country: str | None = None,
    sales_rep: float | None = None,
) -> pd.DataFrame:
    """Return customers filtered by optional country and sales rep.

    Args:
        conn: SQLite connection object.
        country: Optional country filter.
        sales_rep: Optional sales rep employee number filter.

    Returns:
        DataFrame of matching customers.
    """
    query = "SELECT * FROM customers WHERE 1=1"
    params: list[str | float] = []

    if country:
        query += " AND country = ?"
        params.append(country)
    if sales_rep is not None:
        query += " AND salesRepEmployeeNumber = ?"
        params.append(sales_rep)

    query += " ORDER BY customerName"
    return pd.read_sql(query, conn, params=params)


def distinct_countries(conn: sqlite3.Connection) -> list[str]:
    """Return a sorted list of distinct countries from customers.

    Args:
        conn: SQLite connection object.

    Returns:
        Sorted list of country names.
    """
    result = pd.read_sql(
        "SELECT DISTINCT country FROM customers WHERE country IS NOT NULL "
        "ORDER BY country",
        conn,
    )
    return list(result["country"])


def distinct_sales_reps(conn: sqlite3.Connection) -> list[float]:
    """Return a sorted list of distinct sales rep employee numbers.

    Args:
        conn: SQLite connection object.

    Returns:
        Sorted list of employee numbers.
    """
    result = pd.read_sql(
        "SELECT DISTINCT salesRepEmployeeNumber FROM customers "
        "WHERE salesRepEmployeeNumber IS NOT NULL "
        "ORDER BY salesRepEmployeeNumber",
        conn,
    )
    return list(result["salesRepEmployeeNumber"])
