import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
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


def build_preprocessor() -> ColumnTransformer:
    """Build the shared preprocessing step for all classification models."""
    return ColumnTransformer(
        transformers=[
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numbers", "passthrough", NUMERIC_FEATURES),
        ]
    )


def build_dummy_classifier(random_state: int = 42) -> Pipeline:
    """Build a simple majority-class baseline classifier."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", DummyClassifier(strategy="most_frequent", random_state=random_state)),
        ]
    )


def build_logistic_regression_classifier(random_state: int = 42) -> Pipeline:
    """Build a Logistic Regression baseline classifier."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=random_state,
                ),
            ),
        ]
    )


def build_revenue_classifier(random_state: int = 42) -> Pipeline:
    """Build the preprocessing and Random Forest classification pipeline."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
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


def _calculate_metrics(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Calculate classification metrics for a fitted model."""
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "f1": f1_score(y_test, predictions),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "classification_report": classification_report(
            y_test,
            predictions,
            zero_division=0,
        ),
        "predictions": predictions,
    }

    if hasattr(model.named_steps["classifier"], "predict_proba"):
        probabilities = model.predict_proba(X_test)[:, 1]
        metrics["roc_auc"] = roc_auc_score(y_test, probabilities)
        metrics["probabilities"] = probabilities
    else:
        metrics["roc_auc"] = None
        metrics["probabilities"] = None

    return metrics


def _calculate_cross_validation_scores(
    model: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    cv_splits: int = 5,
) -> dict:
    """Calculate cross-validation means and standard deviations."""
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=42)
    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=["accuracy", "f1", "roc_auc"],
        n_jobs=-1,
    )

    return {
        "cv_accuracy_mean": scores["test_accuracy"].mean(),
        "cv_accuracy_std": scores["test_accuracy"].std(),
        "cv_f1_mean": scores["test_f1"].mean(),
        "cv_f1_std": scores["test_f1"].std(),
        "cv_roc_auc_mean": scores["test_roc_auc"].mean(),
        "cv_roc_auc_std": scores["test_roc_auc"].std(),
    }


def evaluate_revenue_models(
    df: pd.DataFrame,
    target_column: str = "High Revenue",
    test_size: float = 0.2,
    random_state: int = 42,
    cv_splits: int = 5,
) -> dict:
    """Compare baseline and Random Forest models using holdout and CV metrics."""
    X = df[FEATURE_COLUMNS]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    models = {
        "Dummy Baseline": build_dummy_classifier(random_state=random_state),
        "Logistic Regression": build_logistic_regression_classifier(random_state=random_state),
        "Random Forest": build_revenue_classifier(random_state=random_state),
    }

    model_results = {}
    summary_rows = []

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        holdout_metrics = _calculate_metrics(model, X_test, y_test)
        cv_metrics = _calculate_cross_validation_scores(
            model,
            X,
            y,
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
                "F1": holdout_metrics["f1"],
                "ROC_AUC": holdout_metrics["roc_auc"],
                "CV_Accuracy_Mean": cv_metrics["cv_accuracy_mean"],
                "CV_Accuracy_Std": cv_metrics["cv_accuracy_std"],
                "CV_F1_Mean": cv_metrics["cv_f1_mean"],
                "CV_F1_Std": cv_metrics["cv_f1_std"],
                "CV_ROC_AUC_Mean": cv_metrics["cv_roc_auc_mean"],
                "CV_ROC_AUC_Std": cv_metrics["cv_roc_auc_std"],
            }
        )

    summary = pd.DataFrame(summary_rows).sort_values("F1", ascending=False)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "models": model_results,
        "summary": summary,
        "best_model_name": summary.iloc[0]["Model"],
    }


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
    metrics = _calculate_metrics(model, X_test, y_test)

    return {
        "model": model,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        **metrics,
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
