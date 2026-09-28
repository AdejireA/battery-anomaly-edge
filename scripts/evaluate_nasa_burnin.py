"""Validation-only burn-in experiment with clean-FPR-gated synthetic reporting."""

import hashlib
import json

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

try:
    from .nasa_development import ROOT, load_development_data, read_config, anomaly_scores
    from .nasa_burnin import (FRACTIONS, KEYS, TOLERANCE, saved_models, prohibit_fitting,
                              protected_hashes, calibrate_and_evaluate_clean, split_clean_validation, eligible_for_review)
    from .inject_nasa_anomalies import generate_validation_copies
    from .train_nasa_isolation_forest import md_table, aggregate_seeds, evaluation_metrics
except ImportError:
    from nasa_development import ROOT, load_development_data, read_config, anomaly_scores
    from nasa_burnin import (FRACTIONS, KEYS, TOLERANCE, saved_models, prohibit_fitting,
                            protected_hashes, calibrate_and_evaluate_clean, split_clean_validation, eligible_for_review)
    from inject_nasa_anomalies import generate_validation_copies
    from train_nasa_isolation_forest import md_table, aggregate_seeds, evaluation_metrics

OUT = ROOT / 'results/nasa_burnin_calibration'
FIG = ROOT / 'figures/nasa/burnin_calibration'


