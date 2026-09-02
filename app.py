from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_high_revenue_target, add_time_features
from src.model import get_feature_importance, train_revenue_classifier


PROJECT_ROOT = Path(__file__).parent
DATA_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"
WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
COLOR_SEQUENCE = [
    "#2F6F73",
    "#C08457",
    "#577590",
    "#8A6FDF",
    "#B56576",
    "#4D908E",
    "#F8961E",
]


st.set_page_config(
    page_title="Restaurant POS Analytics",
    layout="wide",
)


@st.cache_data
def load_dashboard_data() -> pd.DataFrame:
    raw_df = load_pos_data(DATA_PATH)
    df = clean_pos_data(raw_df)
    df = add_time_features(df)
    df = add_high_revenue_target(df)
    return df


@st.cache_resource
def train_dashboard_model(df: pd.DataFrame) -> dict:
    return train_revenue_classifier(df)


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

    categories = st.sidebar.multiselect(
        "Category",
        options=sorted(df["Category"].unique()),
        default=sorted(df["Category"].unique()),
    )
    servers = st.sidebar.multiselect(
        "Server",
        options=sorted(df["Server Name"].unique()),
        default=sorted(df["Server Name"].unique()),
    )
    order_types = st.sidebar.multiselect(
        "Order type",
        options=sorted(df["Order Type"].unique()),
        default=sorted(df["Order Type"].unique()),
    )
    payment_methods = st.sidebar.multiselect(
        "Payment method",
        options=sorted(df["Payment Method"].unique()),
        default=sorted(df["Payment Method"].unique()),
    )

    filtered_df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
        & (df["Category"].isin(categories))
        & (df["Server Name"].isin(servers))
        & (df["Order Type"].isin(order_types))
        & (df["Payment Method"].isin(payment_methods))
    ].copy()

    return filtered_df


def show_kpis(df: pd.DataFrame) -> None:
    total_revenue = df["Revenue"].sum()
    total_orders = len(df)
    average_order_value = df["Revenue"].mean() if total_orders else 0
    total_units = df["Quantity"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total revenue", format_currency(total_revenue))
    col2.metric("Transactions", f"{total_orders:,}")
    col3.metric("Average order value", format_currency(average_order_value))
    col4.metric("Units sold", f"{total_units:,.1f}")


def show_overview_tab(df: pd.DataFrame) -> None:
    category_revenue = (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Transactions=("Revenue", "size"))
        .sort_values("Revenue", ascending=False)
    )

    weekday_revenue = (
        df.groupby("Weekday", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Transactions=("Revenue", "size"))
    )
    weekday_revenue["Weekday"] = pd.Categorical(
        weekday_revenue["Weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )
    weekday_revenue = weekday_revenue.sort_values("Weekday")

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            category_revenue,
            x="Revenue",
            y="Category",
            orientation="h",
            title="Revenue by Category",
            color="Category",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            weekday_revenue,
            x="Weekday",
            y="Revenue",
            title="Revenue by Weekday",
            color="Weekday",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    hourly_revenue = (
        df.groupby("Hour", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Transactions=("Revenue", "size"),
            Average_Order_Value=("Revenue", "mean"),
        )
        .sort_values("Hour")
    )
    fig = px.line(
        hourly_revenue,
        x="Hour",
        y="Revenue",
        markers=True,
        title="Revenue by Hour",
        hover_data=["Transactions", "Average_Order_Value"],
    )
    fig.update_traces(line_color="#2F6F73")
    st.plotly_chart(fig, use_container_width=True)


def show_menu_tab(df: pd.DataFrame) -> None:
    item_revenue = (
        df.groupby(["Menu Item", "Category"], as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
            Transactions=("Revenue", "size"),
            Average_Order_Value=("Revenue", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )

    top_items = item_revenue.head(10)
    fig = px.bar(
        top_items.sort_values("Revenue"),
        x="Revenue",
        y="Menu Item",
        orientation="h",
        title="Top Menu Items by Revenue",
        color="Category",
        color_discrete_sequence=COLOR_SEQUENCE,
        hover_data=["Quantity", "Transactions", "Average_Order_Value"],
    )
    st.plotly_chart(fig, use_container_width=True)

    category_mix = (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Revenue", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    fig = px.pie(
        category_mix,
        names="Category",
        values="Revenue",
        title="Revenue Share by Category",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.45,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        item_revenue,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Average_Order_Value": st.column_config.NumberColumn(format="$%.2f"),
            "Quantity": st.column_config.NumberColumn(format="%.1f"),
        },
    )


def show_operations_tab(df: pd.DataFrame) -> None:
    server_performance = (
        df.groupby("Server Name", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Transactions=("Revenue", "size"),
            Quantity=("Quantity", "sum"),
            Average_Order_Value=("Revenue", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )

    order_type_revenue = (
        df.groupby("Order Type", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Transactions=("Revenue", "size"),
            Average_Order_Value=("Revenue", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            server_performance.sort_values("Revenue"),
            x="Revenue",
            y="Server Name",
            orientation="h",
            title="Revenue by Server",
            color="Server Name",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            order_type_revenue,
            x="Order Type",
            y="Revenue",
            title="Revenue by Order Type",
            color="Order Type",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        server_performance,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Average_Order_Value": st.column_config.NumberColumn(format="$%.2f"),
            "Quantity": st.column_config.NumberColumn(format="%.1f"),
        },
    )


def show_model_tab(df: pd.DataFrame) -> None:
    model_results = train_dashboard_model(df)
    feature_importance = get_feature_importance(model_results["model"]).head(10)

    st.caption("Model results are trained on the full dataset, independent of dashboard filters.")
    st.metric("High-revenue classifier accuracy", f"{model_results['accuracy']:.2%}")

    fig = px.bar(
        feature_importance.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top Model Feature Importances",
        color="Importance",
        color_continuous_scale=["#E9C46A", "#2F6F73"],
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.text("Classification report")
    st.code(model_results["classification_report"])


df = load_dashboard_data()
filtered_df = filter_data(df)

st.title("Restaurant POS Analytics Dashboard")
st.caption(
    "Interactive revenue, menu, server, and order trend analysis from simulated steakhouse POS data."
)

if filtered_df.empty:
    st.warning("No transactions match the selected filters.")
    st.stop()

show_kpis(filtered_df)

overview_tab, menu_tab, operations_tab, model_tab = st.tabs(
    ["Overview", "Menu", "Operations", "Model"]
)

with overview_tab:
    show_overview_tab(filtered_df)

with menu_tab:
    show_menu_tab(filtered_df)

with operations_tab:
    show_operations_tab(filtered_df)

with model_tab:
    show_model_tab(df)
