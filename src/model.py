import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


FEATURE_COLUMNS = [
    "Menu Item",
    "Category",
    "Payment Method",
    "Order Type",
    "Server Name",
    "Weekday",
    "Hour",
    "Month",
    "Day of Week",
    "IsWeekend",
]

CATEGORICAL_FEATURES = [
    "Menu Item",
    "Category",
    "Payment Method",
    "Order Type",
    "Server Name",
    "Weekday",
    "IsWeekend",
]

NUMERIC_FEATURES = ["Hour", "Month", "Day of Week"]


def build_revenue_classifier(random_state: int = 42) -> Pipeline:
    """Build the preprocessing and Random Forest classification pipeline."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numbers", "passthrough", NUMERIC_FEATURES),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=random_state,
                ),
            ),
        ]
    )


def train_revenue_classifier(
    df: pd.DataFrame,
    target_column: str = "High Revenue",
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """Train the high-revenue classifier and return model artifacts."""
    X = df[FEATURE_COLUMNS]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    model = build_revenue_classifier(random_state=random_state)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    return {
        "model": model,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "predictions": predictions,
        "accuracy": accuracy_score(y_test, predictions),
        "classification_report": classification_report(y_test, predictions),
    }


def get_feature_importance(model: Pipeline) -> pd.DataFrame:
    """Extract feature importance values from a trained Random Forest pipeline."""
    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_

    return pd.DataFrame(
        {
            "Feature": feature_names,
            "Importance": importances,
        }
    ).sort_values("Importance", ascending=False)
