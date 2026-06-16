import matplotlib.pyplot as plt
import streamlit as st

from analysis.payment_analysis import (
    credit_vs_payments,
    distinct_customer_numbers,
    filtered_payments,
    late_payments,
    payment_amount_distribution,
    payments_over_time,
)
from database.db_manager import get_connection, get_table_row_count, table_exists
from visualisation.charts import histogram, horizontal_bar_chart, line_chart

st.header("Payments Analysis")

with get_connection() as conn:
    has_payments = table_exists("payments") and get_table_row_count("payments") > 0
    has_orders = table_exists("orders") and get_table_row_count("orders") > 0

    if not has_payments:
        st.info("No payment data loaded. Please upload payment data first.")
        st.stop()

    customer_numbers = distinct_customer_numbers(conn)

    with st.sidebar:
        st.subheader("Filters")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        selected_customer = st.selectbox(
            "Customer Number", ["All"] + [str(c) for c in customer_numbers]
        )

    start_str = str(start_date) if start_date else None
    end_str = str(end_date) if end_date else None
    filter_customer = (
        None if selected_customer == "All" else int(selected_customer)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payments Over Time")
        pay_ts = payments_over_time(conn)
        if not pay_ts.empty:
            fig = line_chart(
                pay_ts,
                x_col="month",
                y_col="total",
                title="Total Payments by Month",
                xlabel="Month",
                ylabel="Total ($)",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    with col2:
        st.subheader("Payment Amount Distribution")
        amount_data = payment_amount_distribution(conn)
        if not amount_data.empty:
            fig = histogram(
                amount_data,
                col="amount",
                title="Payment Amount Distribution",
                xlabel="Amount ($)",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    st.divider()
    st.subheader("Credit Limit vs Total Payments")

    credit_pay = credit_vs_payments(conn)
    if not credit_pay.empty:
        top_credit_pay = credit_pay.head(10)
        fig = horizontal_bar_chart(
            top_credit_pay,
            label_col="customerName",
            value_col="creditLimit",
            title="Top 10 Customers by Credit Limit",
            xlabel="Credit Limit ($)",
        )
        st.pyplot(fig)
        plt.close(fig)

        fig2 = horizontal_bar_chart(
            top_credit_pay,
            label_col="customerName",
            value_col="total_payments",
            title="Top 10 Customers by Total Payments",
            xlabel="Total Payments ($)",
        )
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("No data.")

    if has_orders:
        st.divider()
        st.subheader("Late Payments")
        late_data = late_payments(conn)
        if not late_data.empty:
            st.dataframe(late_data, use_container_width=True)
            st.caption(f"Found {len(late_data)} late payment(s)")
        else:
            st.info("No late payments found.")

    st.divider()
    st.subheader("Payment Data")

    filtered_df = filtered_payments(conn, start_str, end_str, filter_customer)

    sort_options = (
        filtered_df.columns.tolist()
        if not filtered_df.empty
        else ["paymentDate"]
    )
    sort_col = st.selectbox(
        "Sort by",
        options=sort_options,
        index=0,
    )
    sort_asc = st.checkbox("Ascending", value=False)

    if not filtered_df.empty:
        sorted_df = filtered_df.sort_values(
            by=sort_col, ascending=sort_asc
        )
        st.dataframe(sorted_df, use_container_width=True)
        st.caption(f"Showing {len(sorted_df)} payment(s)")
    else:
        st.info("No payments match the selected filters.")
