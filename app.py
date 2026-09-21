from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_high_revenue_target, add_time_features
from src.model import evaluate_revenue_models, get_feature_importance
from src.staffing_model import (
    WEEKDAY_ORDER as STAFFING_WEEKDAY_ORDER,
    build_staffing_schedule,
    evaluate_staffing_models,
)


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
def evaluate_dashboard_models(df: pd.DataFrame) -> dict:
    return evaluate_revenue_models(df)


@st.cache_resource
def evaluate_dashboard_staffing(df: pd.DataFrame) -> dict:
    return evaluate_staffing_models(df)


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
    total_records = len(df)
    average_line_revenue = df["Revenue"].mean() if total_records else 0
    total_units = df["Quantity"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total revenue", format_currency(total_revenue))
    col2.metric("POS records", f"{total_records:,}")
    col3.metric("Average line revenue", format_currency(average_line_revenue))
    col4.metric("Units sold", f"{total_units:,.1f}")


def show_overview_tab(df: pd.DataFrame) -> None:
    category_revenue = (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Revenue", "sum"), POS_Records=("Revenue", "size"))
        .sort_values("Revenue", ascending=False)
    )

    weekday_revenue = (
        df.groupby("Weekday", as_index=False)
        .agg(Revenue=("Revenue", "sum"), POS_Records=("Revenue", "size"))
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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

    hourly_revenue = (
        df.groupby("Hour", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            POS_Records=("Revenue", "size"),
            Average_Line_Revenue=("Revenue", "mean"),
        )
        .sort_values("Hour")
    )
    fig = px.line(
        hourly_revenue,
        x="Hour",
        y="Revenue",
        markers=True,
        title="Revenue by Hour",
        hover_data=["POS_Records", "Average_Line_Revenue"],
    )
    fig.update_traces(line_color="#2F6F73")
    st.plotly_chart(fig, width="stretch")


def show_menu_tab(df: pd.DataFrame) -> None:
    item_revenue = (
        df.groupby(["Menu Item", "Category"], as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
            POS_Records=("Revenue", "size"),
            Average_Line_Revenue=("Revenue", "mean"),
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
        hover_data=["Quantity", "POS_Records", "Average_Line_Revenue"],
    )
    st.plotly_chart(fig, width="stretch")

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
    st.plotly_chart(fig, width="stretch")

    st.dataframe(
        item_revenue,
        width="stretch",
        hide_index=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Average_Line_Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Quantity": st.column_config.NumberColumn(format="%.1f"),
        },
    )


def show_operations_tab(df: pd.DataFrame) -> None:
    server_performance = (
        df.groupby("Server Name", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            POS_Records=("Revenue", "size"),
            Quantity=("Quantity", "sum"),
            Average_Line_Revenue=("Revenue", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )

    order_type_revenue = (
        df.groupby("Order Type", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            POS_Records=("Revenue", "size"),
            Average_Line_Revenue=("Revenue", "mean"),
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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

    st.dataframe(
        server_performance,
        width="stretch",
        hide_index=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Average_Line_Revenue": st.column_config.NumberColumn(format="$%.2f"),
            "Quantity": st.column_config.NumberColumn(format="%.1f"),
        },
    )


def show_model_tab(df: pd.DataFrame) -> None:
    evaluation = evaluate_dashboard_models(df)
    summary = evaluation["summary"].copy()
    summary = summary[["Model", "Accuracy", "F1", "ROC_AUC", "CV_F1_Mean"]].rename(
        columns={"ROC_AUC": "ROC-AUC", "CV_F1_Mean": "CV F1"}
    )
    random_forest_results = evaluation["models"]["Random Forest"]
    feature_importance = get_feature_importance(random_forest_results["model"]).head(10)

    st.caption("Model results are trained on the full dataset, independent of dashboard filters.")
    st.metric("Best holdout F1 model", evaluation["best_model_name"])

    st.subheader("Model Comparison")
    st.dataframe(
        summary,
        width="stretch",
        hide_index=True,
        column_config={
            "Accuracy": st.column_config.NumberColumn(format="%.3f"),
            "F1": st.column_config.NumberColumn(format="%.3f"),
            "ROC-AUC": st.column_config.NumberColumn(format="%.3f"),
            "CV F1": st.column_config.NumberColumn(format="%.3f"),
        },
    )

    confusion = random_forest_results["confusion_matrix"]
    confusion_df = pd.DataFrame(
        confusion,
        index=["Actual Low", "Actual High"],
        columns=["Predicted Low", "Predicted High"],
    )

    left, right = st.columns(2)
    with left:
        fig = px.imshow(
            confusion_df,
            text_auto=True,
            title="Random Forest Confusion Matrix",
            color_continuous_scale=["#F4E3C1", "#2F6F73"],
        )
        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("Random Forest Holdout Metrics")
        st.metric("Accuracy", f"{random_forest_results['accuracy']:.2%}")
        st.metric("F1 score", f"{random_forest_results['f1']:.3f}")
        st.metric("ROC-AUC", f"{random_forest_results['roc_auc']:.3f}")

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
    st.plotly_chart(fig, width="stretch")

    st.text("Random Forest classification report")
    st.code(random_forest_results["classification_report"])


def show_staffing_tab(df: pd.DataFrame) -> None:
    evaluation = evaluate_dashboard_staffing(df)
    schedule = build_staffing_schedule(evaluation)
    random_forest_results = evaluation["models"]["Random Forest"]

    st.caption(
        "Staffing demand is a proxy: full staffing means hourly units sold are at or "
        "above the training period's 75th percentile. Actual staffing levels are not "
        "available in the dataset."
    )

    threshold_col, split_col, recall_col = st.columns(3)
    threshold_col.metric(
        "High-workload threshold",
        f"{evaluation['demand_threshold']:.0f} units/hour",
    )
    split_col.metric("Test period begins", str(evaluation["split_date"].date()))
    recall_col.metric("Random Forest recall", f"{random_forest_results['recall']:.1%}")

    summary = evaluation["summary"][
        [
            "Model",
            "Accuracy",
            "Precision",
            "Recall",
            "F1",
            "ROC_AUC",
            "CV_F1_Mean",
        ]
    ].rename(columns={"ROC_AUC": "ROC-AUC", "CV_F1_Mean": "CV F1"})

    st.subheader("Staffing Model Comparison")
    st.dataframe(
        summary,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(format="%.3f")
            for column in ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "CV F1"]
        },
    )

    schedule_matrix = schedule.pivot(
        index="Weekday",
        columns="Hour",
        values="Staffing Demand Score",
    ).reindex(STAFFING_WEEKDAY_ORDER)
    fig = px.imshow(
        schedule_matrix,
        text_auto=".2f",
        aspect="auto",
        title="Random Forest Staffing-Demand Score by Weekday and Hour",
        labels={"x": "Hour", "y": "Weekday", "color": "Demand score"},
        color_continuous_scale="YlOrRd",
        zmin=0,
        zmax=1,
    )
    st.plotly_chart(fig, width="stretch")

    recommended_windows = (
        schedule.loc[schedule["Full Staffing Recommended"]]
        .groupby("Weekday", observed=True)["Hour"]
        .apply(lambda hours: ", ".join(f"{hour}:00" for hour in hours))
        .reindex(STAFFING_WEEKDAY_ORDER)
        .reset_index(name="Recommended Full-Staffing Hours")
    )

    confusion_df = pd.DataFrame(
        random_forest_results["confusion_matrix"],
        index=["Actual Standard", "Actual Full"],
        columns=["Predicted Standard", "Predicted Full"],
    )
    left, right = st.columns([1, 1.3])
    with left:
        confusion_fig = px.imshow(
            confusion_df,
            text_auto=True,
            title="Random Forest Staffing Confusion Matrix",
            color_continuous_scale=["#F4E3C1", "#2F6F73"],
        )
        st.plotly_chart(confusion_fig, width="stretch")
    with right:
        st.subheader("Recommended Full-Staffing Windows")
        st.dataframe(recommended_windows, width="stretch", hide_index=True)

    st.info(
        "The Random Forest finds 74.9% of high-workload hours, but it also creates "
        "false positives. Managers should treat the schedule as a planning signal and "
        "combine it with reservations, events, weather, labor costs, and local knowledge."
    )


def show_insights_tab() -> None:
    recommendations = pd.DataFrame(
        [
            {
                "Finding": "Entrees generated $272,974.90, about 62.0% of total revenue.",
                "Recommendation": "Prioritize entree inventory, premium steak promotion, and entree pairing offers.",
            },
            {
                "Finding": "Desserts generated $17,739.00, about 4.0% of total revenue.",
                "Recommendation": "Introduce dessert upselling prompts, bundles, or post-entree offers.",
            },
            {
                "Finding": "New York Strip, Filet Mignon, and Ribeye Steak generated $228,576.70 combined, about 51.9% of revenue.",
                "Recommendation": "Protect availability of top steak items and promote beverage or side pairings.",
            },
            {
                "Finding": "Saturday had the highest average daily revenue at about $1,421.85.",
                "Recommendation": "Use Saturday demand patterns to guide inventory and prep planning.",
            },
            {
                "Finding": "The staffing model flags 5 PM through 10 PM daily, plus Saturday at 1 PM.",
                "Recommendation": "Use these windows as a conservative signal, then adjust for reservations and local conditions.",
            },
            {
                "Finding": "Nina led server revenue with $91,506.80, about 20.8% of total revenue.",
                "Recommendation": "Study top-server POS record patterns and use them to form testable training hypotheses.",
            },
        ]
    )

    st.dataframe(
        recommendations,
        width="stretch",
        hide_index=True,
    )


df = load_dashboard_data()
filtered_df = filter_data(df)

st.title("Restaurant POS Analytics Dashboard")
st.caption(
    "Interactive revenue, menu, server, and POS record analysis from simulated steakhouse data."
)

if filtered_df.empty:
    st.warning("No POS records match the selected filters.")
    st.stop()

show_kpis(filtered_df)

overview_tab, menu_tab, operations_tab, model_tab, staffing_tab, insights_tab = st.tabs(
    ["Overview", "Menu", "Operations", "Model", "Staffing", "Insights"]
)

with overview_tab:
    show_overview_tab(filtered_df)

with menu_tab:
    show_menu_tab(filtered_df)

with operations_tab:
    show_operations_tab(filtered_df)

with model_tab:
    show_model_tab(df)

with staffing_tab:
    show_staffing_tab(df)

with insights_tab:
    show_insights_tab()
