"""Phase 4 boundaries, frozen injections and label-free calibration tests.

Only development per-cell CSVs are read. No test-cell fixtures are loaded.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from scripts.nasa_development import (load_development_data, nominal_training, read_config,
                                      fit_development_model, anomaly_scores,
                                      clean_training_thresholds, threshold_review)
from scripts.inject_nasa_anomalies import perturb_window, generate_validation_copies
from scripts.train_nasa_isolation_forest import evaluation_metrics


class DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_development_data()
        cls.nominal = nominal_training(cls.data)
        cls.clean = cls.data.loc[cls.data.cell_id.eq('B0007')].reset_index(drop=True)
        cls.protocol = read_config('anomaly_injection_protocol.json')
        cls.bundle = fit_development_model(cls.nominal, 'degradation_aware', 100, 1.0, 42)

    def test_loader_never_opens_held_out_or_combined_csv(self):
        opened = []
        real_read = pd.read_csv
        def guarded_read(path, *args, **kwargs):
            opened.append(Path(path).name)
            self.assertNotIn('B0018', str(path))
            self.assertNotEqual(Path(path).name, 'nasa_discharge_features.csv')
            return real_read(path, *args, **kwargs)
        with patch('scripts.nasa_development.pd.read_csv', side_effect=guarded_read):
            frame = load_development_data()
        self.assertEqual(opened, [f'{cell}_discharge_features.csv' for cell in ['B0005', 'B0006', 'B0007']])
        self.assertEqual(set(frame.cell_id), {'B0005', 'B0006', 'B0007'})
        # Embedded unexpected IDs in an otherwise allowed file must fail loudly.
        bad = self.data.loc[self.data.cell_id.eq('B0005')].copy()
        bad.loc[bad.index[0], 'cell_id'] = 'B0018'
        with patch('scripts.nasa_development.pd.read_csv', return_value=bad):
            with self.assertRaises(ValueError):
                load_development_data()

    def test_scaler_and_forest_receive_only_nominal_features_without_labels(self):
        captured = {}
        real_scaler_fit, real_forest_fit = StandardScaler.fit, IsolationForest.fit
        def scaler_fit(instance, X, y=None, **kwargs):
            self.assertIsNone(y)
            captured['scaler'] = X.copy()
            return real_scaler_fit(instance, X, y=y, **kwargs)
        def forest_fit(instance, X, y=None, **kwargs):
            self.assertIsNone(y)
            captured['forest'] = X.copy()
            return real_forest_fit(instance, X, y=y, **kwargs)
        with patch.object(StandardScaler, 'fit', scaler_fit), patch.object(IsolationForest, 'fit', forest_fit):
            bundle = fit_development_model(self.nominal, 'degradation_aware', 100, 1.0, 42)
        expected = self.nominal[bundle['features']].dropna()
        pd.testing.assert_frame_equal(captured['scaler'], expected)
        np.testing.assert_allclose(bundle['scaler'].mean_, expected.mean())
        np.testing.assert_allclose(captured['forest'], bundle['scaler'].transform(expected))
        self.assertEqual(bundle['provenance']['training_rows'], 92)
        ids = pd.DataFrame(bundle['provenance']['training_ids'])
        self.assertEqual(ids.groupby('cell_id').size().to_dict(), {'B0005': 46, 'B0006': 46})
        self.assertTrue(ids.cycle.between(5, 50).all())
        other = fit_development_model(self.nominal, 'measurement_oriented', 100, 1.0, 42)
        self.assertEqual(other['provenance']['training_rows'], 100)

    def test_fit_rejects_validation_test_late_cycles_and_synthetic_provenance(self):
        for bad in [self.data, self.clean, self.nominal.assign(cell_id='B0018'),
                    self.nominal.assign(cycle=99), self.nominal.assign(is_synthetic_anomaly=False)]:
            with self.assertRaises(ValueError):
                fit_development_model(bad, 'degradation_aware', 100, 1.0, 42)

    def test_injections_preserve_clean_metadata_and_unaffected_fields(self):
        snapshot = self.clean.copy(deep=True)
        for family, spec in self.protocol['families'].items():
            kwargs = {'channel': 'mean_temp_c', 'sign': -1} if family.startswith('A4') else {}
            altered = perturb_window(self.clean, family, 'strong', 10, self.protocol, **kwargs)
            source = self.clean.iloc[10:10 + len(altered)]
            unaffected = [c for c in self.clean if c not in spec['affected_features']]
            pd.testing.assert_frame_equal(altered[unaffected], source[unaffected])
            self.assertTrue(altered.source_cell.eq('B0007').all())
            self.assertEqual(altered.source_cycle.tolist(), source.cycle.tolist())
            if family.startswith(('A1', 'A4')):
                self.assertFalse(altered.is_synthetic_anomaly.iloc[0])
                self.assertTrue(altered.is_synthetic_anomaly.iloc[1:].all())
        pd.testing.assert_frame_equal(self.clean, snapshot)
        with self.assertRaises(ValueError):
            perturb_window(self.clean.assign(cell_id='B0018'), 'A3_THERMAL_ABNORMALITY', 'mild', 0, self.protocol)

    def test_a1_frozen_retention_and_causal_regression(self):
        family = 'A1_ACCELERATED_DEGRADATION'
        previous = 0
        for severity in ['mild', 'moderate', 'strong']:
            altered = perturb_window(self.clean, family, severity, 10, self.protocol)
            amount = self.protocol['families'][family]['severity'][severity]['retention_total_decrease']
            source = self.clean.iloc[10:101]
            np.testing.assert_allclose(source.capacity_retention - altered.capacity_retention, np.linspace(0, amount, 91), atol=1e-14)
            history = np.r_[self.clean.capacity_retention.iloc[6:10], altered.capacity_retention] * self.clean.capacity_ah.iloc[0]
            for i in [1, 4, 30, 90]:
                slope = np.polyfit(np.arange(5), history[i:i+5], 1)[0]
                self.assertAlmostEqual(altered.capacity_slope_5.iloc[i], slope, places=12)
            self.assertGreater(amount, previous)
            previous = amount
        with self.assertRaises(ValueError):
            perturb_window(self.clean, family, 'mild', 0, self.protocol)

    def test_a2_and_a3_exact_frozen_changes_and_severity(self):
        for family in ['A2_EARLY_VOLTAGE_COLLAPSE', 'A3_THERMAL_ABNORMALITY']:
            previous = {}
            for severity in ['mild', 'moderate', 'strong']:
                altered = perturb_window(self.clean, family, severity, 10, self.protocol)
                source = self.clean.iloc[10:15]
                for feature, value in self.protocol['families'][family]['severity'][severity].items():
                    expected = source[feature] * value['factor'] if family.startswith('A2') else source[feature] + value
                    np.testing.assert_allclose(altered[feature], expected)
                    amount = (altered[feature] - source[feature]).abs().mean()
                    self.assertGreater(amount, previous.get(feature, 0))
                    previous[feature] = amount
                if family.startswith('A2'):
                    self.assertTrue((altered.time_to_3_4v_s <= altered.duration_s).all())
                    self.assertTrue((altered.time_to_3_4v_s > 0).all())
                else:
                    np.testing.assert_allclose(altered.delta_temp_c, altered.max_temp_c - altered.start_temp_c)

    def test_a4_monotonic_frozen_offsets_both_channels_and_signs(self):
        family = 'A4_SENSOR_DRIFT'
        for channel in ['mean_temp_c', 'mean_voltage_v']:
            for sign in [-1, 1]:
                previous = 0
                for severity in ['mild', 'moderate', 'strong']:
                    altered = perturb_window(self.clean, family, severity, 10, self.protocol, channel, sign)
                    amount = self.protocol['families'][family]['severity'][severity][channel]
                    offset = altered[channel] - self.clean[channel].iloc[10:20]
                    np.testing.assert_allclose(offset, sign * np.linspace(0, amount, 10), atol=1e-14)
                    self.assertTrue((sign * np.diff(offset) > 0).all())
                    self.assertGreater(amount, previous)
                    previous = amount

    def test_thresholds_clean_training_only_and_not_f1_selected(self):
        scores, _ = anomaly_scores(self.bundle, self.nominal)
        thresholds = clean_training_thresholds(self.bundle, self.nominal)
        np.testing.assert_allclose([x['threshold'] for x in thresholds], np.percentile(scores, [95, 97.5, 99]))
        with self.assertRaises(ValueError):
            clean_training_thresholds(self.bundle, self.clean)
        with self.assertRaises(ValueError):
            clean_training_thresholds(self.bundle, self.nominal.assign(is_synthetic_anomaly=True))
        changed = self.nominal.copy()
        changed['mean_temp_c'] += 10
        with self.assertRaises(ValueError):
            clean_training_thresholds(self.bundle, changed)
        rows = pd.DataFrame([{'percentile': p, 'seed': seed, 'clean_fpr': rate}
                             for p, rate in [(95, .1), (97.5, .04), (99, .02)] for seed in [42, 123, 2026]])
        advice = threshold_review(rows)
        self.assertEqual(advice['recommended_percentile_for_review'], 97.5)
        self.assertIsNone(advice['final_threshold'])
        self.assertIsNone(threshold_review(rows.assign(clean_fpr=.5))['recommended_percentile_for_review'])
        with self.assertRaises(ValueError):
            threshold_review(rows.assign(f1=1.0))

    def test_score_sign_and_balanced_metrics(self):
        scores, keep = anomaly_scores(self.bundle, self.clean)
        matrix = self.clean.loc[keep, self.bundle['features']]
        np.testing.assert_array_equal(scores, -self.bundle['model'].score_samples(self.bundle['scaler'].transform(matrix)))
        thresholds = [{'threshold': .5, 'percentile': 95}]
        # One FP / two clean points; all positives detected. Balanced precision=2/3.
        result = evaluation_metrics([.1, .6], [.8] * 10, thresholds)[0]
        self.assertEqual(result['clean_fpr'], .5)
        self.assertEqual(result['recall'], 1)
        self.assertAlmostEqual(result['precision'], 2/3)
        self.assertEqual(result['roc_auc'], 1)
        self.assertAlmostEqual(result['pr_auc'], 1)


if __name__ == '__main__':
    unittest.main()
