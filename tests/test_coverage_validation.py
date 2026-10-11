import unittest
import pandas as pd

from src.burden.coverage_validation import validate_seasonal_coverage


class TestCoverageValidation(unittest.TestCase):

    def test_complete_coverage(self):
        air = pd.DataFrame({
            "date_local": pd.date_range("2025-01-01", periods=3),
            "pm25_value": [10, 20, 30],
        })
        result = validate_seasonal_coverage(
            air, "2025-01-01", "2025-01-03"
        )
        self.assertEqual(result["coverage_percent"], 100.0)
        self.assertTrue(result["sufficient_coverage"])

    def test_incomplete_coverage(self):
        air = pd.DataFrame({
            "date_local": ["2025-01-01", "2025-01-03"],
            "pm25_value": [10, 30],
        })
        result = validate_seasonal_coverage(
            air, "2025-01-01", "2025-01-03"
        )
        self.assertAlmostEqual(result["coverage_percent"], 66.67, places=2)
        self.assertFalse(result["sufficient_coverage"])

    def test_rejects_invalid_date_range(self):
        air = pd.DataFrame({
            "date_local": ["2025-01-01"],
            "pm25_value": [10],
        })
        with self.assertRaises(ValueError):
            validate_seasonal_coverage(
                air, "2025-01-03", "2025-01-01"
            )


if __name__ == "__main__":
    unittest.main()
