"""Clean temporal calibration and read-only access to saved development models."""

from contextlib import contextmanager
import hashlib
import itertools
import math
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

try:
    from .nasa_development import ROOT, read_config, anomaly_scores
except ImportError:
    from nasa_development import ROOT, read_config, anomaly_scores

FRACTIONS = [.20, .30, .40]
PERCENTILES = [95., 97.5, 99.]
TOLERANCE = .05
KEYS = ['feature_set', 'n_estimators', 'max_features']


@contextmanager
def prohibit_fitting():
    """Fail immediately if any calibration code accidentally attempts fitting."""
    with patch.object(StandardScaler, 'fit', side_effect=RuntimeError('Refitting forbidden')), \
         patch.object(StandardScaler, 'partial_fit', side_effect=RuntimeError('Refitting forbidden')), \
         patch.object(IsolationForest, 'fit', side_effect=RuntimeError('Refitting forbidden')):
        yield


def saved_models():
    config = read_config('nasa_model_development.json')
    manifest = read_config('nasa_feature_manifest.json')['model_feature_sets']
    for fs, trees, mf, seed in itertools.product(manifest, config['n_estimators'], config['max_features'], config['seeds']):
        path = ROOT / f'models/development/DEVELOPMENT_{fs}_trees{trees}_features{mf}_seed{seed}.joblib'
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        bundle = joblib.load(path)
        p = bundle['provenance']
        if bundle['features'] != manifest[fs] or p['status'] != 'DEVELOPMENT_ONLY':
            raise ValueError('Saved model feature/status mismatch')
        if (p['feature_set'], p['n_estimators'], p['max_features'], p['seed']) != (fs, trees, mf, seed):
            raise ValueError('Saved model configuration mismatch')
        if {r['cell_id'] for r in p['training_ids']} != {'B0005', 'B0006'} or any(r['cycle'] > 50 for r in p['training_ids']):
            raise ValueError('Unexpected saved fitting provenance')
        yield dict(feature_set=fs, n_estimators=trees, max_features=mf, seed=seed), bundle, path, digest


def split_clean_validation(clean, fraction):
    if fraction not in FRACTIONS:
        raise ValueError('Fraction outside predeclared burn-in grid')
    if set(clean.cell_id) != {'B0007'} or clean.cycle.tolist() != list(range(1, 169)):
        raise ValueError('Expected complete ordered clean B0007 trajectory')
    if any(c in clean for c in ['is_synthetic_anomaly', 'severity', 'anomaly_family', 'source_cell']):
        raise ValueError('Synthetic provenance forbidden in clean calibration input')
    boundary = math.floor(len(clean) * fraction)
    return clean.loc[clean.cycle <= boundary].copy(), clean.loc[clean.cycle > boundary].copy(), boundary


def calibrate_and_evaluate_clean(bundle, clean, fraction):
    calibration, evaluation, boundary = split_clean_validation(clean, fraction)
    early_scores, _ = anomaly_scores(bundle, calibration)
    late_scores, _ = anomaly_scores(bundle, evaluation)
    rows = []
    for percentile in PERCENTILES:
        threshold = float(np.percentile(early_scores, percentile, method='linear'))
        rows.append(dict(calibration_fraction=fraction, boundary_cycle=boundary,
                         percentile=percentile, calibration_rows=len(early_scores),
                         post_calibration_clean_rows=len(late_scores), threshold=threshold,
                         post_calibration_clean_fpr=float((late_scores > threshold).mean()),
                         threshold_source=f'clean_B0007_cycles_1_to_{boundary}_required_features_complete'))
    return rows, early_scores, late_scores


def eligible_for_review(thresholds):
    """Clean-only eligibility: all seeds must meet tolerance; no final selection."""
    allowed = KEYS + ['seed', 'calibration_fraction', 'percentile', 'post_calibration_clean_fpr']
    if set(thresholds.columns) != set(allowed):
        raise ValueError('Review accepts only clean FPR/configuration columns')
    rows = []
    for key, group in thresholds.groupby(KEYS + ['calibration_fraction', 'percentile']):
        if len(group) != 3 or set(group.seed) != {42, 123, 2026}:
            raise ValueError('Need all three seeds exactly once')
        rows.append(dict(zip(KEYS + ['calibration_fraction', 'percentile'], key)) |
                    {'clean_fpr_mean': group.post_calibration_clean_fpr.mean(),
                     'clean_fpr_std': group.post_calibration_clean_fpr.std(ddof=1),
                     'clean_fpr_max': group.post_calibration_clean_fpr.max(),
                     'eligible': bool(group.post_calibration_clean_fpr.le(TOLERANCE).all())})
    reviewed = pd.DataFrame(rows)
    eligible = reviewed.loc[reviewed.eligible].sort_values(['calibration_fraction', 'percentile'] + KEYS).reset_index(drop=True)
    eligible['review_priority'] = [1 + sum((eligible.calibration_fraction < r.calibration_fraction) |
                                         ((eligible.calibration_fraction == r.calibration_fraction) & (eligible.percentile < r.percentile)))
                                   for r in eligible.itertuples()]
    return reviewed, eligible


def protected_hashes():
    paths = [ROOT / f'data/processed/nasa/{cell}_discharge_features.csv' for cell in ['B0005', 'B0006', 'B0007']]
    paths += [ROOT / 'config' / name for name in ['anomaly_injection_protocol.json', 'nasa_feature_manifest.json', 'nasa_model_development.json']]
    paths += sorted((ROOT / 'models/development').glob('DEVELOPMENT_*.joblib'))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
