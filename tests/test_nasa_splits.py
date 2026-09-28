"""Cell separation, chronological prefixes and feature-independent membership."""

import json
import unittest

import pandas as pd

from scripts.build_nasa_splits import ROOT, build_splits


class SplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = pd.read_csv(ROOT / "data/processed/nasa/nasa_discharge_features.csv")
        cls.protocol = json.loads((ROOT / "config/nasa_experiment_protocol.json").read_text())

    def test_cell_assignments_are_exclusive_and_complete(self):
        splits = build_splits(self.frame, self.protocol)
        expected = {"train": {"B0005", "B0006"}, "validation": {"B0007"}, "test": {"B0018"}}
        seen = set()
        for name, cells in expected.items():
            actual = set(splits[name].cell_id)
            self.assertEqual(actual, cells)
            self.assertFalse(seen & actual)
            seen |= actual
        self.assertEqual([len(splits[k]) for k in expected], [336, 168, 132])

    def test_fraction_prefixes_are_nested_and_feature_independent(self):
        altered = self.frame.copy()
        # Change future health/measurement values, not cycle identity or timestamps.
        fields = altered.columns.difference(["cell_id", "cycle", "operation_index", "timestamp", "nasa_eol_reached"])
        altered.loc[altered.cycle > 33, fields] = 0
        altered.loc[altered.cycle > 33, "nasa_eol_reached"] = True
        previous = set()
        for fraction, count in [(0.20, 33), (0.30, 50), (0.40, 67)]:
            nominal = build_splits(self.frame, self.protocol, fraction)["nominal_train"]
            changed = build_splits(altered, self.protocol, fraction)["nominal_train"]
            pd.testing.assert_frame_equal(nominal[["cell_id", "cycle"]], changed[["cell_id", "cycle"]])
            self.assertEqual(set(nominal.cell_id), {"B0005", "B0006"})
            for _, group in nominal.groupby("cell_id"):
                self.assertEqual(group.cycle.tolist(), list(range(1, count + 1)))
            keys = set(zip(nominal.cell_id, nominal.cycle))
            self.assertTrue(previous <= keys)
            previous = keys

    def test_shuffled_input_restores_chronological_order(self):
        splits = build_splits(self.frame.sample(frac=1, random_state=7), self.protocol)
        for part in splits.values():
            for _, group in part.groupby("cell_id"):
                self.assertTrue(group.cycle.is_monotonic_increasing)
                self.assertTrue(pd.to_datetime(group.timestamp).is_monotonic_increasing)

    def test_invalid_cells_and_overlapping_assignments_fail(self):
        bad = self.frame.copy()
        bad.loc[0, "cell_id"] = "B9999"
        with self.assertRaises(ValueError):
            build_splits(bad, self.protocol)
        with self.assertRaises(ValueError):
            build_splits(self.frame, dict(self.protocol, validation_cell="B0005"))


if __name__ == "__main__":
    unittest.main()
