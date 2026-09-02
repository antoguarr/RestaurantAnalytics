from pathlib import Path
from typing import Union

import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Time",
    "Menu Item",
    "Category",
    "Quantity",
    "Price (per item)",
    "Revenue",
    "Payment Method",
    "Order Type",
    "Server ID",
    "Server Name",
]


def load_pos_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load the restaurant POS dataset from a CSV file."""
    return pd.read_csv(file_path)


def clean_pos_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column types, standardize text fields, and remove duplicate rows."""
    clean_df = df.copy()

    missing_columns = set(REQUIRED_COLUMNS) - set(clean_df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    clean_df["Date"] = pd.to_datetime(clean_df["Date"])
    clean_df["Time"] = pd.to_datetime(
        clean_df["Time"],
        format="%I:%M:%S %p",
    ).dt.time

    numeric_columns = ["Quantity", "Price (per item)", "Revenue"]
    for column in numeric_columns:
        clean_df[column] = pd.to_numeric(clean_df[column], errors="coerce")

    text_columns = [
        "Menu Item",
        "Category",
        "Payment Method",
        "Order Type",
        "Server Name",
    ]
    for column in text_columns:
        clean_df[column] = clean_df[column].astype(str).str.strip()

    clean_df = clean_df.drop_duplicates().reset_index(drop=True)
    return clean_df


def get_data_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact data quality summary for each column."""
    return pd.DataFrame(
        {
            "missing_values": df.isna().sum(),
            "unique_values": df.nunique(),
            "data_type": df.dtypes.astype(str),
        }
    )
