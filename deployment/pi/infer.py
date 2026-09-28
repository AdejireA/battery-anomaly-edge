"""Hash-verified frozen NASA inference; no training or calibration entry point."""
import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_name, '1')
import sys
sys.dont_write_bytecode = True
import argparse
import csv
import hashlib
import json
from pathlib import Path
import warnings
from features import BASE_FEATURES, FEATURE_NAMES, HISTORY, MAD_SCALE, EPSILON, CausalHistory

HERE = Path(__file__).resolve().parent
FROZEN_CONFIG_SHA256 = 'fd4747b45ef8edfae3674fd284209b8df7b2aa4520906ca7ba9799eda46cde21'
EXPECTED_THRESHOLD = 0.5548682376720724
EXPECTED_VERSIONS = {'numpy': '2.5.3', 'scipy': '1.18.1', 'scikit-learn': '1.9.1', 'joblib': '1.6.0'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FrozenRunner:
    def __init__(self, artifacts=None):
        directory = Path(artifacts or HERE / 'artifacts')
        if digest(directory / 'final_nasa_model.json') != FROZEN_CONFIG_SHA256:
            raise ValueError('Frozen NASA configuration hash mismatch')
        self.config = json.loads((directory / 'final_nasa_model.json').read_text())
        for name, source in [('model.joblib', 'models/final_nasa/model.joblib'),
                             ('scaler.joblib', 'models/final_nasa/scaler.joblib'),
                             ('nasa_relative_feature_manifest.json', 'config/nasa_relative_feature_manifest.json')]:
            if digest(directory / name) != self.config['hashes'][source]:
                raise ValueError('Frozen artifact hash mismatch: ' + name)
        manifest = json.loads((directory / 'nasa_relative_feature_manifest.json').read_text())
        if (self.config['history_window'] != HISTORY or tuple(self.config['features']) != FEATURE_NAMES
                or manifest['feature_sets']['10']['RELATIVE_B'] != list(FEATURE_NAMES)
                or manifest['epsilon'] != EPSILON or manifest['mad_scale'] != MAD_SCALE
                or self.config['threshold_value'] != EXPECTED_THRESHOLD):
            raise ValueError('Frozen feature/threshold definition mismatch')
        from importlib.metadata import version
        for name, expected in EXPECTED_VERSIONS.items():
            if version(name) != expected:
                raise RuntimeError(f'{name} must match frozen environment {expected}; found {version(name)}')
        import joblib
        from sklearn.exceptions import InconsistentVersionWarning
        with warnings.catch_warnings():
            warnings.simplefilter('error', InconsistentVersionWarning)
            self.scaler = joblib.load(directory / 'scaler.joblib')
            self.model = joblib.load(directory / 'model.joblib')
        if (tuple(self.scaler.feature_names_in_) != FEATURE_NAMES
                or self.scaler.n_features_in_ != len(FEATURE_NAMES)
                or self.model.n_features_in_ != len(FEATURE_NAMES)):
            raise ValueError('Serialized feature order/dimension mismatch')
        if any(self.model.get_params()[key] != value for key, value in self.config['hyperparameters'].items()):
            raise ValueError('Serialized hyperparameters mismatch')
        self.threshold = self.config['threshold_value']
        self.state = CausalHistory()

    def score_vector(self, vector):
        import numpy as np
        x = np.asarray(vector, dtype=np.float64).reshape(1, -1)
        if x.shape != (1, len(FEATURE_NAMES)) or not np.isfinite(x).all():
            raise ValueError('Invalid ordered feature vector')
        # Feature order is checked explicitly above; ndarray avoids a pandas dependency.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='X does not have valid feature names, but StandardScaler was fitted with feature names', category=UserWarning)
            transformed = self.scaler.transform(x)
        return float(-self.model.score_samples(transformed)[0])

    def observe(self, row):
        cell, cycle, vector = self.state.push(row)
        score = None if vector is None else self.score_vector(vector)
        return dict(cell_id=cell, cycle=cycle, anomaly_score=score, threshold=self.threshold,
                    prediction='INSUFFICIENT_HISTORY' if score is None else ('ALERT' if score > self.threshold else 'NORMAL'))


def read_rows(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        required = {'cycle', *BASE_FEATURES}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('CSV missing required columns: ' + ', '.join(sorted(required - set(reader.fieldnames or []))))
        yield from reader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', type=Path, help='CSV output; otherwise stdout')
    args = parser.parse_args()
    if args.output and args.input.resolve() == args.output.resolve():
        parser.error('Output cannot overwrite input')
    runner = FrozenRunner()
    stream = args.output.open('w', newline='', encoding='utf-8') if args.output else sys.stdout
    try:
        writer = csv.DictWriter(stream, fieldnames=['cell_id', 'cycle', 'anomaly_score', 'threshold', 'prediction'])
        writer.writeheader()
        for row in read_rows(args.input):
            writer.writerow(runner.observe(row))
    finally:
        if args.output:
            stream.close()


if __name__ == '__main__':
    main()
