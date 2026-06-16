import unittest

import pandas as pd

from ingestion.validator import validate_file


class TestValidator(unittest.TestCase):

    def setUp(self) -> None:
        self.valid_customers = pd.DataFrame({
            "customerNumber": [101, 102, 103],
            "customerName": ["Alpha Co", "Beta Inc", "Gamma LLC"],
            "contactLastName": ["Smith", "Jones", "Brown"],
            "contactFirstName": ["John", "Jane", "Bob"],
            "phone": ["123-456", "789-012", "345-678"],
            "addressLine1": ["1 Main St", "2 Oak Ave", "3 Pine Rd"],
            "addressLine2": ["", None, "Suite 4"],
            "city": ["New York", "Los Angeles", "Chicago"],
            "state": ["NY", "CA", "IL"],
            "postalCode": ["10001", "90001", "60601"],
            "country": ["USA", "USA", "USA"],
            "salesRepEmployeeNumber": [1002.0, 1003.0, None],
            "creditLimit": [50000.0, 75000.0, 30000.0],
        })

    def test_valid_customers_passes(self) -> None:
        is_valid, errors = validate_file(self.valid_customers, "customers")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_required_column_fails(self) -> None:
        df = self.valid_customers.drop(columns=["customerName"])
        is_valid, errors = validate_file(df, "customers")
        self.assertFalse(is_valid)
        self.assertTrue(any("customerName" in err for err in errors))

    def test_primary_key_null_fails(self) -> None:
        df = self.valid_customers.copy()
        df.loc[0, "customerNumber"] = None
        is_valid, errors = validate_file(df, "customers")
        self.assertFalse(is_valid)
        self.assertTrue(any("customerNumber" in err for err in errors))

    def test_non_numeric_credit_limit_fails(self) -> None:
        df = self.valid_customers.copy()
        df["creditLimit"] = df["creditLimit"].astype(object)
        df.loc[1, "creditLimit"] = "not-a-number"
        is_valid, errors = validate_file(df, "customers")
        self.assertFalse(is_valid)
        self.assertTrue(any("creditLimit" in err for err in errors))

    def test_invalid_date_format_fails(self) -> None:
        df = pd.DataFrame({
            "orderNumber": [1, 2],
            "orderDate": ["2024-01-15", "not-a-date"],
            "requiredDate": ["2024-02-15", "2024-03-01"],
            "shippedDate": [None, None],
            "status": ["Shipped", "Pending"],
            "comments": [None, None],
            "customerNumber": [101, 102],
        })
        is_valid, errors = validate_file(df, "orders")
        self.assertFalse(is_valid)
        self.assertTrue(any("orderDate" in err for err in errors))

    def test_valid_orders_passes(self) -> None:
        df = pd.DataFrame({
            "orderNumber": [1, 2],
            "orderDate": ["2024-01-15", "2024-02-01"],
            "requiredDate": ["2024-02-15", "2024-03-01"],
            "shippedDate": ["2024-02-10", None],
            "status": ["Shipped", "Pending"],
            "comments": [None, "Urgent"],
            "customerNumber": [101, 102],
        })
        is_valid, errors = validate_file(df, "orders")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_unknown_table_name_fails(self) -> None:
        is_valid, errors = validate_file(self.valid_customers, "unknown")
        self.assertFalse(is_valid)

    def test_payments_valid_passes(self) -> None:
        df = pd.DataFrame({
            "customerNumber": [101, 101, 102],
            "checkNumber": ["CHK001", "CHK002", "CHK003"],
            "paymentDate": ["2024-01-10", "2024-02-10", "2024-03-10"],
            "amount": [1000.0, 2500.0, 1500.0],
        })
        is_valid, errors = validate_file(df, "payments")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_payments_primary_key_null_fails(self) -> None:
        df = pd.DataFrame({
            "customerNumber": [101, None],
            "checkNumber": ["CHK001", "CHK002"],
            "paymentDate": ["2024-01-10", "2024-02-10"],
            "amount": [1000.0, 500.0],
        })
        is_valid, errors = validate_file(df, "payments")
        self.assertFalse(is_valid)
        self.assertTrue(any("customerNumber" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
