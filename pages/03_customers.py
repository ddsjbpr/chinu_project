import matplotlib.pyplot as plt
import streamlit as st

from analysis.customer_analysis import (
    credit_limit_distribution,
    customers_by_country,
    distinct_countries,
    distinct_sales_reps,
    filtered_customers,
    sales_rep_workload,
    top_cities,
)
from database.db_manager import get_connection, get_table_row_count, table_exists
from visualisation.charts import bar_chart, histogram, horizontal_bar_chart, pie_chart

st.header("Customer Analysis")

with get_connection() as conn:
    if not table_exists("customers") or get_table_row_count("customers") == 0:
        st.info("No customer data loaded. Please upload customer data first.")
        st.stop()

    countries = distinct_countries(conn)
    sales_reps = distinct_sales_reps(conn)

    with st.sidebar:
        st.subheader("Filters")
        selected_country = st.selectbox(
            "Country", ["All"] + countries
        )
        selected_rep = st.selectbox(
            "Sales Rep", ["All"] + [str(r) for r in sales_reps]
        )

    filter_country = None if selected_country == "All" else selected_country
    filter_rep = None if selected_rep == "All" else float(selected_rep)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Credit Limit Distribution")
        credit_data = credit_limit_distribution(conn)
        if not credit_data.empty:
            fig = histogram(
                credit_data,
                col="creditLimit",
                title="Credit Limit Distribution",
                xlabel="Credit Limit ($)",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    with col2:
        st.subheader("Customers by Country")
        country_data = customers_by_country(conn)
        if not country_data.empty:
            if len(country_data) < 7:
                fig = pie_chart(
                    country_data,
                    label_col="country",
                    value_col="count",
                    title="Customers by Country",
                )
            else:
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
            st.info("No data.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Top 10 Cities")
        cities_data = top_cities(conn, n=10)
        if not cities_data.empty:
            fig = horizontal_bar_chart(
                cities_data,
                label_col="city",
                value_col="count",
                title="Top 10 Cities",
                xlabel="Customer Count",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    with col4:
        st.subheader("Sales Rep Workload")
        rep_data = sales_rep_workload(conn)
        if not rep_data.empty:
            rep_data["rep_label"] = (
    rep_data["salesRepEmployeeNumber"].astype(int).astype(str)
)
            fig = horizontal_bar_chart(
                rep_data,
                label_col="rep_label",
                value_col="customer_count",
                title="Customers per Sales Rep",
                xlabel="Customer Count",
            )
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No data.")

    st.divider()
    st.subheader("Customer Data")

    filtered_df = filtered_customers(conn, filter_country, filter_rep)

    sort_options = (
        filtered_df.columns.tolist()
        if not filtered_df.empty
        else ["customerName"]
    )
    sort_col = st.selectbox(
        "Sort by",
        options=sort_options,
        index=0,
    )
    sort_asc = st.checkbox("Ascending", value=True)

    if not filtered_df.empty:
        sorted_df = filtered_df.sort_values(
            by=sort_col, ascending=sort_asc
        )
        st.dataframe(sorted_df, use_container_width=True)
        st.caption(f"Showing {len(sorted_df)} customer(s)")
    else:
        st.info("No customers match the selected filters.")