def run():
    before = protected_hashes()
    data = load_development_data()
    clean = data.loc[data.cell_id.eq('B0007')].reset_index(drop=True)
    config = read_config('nasa_model_development.json')
    protocol = read_config('anomaly_injection_protocol.json')
    thresholds, score_rows = [], []
    for info, bundle, path, digest in saved_models():
        state = joblib.hash(bundle)
        for fraction in FRACTIONS:
            rows, early_scores, late_scores = calibrate_and_evaluate_clean(bundle, clean, fraction)
            thresholds.extend(dict(info, **row) for row in rows)
            for region, scores in [('calibration', early_scores), ('post_calibration_clean', late_scores)]:
                for index, score in scores.items():
                    score_rows.append(dict(info, calibration_fraction=fraction, region=region,
                                           source_cycle=int(clean.loc[index, 'cycle']), score=score))
        if joblib.hash(bundle) != state:
            raise AssertionError('Model or scaler mutated')
    thresholds = pd.DataFrame(thresholds)
    reviewed, eligible = eligible_for_review(thresholds[KEYS + ['seed', 'calibration_fraction', 'percentile', 'post_calibration_clean_fpr']])
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    thresholds.to_csv(OUT / 'burnin_thresholds.csv', index=False)
    pd.DataFrame(score_rows).to_csv(OUT / 'burnin_clean_scores.csv', index=False)
    reviewed.to_csv(OUT / 'burnin_review.csv', index=False)
    eligible.to_csv(OUT / 'eligible_configurations.csv', index=False)
    stability = aggregate_seeds(thresholds, KEYS + ['calibration_fraction', 'percentile'],
                                ['threshold', 'post_calibration_clean_fpr'])
    stability.to_csv(OUT / 'burnin_seed_stability.csv', index=False)
    # Eligibility is determined and saved BEFORE any synthetic generation/scoring.
    metric_rows, window_counts = [], []
    for fraction in sorted(eligible.calibration_fraction.unique()):
        _, evaluation, boundary = split_clean_validation(clean, fraction)
        copies, counts = generate_validation_copies(clean, protocol, min_source_cycle=boundary + 1)
        if not copies.source_cycle.gt(boundary).all() or not copies.window_start_cycle.gt(boundary).all():
            raise AssertionError('Synthetic/calibration overlap')
        counts['calibration_fraction'] = fraction
        window_counts.append(counts)
        copies.to_csv(OUT / f'eligible_postcalibration_copies_{fraction:.2f}.csv.gz', index=False, compression={'method':'gzip','mtime':0})
        for info, bundle, path, digest in saved_models():
            selected = eligible.loc[eligible.calibration_fraction.eq(fraction)]
            for key in KEYS:
                selected = selected.loc[selected[key].eq(info[key])]
            if selected.empty:
                continue
            allowed = [family for family, spec in protocol['families'].items() if info['feature_set'] in spec['feature_sets']]
            scored, keep = anomaly_scores(bundle, copies.loc[copies.is_synthetic_anomaly & copies.anomaly_family.isin(allowed)])
            frame = copies.loc[scored.index].copy()
            frame['score'] = scored
            negative, _ = anomaly_scores(bundle, evaluation)
            ts = thresholds.loc[thresholds.calibration_fraction.eq(fraction) & thresholds.percentile.isin(selected.percentile)]
            for key in KEYS + ['seed']:
                ts = ts.loc[ts[key].eq(info[key])]
            for (family, severity), group in frame.groupby(['anomaly_family','severity']):
                variants = [('pooled', group)]
                if family.startswith('A4_'):
                    variants += [(f'{ch}_{sign}', sub) for (ch, sign), sub in group.groupby(['channel','drift_sign'])]
                for variant, part in variants:
                    for metric in evaluation_metrics(negative, part.score, ts[['percentile','threshold']].to_dict('records')):
                        metric_rows.append(dict(info, calibration_fraction=fraction, anomaly_family=family,
                                                severity=severity, variant=variant, **metric))
    columns = KEYS + ['seed','calibration_fraction','anomaly_family','severity','variant','percentile','threshold',
                      'precision','recall','f1','clean_fpr','pr_auc','roc_auc','raw_precision','raw_f1','raw_pr_auc','clean_rows','synthetic_rows']
    metrics = pd.DataFrame(metric_rows, columns=columns)
    metrics.to_csv(OUT / 'eligible_anomaly_metrics.csv', index=False)
    if window_counts:
        pd.concat(window_counts).to_csv(OUT / 'eligible_injection_window_counts.csv', index=False)
    if not metrics.empty:
        aggregate_seeds(metrics, KEYS + ['calibration_fraction','anomaly_family','severity','variant','percentile'],
                        ['precision','recall','f1','pr_auc','roc_auc']).to_csv(OUT / 'eligible_anomaly_seed_stability.csv', index=False)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=True)
    for row, fs in enumerate(read_config('nasa_feature_manifest.json')['model_feature_sets']):
        for col, fraction in enumerate(FRACTIONS):
            ax = axes[row,col]
            part = stability.loc[stability.feature_set.eq(fs) & stability.calibration_fraction.eq(fraction)]
            for (trees, mf), group in part.groupby(['n_estimators','max_features']):
                ax.errorbar(group.percentile, group.post_calibration_clean_fpr_mean,
                            yerr=group.post_calibration_clean_fpr_std, marker='o', capsize=3, label=f'{trees} trees; features={mf}')
            ax.axhline(TOLERANCE, color='red', linestyle='--', label='5% tolerance')
            ax.set(title=f'{fs}\n{fraction:.0%} burn-in', xlabel='Burn-in score percentile', ylabel='Post-calibration clean FPR', ylim=(0,1.05))
            ax.grid(alpha=.2)
            if col == 0:
                ax.legend(fontsize=7)
    fig.suptitle('Saved models only; mean +/- sample SD across three seeds')
    fig.tight_layout()
    fig.savefig(FIG / 'post_calibration_fpr.png', dpi=160)
    plt.close(fig)
    parts = ['# Label-free B0007 burn-in calibration',
             'Validation experiment only: no final model/threshold selection and no final-test access. All 24 saved development models are loaded read-only; StandardScaler.fit/partial_fit and IsolationForest.fit are disabled at runtime. No scaler/model refitting or frozen magnitude/feature changes.',
             f"Result: {len(eligible)} of {len(reviewed)} configuration/fraction/percentile combinations meet the all-seed clean-FPR requirement. Individual-run FPR spans {thresholds.post_calibration_clean_fpr.min():.2%}–{thresholds.post_calibration_clean_fpr.max():.2%}. " + ('The tested early per-cell burn-in calibration does not solve the later clean-trajectory threshold shift.' if eligible.empty else 'Eligible configurations are returned for review only.'),
             '### Calibration/evaluation row counts',
             md_table(thresholds[['feature_set','calibration_fraction','boundary_cycle','calibration_rows','post_calibration_clean_rows']].drop_duplicates()),
             '### Predeclared reference (100 trees, max_features=1.0): mean and seed SD',
             md_table(stability.loc[stability.n_estimators.eq(100) & stability.max_features.eq(1.0)]),
             '## Predeclared policy',
             'Fractions 20%, 30%, 40% use floor(fraction*168), ending at cycles 33, 50, 67. The boundary is set before feature-NaN dropping. Calibration uses only required-feature-complete CLEAN B0007 observations up to that boundary; clean evaluation uses only later cycles. Scores are -score_samples. Thresholds are linear P95/P97.5/P99 of burn-in scores only; alarm iff score > threshold. No synthetic labels enter threshold calculation.',
             'Eligibility requires post-calibration clean FPR <=5% for EACH of seeds 42/123/2026, not just their mean. Eligible rows are ordered by shorter calibration fraction first, then the lowest satisfying percentile. All eligible model configurations remain for review; no synthetic metric is a selection criterion and no automatic finalization occurs.',
             '## Counts and thresholds for every seed/configuration', md_table(thresholds),
             '## Seed stability for every configuration', md_table(stability),
             '## Eligibility review', md_table(reviewed),
             f'Eligible configuration/fraction/percentile combinations: **{len(eligible)}**.',
             md_table(eligible) if len(eligible) else 'None satisfies the clean-FPR requirement across all three seeds. No winner is proposed.',
             '## Controlled anomalies — clean-FPR gate',
             'Part 4 and the requested completion report require synthetic performance only after the clean-FPR condition is satisfied. All configurations are first evaluated on clean post-calibration data; synthetic evaluation is then run only for eligible configurations. It is not used to rescue an ineligible threshold.',
             'When eligible, whole synthetic windows must start after the boundary, not merely have their late rows filtered from a window that began during calibration. A1 may read the four preceding CLEAN observations and original initial capacity for its frozen causal calculation; these rows are neither perturbed nor emitted. Zero-offset ramp onsets are not synthetic positives. Precision/F1/AP retain the Phase 4 equal-class-weight 50% evaluation prevalence; PR-AUC is average precision. Overlapping windows are dependent.',
             md_table(metrics) if len(metrics) else 'No eligible configurations: synthetic metrics are intentionally withheld, and no new synthetic datasets were generated in this run. A4 performance after burn-in cannot be claimed or compared under this gate. Prior Phase 4 weakness is not evidence that calibration fixes or worsens A4.',
             '## Interpretation',
             f'Post-calibration clean FPR across all individual runs: {thresholds.post_calibration_clean_fpr.min():.2%}–{thresholds.post_calibration_clean_fpr.max():.2%}.',
             'Early clean burn-in calibrates the initial cell score distribution; it does not guarantee control during later trajectory evolution. A full clean aging trajectory is not a stationary negative population or independently verified fault-free ground truth. Clean-FPR eligibility is a validation-screening result, not an out-of-sample guarantee. Seed SD quantifies forest randomness, not uncertainty from independent batteries. Windows differ in evaluation length, so fraction comparisons do not hold the evaluated cycles fixed.',
             '## Artifacts',
             'Detailed CSVs in `results/nasa_burnin_calibration/`: burnin_thresholds.csv, burnin_clean_scores.csv, burnin_seed_stability.csv, burnin_review.csv, eligible_configurations.csv, eligible_anomaly_metrics.csv. Empty eligible metrics contain headers, not fabricated zero scores. Figure: `figures/nasa/burnin_calibration/post_calibration_fpr.png`. Shift analysis is in `results/nasa_cross_cell_shift.md`.']
    (ROOT / 'results/nasa_burnin_calibration.md').write_text('\n\n'.join(parts)+'\n', encoding='utf-8')
    if protected_hashes() != before:
        raise AssertionError('Protected source, config or saved model changed')
    (OUT / 'burnin_integrity.json').write_text(json.dumps({'protected_sha256':before,'unchanged':True,'refitting_disabled':True,
                                                       'fractions':FRACTIONS,'tolerance':TOLERANCE,'eligibility':'all_three_seeds',
                                                       'eligible_count':len(eligible),'final_model':None,'final_threshold':None,
                                                       'script_sha256':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['evaluate_nasa_burnin.py','nasa_burnin.py','inject_nasa_anomalies.py']}}, indent=2)+'\n')
    print(thresholds.groupby(['feature_set','calibration_fraction','percentile']).post_calibration_clean_fpr.agg(['mean','min','max']).to_string())
    print(f'Eligible configurations: {len(eligible)}. No refitting or finalization.')


if __name__ == '__main__':
    with prohibit_fitting():
        run()
