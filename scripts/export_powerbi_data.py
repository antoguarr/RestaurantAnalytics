from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_high_revenue_target, add_time_features


INPUT_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"
OUTPUT_PATH = PROJECT_ROOT / "powerbi" / "data" / "restaurant_pos_powerbi.csv"


POWERBI_COLUMNS = {
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


def build_powerbi_dataset() -> None:
    raw_df = load_pos_data(INPUT_PATH)
    df = clean_pos_data(raw_df)
    df = add_time_features(df)
    df = add_high_revenue_target(df)
    df = df.rename(columns=POWERBI_COLUMNS)

    output_columns = list(POWERBI_COLUMNS.values())
    df = df[output_columns]
    df["date"] = df["date"].dt.date
    df["time"] = df["time"].astype(str)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Exported {len(df):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_powerbi_dataset()
