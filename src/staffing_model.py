from math import cos, pi, sin

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

STAFFING_FEATURE_COLUMNS = [
    "Hour",
    "Weekday",
    "Month Sin",
    "Month Cos",
]

STAFFING_CATEGORICAL_FEATURES = ["Hour", "Weekday"]
STAFFING_NUMERIC_FEATURES = ["Month Sin", "Month Cos"]


def _add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    featured_df = df.copy()
    featured_df["Weekday"] = featured_df["Date"].dt.day_name()
    featured_df["Month"] = featured_df["Date"].dt.month
    featured_df["Month Sin"] = featured_df["Month"].map(
        lambda month: sin(2 * pi * (month - 1) / 12)
    )
    featured_df["Month Cos"] = featured_df["Month"].map(
        lambda month: cos(2 * pi * (month - 1) / 12)
    )
    return featured_df


def build_hourly_staffing_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate POS records into a complete grid of open date-hour slots."""
    required_columns = {"Date", "Hour", "Quantity", "Revenue"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing staffing model columns: {missing}")

    hourly_demand = (
        df.groupby(["Date", "Hour"], as_index=False)
        .agg(
            POS_Records=("Revenue", "size"),
            Units_Sold=("Quantity", "sum"),
            Revenue=("Revenue", "sum"),
        )
    )

    dates = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
    hours = range(int(df["Hour"].min()), int(df["Hour"].max()) + 1)
    complete_grid = pd.MultiIndex.from_product(
        [dates, hours],
        names=["Date", "Hour"],
    ).to_frame(index=False)

    staffing_df = complete_grid.merge(
        hourly_demand,
        on=["Date", "Hour"],
        how="left",
    )
    staffing_df[["POS_Records", "Units_Sold", "Revenue"]] = staffing_df[
        ["POS_Records", "Units_Sold", "Revenue"]
    ].fillna(0)
    staffing_df["POS_Records"] = staffing_df["POS_Records"].astype(int)
    staffing_df = _add_calendar_features(staffing_df)
    return staffing_df.sort_values(["Date", "Hour"]).reset_index(drop=True)


def build_staffing_preprocessor() -> ColumnTransformer:
    """Build preprocessing for schedule-time staffing features."""
    return ColumnTransformer(
        transformers=[
            (
                "categories",
                OneHotEncoder(handle_unknown="ignore"),
                STAFFING_CATEGORICAL_FEATURES,
            ),
            ("numbers", "passthrough", STAFFING_NUMERIC_FEATURES),
        ]
    )


def _build_staffing_pipeline(classifier) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_staffing_preprocessor()),
            ("classifier", classifier),
        ]
    )


def _calculate_staffing_metrics(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "predictions": predictions,
        "probabilities": probabilities,
    }


def _calculate_staffing_cv_scores(
    model: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv_splits: int,
) -> dict:
    scores = cross_validate(
        model,
        X_train,
        y_train,
        cv=TimeSeriesSplit(n_splits=cv_splits),
        scoring=["recall", "f1", "roc_auc"],
        n_jobs=-1,
    )
    return {
        "cv_recall_mean": scores["test_recall"].mean(),
        "cv_f1_mean": scores["test_f1"].mean(),
        "cv_roc_auc_mean": scores["test_roc_auc"].mean(),
    }


def evaluate_staffing_models(
    df: pd.DataFrame,
    demand_quantile: float = 0.75,
    train_fraction: float = 0.80,
    cv_splits: int = 5,
    random_state: int = 42,
) -> dict:
    """Evaluate schedule-time models for a high-workload staffing proxy."""
    staffing_df = build_hourly_staffing_data(df)
    unique_dates = staffing_df["Date"].drop_duplicates().sort_values().tolist()
    split_index = int(len(unique_dates) * train_fraction)
    split_date = pd.Timestamp(unique_dates[split_index])

    train_mask = staffing_df["Date"] < split_date
    test_mask = ~train_mask
    demand_threshold = staffing_df.loc[train_mask, "Units_Sold"].quantile(
        demand_quantile
    )
    staffing_df["Full Staffing Proxy"] = (
        staffing_df["Units_Sold"] >= demand_threshold
    ).astype(int)

    X = staffing_df[STAFFING_FEATURE_COLUMNS]
    y = staffing_df["Full Staffing Proxy"]
    X_train, X_test = X.loc[train_mask], X.loc[test_mask]
    y_train, y_test = y.loc[train_mask], y.loc[test_mask]

    models = {
        "Dummy Baseline": _build_staffing_pipeline(
            DummyClassifier(strategy="most_frequent", random_state=random_state)
        ),
        "Logistic Regression": _build_staffing_pipeline(
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=random_state,
            )
        ),
        "Random Forest": _build_staffing_pipeline(
            RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_leaf=8,
                class_weight="balanced",
                random_state=random_state,
            )
        ),
    }

    model_results = {}
    summary_rows = []
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        holdout_metrics = _calculate_staffing_metrics(model, X_test, y_test)
        cv_metrics = _calculate_staffing_cv_scores(
            model,
            X_train,
            y_train,
            cv_splits=cv_splits,
        )
        model_results[model_name] = {
            "model": model,
            **holdout_metrics,
            **cv_metrics,
        }
        summary_rows.append(
            {
                "Model": model_name,
                "Accuracy": holdout_metrics["accuracy"],
                "Precision": holdout_metrics["precision"],
                "Recall": holdout_metrics["recall"],
                "F1": holdout_metrics["f1"],
                "ROC_AUC": holdout_metrics["roc_auc"],
                "CV_F1_Mean": cv_metrics["cv_f1_mean"],
                "CV_Recall_Mean": cv_metrics["cv_recall_mean"],
                "CV_ROC_AUC_Mean": cv_metrics["cv_roc_auc_mean"],
            }
        )

    summary = pd.DataFrame(summary_rows).sort_values("F1", ascending=False)
    return {
        "staffing_data": staffing_df,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "models": model_results,
        "summary": summary,
        "best_model_name": summary.iloc[0]["Model"],
        "demand_threshold": demand_threshold,
        "demand_quantile": demand_quantile,
        "split_date": split_date,
    }


def build_staffing_schedule(
    evaluation: dict,
    model_name: str = "Random Forest",
) -> pd.DataFrame:
    """Create average staffing-demand scores for each weekday-hour combination."""
    model = evaluation["models"][model_name]["model"]
    staffing_data = evaluation["staffing_data"]
    opening_hour = int(staffing_data["Hour"].min())
    closing_hour = int(staffing_data["Hour"].max())
    rows = []
    for month in range(1, 13):
        month_sin = sin(2 * pi * (month - 1) / 12)
        month_cos = cos(2 * pi * (month - 1) / 12)
        for weekday in WEEKDAY_ORDER:
            for hour in range(opening_hour, closing_hour + 1):
                rows.append(
                    {
                        "Hour": hour,
                        "Weekday": weekday,
                        "Month Sin": month_sin,
                        "Month Cos": month_cos,
                    }
                )

    scoring_data = pd.DataFrame(rows)
    scoring_data["Staffing Demand Score"] = model.predict_proba(scoring_data)[:, 1]
    schedule = (
        scoring_data.groupby(["Weekday", "Hour"], as_index=False)[
            "Staffing Demand Score"
        ]
        .mean()
    )
    schedule["Full Staffing Recommended"] = (
        schedule["Staffing Demand Score"] >= 0.5
    )
    schedule["Weekday"] = pd.Categorical(
        schedule["Weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )
    return schedule.sort_values(["Weekday", "Hour"]).reset_index(drop=True)


def get_staffing_feature_importance(model: Pipeline) -> pd.DataFrame:
    """Extract Random Forest feature importances from a staffing pipeline."""
    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_
    return pd.DataFrame(
        {"Feature": feature_names, "Importance": importances}
    ).sort_values("Importance", ascending=False)
