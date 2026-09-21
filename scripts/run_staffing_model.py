from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_time_features
from src.staffing_model import (
    WEEKDAY_ORDER,
    build_staffing_schedule,
    evaluate_staffing_models,
)


DATA_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "model_outputs"
SCREENSHOT_PATH = PROJECT_ROOT / "docs" / "screenshots" / "staffing-model-evaluation.png"
COLORS = {
    "teal": "#2F6F73",
    "copper": "#C08457",
    "ink": "#1F2933",
    "muted": "#667085",
    "grid": "#D8DEE4",
}


def load_project_data() -> pd.DataFrame:
    df = clean_pos_data(load_pos_data(DATA_PATH))
    return add_time_features(df)


def save_staffing_figure(evaluation: dict, schedule: pd.DataFrame) -> None:
    summary = evaluation["summary"]
    confusion = evaluation["models"]["Random Forest"]["confusion_matrix"]
    schedule_matrix = schedule.pivot(
        index="Weekday",
        columns="Hour",
        values="Staffing Demand Score",
    ).reindex(WEEKDAY_ORDER)

    fig = plt.figure(figsize=(16, 9), facecolor="white")
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 2.4],
        width_ratios=[0.8, 1.5],
        hspace=0.46,
        wspace=0.42,
    )
    fig.suptitle(
        "Staffing-Demand Model Evaluation",
        x=0.05,
        ha="left",
        fontsize=22,
        weight="bold",
    )
    fig.text(
        0.05,
        0.92,
        "High workload proxy: hourly units sold at or above the training-period 75th percentile",
        fontsize=12,
        color=COLORS["muted"],
    )

    table_ax = fig.add_subplot(grid[0, :])
    table_ax.axis("off")
    columns = [
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "ROC_AUC",
        "CV_F1_Mean",
    ]
    table_data = summary[columns].copy()
    for column in columns[1:]:
        table_data[column] = table_data[column].map(lambda value: f"{value:.3f}")
    table = table_ax.table(
        cellText=table_data.values,
        colLabels=[
            "Model",
            "Accuracy",
            "Precision",
            "Recall",
            "F1",
            "ROC-AUC",
            "CV F1",
        ],
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor(COLORS["grid"])
        if row == 0:
            cell.set_facecolor(COLORS["teal"])
            cell.set_text_props(color="white", weight="bold")

    confusion_ax = fig.add_subplot(grid[1, 0])
    confusion_ax.imshow(confusion, cmap="YlGnBu")
    confusion_ax.set_title(
        "Random Forest Confusion Matrix",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    confusion_ax.set_xticks(
        [0, 1],
        labels=["Predicted Standard", "Predicted Full"],
    )
    confusion_ax.set_yticks(
        [0, 1],
        labels=["Actual Standard", "Actual Full"],
    )
    for row in range(confusion.shape[0]):
        for column in range(confusion.shape[1]):
            confusion_ax.text(
                column,
                row,
                confusion[row, column],
                ha="center",
                va="center",
                color=COLORS["ink"],
                fontsize=16,
                weight="bold",
            )

    schedule_ax = fig.add_subplot(grid[1, 1])
    image = schedule_ax.imshow(
        schedule_matrix,
        aspect="auto",
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
    )
    schedule_ax.set_title(
        "Random Forest Staffing-Demand Score",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    schedule_ax.set_xticks(
        range(len(schedule_matrix.columns)),
        labels=[f"{hour}:00" for hour in schedule_matrix.columns],
        rotation=45,
        ha="right",
    )
    schedule_ax.set_yticks(
        range(len(schedule_matrix.index)),
        labels=schedule_matrix.index,
    )
    for row in range(schedule_matrix.shape[0]):
        for column in range(schedule_matrix.shape[1]):
            value = schedule_matrix.iloc[row, column]
            schedule_ax.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="black" if value < 0.65 else "white",
            )
    colorbar = fig.colorbar(image, ax=schedule_ax, fraction=0.035, pad=0.03)
    colorbar.set_label("Demand score")

    fig.savefig(SCREENSHOT_PATH, dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    evaluation = evaluate_staffing_models(load_project_data())
    schedule = build_staffing_schedule(evaluation)

    evaluation["summary"].to_csv(
        OUTPUT_DIR / "staffing_model_results.csv",
        index=False,
    )
    schedule.to_csv(
        OUTPUT_DIR / "staffing_schedule.csv",
        index=False,
    )
    save_staffing_figure(evaluation, schedule)

    print(evaluation["summary"].round(3).to_string(index=False))
    print(f"Workload threshold: {evaluation['demand_threshold']:.1f} units per hour")
    print(f"Chronological test period begins: {evaluation['split_date'].date()}")
    print(f"Saved outputs to {OUTPUT_DIR}")
    print(f"Saved figure to {SCREENSHOT_PATH}")


if __name__ == "__main__":
    main()
