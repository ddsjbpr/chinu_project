import matplotlib.pyplot as plt
import streamlit as st

from analysis.summary_stats import (
    avg_credit_limit,
    customers_by_country,
    revenue_over_time,
    top_customers_by_credit,
    total_customers,
    total_orders,
    total_revenue,
)
from database.db_manager import get_connection, table_exists
from visualisation.charts import bar_chart, horizontal_bar_chart, line_chart
from visualisation.kpi_cards import kpi_card

st.header("Dashboard Overview")

with get_connection() as conn:
    has_customers = table_exists("customers") and total_customers(conn) > 0
    has_payments = table_exists("payments") and total_revenue(conn) > 0
    has_orders = table_exists("orders") and total_orders(conn) > 0

    if not has_customers:
        st.info("No data loaded yet. Go to the Upload page to add data.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Customers", f"{total_customers(conn):,}")
    with col2:
        kpi_card("Total Orders", f"{total_orders(conn):,}" if has_orders else "N/A")
    with col3:
        revenue = total_revenue(conn)
        kpi_card("Total Revenue", f"${revenue:,.2f}" if has_payments else "N/A")
    with col4:
        avg_limit = avg_credit_limit(conn)
        kpi_card("Avg Credit Limit", f"${avg_limit:,.2f}")

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Customers by Country")
        country_data = customers_by_country(conn)
        if not country_data.empty:
            fig = bar_chart(
                country_data,
                x_col="country",
                y_col="count",
                title="Customers by Country",
                xlabel="Country",
                ylabel="Count",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No customer data.")

    with chart_col2:
        st.subheader("Revenue Over Time")
        if has_payments:
            revenue_data = revenue_over_time(conn)
            if not revenue_data.empty:
                fig = line_chart(
                    revenue_data,
                    x_col="month",
                    y_col="revenue",
                    title="Revenue Trend",
                    xlabel="Month",
                    ylabel="Revenue ($)",
                )
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No revenue data.")
        else:
            st.info("No payment data loaded.")

    st.divider()
    st.subheader("Top 10 Customers by Credit Limit")
    top_customers = top_customers_by_credit(conn, n=10)
    if not top_customers.empty:
        fig = horizontal_bar_chart(
            top_customers,
            label_col="customerName",
            value_col="creditLimit",
            title="Top 10 Customers by Credit Limit",
            xlabel="Credit Limit ($)",
        )
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No customer data.")
