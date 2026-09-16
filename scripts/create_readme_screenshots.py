from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_high_revenue_target, add_time_features
from src.model import evaluate_revenue_models


DATA_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "screenshots"
COLORS = {
    "teal": "#2F6F73",
    "copper": "#C08457",
    "blue": "#577590",
    "purple": "#8A6FDF",
    "rose": "#B56576",
    "green": "#4D908E",
    "gold": "#E9C46A",
    "ink": "#1F2933",
    "muted": "#667085",
    "grid": "#D8DEE4",
}


def load_project_data() -> pd.DataFrame:
    df = clean_pos_data(load_pos_data(DATA_PATH))
    df = add_time_features(df)
    df = add_high_revenue_target(df)
    return df


def currency(value: float) -> str:
    if value >= 1000:
        return f"${value / 1000:,.1f}K"
    return f"${value:,.0f}"


def add_kpi(ax, title: str, value: str) -> None:
    ax.axis("off")
    ax.text(0.02, 0.72, title, fontsize=12, color=COLORS["muted"], weight="bold")
    ax.text(0.02, 0.24, value, fontsize=24, color=COLORS["ink"], weight="bold")
    ax.axhline(0.02, color=COLORS["grid"], linewidth=2)


def save_overview(df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(14, 9), facecolor="white")
    gs = fig.add_gridspec(3, 4, height_ratios=[0.8, 2.2, 2.2], hspace=0.55, wspace=0.45)

    fig.suptitle("Restaurant POS Analytics Dashboard", x=0.05, ha="left", fontsize=22, weight="bold")
    fig.text(0.05, 0.92, "Executive overview of revenue, demand timing, and POS record volume", fontsize=12, color=COLORS["muted"])

    kpis = [
        ("Total Revenue", currency(df["Revenue"].sum())),
        ("POS Records", f"{len(df):,}"),
        ("Avg Line Revenue", currency(df["Revenue"].mean())),
        ("Units Sold", f"{df['Quantity'].sum():,.1f}"),
    ]
    for idx, (title, value) in enumerate(kpis):
        add_kpi(fig.add_subplot(gs[0, idx]), title, value)

    category_revenue = df.groupby("Category")["Revenue"].sum().sort_values()
    ax = fig.add_subplot(gs[1, :2])
    category_revenue.plot(kind="barh", ax=ax, color=COLORS["teal"])
    ax.set_title("Revenue by Category", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_revenue = df.groupby("Weekday")["Revenue"].sum().reindex(weekday_order)
    ax = fig.add_subplot(gs[1, 2:])
    weekday_revenue.plot(kind="bar", ax=ax, color=COLORS["copper"])
    ax.set_title("Revenue by Weekday", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)

    hourly = df.groupby("Hour")["Revenue"].sum().sort_index()
    ax = fig.add_subplot(gs[2, :])
    ax.plot(hourly.index, hourly.values, marker="o", color=COLORS["blue"], linewidth=2.5)
    ax.fill_between(hourly.index, hourly.values, color=COLORS["blue"], alpha=0.12)
    ax.set_title("Revenue by Hour", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Revenue")
    ax.grid(color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)

    fig.savefig(OUTPUT_DIR / "dashboard-overview.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_menu_operations(df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(14, 8), facecolor="white")
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.35)

    fig.suptitle("Menu and Operations Performance", x=0.05, ha="left", fontsize=22, weight="bold")
    fig.text(0.05, 0.92, "Top-selling items, server revenue, and category mix", fontsize=12, color=COLORS["muted"])

    top_items = df.groupby("Menu Item")["Revenue"].sum().sort_values(ascending=False).head(10).sort_values()
    ax = fig.add_subplot(gs[:, 0])
    top_items.plot(kind="barh", ax=ax, color=COLORS["green"])
    ax.set_title("Top 10 Menu Items by Revenue", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    server_revenue = df.groupby("Server Name")["Revenue"].sum().sort_values()
    ax = fig.add_subplot(gs[0, 1])
    server_revenue.plot(kind="barh", ax=ax, color=COLORS["purple"])
    ax.set_title("Revenue by Server", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    category_revenue = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    ax = fig.add_subplot(gs[1, 1])
    ax.pie(
        category_revenue,
        labels=category_revenue.index,
        autopct="%1.1f%%",
        startangle=120,
        colors=[COLORS["teal"], COLORS["copper"], COLORS["blue"], COLORS["rose"], COLORS["gold"]],
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title("Revenue Share by Category", loc="left", fontsize=14, weight="bold")

    fig.savefig(OUTPUT_DIR / "dashboard-menu-operations.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_model_evaluation(df: pd.DataFrame) -> None:
    evaluation = evaluate_revenue_models(df)
    summary = evaluation["summary"].copy()
    confusion = evaluation["models"]["Random Forest"]["confusion_matrix"]

    fig = plt.figure(figsize=(16, 8), facecolor="white")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 2.3], width_ratios=[0.9, 1.4], hspace=0.5, wspace=0.55)

    fig.suptitle("High-Revenue POS Record Model Evaluation", x=0.05, ha="left", fontsize=22, weight="bold")
    fig.text(0.05, 0.92, "Baseline comparison, cross-validation, and Random Forest confusion matrix", fontsize=12, color=COLORS["muted"])

    table_ax = fig.add_subplot(gs[0, :])
    table_ax.axis("off")
    display_columns = ["Model", "Accuracy", "F1", "ROC_AUC", "CV_F1_Mean"]
    table_data = summary[display_columns].copy()
    for column in display_columns[1:]:
        table_data[column] = table_data[column].map(lambda value: f"{value:.3f}")
    table = table_ax.table(
        cellText=table_data.values,
        colLabels=["Model", "Accuracy", "F1", "ROC-AUC", "CV F1"],
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(COLORS["grid"])
        if row == 0:
            cell.set_facecolor(COLORS["teal"])
            cell.set_text_props(color="white", weight="bold")

    ax = fig.add_subplot(gs[1, 0])
    im = ax.imshow(confusion, cmap="YlGnBu")
    ax.set_title("Random Forest Confusion Matrix", loc="left", fontsize=14, weight="bold")
    ax.set_xticks([0, 1], labels=["Predicted Low", "Predicted High"])
    ax.set_yticks([0, 1], labels=["Actual Low", "Actual High"])
    for row in range(confusion.shape[0]):
        for col in range(confusion.shape[1]):
            ax.text(col, row, confusion[row, col], ha="center", va="center", color=COLORS["ink"], fontsize=16, weight="bold")
    im.set_clim(confusion.min(), confusion.max())

    importance = evaluation["models"]["Random Forest"]["model"]
    from src.model import get_feature_importance

    top_features = get_feature_importance(importance).head(10).sort_values("Importance")
    top_features["Feature"] = (
        top_features["Feature"]
        .str.replace("categories__", "", regex=False)
        .str.replace("numbers__", "", regex=False)
        .str.replace("_", " ", regex=False)
    )
    ax = fig.add_subplot(gs[1, 1])
    ax.barh(top_features["Feature"], top_features["Importance"], color=COLORS["rose"])
    ax.set_title("Top Random Forest Feature Importances", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Importance")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    fig.savefig(OUTPUT_DIR / "dashboard-model-evaluation.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_project_data()
    save_overview(df)
    save_menu_operations(df)
    save_model_evaluation(df)
    print(f"Saved screenshots to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
