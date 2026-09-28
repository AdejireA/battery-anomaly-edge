"""Phase 4 data boundary and label-free fitting helpers. Never open test data."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_CELLS = ('B0005', 'B0006', 'B0007')


def read_config(name):
    return json.loads((ROOT / 'config' / name).read_text(encoding='utf-8'))


def load_development_data(directory=ROOT / 'data/processed/nasa'):
    """Whitelist individual cell CSVs; combined CSV and B0018 are never opened."""
    frames = []
    for cell in DEVELOPMENT_CELLS:
        frame = pd.read_csv(Path(directory) / f'{cell}_discharge_features.csv')
        if set(frame.cell_id) != {cell}:
            raise ValueError(f'Unexpected cell in {cell} development file')
        frame = frame.sort_values('cycle').reset_index(drop=True)
        if frame.cycle.tolist() != list(range(1, 169)):
            raise ValueError(f'{cell}: expected cycles 1..168')
        if not pd.to_datetime(frame.timestamp).is_monotonic_increasing:
            raise ValueError(f'{cell}: nonchronological timestamps')
        if any(c in frame for c in ['is_synthetic_anomaly', 'anomaly_family', 'severity', 'source_cell']):
            raise ValueError('Development source must be clean extracted data')
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def nominal_training(frame):
    if not set(frame.cell_id).issubset(DEVELOPMENT_CELLS):
        raise ValueError('Non-development cell supplied')
    return frame.loc[frame.cell_id.isin(['B0005', 'B0006']) & frame.cycle.between(1, 50)].sort_values(['cell_id', 'cycle']).copy()


def validate_nominal(frame):
    if set(frame.cell_id) != {'B0005', 'B0006'} or not frame.cycle.between(1, 50).all():
        raise ValueError('Fit input must contain only nominal B0005/B0006 cycles 1..50')
    if frame.duplicated(['cell_id', 'cycle']).any():
        raise ValueError('Duplicate training observations')
    if any(c in frame for c in ['is_synthetic_anomaly', 'anomaly_family', 'severity', 'source_cell']):
        raise ValueError('Synthetic/evaluation provenance is forbidden in fitting input')


def feature_matrix(frame, features):
    matrix = frame.loc[:, features]
    keep = matrix.notna().all(axis=1)
    matrix = matrix.loc[keep]
    if not np.isfinite(matrix.to_numpy()).all():
        raise ValueError('Infinite model feature')
    return matrix, keep


def fit_development_model(nominal, feature_set, n_estimators, max_features, seed):
    validate_nominal(nominal)
    features = read_config('nasa_feature_manifest.json')['model_feature_sets'][feature_set]
    config = read_config('nasa_model_development.json')
    if n_estimators not in config['n_estimators'] or max_features not in config['max_features'] or seed not in config['seeds']:
        raise ValueError('Configuration outside predefined grid')
    matrix, keep = feature_matrix(nominal, features)
    expected = 92 if feature_set == 'degradation_aware' else 100
    if len(matrix) != expected:
        raise ValueError(f'Unexpected effective nominal count {len(matrix)}; expected {expected}')
    scaler = StandardScaler()
    transformed = scaler.fit_transform(matrix)  # Only clean nominal rows; no y argument.
    model = IsolationForest(n_estimators=n_estimators, max_features=max_features,
                            max_samples='auto', contamination='auto', random_state=seed, n_jobs=1)
    model.fit(transformed)  # Unsupervised fit, never synthetic labels.
    ids = nominal.loc[keep, ['cell_id', 'cycle']].to_dict(orient='records')
    provenance = {'status': 'DEVELOPMENT_ONLY', 'feature_set': feature_set, 'features': features,
                  'training_rows': len(matrix), 'training_ids': ids,
                  'training_sha256': hashlib.sha256(matrix.to_csv(index=False, float_format='%.17g').encode()).hexdigest(),
                  'scaler_mean': scaler.mean_.tolist(), 'scaler_var': scaler.var_.tolist(),
                  'scaler_scale': scaler.scale_.tolist(), 'scaler_n_samples_seen': int(scaler.n_samples_seen_),
                  'seed': seed, 'n_estimators': n_estimators, 'max_features': max_features,
                  'max_samples': 'auto', 'effective_max_samples': int(model.max_samples_), 'contamination': 'auto',
                  'score_convention': '-score_samples; higher is more anomalous'}
    return {'scaler': scaler, 'model': model, 'features': features, 'provenance': provenance}


def anomaly_scores(bundle, frame):
    matrix, keep = feature_matrix(frame, bundle['features'])
    scores = -bundle['model'].score_samples(bundle['scaler'].transform(matrix))
    return pd.Series(scores, index=matrix.index, name='anomaly_score'), keep


def clean_training_thresholds(bundle, nominal):
    """No validation or synthetic scores accepted: recompute from verified fit rows."""
    validate_nominal(nominal)
    matrix, _ = feature_matrix(nominal, bundle['features'])
    digest = hashlib.sha256(matrix.to_csv(index=False, float_format='%.17g').encode()).hexdigest()
    if digest != bundle['provenance']['training_sha256']:
        raise ValueError('Threshold source differs from fitted clean nominal observations')
    scores, _ = anomaly_scores(bundle, nominal)
    config = read_config('nasa_model_development.json')
    return [{'percentile': p, 'threshold': float(np.percentile(scores, p, method='linear')),
             'threshold_source': config['threshold_source'], 'calibration_rows': len(scores)}
            for p in config['threshold_percentiles']]


def threshold_review(clean_threshold_results, tolerance=0.05):
    """Accept only clean FPR results, never synthetic metrics; return review advice."""
    allowed = {'percentile', 'seed', 'clean_fpr'}
    if set(clean_threshold_results.columns) != allowed:
        raise ValueError('Threshold review accepts only percentile, seed and clean_fpr')
    eligible = []
    for percentile, group in clean_threshold_results.groupby('percentile'):
        if set(group.seed) != {42, 123, 2026} or len(group) != 3:
            raise ValueError('Threshold review needs exactly all three predefined seeds')
        if group.clean_fpr.le(tolerance).all():
            eligible.append(float(percentile))
    return {'recommended_percentile_for_review': min(eligible) if eligible else None,
            'final_threshold': None, 'status': 'review_only' if eligible else 'no_candidate_meets_clean_fpr_tolerance'}
