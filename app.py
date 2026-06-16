import streamlit as st

from config import APP_TITLE, PAGE_ICON
from database.db_manager import initialise_db

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)

initialise_db()

st.sidebar.title(APP_TITLE)
st.sidebar.markdown("Navigate using the pages above.")
