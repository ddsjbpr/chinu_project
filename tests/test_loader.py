import sqlite3
import unittest
from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import patch

import pandas as pd

from ingestion.loader import load_dataframe


class TestLoader(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            "CREATE TABLE customers ("
            "customerNumber INTEGER PRIMARY KEY, "
            "customerName TEXT, "
            "contactLastName TEXT, "
            "contactFirstName TEXT, "
            "phone TEXT, "
            "addressLine1 TEXT, "
            "addressLine2 TEXT, "
            "city TEXT, "
            "state TEXT, "
            "postalCode TEXT, "
            "country TEXT, "
            "salesRepEmployeeNumber REAL, "
            "creditLimit REAL)"
        )

        @contextmanager
        def mock_get_connection() -> Generator[sqlite3.Connection, None, None]:
            try:
                yield self.conn
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise

        self.mock_get_connection = mock_get_connection

    def test_load_dataframe_replace(self) -> None:
        df = pd.DataFrame({
            "customerNumber": [1, 2],
            "customerName": ["A", "B"],
            "contactLastName": ["X", "Y"],
            "contactFirstName": ["x", "y"],
            "phone": ["1", "2"],
            "addressLine1": ["Addr1", "Addr2"],
            "addressLine2": [None, None],
            "city": ["NY", "LA"],
            "state": ["NY", "CA"],
            "postalCode": ["10001", "90001"],
            "country": ["USA", "USA"],
            "salesRepEmployeeNumber": [None, None],
            "creditLimit": [1000.0, 2000.0],
        })

        with patch("ingestion.loader.get_connection", self.mock_get_connection):
            load_dataframe(df, "customers", mode="replace")

        result = pd.read_sql(
            "SELECT * FROM customers ORDER BY customerNumber", self.conn
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result["customerName"].iloc[0], "A")

    def test_load_dataframe_append(self) -> None:
        df1 = pd.DataFrame({
            "customerNumber": [1],
            "customerName": ["A"],
            "contactLastName": ["X"],
            "contactFirstName": ["x"],
            "phone": ["1"],
            "addressLine1": ["Addr"],
            "addressLine2": [None],
            "city": ["NY"],
            "state": ["NY"],
            "postalCode": ["10001"],
            "country": ["USA"],
            "salesRepEmployeeNumber": [None],
            "creditLimit": [1000.0],
        })

        df2 = pd.DataFrame({
            "customerNumber": [2],
            "customerName": ["B"],
            "contactLastName": ["Y"],
            "contactFirstName": ["y"],
            "phone": ["2"],
            "addressLine1": ["Addr2"],
            "addressLine2": [None],
            "city": ["LA"],
            "state": ["CA"],
            "postalCode": ["90001"],
            "country": ["USA"],
            "salesRepEmployeeNumber": [None],
            "creditLimit": [2000.0],
        })

        with patch("ingestion.loader.get_connection", self.mock_get_connection):
            load_dataframe(df1, "customers", mode="append")
            load_dataframe(df2, "customers", mode="append")

        result = pd.read_sql(
            "SELECT * FROM customers ORDER BY customerNumber", self.conn
        )
        self.assertEqual(len(result), 2)

    def test_invalid_mode_raises(self) -> None:
        df = pd.DataFrame({"customerNumber": [1]})
        with self.assertRaises(ValueError):
            load_dataframe(df, "customers", mode="invalid")


if __name__ == "__main__":
    unittest.main()
