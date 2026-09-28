"""Causal edge inference and frozen held-out equivalence; never fit models."""
import sys
sys.dont_write_bytecode = True
import ast
import json
from pathlib import Path
import shutil
import uuid
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
PI = ROOT / 'deployment/pi'
sys.path.insert(0, str(PI))
import numpy as np
from features import BASE_FEATURES, CausalHistory, relative_vector
from infer import FrozenRunner, read_rows, digest
from validate_playback import validate


class DeploymentTests(unittest.TestCase):
    def test_frozen_b0018_equivalence(self):
        result = validate(PI / 'sample_data/B0018_cycles.csv', PI / 'sample_data/B0018_expected.csv')
        self.assertEqual(result['usable_cycles'], 122)
        self.assertEqual(result['warmup_cycles'], 10)
        self.assertEqual(result['mismatch_count'], 0)
        self.assertLessEqual(result['max_score_difference'], 1e-12)
        self.assertEqual(result['flagged_cycles'], [46, 47, 106, 107, 108])

    def row(self, cycle, cell='A', offset=0):
        return dict(cell_id=cell, cycle=cycle, **{b: cycle + i + offset for i, b in enumerate(BASE_FEATURES)})

    def test_prior_only_and_no_cross_cell_history(self):
        state = CausalHistory()
        prior = []
        for cycle in range(1, 11):
            row = self.row(cycle)
            prior.append([row[b] for b in BASE_FEATURES])
            self.assertIsNone(state.push(row)[2])
            self.assertIsNone(state.push(self.row(cycle, 'B', 10000))[2])
        row = self.row(11, offset=100)
        result = state.push(row)[2]
        expected = relative_vector([row[b] for b in BASE_FEATURES], prior)
        np.testing.assert_array_equal(result, expected)
        median = np.median(prior, axis=0)
        mad = np.median(np.abs(np.array(prior) - median), axis=0)
        np.testing.assert_array_equal(result, (np.array([row[b] for b in BASE_FEATURES]) - median) / (1.4826 * mad + 1e-9))
        saved = result.copy()
        state.push(self.row(12, offset=1e6))
        np.testing.assert_array_equal(saved, result)

    def test_invalid_rows_do_not_advance_history(self):
        state = CausalHistory(); state.push(self.row(1))
        for cycle in [1, 0, 3]:
            with self.assertRaises(ValueError): state.push(self.row(cycle))
        invalid = self.row(2); invalid['duration_s'] = 'nan'
        with self.assertRaises(ValueError): state.push(invalid)
        self.assertEqual(state.last_cycle['A'], 1)
        state.push(self.row(2))
        self.assertEqual(state.last_cycle['A'], 2)

    def test_tampered_artifact_rejected_before_deserialization(self):
        for name in ['model.joblib', 'scaler.joblib', 'final_nasa_model.json', 'nasa_relative_feature_manifest.json']:
            destination = PI / 'results' / ('tamper_fixture_' + uuid.uuid4().hex)
            self.assertTrue(destination.resolve().is_relative_to(PI.resolve()))
            try:
                shutil.copytree(PI / 'artifacts', destination)
                with (destination / name).open('ab') as stream: stream.write(b'changed')
                with self.assertRaises(ValueError): FrozenRunner(destination)
            finally:
                if destination.exists():
                    for child in destination.iterdir(): child.unlink()
                    destination.rmdir()

    def test_copied_hashes_match_research_sources(self):
        records = json.loads((PI / 'artifacts/artifact_hashes.json').read_text())
        for name, record in records.items():
            self.assertEqual(digest(PI / 'artifacts' / name), record['sha256'])
            self.assertEqual(digest(ROOT / record['source']), record['sha256'])
        for name, record in json.loads((PI / 'sample_data/provenance.json').read_text()).items():
            self.assertEqual(digest(PI / 'sample_data' / name), record['sha256'])
            self.assertEqual(digest(ROOT / record['source']), record['source_sha256'])

    def test_no_fitting_calls_and_score_sign(self):
        for file in PI.glob('*.py'):
            for node in ast.walk(ast.parse(file.read_text())):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, {'fit', 'fit_transform', 'fit_predict', 'partial_fit'})
        runner = FrozenRunner()
        with patch.object(runner.model, 'fit', side_effect=AssertionError('forbidden')), patch.object(runner.scaler, 'fit', side_effect=AssertionError('forbidden')):
            rows = list(read_rows(PI / 'sample_data/B0018_cycles.csv'))[:11]
            result = [runner.observe(row) for row in rows][-1]
            self.assertAlmostEqual(result['anomaly_score'], .34189930552507664, places=12)

    def test_all_research_artifacts_unchanged(self):
        before = json.loads((PI / 'results/research_hashes_before.json').read_text())
        for source, expected in before.items():
            self.assertEqual(digest(ROOT / source), expected, source)


if __name__ == '__main__':
    unittest.main()
