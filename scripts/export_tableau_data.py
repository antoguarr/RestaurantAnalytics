from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_high_revenue_target, add_time_features
from src.model import evaluate_revenue_models
from src.staffing_model import build_staffing_schedule, evaluate_staffing_models


INPUT_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "tableau" / "data"


TABLEAU_COLUMNS = {
    "Date": "date",
    "Time": "time",
    "Menu Item": "menu_item",
    "Category": "category",
    "Quantity": "quantity",
    "Price (per item)": "price_per_item",
    "Revenue": "revenue",
    "Payment Method": "payment_method",
    "Order Type": "order_type",
    "Server ID": "server_id",
    "Server Name": "server_name",
    "Hour": "hour",
    "Weekday": "weekday",
    "Month": "month_number",
    "Month Name": "month_name",
    "Day of Week": "day_of_week",
    "IsWeekend": "is_weekend",
    "High Revenue": "high_revenue",
}


def load_analysis_data() -> pd.DataFrame:
    """Load, clean, and feature-engineer the POS source."""
    df = clean_pos_data(load_pos_data(INPUT_PATH))
    df = add_time_features(df)
    return add_high_revenue_target(df)


def build_pos_records(df: pd.DataFrame) -> pd.DataFrame:
    """Build the Tableau-ready row-level POS dataset."""
    output = df.rename(columns=TABLEAU_COLUMNS).copy()
    output.insert(0, "record_id", range(1, len(output) + 1))
    output["date_hour"] = pd.to_datetime(output["date"]) + pd.to_timedelta(
        output["hour"], unit="h"
    )
    output["service_period"] = output["hour"].map(
        lambda hour: "Lunch" if hour < 17 else "Dinner"
    )
    output["weekend_label"] = output["is_weekend"].map(
        {True: "Weekend", False: "Weekday"}
    )
    output["high_revenue_label"] = output["high_revenue"].map(
        {True: "High-value record", False: "Other record"}
    )

    output_columns = [
        "record_id",
        *TABLEAU_COLUMNS.values(),
        "date_hour",
        "service_period",
        "weekend_label",
        "high_revenue_label",
    ]
    output = output[output_columns]
    output["date"] = pd.to_datetime(output["date"]).dt.strftime("%Y-%m-%d")
    output["date_hour"] = output["date_hour"].dt.strftime("%Y-%m-%d %H:%M:%S")
    output["time"] = output["time"].astype(str)
    return output


def _revenue_model_results(df: pd.DataFrame) -> pd.DataFrame:
    summary = evaluate_revenue_models(df)["summary"].copy()
    summary.insert(0, "Model Task", "High-value POS record classification")
    summary["Precision"] = pd.NA
    summary["Recall"] = pd.NA
    summary["CV_Recall_Mean"] = pd.NA
    return summary


def _staffing_model_results(staffing_evaluation: dict) -> pd.DataFrame:
    summary = staffing_evaluation["summary"].copy()
    summary.insert(0, "Model Task", "Full-staffing demand classification")
    summary["CV_Accuracy_Mean"] = pd.NA
    summary["CV_Accuracy_Std"] = pd.NA
    summary["CV_F1_Std"] = pd.NA
    summary["CV_ROC_AUC_Std"] = pd.NA
    return summary


def build_model_results(
    df: pd.DataFrame,
    staffing_evaluation: dict,
) -> pd.DataFrame:
    """Combine both model experiments into one Tableau comparison table."""
    columns = [
        "Model Task",
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "ROC_AUC",
        "CV_Accuracy_Mean",
        "CV_Accuracy_Std",
        "CV_F1_Mean",
        "CV_F1_Std",
        "CV_Recall_Mean",
        "CV_ROC_AUC_Mean",
        "CV_ROC_AUC_Std",
    ]
    revenue_rows = _revenue_model_results(df).to_dict("records")
    staffing_rows = _staffing_model_results(staffing_evaluation).to_dict("records")
    results = pd.DataFrame([*revenue_rows, *staffing_rows])
    return results.reindex(columns=columns)


def export_tableau_data() -> None:
    """Regenerate all flat files used by the Tableau workbook."""
    df = load_analysis_data()
    staffing_evaluation = evaluate_staffing_models(df)

    pos_records = build_pos_records(df)
    staffing_schedule = build_staffing_schedule(staffing_evaluation).copy()
    staffing_schedule["Weekday"] = staffing_schedule["Weekday"].astype(str)
    model_results = build_model_results(df, staffing_evaluation)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "pos_records.csv": pos_records,
        "staffing_schedule.csv": staffing_schedule,
        "model_results.csv": model_results,
    }
    for filename, output_df in outputs.items():
        output_path = OUTPUT_DIR / filename
        output_df.to_csv(output_path, index=False)
        print(f"Exported {len(output_df):,} rows to {output_path}")


if __name__ == "__main__":
    export_tableau_data()
