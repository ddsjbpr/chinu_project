import sqlite3
import unittest

import pandas as pd

from analysis.customer_analysis import (
    credit_limit_distribution,
    sales_rep_workload,
)
from analysis.order_analysis import (
    order_status_breakdown,
)
from analysis.payment_analysis import (
    credit_vs_payments,
    late_payments,
    payment_amount_distribution,
)
from analysis.summary_stats import (
    avg_credit_limit,
    customers_by_country,
    top_customers_by_credit,
    total_customers,
    total_orders,
    total_revenue,
)


class TestSummaryStats(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
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
            "creditLimit REAL);"
            "CREATE TABLE orders ("
            "orderNumber INTEGER PRIMARY KEY, "
            "orderDate TEXT, "
            "requiredDate TEXT, "
            "shippedDate TEXT, "
            "status TEXT, "
            "comments TEXT, "
            "customerNumber INTEGER);"
            "CREATE TABLE payments ("
            "customerNumber INTEGER, "
            "checkNumber TEXT, "
            "paymentDate TEXT, "
            "amount REAL, "
            "PRIMARY KEY (customerNumber, checkNumber));"
        )

        sample_customers = pd.DataFrame({
            "customerNumber": [1, 2, 3],
            "customerName": ["A", "B", "C"],
            "contactLastName": ["X", "Y", "Z"],
            "contactFirstName": ["x", "y", "z"],
            "phone": ["1", "2", "3"],
            "addressLine1": ["Addr1", "Addr2", "Addr3"],
            "addressLine2": [None, None, None],
            "city": ["NY", "LA", "NY"],
            "state": ["NY", "CA", "NY"],
            "postalCode": ["10001", "90001", "10002"],
            "country": ["USA", "USA", "UK"],
            "salesRepEmployeeNumber": [1001.0, 1002.0, None],
            "creditLimit": [50000.0, 75000.0, 30000.0],
        })
        sample_customers.to_sql(
            "customers", self.conn, if_exists="replace", index=False
        )

        sample_orders = pd.DataFrame({
            "orderNumber": [1, 2, 3],
            "orderDate": ["2024-01-15", "2024-02-01", "2024-03-10"],
            "requiredDate": ["2024-02-15", "2024-03-01", "2024-04-10"],
            "shippedDate": ["2024-02-10", None, "2024-03-15"],
            "status": ["Shipped", "Pending", "Shipped"],
            "comments": [None, "Urgent", None],
            "customerNumber": [1, 2, 1],
        })
        sample_orders.to_sql("orders", self.conn, if_exists="replace", index=False)

        sample_payments = pd.DataFrame({
            "customerNumber": [1, 2],
            "checkNumber": ["CHK001", "CHK002"],
            "paymentDate": ["2024-01-20", "2024-02-15"],
            "amount": [10000.0, 20000.0],
        })
        sample_payments.to_sql("payments", self.conn, if_exists="replace", index=False)

    def test_total_customers(self) -> None:
        self.assertEqual(total_customers(self.conn), 3)

    def test_total_orders(self) -> None:
        self.assertEqual(total_orders(self.conn), 3)

    def test_total_revenue(self) -> None:
        self.assertAlmostEqual(total_revenue(self.conn), 30000.0)

    def test_avg_credit_limit(self) -> None:
        self.assertAlmostEqual(avg_credit_limit(self.conn), 51666.67, places=2)

    def test_customers_by_country(self) -> None:
        result = customers_by_country(self.conn)
        self.assertEqual(len(result), 2)
        usa_row = result[result["country"] == "USA"].iloc[0]
        self.assertEqual(usa_row["count"], 2)

    def test_top_customers_by_credit(self) -> None:
        result = top_customers_by_credit(self.conn, n=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["customerName"], "B")

    def test_credit_limit_distribution(self) -> None:
        result = credit_limit_distribution(self.conn)
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result["creditLimit"].sum(), 155000.0)

    def test_sales_rep_workload(self) -> None:
        result = sales_rep_workload(self.conn)
        self.assertEqual(len(result), 2)

    def test_order_status_breakdown(self) -> None:
        result = order_status_breakdown(self.conn)
        self.assertEqual(len(result), 2)
        shipped_row = result[result["status"] == "Shipped"].iloc[0]
        self.assertEqual(shipped_row["count"], 2)

    def test_credit_vs_payments(self) -> None:
        result = credit_vs_payments(self.conn)
        self.assertEqual(len(result), 3)
        cust1 = result[result["customerName"] == "A"].iloc[0]
        self.assertAlmostEqual(cust1["total_payments"], 10000.0)

    def test_late_payments_empty(self) -> None:
        result = late_payments(self.conn)
        self.assertTrue(len(result) == 0 or "days_late" in result.columns)

    def test_payment_amount_distribution(self) -> None:
        result = payment_amount_distribution(self.conn)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result["amount"].sum(), 30000.0)


class TestEmptyDataFrames(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
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
            "creditLimit REAL);"
            "CREATE TABLE payments ("
            "customerNumber INTEGER, "
            "checkNumber TEXT, "
            "paymentDate TEXT, "
            "amount REAL, "
            "PRIMARY KEY (customerNumber, checkNumber));"
        )

    def test_total_customers_empty(self) -> None:
        self.assertEqual(total_customers(self.conn), 0)

    def test_total_revenue_empty(self) -> None:
        self.assertAlmostEqual(total_revenue(self.conn), 0.0)

    def test_avg_credit_limit_empty(self) -> None:
        self.assertAlmostEqual(avg_credit_limit(self.conn), 0.0)


if __name__ == "__main__":
    unittest.main()
