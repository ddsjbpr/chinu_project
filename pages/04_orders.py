import matplotlib.pyplot as plt
import streamlit as st

from analysis.order_analysis import (
    avg_order_value_trend,
    distinct_order_statuses,
    filtered_orders,
    order_status_breakdown,
    orders_over_time,
    top_customers_by_order_count,
)
from database.db_manager import get_connection, get_table_row_count, table_exists
from visualisation.charts import bar_chart, horizontal_bar_chart, line_chart, pie_chart

st.header("Orders Analysis")

with get_connection() as conn:
    if not table_exists("orders") or get_table_row_count("orders") == 0:
        st.info("No order data loaded. Please upload order data first.")
        st.stop()

    statuses = distinct_order_statuses(conn)

    with st.sidebar:
        st.subheader("Filters")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        selected_status = st.selectbox("Status", ["All"] + statuses)

    start_str = str(start_date) if start_date else None
    end_str = str(end_date) if end_date else None
    filter_status = None if selected_status == "All" else selected_status

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orders Over Time")
        orders_ts = orders_over_time(conn)
        if not orders_ts.empty:
            fig = line_chart(
                orders_ts,
                x_col="month",
                y_col="order_count",
                title="Orders by Month",
                xlabel="Month",
                ylabel="Order Count",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    with col2:
        st.subheader("Order Status Breakdown")
        status_data = order_status_breakdown(conn)
        if not status_data.empty:
            if len(status_data) < 7:
                fig = pie_chart(
                    status_data,
                    label_col="status",
                    value_col="count",
                    title="Order Status",
                )
            else:
                fig = bar_chart(
                    status_data,
                    x_col="status",
                    y_col="count",
                    title="Order Status",
                    xlabel="Status",
                    ylabel="Count",
                )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Average Order Value Trend")
        avg_trend = avg_order_value_trend(conn)
        if not avg_trend.empty:
            fig = line_chart(
                avg_trend,
                x_col="month",
                y_col="avg_value",
                title="Average Order Value by Month",
                xlabel="Month",
                ylabel="Avg Value ($)",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    with col4:
        st.subheader("Top Customers by Order Count")
        top_customers = top_customers_by_order_count(conn, n=10)
        if not top_customers.empty:
            top_customers["customer_label"] = (
                "Cust #" + top_customers["customerNumber"].astype(str)
            )
            fig = horizontal_bar_chart(
                top_customers,
                label_col="customer_label",
                value_col="order_count",
                title="Top 10 Customers",
                xlabel="Order Count",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    st.divider()
    st.subheader("Order Data")

    filtered_df = filtered_orders(conn, start_str, end_str, filter_status)

    sort_options = (
        filtered_df.columns.tolist()
        if not filtered_df.empty
        else ["orderDate"]
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
        st.caption(f"Showing {len(sorted_df)} order(s)")
    else:
        st.info("No orders match the selected filters.")
