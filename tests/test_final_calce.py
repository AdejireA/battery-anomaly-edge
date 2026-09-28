"""Frozen final-test gate, unchanged mathematics, and artifact integrity."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import joblib
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evaluate_final_calce as final


class FinalCalceTests(unittest.TestCase):
    def test_gate_blocks_test_before_freeze_unlock(self):
        with patch.object(final, 'UNLOCKED', False):
            with self.assertRaisesRegex(RuntimeError, 'locked'):
                final.guard('open', (str(final.TEST), 'r', 0))

    def test_freeze_is_write_once(self):
        before = final.sha(final.CONFIG)
        with self.assertRaises(RuntimeError):
            final.freeze()
        with self.assertRaises(FileExistsError):
            final.write_once(final.CONFIG, {'test_metric': 1})
        self.assertEqual(before, final.sha(final.CONFIG))

    def test_all_frozen_hashes_and_test_access_order(self):
        receipt = final.verify_freeze()
        audit = json.loads((final.OUT / 'integrity_checks.json').read_text())
        self.assertEqual(audit['frozen_hashes_before'], audit['frozen_hashes_after'])
        self.assertGreater(audit['first_test_access_at_utc'], receipt['receipt_at_utc'])
        self.assertEqual(final.helpers('CS2-37')['nasa_hashes'](), receipt['nasa_hashes'])
        self.assertTrue(audit['no_refit'] and audit['no_retuning'])

    def test_clean_only_selection_and_training_provenance(self):
        cfg = json.loads(final.CONFIG.read_text())
        evidence = pd.DataFrame(cfg['development_clean_fpr_evidence'])
        self.assertEqual(final.helpers('CS2-37')['select_threshold'](evidence[['seed', 'percentile', 'clean_fpr']]), 95)
        bundle = joblib.load(final.FINAL / 'model_bundle.joblib')
        self.assertEqual(bundle['seed'], 42)
        ids = pd.DataFrame(bundle['training_ids'])
        self.assertEqual(ids.groupby('cell_id').size().to_dict(), {'CS2-35': 254, 'CS2-36': 281})
        self.assertEqual(cfg['threshold_value'], 0.595563163424274)
        self.assertEqual(cfg['history_window'], 10)
        self.assertEqual(bundle['features'], cfg['feature_names'])
        self.assertEqual(int(bundle['scaler'].n_samples_seen_), 535)

    def test_test_cell_adapter_preserves_feature_and_injection_math(self):
        source = pd.read_csv(final.ROOT / 'data/processed/calce/CS2_37_discharge_features.csv').iloc[:22].copy()
        protocol = json.loads((final.ROOT / 'config/calce_anomaly_injection_protocol.json').read_text())
        dev = final.helpers('CS2-37'); test = final.helpers('CS2-38')
        changed = source.assign(cell_id='CS2-38')
        a = dev['build_relative'](source); b = test['build_relative'](changed)
        pd.testing.assert_frame_equal(a.drop(columns='cell_id'), b.drop(columns='cell_id'))
        ac, an = dev['injected_copies'](source, protocol)
        bc, bn = test['injected_copies'](changed, protocol)
        pd.testing.assert_frame_equal(an, bn)
        pd.testing.assert_frame_equal(ac.drop(columns=['cell_id', 'source_cell']), bc.drop(columns=['cell_id', 'source_cell']))
        self.assertTrue(b[test['features']()].iloc[:10].isna().all().all())
        altered = changed.copy(); altered.loc[10:, 'duration_s'] *= 2
        rebuilt = test['build_relative'](altered)
        self.assertEqual(b.loc[10, 'duration_s_prior10_median'], rebuilt.loc[10, 'duration_s_prior10_median'])

    def test_scoring_cannot_fit(self):
        bundle = joblib.load(final.FINAL / 'model_bundle.joblib')
        features = bundle['features']
        data = pd.DataFrame(np.zeros((2, len(features))), columns=features)
        expected = -bundle['model'].score_samples(bundle['scaler'].transform(data))
        with patch.object(bundle['model'], 'fit', side_effect=AssertionError('refit')), patch.object(bundle['scaler'], 'fit', side_effect=AssertionError('refit')):
            actual = final.helpers('CS2-38')['score'](bundle, data)
        np.testing.assert_array_equal(actual, expected)
        namespace = final.helpers('CS2-38')
        self.assertNotIn('fit_model', namespace)
        self.assertNotIn('anomaly_protocol', namespace)

    def test_serialized_components_match_original_development_bundle(self):
        original = joblib.load(final.ROOT / 'models/development/calce_replication/DEVELOPMENT_CALCE_seed42.joblib')
        model = joblib.load(final.FINAL / 'model.joblib')
        scaler = joblib.load(final.FINAL / 'scaler.joblib')
        np.testing.assert_array_equal(scaler.mean_, original['scaler'].mean_)
        np.testing.assert_array_equal(scaler.scale_, original['scaler'].scale_)
        probe = np.array([[0., 0., 0., 0.], [1., -2., 3., -4.]])
        np.testing.assert_array_equal(model.score_samples(probe), original['model'].score_samples(probe))
        self.assertEqual(final.sha(final.FINAL / 'model_bundle.joblib'), final.sha(final.ROOT / 'models/development/calce_replication/DEVELOPMENT_CALCE_seed42.joblib'))


if __name__ == '__main__':
    unittest.main()
