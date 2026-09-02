import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and hour-based features used in analysis and modeling."""
    featured_df = df.copy()

    featured_df["Date"] = pd.to_datetime(featured_df["Date"])
    featured_df["Hour"] = featured_df["Time"].apply(lambda value: value.hour)
    featured_df["Weekday"] = featured_df["Date"].dt.day_name()
    featured_df["Month"] = featured_df["Date"].dt.month
    featured_df["Month Name"] = featured_df["Date"].dt.month_name()
    featured_df["Day of Week"] = featured_df["Date"].dt.dayofweek
    featured_df["IsWeekend"] = featured_df["Day of Week"].isin([5, 6])

    return featured_df


def add_high_revenue_target(df: pd.DataFrame) -> pd.DataFrame:
    """Add a binary target for orders above the median revenue."""
    featured_df = df.copy()
    featured_df["High Revenue"] = featured_df["Revenue"] > featured_df["Revenue"].median()
    return featured_df
