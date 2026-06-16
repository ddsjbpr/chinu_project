import streamlit as st


def kpi_card(label: str, value: str, delta: str | None = None) -> None:
    """Render a single KPI metric card using Streamlit's metric component.

    Args:
        label: Display label for the metric.
        value: The metric value as a string (e.g. "1,234" or "$50K").
        delta: Optional delta indicator string (e.g. "+12%").
    """
    st.metric(label=label, value=value, delta=delta)
