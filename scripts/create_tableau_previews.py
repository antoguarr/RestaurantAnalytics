from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tableau" / "data"
OUTPUT_DIR = PROJECT_ROOT / "tableau" / "screenshots"

COLORS = {
    "teal": "#147D7E",
    "coral": "#E76F51",
    "gold": "#E9C46A",
    "blue": "#457B9D",
    "green": "#2A9D8F",
    "ink": "#202A33",
    "muted": "#66727D",
    "grid": "#D9E1E5",
    "panel": "#F5F7F8",
}


def currency(value: float) -> str:
    return f"${value / 1000:,.1f}K" if value >= 1000 else f"${value:,.0f}"


def add_kpi(ax, title: str, value: str, accent: str) -> None:
    ax.set_facecolor(COLORS["panel"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axvline(0, color=accent, linewidth=6)
    ax.text(0.08, 0.67, title, color=COLORS["muted"], fontsize=11, weight="bold")
    ax.text(0.08, 0.18, value, color=COLORS["ink"], fontsize=23, weight="bold")


def compact_hour_ranges(hours: pd.Series) -> str:
    """Format consecutive hours as compact ranges for the dashboard table."""
    values = sorted(int(hour) for hour in hours)
    groups = []
    start = previous = values[0]
    for hour in values[1:]:
        if hour == previous + 1:
            previous = hour
            continue
        groups.append((start, previous))
        start = previous = hour
    groups.append((start, previous))
    return ", ".join(
        f"{start}:00-{end}:00" if start != end else f"{start}:00"
        for start, end in groups
    )


def save_executive_overview(pos: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(15, 9), facecolor="white")
    grid = fig.add_gridspec(3, 4, height_ratios=[0.72, 2.1, 2.2], hspace=0.55, wspace=0.42)

    fig.suptitle("Restaurant POS Executive Overview", x=0.05, ha="left", fontsize=23, weight="bold", color=COLORS["ink"])
    fig.text(0.05, 0.92, "Tableau dashboard design preview | Filterable by date, category, server, order type, and payment method", fontsize=11, color=COLORS["muted"])

    kpis = [
        ("Total Revenue", currency(pos["revenue"].sum()), COLORS["teal"]),
        ("POS Records", f"{len(pos):,}", COLORS["coral"]),
        ("Average Line Revenue", currency(pos["revenue"].mean()), COLORS["gold"]),
        ("Units Sold", f"{pos['quantity'].sum():,.0f}", COLORS["blue"]),
    ]
    for index, (title, value, accent) in enumerate(kpis):
        add_kpi(fig.add_subplot(grid[0, index]), title, value, accent)

    category = pos.groupby("category")["revenue"].sum().sort_values()
    ax = fig.add_subplot(grid[1, :2])
    ax.barh(category.index, category.values, color=COLORS["teal"])
    ax.set_title("Revenue by Category", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Revenue")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    top_items = pos.groupby("menu_item")["revenue"].sum().nlargest(8).sort_values()
    ax = fig.add_subplot(grid[1, 2:])
    ax.barh(top_items.index, top_items.values, color=COLORS["coral"])
    ax.set_title("Top Menu Items by Revenue", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Revenue")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)

    hourly = pos.groupby("hour")["revenue"].sum().sort_index()
    ax = fig.add_subplot(grid[2, :])
    ax.plot(hourly.index, hourly.values, color=COLORS["blue"], marker="o", linewidth=2.7)
    ax.fill_between(hourly.index, hourly.values, color=COLORS["blue"], alpha=0.12)
    ax.set_title("Revenue by Hour", loc="left", fontsize=14, weight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Revenue")
    ax.set_xticks(hourly.index)
    ax.grid(color=COLORS["grid"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)

    fig.savefig(OUTPUT_DIR / "tableau-executive-overview.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_staffing_and_models(schedule: pd.DataFrame, results: pd.DataFrame) -> None:
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap = schedule.pivot(index="Weekday", columns="Hour", values="Staffing Demand Score").reindex(weekday_order)
    staffing_results = results[results["Model Task"] == "Full-staffing demand classification"].copy()
    staffing_results = staffing_results.sort_values("F1", ascending=False)

    fig = plt.figure(figsize=(15, 8.5), facecolor="white")
    grid = fig.add_gridspec(2, 2, height_ratios=[1.55, 1], width_ratios=[1.45, 1], hspace=0.45, wspace=0.38)
    fig.suptitle("Staffing Demand and Model Evaluation", x=0.05, ha="left", fontsize=23, weight="bold", color=COLORS["ink"])
    fig.text(0.05, 0.92, "Tableau dashboard design preview | Full staffing is a model-based demand proxy, not observed labor need", fontsize=11, color=COLORS["muted"])

    ax = fig.add_subplot(grid[0, :])
    image = ax.imshow(heatmap.values, cmap="YlGnBu", vmin=0.2, vmax=0.7, aspect="auto")
    ax.set_title("Predicted Full-Staffing Demand by Weekday and Hour", loc="left", fontsize=14, weight="bold")
    ax.set_xticks(range(len(heatmap.columns)), labels=heatmap.columns)
    ax.set_yticks(range(len(heatmap.index)), labels=heatmap.index)
    ax.set_xlabel("Hour of Day")
    for row in range(heatmap.shape[0]):
        for col in range(heatmap.shape[1]):
            value = heatmap.iloc[row, col]
            text_color = "white" if value >= 0.55 else COLORS["ink"]
            ax.text(col, row, f"{value:.0%}", ha="center", va="center", fontsize=8.5, color=text_color)
    colorbar = fig.colorbar(image, ax=ax, pad=0.015)
    colorbar.set_label("Demand score")

    ax = fig.add_subplot(grid[1, 0])
    x = range(len(staffing_results))
    width = 0.24
    ax.bar([value - width for value in x], staffing_results["Recall"], width, label="Recall", color=COLORS["teal"])
    ax.bar(x, staffing_results["F1"], width, label="F1", color=COLORS["coral"])
    ax.bar([value + width for value in x], staffing_results["ROC_AUC"], width, label="ROC-AUC", color=COLORS["gold"])
    ax.set_title("Staffing Model Comparison", loc="left", fontsize=14, weight="bold")
    ax.set_xticks(list(x), staffing_results["Model"], rotation=10)
    ax.set_ylim(0, 0.85)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.8)
    ax.legend(frameon=False, ncol=3)
    ax.spines[["top", "right"]].set_visible(False)

    recommendations = schedule[schedule["Full Staffing Recommended"]]
    summary = (
        recommendations.groupby("Weekday")["Hour"]
        .apply(compact_hour_ranges)
        .reindex(weekday_order)
    )
    ax = fig.add_subplot(grid[1, 1])
    ax.axis("off")
    ax.set_title("Recommended Full-Staffing Windows", loc="left", fontsize=14, weight="bold")
    rows = [[day, hours] for day, hours in summary.items()]
    table = ax.table(cellText=rows, colLabels=["Weekday", "Hours"], cellLoc="left", colLoc="left", bbox=[0, 0, 1, 0.92])
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(COLORS["grid"])
        if row == 0:
            cell.set_facecolor(COLORS["ink"])
            cell.set_text_props(color="white", weight="bold")

    fig.savefig(OUTPUT_DIR / "tableau-staffing-models.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pos = pd.read_csv(DATA_DIR / "pos_records.csv")
    schedule = pd.read_csv(DATA_DIR / "staffing_schedule.csv")
    results = pd.read_csv(DATA_DIR / "model_results.csv")
    save_executive_overview(pos)
    save_staffing_and_models(schedule, results)
    print(f"Saved Tableau dashboard previews to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
