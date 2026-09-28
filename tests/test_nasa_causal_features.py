"""Regression checks for causal timing and five-cycle OLS definitions."""

import unittest

import numpy as np
import pandas as pd

from scripts.extract_nasa import causal_capacity_features


class CausalFeatureTests(unittest.TestCase):
    def frame(self, capacity):
        values = np.asarray(capacity, dtype=float)
        return pd.DataFrame({"cycle": np.arange(1, len(values) + 1),
                             "capacity_ah": values, "capacity_retention": values / values[0]})

    def test_regression_and_median_against_independent_calculation(self):
        frame = self.frame([2, 1.9, 1.85, 1.95, 1.7, 1.8, 1.65])
        result = causal_capacity_features(frame)
        self.assertTrue(result.iloc[:4].isna().all().all())
        self.assertTrue(result.iloc[4:].notna().all().all())
        for end in range(4, len(frame)):
            window = frame.iloc[end - 4:end + 1]
            self.assertAlmostEqual(result.capacity_rolling_median_5.iloc[end], np.median(window.capacity_ah))
            for source, target in [("capacity_ah", "capacity_slope_5"), ("capacity_retention", "retention_slope_5")]:
                slope = np.polyfit(window.cycle, window[source], 1)[0]
                self.assertAlmostEqual(result[target].iloc[end], slope)

    def test_future_changes_and_prefixes_cannot_change_past(self):
        frame = self.frame([2, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3])
        expected = causal_capacity_features(frame)
        changed = frame.copy()
        changed.loc[6:, ["capacity_ah", "capacity_retention"]] = 100
        pd.testing.assert_frame_equal(expected.iloc[:6], causal_capacity_features(changed).iloc[:6])
        for stop in range(1, len(frame) + 1):
            pd.testing.assert_frame_equal(expected.iloc[:stop], causal_capacity_features(frame.iloc[:stop]))

    def test_cells_start_independent_windows(self):
        for values in [[2] * 8, [1.5] * 6]:
            result = causal_capacity_features(self.frame(values))
            self.assertTrue(result.iloc[:4].isna().all().all())
            np.testing.assert_allclose(result.iloc[4:][["capacity_slope_5", "retention_slope_5"]], 0, atol=1e-15)


if __name__ == "__main__":
    unittest.main()
