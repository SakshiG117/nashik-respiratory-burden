import unittest

from src.burden.health_burden import calculate_attributable_burden


class TestHealthBurden(unittest.TestCase):

    def test_calculates_illustrative_scenario(self):
        result = calculate_attributable_burden(
            baseline_cases=1000,
            relative_risk=1.10,
            exposure_increment=10,
            reference_exposure=5,
            observed_exposure=15,
        )
        self.assertAlmostEqual(result["attributable_fraction"], 0.090909, places=6)
        self.assertAlmostEqual(result["scenario_attributable_cases"], 90.91, places=2)

    def test_rejects_negative_baseline(self):
        with self.assertRaises(ValueError):
            calculate_attributable_burden(-1, 1.1, 10, 5, 15)

    def test_rejects_relative_risk_below_one(self):
        with self.assertRaises(ValueError):
            calculate_attributable_burden(100, 0.9, 10, 5, 15)

    def test_rejects_zero_exposure_increment(self):
        with self.assertRaises(ValueError):
            calculate_attributable_burden(100, 1.1, 0, 5, 15)

    def test_rejects_negative_reference_exposure(self):
        with self.assertRaises(ValueError):
            calculate_attributable_burden(100, 1.1, 10, -1, 15)

    def test_higher_exposure_gives_positive_burden(self):
        result = calculate_attributable_burden(100, 1.1, 10, 5, 15)
        self.assertGreater(result["scenario_attributable_cases"], 0)

    def test_equal_exposure_gives_zero_burden(self):
        result = calculate_attributable_burden(100, 1.1, 10, 5, 5)
        self.assertEqual(result["scenario_attributable_cases"], 0)

    def test_lower_exposure_is_clipped_to_zero(self):
        result = calculate_attributable_burden(100, 1.1, 10, 5, 2)
        self.assertEqual(result["scenario_attributable_cases"], 0)


if __name__ == "__main__":
    unittest.main()
