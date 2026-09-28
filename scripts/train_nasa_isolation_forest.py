"""Label-free Phase 4 development grid; only B0005/B0006 fitting and B0007 evaluation."""

import hashlib
import itertools
import json
import platform
from pathlib import Path

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score

try:
    from .nasa_development import (ROOT, read_config, load_development_data, nominal_training,
                                   fit_development_model, anomaly_scores, clean_training_thresholds, threshold_review)
    from .inject_nasa_anomalies import generate_validation_copies
except ImportError:
    from nasa_development import (ROOT, read_config, load_development_data, nominal_training,
                                  fit_development_model, anomaly_scores, clean_training_thresholds, threshold_review)
    from inject_nasa_anomalies import generate_validation_copies

OUTPUT = ROOT / 'results/nasa_model_validation'
FIGURES = ROOT / 'figures/nasa/model_validation'
SEVERITIES = ['mild', 'moderate', 'strong']
CONFIG_KEYS = ['feature_set', 'n_estimators', 'max_features']
RUN_KEYS = CONFIG_KEYS + ['seed']


def evaluation_metrics(clean_scores, synthetic_scores, thresholds):
    """Class-balanced primary metrics; raw instance metrics supplied separately.

    No metric in this function feeds fitting or threshold review.
    PR-AUC is non-interpolated average precision, explicitly not trapezoidal AUC.
    """
    clean_scores = np.asarray(clean_scores)
    synthetic_scores = np.asarray(synthetic_scores)
    if not len(clean_scores) or not len(synthetic_scores):
        raise ValueError('Both clean and synthetic evaluation classes are required')
    y = np.r_[np.zeros(len(clean_scores)), np.ones(len(synthetic_scores))]
    score = np.r_[clean_scores, synthetic_scores]
    weights = np.r_[np.full(len(clean_scores), 0.5 / len(clean_scores)),
                    np.full(len(synthetic_scores), 0.5 / len(synthetic_scores))]
    ap = float(average_precision_score(y, score, sample_weight=weights))
    raw_ap = float(average_precision_score(y, score))
    roc = float(roc_auc_score(y, score))
    result = []
    for t in thresholds:
        fp = int((clean_scores > t['threshold']).sum())
        tp = int((synthetic_scores > t['threshold']).sum())
        fpr, recall = fp / len(clean_scores), tp / len(synthetic_scores)
        precision = recall / (recall + fpr) if recall + fpr else 0.0
        raw_precision = tp / (tp + fp) if tp + fp else 0.0
        result.append(dict(t, precision=precision, recall=recall,
                           f1=2 * precision * recall / (precision + recall) if precision + recall else 0.0,
                           clean_fpr=fpr, pr_auc=ap, roc_auc=roc,
                           raw_precision=raw_precision,
                           raw_f1=2 * raw_precision * recall / (raw_precision + recall) if raw_precision + recall else 0.0,
                           raw_pr_auc=raw_ap, clean_rows=len(clean_scores), synthetic_rows=len(synthetic_scores)))
    return result


def distribution(scores):
    values = np.asarray(scores)
    return {'count': len(values), 'score_mean': float(values.mean()), 'score_std': float(values.std(ddof=1)),
            'score_min': float(values.min()), 'score_p05': float(np.quantile(values, .05)),
            'score_median': float(np.median(values)), 'score_p95': float(np.quantile(values, .95)),
            'score_max': float(values.max())}


def aggregate_seeds(frame, keys, metrics):
    result = frame.groupby(keys, dropna=False)[metrics].agg(['mean', 'std']).reset_index()
    result.columns = ['_'.join(x for x in col if x) if isinstance(col, tuple) else col for col in result.columns]
    return result


