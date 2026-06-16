import re
from datetime import datetime

import pandas as pd

SCHEMAS: dict[str, dict[str, str]] = {
    "customers": {
        "customerNumber": "INTEGER",
        "customerName": "TEXT",
        "contactLastName": "TEXT",
        "contactFirstName": "TEXT",
        "phone": "TEXT",
        "addressLine1": "TEXT",
        "addressLine2": "TEXT",
        "city": "TEXT",
        "state": "TEXT",
        "postalCode": "TEXT",
        "country": "TEXT",
        "salesRepEmployeeNumber": "REAL",
        "creditLimit": "REAL",
    },
    "orders": {
        "orderNumber": "INTEGER",
        "orderDate": "TEXT",
        "requiredDate": "TEXT",
        "shippedDate": "TEXT",
        "status": "TEXT",
        "comments": "TEXT",
        "customerNumber": "INTEGER",
    },
    "payments": {
        "customerNumber": "INTEGER",
        "checkNumber": "TEXT",
        "paymentDate": "TEXT",
        "amount": "REAL",
    },
}

PRIMARY_KEYS: dict[str, list[str]] = {
    "customers": ["customerNumber"],
    "orders": ["orderNumber"],
    "payments": ["customerNumber", "checkNumber"],
}

NUMERIC_COLUMNS: dict[str, list[str]] = {
    "customers": ["creditLimit", "customerNumber"],
    "orders": ["orderNumber", "customerNumber"],
    "payments": ["customerNumber", "amount"],
}

DATE_COLUMNS: dict[str, list[str]] = {
    "orders": ["orderDate", "requiredDate", "shippedDate"],
    "payments": ["paymentDate"],
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _check_required_columns(df: pd.DataFrame, table_name: str) -> list[str]:
    """Verify that all required columns exist in the DataFrame.

    Args:
        df: The uploaded DataFrame.
        table_name: Target table name.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    schema = SCHEMAS.get(table_name)
    if schema is None:
        errors.append(f"Unknown table name: {table_name}")
        return errors

    for col in schema:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    return errors


def _check_primary_key_null(df: pd.DataFrame, table_name: str) -> list[str]:
    """Verify that primary key columns have no null values.

    Args:
        df: The uploaded DataFrame.
        table_name: Target table name.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    pk_columns = PRIMARY_KEYS.get(table_name, [])

    for col in pk_columns:
        if col not in df.columns:
            continue
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(
                f"Primary key column '{col}' has {null_count} null value(s)"
            )
    return errors


def _check_numeric_columns(df: pd.DataFrame, table_name: str) -> list[str]:
    """Verify that numeric columns can be cast to numeric types.

    Args:
        df: The uploaded DataFrame.
        table_name: Target table name.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    num_cols = NUMERIC_COLUMNS.get(table_name, [])

    for col in num_cols:
        if col not in df.columns:
            continue
        non_numeric = (
            pd.to_numeric(df[col], errors="coerce").isnull() & df[col].notnull()
        )
        if non_numeric.any():
            errors.append(
                f"Column '{col}' contains {non_numeric.sum()} non-numeric value(s)"
            )
    return errors


def _check_date_columns(df: pd.DataFrame, table_name: str) -> list[str]:
    """Verify that date columns match YYYY-MM-DD format.

    Args:
        df: The uploaded DataFrame.
        table_name: Target table name.

    Returns:
        A list of error messages (empty if valid).
    """
    errors: list[str] = []
    date_cols = DATE_COLUMNS.get(table_name, [])

    for col in date_cols:
        if col not in df.columns:
            continue
        non_null_vals = df[col].dropna()
        for idx, val in non_null_vals.items():
            str_val = str(val).strip()
            if not DATE_PATTERN.match(str_val):
                try:
                    datetime.strptime(str_val, "%Y-%m-%d")
                except (ValueError, TypeError):
                    errors.append(
                        f"Row {idx + 2}: Column '{col}' has invalid date format: {val}"
                    )
    return errors


def validate_file(df: pd.DataFrame, table_name: str) -> tuple[bool, list[str]]:
    """Validate a DataFrame against the expected schema for a table.

    Checks required columns, primary key nulls, numeric castability,
    and date format. Collects all errors before returning.

    Args:
        df: The DataFrame to validate.
        table_name: Target table name (customers, orders, payments).

    Returns:
        A tuple of (is_valid: bool, errors: list[str]).
    """
    errors: list[str] = []

    errors.extend(_check_required_columns(df, table_name))
    errors.extend(_check_primary_key_null(df, table_name))
    errors.extend(_check_numeric_columns(df, table_name))
    errors.extend(_check_date_columns(df, table_name))

    return len(errors) == 0, errors
