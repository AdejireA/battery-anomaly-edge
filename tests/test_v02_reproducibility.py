"""Public-safe v0.2 checks: no external datasets required."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'demo'))
from verify_artifacts import verify
from run_demo import run_demo, synthetic_rows, vectors
from prepare_reproduction import prepare


def independent_process_when_guarded(test):
    """Historical tests install permanent process-wide research audit hooks."""
    from functools import wraps

    @wraps(test)
    def run(self):
        if 'diagnose_nasa_failures' not in sys.modules:
            return test(self)
        import subprocess
        result = subprocess.run(
            [sys.executable, '-B', str(Path(__file__).resolve()),
             f'{type(self).__name__}.{test.__name__}'],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    return run


class ReproducibilityTests(unittest.TestCase):
    @independent_process_when_guarded
    def test_all_released_hashes_and_loads(self):
        self.assertGreater(verify(load_models=True), 14)

    def test_demo_deterministic_warmup_and_scoring(self):
        rows, predictions = run_demo()
        self.assertEqual((rows, predictions), run_demo())
        self.assertEqual(len(predictions), 30)
        self.assertTrue(all(p['prediction'] == 'INSUFFICIENT_HISTORY' for p in predictions[:10]))
        self.assertTrue(all(np.isfinite(p['anomaly_score']) for p in predictions[10:]))
        self.assertTrue(any(p['prediction'] == 'ALERT' for p in predictions[20:23]))
        for p in predictions[10:]:
            self.assertEqual(p['prediction'] == 'ALERT', p['anomaly_score'] > p['threshold'])

    def test_future_changes_cannot_change_prefix(self):
        rows = synthetic_rows('PREFIX', 30, 7)
        before = vectors(rows)
        for row in rows[20:]:
            row['mean_voltage_v'] += 1e6
        after = vectors(rows)
        for a, b in zip(before[10:20], after[10:20]):
            np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(before[19], vectors(rows[:20])[-1])

    @independent_process_when_guarded
    def test_final_model_configuration_and_bundle_equivalence(self):
        import joblib
        import pandas as pd
        verify()
        for dataset in ['nasa', 'calce']:
            cfg = json.loads((ROOT / f'config/final_{dataset}_model.json').read_text())
            directory = ROOT / f'models/final_{dataset}'
            model = joblib.load(directory / 'model.joblib')
            scaler = joblib.load(directory / 'scaler.joblib')
            bundle = joblib.load(directory / 'model_bundle.joblib')
            features = cfg.get('features', cfg.get('feature_names'))
            self.assertEqual(list(scaler.feature_names_in_), features)
            self.assertEqual(model.random_state, 42)
            self.assertEqual(model.n_estimators, 100)
            self.assertEqual(cfg['history_window'], 10)
            x = pd.DataFrame(np.zeros((2, len(features))), columns=features)
            np.testing.assert_array_equal(model.score_samples(scaler.transform(x)),
                                          bundle['model'].score_samples(bundle['scaler'].transform(x)))

    def test_clean_reference_rates_are_distinct_and_consistent(self):
        import pandas as pd
        nasa = pd.read_csv(ROOT / 'results/nasa_relative_features/thresholds.csv')
        selected = nasa.loc[(nasa.feature_set == 'RELATIVE_B') & (nasa.history_window == 10)
            & (nasa.n_estimators == 100) & (nasa.max_features == 1.) & (nasa.seed == 42)
            & (nasa.percentile == 95)].iloc[0]
        self.assertEqual(int(selected.validation_rows), 158)
        self.assertAlmostEqual(selected.clean_fpr, 3/158)
        periods = pd.read_csv(ROOT / 'results/nasa_final_test/clean_temporal_statistics.csv')
        self.assertEqual((int(periods.flagged.sum()), int(periods['count'].sum())), (5, 122))
        calce = pd.read_csv(ROOT / 'results/calce_replication/thresholds.csv')
        p95 = calce.loc[calce.percentile == 95]
        self.assertEqual(set(p95.seed), {42, 123, 2026})
        self.assertAlmostEqual(p95.loc[p95.seed == 42, 'clean_fpr'].iloc[0], 26/1026)
        self.assertEqual(round(p95.clean_fpr.mean()*100, 2), 3.15)
        final = json.loads((ROOT / 'results/calce_final_test/summary.json').read_text())
        self.assertEqual((final['flagged'], final['usable_cycles']), (32, 1015))
        self.assertAlmostEqual(final['clean_fpr'], 32/1015)

    def test_reproduction_preparation_rejects_release_root(self):
        with self.assertRaises(ValueError):
            prepare(ROOT)

    def test_reproduction_preparation_preserves_existing_directory(self):
        from tempfile import TemporaryDirectory
        (ROOT / 'output').mkdir(exist_ok=True)
        with TemporaryDirectory(dir=ROOT / 'output') as existing:
            with self.assertRaises(FileExistsError):
                prepare(Path(existing))

    @independent_process_when_guarded
    def test_tampering_rejected_before_deserialization(self):
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        (ROOT / 'output').mkdir(exist_ok=True)
        with TemporaryDirectory(dir=ROOT / 'output') as directory:
            root = Path(directory)
            (root / 'artifacts').mkdir()
            (root / 'model.joblib').write_bytes(b'changed')
            manifest = dict(models=[dict(path='model.joblib', size_bytes=7, sha256='0'*64)], figures=[], evidence=[])
            (root / 'artifacts/manifest.json').write_text(json.dumps(manifest))
            with patch('joblib.load') as loader:
                with self.assertRaises(ValueError):
                    verify(root, load_models=True)
                loader.assert_not_called()

    def test_frozen_pi_runner_loads_and_scores_synthetic_rows(self):
        from infer import FrozenRunner
        from unittest.mock import patch
        runner = FrozenRunner()
        with patch.object(runner.model, 'fit', side_effect=AssertionError('fitting forbidden')):
            results = [runner.observe(row) for row in synthetic_rows('LOAD_CHECK', 11, 99)]
        self.assertTrue(all(r['anomaly_score'] is None for r in results[:10]))
        self.assertTrue(np.isfinite(results[-1]['anomaly_score']))
        self.assertEqual(results[-1]['threshold'], 0.5548682376720724)


if __name__ == '__main__':
    unittest.main()
