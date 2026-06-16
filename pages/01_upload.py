import io

import pandas as pd
import streamlit as st

from config import SUPPORTED_FILE_TYPES
from database.db_manager import get_table_row_count, table_exists
from ingestion.file_parser import parse_file_bytes
from ingestion.loader import load_dataframe
from ingestion.validator import SCHEMAS, validate_file

st.header("Upload Data")
st.markdown("Upload a CSV or XLSX file and load it into the dashboard.")

if "in_memory_data" not in st.session_state:
    st.session_state.in_memory_data = {}

uploaded_file = st.file_uploader(
    "Choose a file",
    type=SUPPORTED_FILE_TYPES,
)

table_name = st.selectbox(
    "Select target table",
    ["customers", "orders", "payments"],
)

persist = st.checkbox("Load to SQLite (persistent)", value=True)

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        file_bytes = io.BytesIO(bytes_data)

        with st.spinner("Parsing file..."):
            df = parse_file_bytes(file_bytes, uploaded_file.name)

        st.subheader("Raw Data Preview")
        st.dataframe(df.head(5))
        st.caption(f"Total rows in file: {len(df)}")

        is_valid, errors = validate_file(df, table_name)

        if not is_valid:
            st.error("Validation failed:")
            for err in errors:
                st.write(f"- {err}")
        else:
            st.success("Validation passed!")

            if st.button("Confirm & Load"):
                with st.spinner("Loading data..."):
                    if persist:
                        load_dataframe(df, table_name, mode="replace")
                        row_count = get_table_row_count(table_name)
                        st.success(
                            f"Loaded {row_count} rows into '{table_name}' table."
                        )
                    else:
                        st.session_state.in_memory_data[table_name] = df
                        st.success(
                            f"Loaded {len(df)} rows into memory "
                            f"('{table_name}' session only)."
                        )

    except Exception as e:
        st.error(f"An error occurred: {e}")

st.divider()
st.subheader("Currently Loaded Data")

for tbl in ["customers", "orders", "payments"]:
    persistent_count = (
        get_table_row_count(tbl) if table_exists(tbl) else 0
    )
    memory_count = len(
        st.session_state.in_memory_data.get(tbl, pd.DataFrame())
    )
    st.write(
        f"- **{tbl}**: "
        f"{persistent_count} persistent / {memory_count} in-memory rows"
    )

if st.button("Clear All Tables"):
    if persist:
        for tbl in ["customers", "orders", "payments"]:
            load_dataframe(
                pd.DataFrame(columns=list(SCHEMAS[tbl].keys())),
                tbl,
                mode="replace",
            )
    st.session_state.in_memory_data = {}
    st.success("All tables cleared.")
    st.rerun()
