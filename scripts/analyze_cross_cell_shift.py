"""Clean-only feature and score shift audit; never reads held-out test data."""

import json

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from .nasa_development import ROOT, load_development_data, nominal_training, feature_matrix, anomaly_scores, read_config
    from .nasa_burnin import saved_models, prohibit_fitting, protected_hashes
    from .train_nasa_isolation_forest import md_table, distribution, aggregate_seeds
except ImportError:
    from nasa_development import ROOT, load_development_data, nominal_training, feature_matrix, anomaly_scores, read_config
    from nasa_burnin import saved_models, prohibit_fitting, protected_hashes
    from train_nasa_isolation_forest import md_table, distribution, aggregate_seeds

OUT = ROOT / 'results/nasa_burnin_calibration'
FIG = ROOT / 'figures/nasa/burnin_calibration'


def feature_shift(nominal, early, manifest):
    rows = []
    for fs, features in manifest.items():
        train, _ = feature_matrix(nominal, features)
        validation, _ = feature_matrix(early, features)
        for feature in features:
            a, b = train[feature], validation[feature]
            train_mad, early_mad = (a-a.median()).abs().median(), (b-b.median()).abs().median()
            shift = b.median() - a.median()
            rows.append(dict(feature_set=fs, feature=feature, training_rows=len(a), early_rows=len(b),
                             training_median=a.median(), early_median=b.median(), training_MAD=train_mad,
                             early_MAD=early_mad, median_shift=shift,
                             robust_standardized_shift=shift/train_mad if train_mad > 0 else np.nan,
                             training_p05=a.quantile(.05), training_p95=a.quantile(.95),
                             early_p05=b.quantile(.05), early_p95=b.quantile(.95),
                             zero_training_MAD=bool(train_mad == 0)))
    frame = pd.DataFrame(rows)
    frame['absolute_shift'] = frame.robust_standardized_shift.abs()
    return frame.sort_values(['feature_set', 'absolute_shift'], ascending=[True, False]).reset_index(drop=True)


def run():
    before = protected_hashes()
    data = load_development_data()
    nominal = nominal_training(data)
    clean = data.loc[data.cell_id.eq('B0007')].reset_index(drop=True)
    manifest = read_config('nasa_feature_manifest.json')['model_feature_sets']
    shifts = feature_shift(nominal, clean.loc[clean.cycle <= 50], manifest)
    stats, score_rows = [], []
    for run_info, bundle, path, digest in saved_models():
        model_hash = joblib.hash(bundle)
        for region, frame in [('training_nominal', nominal), ('early_B0007', clean.loc[clean.cycle <= 50]), ('late_B0007', clean.loc[clean.cycle > 50])]:
            scores, keep = anomaly_scores(bundle, frame)
            stats.append(dict(run_info, region=region, **distribution(scores)))
            for index, score in scores.items():
                score_rows.append(dict(run_info, region=region, cell_id=frame.loc[index, 'cell_id'], cycle=int(frame.loc[index, 'cycle']), score=score))
        if joblib.hash(bundle) != model_hash:
            raise AssertionError('Saved object mutated during scoring')
    stats = pd.DataFrame(stats)
    scores = pd.DataFrame(score_rows)
    stability = aggregate_seeds(stats, ['feature_set', 'n_estimators', 'max_features', 'region'], ['score_mean', 'score_median', 'score_p05', 'score_p95'])
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    for name, frame in [('feature_shifts', shifts), ('shift_score_distributions', stats), ('shift_scores', scores), ('shift_score_seed_stability', stability)]:
        frame.to_csv(OUT / f'{name}.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, fs in zip(axes, manifest):
        subset = shifts.loc[shifts.feature_set.eq(fs)].iloc[::-1]
        ax.barh(subset.feature, subset.robust_standardized_shift)
        ax.axvline(0, color='black', linewidth=.8)
        ax.set(title=fs, xlabel='(Early B0007 median - training median) / training MAD')
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(axis='x', alpha=.2)
    fig.tight_layout()
    fig.savefig(FIG / 'feature_shift_summary.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, fs in zip(axes, manifest):
        part = scores.loc[scores.feature_set.eq(fs) & scores.n_estimators.eq(100) & scores.max_features.eq(1.0)]
        regions = ['training_nominal', 'early_B0007', 'late_B0007']
        ax.boxplot([part.loc[part.region.eq(r), 'score'] for r in regions], tick_labels=['Train nominal', 'B0007 1–50', 'B0007 51–168'])
        ax.set(title=fs, ylabel='Anomaly score (higher = more anomalous)')
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Predeclared display reference: 100 trees, max_features=1.0; three seeds pooled')
    fig.tight_layout()
    fig.savefig(FIG / 'training_vs_b0007_score_distribution.png', dpi=160)
    plt.close(fig)
    parts = ['# Cross-cell shift audit — clean observations only',
             'No synthetic observations or scores are used. Only per-cell B0005/B0006/B0007 files and the 24 saved development models are read. Model and scaler fitting are disabled at runtime. No feature removal or recalibration of anomaly magnitudes.',
             'Training = B0005/B0006 cycles 1–50; early validation = B0007 cycles 1–50 (floor(0.30*168)); late validation = cycles 51–168. Required-feature NaNs are dropped separately per frozen feature set, matching fitting eligibility. Raw MAD is unscaled; a zero training MAD is flagged and its standardized shift reported NaN rather than divided by zero. P5–P95 describes observed spread, not a confidence interval.',
             '## Leading shifts', md_table(shifts.groupby('feature_set', sort=False).head(3)[['feature_set','feature','median_shift','robust_standardized_shift']]),
             '## Predeclared reference (100 trees, max_features=1.0): score seed mean and SD',
             md_table(stability.loc[stability.n_estimators.eq(100) & stability.max_features.eq(1.0)]),
             '## Features ranked by absolute robust standardized median shift', md_table(shifts.drop(columns='absolute_shift')),
             '## Score distributions across all configurations and seeds', md_table(stats),
             '## Seed mean and sample SD of score summaries', md_table(stability),
             'Interpretation: early-vs-training shifts quantify cross-cell differences, whereas late-vs-early score changes additionally include trajectory evolution. A high late clean alarm fraction cannot be attributed solely to a stationary cell offset. Clean means unmodified, not independently certified fault-free.',
             'Detailed CSVs: `results/nasa_burnin_calibration/feature_shifts.csv`, `shift_score_distributions.csv`, `shift_scores.csv`, `shift_score_seed_stability.csv`. Figures are under `figures/nasa/burnin_calibration/`.']
    (ROOT / 'results/nasa_cross_cell_shift.md').write_text('\n\n'.join(parts)+'\n', encoding='utf-8')
    if protected_hashes() != before:
        raise AssertionError('Protected data/config/model file changed')
    (OUT / 'shift_integrity.json').write_text(json.dumps({'protected_sha256': before, 'unchanged': True, 'refitting_disabled': True}, indent=2)+'\n')
    print(shifts[['feature_set','feature','robust_standardized_shift']].to_string(index=False))
    print('Saved clean-only shift report and two figures. No fitting.')


if __name__ == '__main__':
    with prohibit_fitting():
        run()
