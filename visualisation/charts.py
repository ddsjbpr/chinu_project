import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from config import DEFAULT_THEME

plt.style.use(DEFAULT_THEME)


def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    horizontal: bool = False,
    top_n: int | None = None,
) -> Figure:
    """Create a vertical or horizontal bar chart from a DataFrame.

    Args:
        df: Input DataFrame.
        x_col: Column name for the x-axis (categories).
        y_col: Column name for the y-axis (values).
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        horizontal: If True, draw a horizontal bar chart.
        top_n: If set, only show the top N rows.

    Returns:
        A Matplotlib Figure object.
    """
    data = df.copy()
    if top_n is not None:
        data = data.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))

    if horizontal:
        sns.barplot(data=data, y=x_col, x=y_col, ax=ax, hue=x_col, legend=False)
        ax.set_xlabel(ylabel or y_col)
        ax.set_ylabel(xlabel or x_col)
    else:
        sns.barplot(data=data, x=x_col, y=y_col, ax=ax, hue=x_col, legend=False)
        ax.set_xlabel(xlabel or x_col)
        ax.set_ylabel(ylabel or y_col)
        if len(data) > 5:
            ax.tick_params(axis="x", rotation=45)

    ax.set_title(title)
    fig.tight_layout()
    return fig


def line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    marker: str = "o",
) -> Figure:
    """Create a line chart from a DataFrame.

    Args:
        df: Input DataFrame.
        x_col: Column name for the x-axis.
        y_col: Column name for the y-axis.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        marker: Marker style for data points.

    Returns:
        A Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df[x_col], df[y_col], marker=marker, linestyle="-", linewidth=2)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    ax.set_title(title)
    if len(df) > 5:
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df[x_col], rotation=45, ha="right")
    fig.tight_layout()
    return fig


def histogram(
    df: pd.DataFrame,
    col: str,
    title: str = "",
    xlabel: str = "",
    bins: int = 20,
) -> Figure:
    """Create a histogram from a DataFrame column.

    Args:
        df: Input DataFrame.
        col: Column name to plot.
        title: Chart title.
        xlabel: X-axis label.
        bins: Number of bins.

    Returns:
        A Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(data=df, x=col, bins=bins, kde=True, ax=ax)
    ax.set_xlabel(xlabel or col)
    ax.set_ylabel("Frequency")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def pie_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str = "",
) -> Figure:
    """Create a pie chart from a DataFrame.

    Only use when there are fewer than 7 categories.

    Args:
        df: Input DataFrame.
        label_col: Column name for slice labels.
        value_col: Column name for slice values.
        title: Chart title.

    Returns:
        A Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        df[value_col],
        labels=df[label_col],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title(title)
    fig.tight_layout()
    return fig


def horizontal_bar_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    top_n: int | None = None,
) -> Figure:
    """Create a horizontal bar chart — ideal for ranked/categorical data.

    Args:
        df: Input DataFrame.
        label_col: Column name for bar labels (y-axis).
        value_col: Column name for bar values (x-axis).
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        top_n: If set, only show the top N rows.

    Returns:
        A Matplotlib Figure object.
    """
    data = df.copy()
    if top_n is not None:
        data = data.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=data, y=label_col, x=value_col, ax=ax, hue=label_col, legend=False)
    ax.set_xlabel(xlabel or value_col)
    ax.set_ylabel(ylabel or label_col)
    ax.set_title(title)
    fig.tight_layout()
    return fig
