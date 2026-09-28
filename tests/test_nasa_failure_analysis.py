"""Read-only diagnostic safety checks; never open excluded source data."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import diagnose_nasa_failures as diagnostic
from nasa_burnin import prohibit_fitting
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


class DiagnosticSafetyTests(unittest.TestCase):
    def test_protected_artifacts_unchanged(self):
        saved = json.loads((diagnostic.OUT / 'integrity_checks.json').read_text())
        self.assertEqual(saved['sha256_before'], saved['sha256_after'])
        self.assertEqual(saved['sha256_after'], diagnostic.hashes())

    def test_forbidden_paths_rejected_before_open(self):
        # Call guard with hypothetical paths; no filesystem read is attempted.
        for rel in ['data/processed/nasa/B0018_discharge_features.csv',
                    'data/processed/nasa/nasa_discharge_features.csv',
                    'data/raw/anything.mat']:
            with self.assertRaises(RuntimeError):
                diagnostic.access_guard('open', (str(ROOT / rel), 'r', os.O_RDONLY))

    def test_experimental_writes_rejected_before_open(self):
        for rel in ['config/anomaly_injection_protocol.json',
                    'results/nasa_relative_features/thresholds.csv',
                    'models/development/example.joblib',
                    'data/processed/nasa/B0007_discharge_features.csv']:
            with self.assertRaises(RuntimeError):
                diagnostic.access_guard('open', (str(ROOT / rel), 'w', os.O_WRONLY))

    def test_fitting_blocked(self):
        with prohibit_fitting():
            for estimator in [StandardScaler(), IsolationForest()]:
                with self.assertRaises(RuntimeError):
                    estimator.fit([[0.], [1.]])

    def test_recorded_access_excludes_test_data(self):
        saved = json.loads((diagnostic.OUT / 'integrity_checks.json').read_text())
        self.assertFalse(saved['test_cell_accessed'])
        self.assertFalse(any('b0018' in path.lower() for path in saved['accessed_repository_files']))


if __name__ == '__main__':
    unittest.main()
