from pathlib import Path
import unittest

from src.data_cleaning import clean_pos_data, load_pos_data
from src.feature_engineering import add_time_features
from src.staffing_model import (
    build_hourly_staffing_data,
    build_staffing_schedule,
    evaluate_staffing_models,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "Data" / "steakhouse_pos_simulated_data.csv"


class StaffingModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.df = add_time_features(clean_pos_data(load_pos_data(DATA_PATH)))
        cls.evaluation = evaluate_staffing_models(cls.df)

    def test_hourly_data_contains_complete_open_hour_grid(self) -> None:
        staffing_df = build_hourly_staffing_data(self.df)
        expected_rows = self.df["Date"].nunique() * (
            self.df["Hour"].max() - self.df["Hour"].min() + 1
        )
        self.assertEqual(len(staffing_df), expected_rows)
        self.assertFalse(staffing_df[["POS_Records", "Units_Sold"]].isna().any().any())

    def test_evaluation_has_expected_models_and_temporal_split(self) -> None:
        self.assertEqual(
            set(self.evaluation["summary"]["Model"]),
            {"Dummy Baseline", "Logistic Regression", "Random Forest"},
        )
        self.assertEqual(self.evaluation["demand_threshold"], 9.0)
        self.assertLess(
            self.evaluation["X_train"].index.max(),
            self.evaluation["X_test"].index.min(),
        )

    def test_schedule_covers_every_weekday_and_open_hour(self) -> None:
        schedule = build_staffing_schedule(self.evaluation)
        self.assertEqual(schedule["Weekday"].nunique(), 7)
        self.assertEqual(schedule["Hour"].nunique(), 12)
        self.assertTrue(schedule["Staffing Demand Score"].between(0, 1).all())


if __name__ == "__main__":
    unittest.main()