def md_table(frame, digits=4):
    def cell(value):
        return f'{value:.{digits}f}' if isinstance(value, (float, np.floating)) else str(value)
    return '\n'.join(['| ' + ' | '.join(map(str, frame.columns)) + ' |',
                      '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in frame.itertuples(index=False, name=None)])


def render_figures(clean_scores, reference_synthetic, thresholds, metrics, config):
    FIGURES.mkdir(parents=True, exist_ok=True)
    feature_sets = list(read_config('nasa_feature_manifest.json')['model_feature_sets'])
    ref = config['display_reference']
    def reference(frame):
        return frame.loc[frame.n_estimators.eq(ref['n_estimators']) & frame.max_features.eq(ref['max_features'])]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, fs in zip(axes, feature_sets):
        rows = reference(clean_scores.loc[clean_scores.feature_set.eq(fs)])
        summary = rows.groupby('cycle').anomaly_score.agg(['mean', 'std'])
        ax.plot(summary.index, summary['mean'], label='Clean score: seed mean')
        ax.fill_between(summary.index, summary['mean'] - summary['std'], summary['mean'] + summary['std'], alpha=.2, label='+/- seed SD')
        for percentile, group in reference(thresholds.loc[thresholds.feature_set.eq(fs)]).groupby('percentile'):
            ax.axhline(group.threshold.mean(), linestyle='--', linewidth=1, label=f'Train P{percentile:g}, seed mean')
        ax.set(title=fs, xlabel='B0007 discharge cycle', ylabel='Anomaly score (higher = more anomalous)')
        ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    fig.suptitle('Development reference: 100 trees, max_features=1.0; not a selected model')
    fig.tight_layout()
    fig.savefig(FIGURES / 'clean_score_vs_cycle.png', dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(13, 9))
    for ax, fs in zip(axes, feature_sets):
        clean = reference(clean_scores.loc[clean_scores.feature_set.eq(fs)])
        values, labels = [clean.anomaly_score.to_numpy()], ['Clean']
        for (family, severity), group in reference_synthetic.loc[reference_synthetic.feature_set.eq(fs)].groupby(['anomaly_family', 'severity'], sort=False):
            values.append(group.anomaly_score.to_numpy())
            labels.append(f'{family[:2]}\n{severity}')
        ax.boxplot(values, tick_labels=labels, showfliers=False)
        ax.set(title=fs + ' (reference configuration; three seeds pooled)', ylabel='Anomaly score')
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(axis='y', alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / 'score_distribution_by_family.png', dpi=160)
    plt.close(fig)

    for short in ['A1', 'A2', 'A3', 'A4']:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        for ax, fs in zip(axes, feature_sets):
            sub = reference_synthetic.loc[reference_synthetic.feature_set.eq(fs) & reference_synthetic.anomaly_family.str.startswith(short)]
            if sub.empty:
                ax.text(.5, .5, 'Not applicable to frozen feature set', ha='center', transform=ax.transAxes)
            else:
                # Separate A4 channels/signs instead of hiding opposing drift responses.
                for variant, group in sub.groupby('variant'):
                    seed_means = group.groupby(['severity', 'seed']).anomaly_score.mean().reset_index()
                    means = seed_means.groupby('severity').anomaly_score.agg(['mean', 'std']).reindex(SEVERITIES)
                    ax.errorbar(range(3), means['mean'], yerr=means['std'], marker='o', capsize=3, label=variant)
                baseline = reference(clean_scores.loc[clean_scores.feature_set.eq(fs)]).anomaly_score.mean()
                ax.axhline(baseline, color='gray', linestyle='--', label='Clean mean')
                ax.set_xticks(range(3), SEVERITIES)
                ax.legend(fontsize=7)
            ax.set(title=fs, ylabel='Mean anomaly score +/- seed SD', xlabel='Frozen severity')
            ax.grid(alpha=.2)
        fig.suptitle(f'{short} severity response: reference configuration')
        fig.tight_layout()
        fig.savefig(FIGURES / f'severity_response_{short}.png', dpi=160)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, fs in zip(axes, feature_sets):
        for (trees, mf), group in thresholds.loc[thresholds.feature_set.eq(fs)].groupby(['n_estimators', 'max_features']):
            summary = group.groupby('percentile').clean_fpr.agg(['mean', 'std'])
            ax.errorbar(summary.index, summary['mean'], yerr=summary['std'], marker='o', capsize=3, label=f'{trees} trees, features={mf}')
        ax.axhline(config['clean_validation_false_positive_tolerance'], color='red', linestyle='--', label='Predefined 5% tolerance')
        ax.set(title=fs, xlabel='Percentile of clean nominal training scores', ylabel='Clean B0007 alarm fraction (FPR proxy)')
        ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / 'threshold_false_positive_tradeoff.png', dpi=160)
    plt.close(fig)


def write_report(config, train_info, thresholds, metrics, stability, score_stability, reviews, counts, provenance):
    ref = config['display_reference']
    reference = stability.loc[stability.n_estimators.eq(ref['n_estimators']) & stability.max_features.eq(ref['max_features']) & stability.variant.eq('pooled')]
    summary = reference.loc[reference.percentile.eq(97.5)]
    columns = ['feature_set', 'anomaly_family', 'severity', 'precision_mean', 'precision_std', 'recall_mean', 'recall_std',
               'f1_mean', 'f1_std', 'pr_auc_mean', 'pr_auc_std', 'roc_auc_mean', 'roc_auc_std']
    threshold_stability = aggregate_seeds(thresholds, CONFIG_KEYS + ['percentile'], ['threshold', 'clean_fpr'])
    threshold_stability.to_csv(OUTPUT / 'threshold_seed_stability.csv', index=False)
    grid = metrics.loc[metrics.variant.eq('pooled') & metrics.percentile.eq(97.5)].groupby(RUN_KEYS)[['pr_auc', 'roc_auc', 'recall']].mean().reset_index()
    grid_summary = aggregate_seeds(grid, CONFIG_KEYS, ['pr_auc', 'roc_auc', 'recall'])
    a4_details = stability.loc[stability.n_estimators.eq(ref['n_estimators']) & stability.max_features.eq(ref['max_features'])
                               & stability.percentile.eq(97.5) & stability.anomaly_family.str.startswith('A4_') & stability.variant.ne('pooled')]
    stability_ranges = summary.groupby('feature_set')[['recall_std', 'f1_std', 'pr_auc_std', 'roc_auc_std']].agg(['min', 'max'])
    stability_ranges.columns = ['_'.join(c) for c in stability_ranges.columns]
    # A1 is excluded from B by design: pooled comparison is not apples-to-apples.
    parts = ['# NASA Isolation Forest development validation',
             'DEVELOPMENT ONLY. No model, feature set or threshold is finalized. B0018 was never opened by the Phase 4 loader or used in calculations. Only individual B0005/B0006/B0007 CSVs were read. Frozen anomaly protocol and feature sets were not changed.',
             '## Training and preprocessing', md_table(pd.DataFrame(train_info)),
             'Nominal selection is cycles 1–50 of each training cell (floor(0.30*168)); then required-feature NaNs are dropped, never imputed. Rows stay in cell/cycle order. StandardScaler fit and IsolationForest fit receive only these same feature matrices, no labels. Per-model scaler means, variances, sample counts, exact training row IDs and hashes are in training_provenance.json and the DEVELOPMENT joblib bundles. B0007 is transform/score only.',
             '## Scores, thresholds and review rule',
             'Anomaly score = -IsolationForest.score_samples(scaled X). Higher means more anomalous; an alarm uses strict score > threshold. predict() and the contamination=auto offset are not decision rules. See [scikit-learn IsolationForest API](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).',
             'Every threshold is the linear-interpolated 95th, 97.5th or 99th percentile of the SAME model’s CLEAN NOMINAL TRAINING scores, after feature filtering. These are in-sample scores, not a held-out calibration set; false-alarm control on another battery is not guaranteed. No B0007 or synthetic score is used to calculate percentile values.',
             'Predeclared tolerance: clean B0007 FPR <=5% for EVERY seed. Per configuration the lowest percentile satisfying this condition is only a review suggestion, never final. Synthetic F1/precision/recall/AP never enter this rule. Clean B0007 is an unmodified aging trajectory, not certified fault-free data: reported FPR is a baseline alarm fraction, not a verified natural-fault false-positive rate.',
             md_table(threshold_stability), '### Threshold review decisions', md_table(pd.DataFrame(reviews)),
             '## Evaluation design and dependence',
             'All frozen eligible contiguous windows are evaluated as separate counterfactual copies. Zero-offset A1/A4 onset rows are saved with false synthetic labels and excluded from positive-class metrics; clean full trajectory supplies the negative class once per comparison. Only required-feature-complete observations are scored. A1 is NOT applicable to measurement_oriented and is not treated as a detection failure.',
             'Primary precision, F1 and PR-AUC use equal total class weights (50% synthetic evaluation prevalence); PR-AUC is non-interpolated average precision, baseline 0.5. This avoids artificial precision inflation from thousands of overlapping positive copies versus 164/168 clean observations. Raw instance precision/F1/AP and class counts are also in metrics.csv. ROC-AUC and within-class recall/FPR do not depend on this class balancing. These are descriptive counterfactual-instance metrics, not real-world precision estimates; overlapping windows and repeated source cycles are dependent. Seed SD measures model randomness only, not sampling uncertainty. A4 pooled metrics combine four scenarios; channel/sign results are separately retained. Paired score differences compare each copy to its original cycle.',
             '### Window acceptance', md_table(counts),
             '## Model grid (macro average over applicable families/severities at P97.5)',
             'Grid: 100/200 trees x max_features 0.75/1.0 x seeds 42/123/2026; max_samples=auto, contamination=auto. Effective max_samples is 92 or 100 because these training sets have fewer than 256 rows. No search expansion. Macro scores have different family coverage across feature sets (A1 only in A); use shared-family tables for direct comparison.',
             md_table(grid_summary),
             '## Predeclared display reference: 100 trees, max_features=1.0',
             'This configuration was specified before fitting for reporting/plots, not chosen for favorable metrics. P97.5 below is a display threshold, NOT a selected threshold. Means and sample SD are across the three fixed seeds.',
             md_table(summary[columns]),
             '### Comparison and observed failures',
             'Neither feature set meets the predefined clean-FPR tolerance at any threshold/configuration. There is no acceptable model/threshold recommendation under this policy. The reference degradation-aware model has lower clean alarm rates at P95/P97.5, while measurement-oriented has lower clean alarm rate at P99 and stronger thermal separation. These trade-offs do not establish a winner.',
             'A1 mild separation is weak (reference balanced AP about 0.52, ROC-AUC about 0.54). A4 pooled separation is near chance for both feature sets; negative temperature drift and positive voltage drift often LOWER the score relative to the same clean source cycle. A2 moderate and strong give identical reference scores/metrics despite strictly larger physical perturbations: model score saturation, not an injection error. High A2 recall coexists with high clean alarm rates and only modest ROC-AUC.',
             'A3 improves with severity and measurement-oriented shows stronger thermal ROC-AUC than degradation-aware in the reference configuration, but this does not resolve the baseline alarm-rate problem. A1 is excluded from measurement-oriented rather than scored as an unobservable anomaly.',
             '### A4 channel/sign reference results',
             md_table(a4_details[['feature_set', 'variant', 'severity', 'pr_auc_mean', 'pr_auc_std', 'roc_auc_mean', 'roc_auc_std', 'paired_score_change_mean_mean']]),
             '### Reference seed variability ranges across applicable families/severities',
             md_table(stability_ranges.reset_index()),
             'At the reference configuration, AP seed SD stays below 0.027, but thresholded recall SD reaches about 0.093. Across the wider predefined grid, measurement-oriented with 100 trees/max_features=0.75 at P99 has clean-FPR seed SD about 0.163: do not select its unusually favorable individual seed. Seed variability is reported separately from configuration differences.',
             '## All configurations: family/severity/threshold seed mean and SD',
             'metrics.csv contains every seed/configuration/threshold/family/severity plus separate A4 channel/sign metrics. metric_seed_stability.csv contains all seed aggregates. The following table includes all pooled-family aggregates; PR/ROC-AUC are threshold-independent and therefore repeat across thresholds.',
             md_table(stability.loc[stability.variant.eq('pooled'), CONFIG_KEYS + ['anomaly_family', 'severity', 'percentile', 'precision_mean', 'precision_std', 'recall_mean', 'recall_std', 'f1_mean', 'f1_std', 'clean_fpr_mean', 'clean_fpr_std', 'pr_auc_mean', 'pr_auc_std', 'roc_auc_mean', 'roc_auc_std']]),
             '## Score distributions and seed stability',
             'score_distributions.csv: count, mean, SD, minimum, P5, median, P95, maximum for each seed/configuration and clean or family/severity/variant. score_seed_stability.csv: cross-seed mean and SD of those summaries. scores.csv.gz preserves every scored copy with scenario/source provenance and paired clean score. Clean unscorable initial cycles are retained as NaN in clean_scores.csv.',
             md_table(score_stability.loc[score_stability.n_estimators.eq(100) & score_stability.max_features.eq(1.0) & score_stability.variant.eq('pooled')]),
             '## Limitations and suspicious behaviour',
             f"Across the grid, clean B0007 FPR ranges from {thresholds.clean_fpr.min():.2%} to {thresholds.clean_fpr.max():.2%}. High baseline alarm fractions indicate transfer/aging mismatch with early training cycles; high injected recall alone does not establish useful separation.",
             'Isolation Forest scores need not increase monotonically with perturbation magnitude. Outside training support, scores can saturate; weak sensor drift or thermal shifts can move a point toward learned nominal regions. Compare channel/sign results and paired score changes, not only pooled recall. Feature-summary injections are not natural fault labels or full physical simulations. No threshold/model is automatically frozen or deployed.',
             '## Reproducibility and artifacts',
             'Run `.venv/Scripts/python.exe scripts/train_nasa_isolation_forest.py`. Artifacts: `models/development/` (24 DEVELOPMENT bundles), `results/nasa_model_validation/` (copies, metrics, distributions, scores, provenance, dependency versions and hashes), `figures/nasa/model_validation/` (seven requested plots).',
             '```json\n' + json.dumps(provenance, indent=2) + '\n```']
    (ROOT / 'results/nasa_model_validation.md').write_text('\n\n'.join(parts) + '\n', encoding='utf-8')


def main():
    config = read_config('nasa_model_development.json')
    experiment = read_config('nasa_experiment_protocol.json')
    if experiment['nominal_training_fraction'] != .30 or config['nominal_last_cycle'] != 50:
        raise ValueError('Frozen nominal default changed')
    data = load_development_data()
    nominal = nominal_training(data)
    clean = data.loc[data.cell_id.eq('B0007')].reset_index(drop=True)
    protocol = read_config('anomaly_injection_protocol.json')
    manifest = read_config('nasa_feature_manifest.json')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    model_dir = ROOT / 'models/development'
    model_dir.mkdir(parents=True, exist_ok=True)
    copies, counts = generate_validation_copies(clean, protocol)
    copies.to_csv(OUTPUT / 'B0007_synthetic_evaluation_copies.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    counts.to_csv(OUTPUT / 'injection_window_counts.csv', index=False)
    print(f'B0007 only: generated {len(copies)} copied rows across {copies.scenario_id.nunique()} independent scenario copies.', flush=True)
    metric_rows, threshold_rows, distributions, score_frames, clean_frames = [], [], [], [], []
    training_provenance, train_info = [], []
    for feature_set in manifest['model_feature_sets']:
        for n_estimators, max_features, seed in itertools.product(config['n_estimators'], config['max_features'], config['seeds']):
            run = dict(feature_set=feature_set, n_estimators=n_estimators, max_features=max_features, seed=seed)
            bundle = fit_development_model(nominal, feature_set, n_estimators, max_features, seed)
            thresholds = clean_training_thresholds(bundle, nominal)
            clean_score, clean_keep = anomaly_scores(bundle, clean)
            full_clean = clean[['cell_id', 'cycle']].copy()
            full_clean['anomaly_score'] = clean_score
            for key, value in run.items():
                full_clean[key] = value
            clean_frames.append(full_clean)
            for row in thresholds:
                threshold_rows.append(dict(run, **row, clean_fpr=float((clean_score > row['threshold']).mean()), clean_rows=len(clean_score)))
            distributions.append(dict(run, anomaly_family='CLEAN', severity='clean', variant='pooled', **distribution(clean_score)))
            allowed = [f for f, spec in protocol['families'].items() if feature_set in spec['feature_sets']]
            evaluation = copies.loc[copies.anomaly_family.isin(allowed) & copies.is_synthetic_anomaly].copy()
            synthetic_score, keep = anomaly_scores(bundle, evaluation)
            scored = evaluation.loc[keep, ['source_cell', 'source_cycle', 'anomaly_family', 'severity', 'channel', 'drift_sign', 'scenario_id', 'window_start_cycle', 'offset_in_window', 'is_synthetic_anomaly']].copy()
            scored['anomaly_score'] = synthetic_score
            scored['variant'] = np.where(scored.anomaly_family.str.startswith('A4_'), scored.channel + '_' + scored.drift_sign.astype(str), 'joint')
            by_cycle = pd.Series(clean_score.to_numpy(), index=clean.loc[clean_keep, 'cycle'])
            scored['paired_clean_score'] = scored.source_cycle.map(by_cycle)
            scored['paired_score_change'] = scored.anomaly_score - scored.paired_clean_score
            for key, value in run.items():
                scored[key] = value
            score_frames.append(scored.reset_index(drop=True))
            for (family, severity), group in scored.groupby(['anomaly_family', 'severity']):
                variants = [('pooled', group)]
                if family.startswith('A4_'):
                    variants += list(group.groupby('variant'))
                for variant, part in variants:
                    paired_mean = float(part.paired_score_change.mean())
                    positive_fraction = float(part.paired_score_change.gt(0).mean())
                    distributions.append(dict(run, anomaly_family=family, severity=severity, variant=variant, **distribution(part.anomaly_score)))
                    for row in evaluation_metrics(clean_score, part.anomaly_score, thresholds):
                        metric_rows.append(dict(run, anomaly_family=family, severity=severity, variant=variant,
                                                paired_score_change_mean=paired_mean, paired_score_increase_fraction=positive_fraction, **row))
            bundle['threshold_candidates'] = thresholds
            bundle['final_threshold'] = None
            training_provenance.append(bundle['provenance'])
            filename = f'DEVELOPMENT_{feature_set}_trees{n_estimators}_features{max_features}_seed{seed}.joblib'
            joblib.dump(bundle, model_dir / filename, compress=3)
            if n_estimators == 100 and max_features == .75 and seed == 42:
                ids = pd.DataFrame(bundle['provenance']['training_ids'])
                train_info.append({'feature_set': feature_set, 'initial_nominal_rows': len(nominal),
                                   'effective_rows': len(ids), 'B0005': int(ids.cell_id.eq('B0005').sum()),
                                   'B0006': int(ids.cell_id.eq('B0006').sum()), 'clean_validation_scored': len(clean_score)})
            print(f"{feature_set}: trees={n_estimators}, features={max_features}, seed={seed}; train={bundle['provenance']['training_rows']}, B0007={len(clean_score)}", flush=True)
    metrics, thresholds = pd.DataFrame(metric_rows), pd.DataFrame(threshold_rows)
    distributions = pd.DataFrame(distributions)
    all_scores, all_clean = pd.concat(score_frames, ignore_index=True), pd.concat(clean_frames, ignore_index=True)
    stability = aggregate_seeds(metrics, CONFIG_KEYS + ['anomaly_family', 'severity', 'variant', 'percentile'],
                                ['precision', 'recall', 'f1', 'clean_fpr', 'pr_auc', 'roc_auc', 'paired_score_change_mean', 'paired_score_increase_fraction'])
    score_stability = aggregate_seeds(distributions, CONFIG_KEYS + ['anomaly_family', 'severity', 'variant'],
                                      ['score_mean', 'score_std', 'score_median', 'score_p05', 'score_p95'])
    reviews = []
    for key, part in thresholds.groupby(CONFIG_KEYS):
        reviews.append(dict(zip(CONFIG_KEYS, key)) | threshold_review(part[['percentile', 'seed', 'clean_fpr']], config['clean_validation_false_positive_tolerance']))
    for name, frame in [('metrics', metrics), ('thresholds', thresholds), ('metric_seed_stability', stability),
                        ('score_distributions', distributions), ('score_seed_stability', score_stability), ('clean_scores', all_clean)]:
        frame.to_csv(OUTPUT / f'{name}.csv', index=False)
    all_scores.to_csv(OUTPUT / 'scores.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    (OUTPUT / 'training_provenance.json').write_text(json.dumps(training_provenance, indent=2) + '\n', encoding='utf-8')
    (OUTPUT / 'threshold_review.json').write_text(json.dumps(reviews, indent=2) + '\n', encoding='utf-8')
    paths = [ROOT / 'config' / name for name in ['nasa_feature_manifest.json', 'anomaly_injection_protocol.json', 'nasa_experiment_protocol.json', 'nasa_model_development.json']]
    paths += [ROOT / f'data/processed/nasa/{cell}_discharge_features.csv' for cell in ['B0005', 'B0006', 'B0007']]
    paths += [Path(__file__), ROOT / 'scripts/nasa_development.py', ROOT / 'scripts/inject_nasa_anomalies.py']
    provenance = {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__,
                  'scipy': scipy.__version__, 'scikit_learn': sklearn.__version__, 'joblib': joblib.__version__,
                  'matplotlib': matplotlib.__version__,
                  'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUTPUT / 'run_provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    reference_scores = all_scores.loc[all_scores.n_estimators.eq(config['display_reference']['n_estimators']) & all_scores.max_features.eq(config['display_reference']['max_features'])]
    render_figures(all_clean, reference_scores, thresholds, metrics, config)
    write_report(config, train_info, thresholds, metrics, stability, score_stability, reviews, counts, provenance)
    print('Completed 24 DEVELOPMENT models. No final model or threshold selected; no B0018 file opened.', flush=True)


if __name__ == '__main__':
    main()
