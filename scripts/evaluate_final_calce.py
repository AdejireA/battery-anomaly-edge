"""Write-once CALCE freeze, followed by explicitly gated held-out evaluation.

Development functions are compiled verbatim from their AST definitions, without
importing the development entry point or making its fitting functions reachable.
Only cell-authorization literals in the injection adapter change to CS2-38.
"""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / 'models/final_calce'
CONFIG = ROOT / 'config/final_calce_model.json'
OUT = ROOT / 'results/calce_final_test'
FIG = ROOT / 'figures/calce/final_test'
DEV = ROOT / 'results/calce_replication'
TEST = ROOT / 'data/processed/calce/CS2_38_discharge_features.csv'
UNLOCKED = False
FIRST_ACCESS = None
PROTECTED = set()


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def guard(event, args):
    global FIRST_ACCESS
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    flags = args[2] if isinstance(args[2], int) else 0
    writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if writing and path in PROTECTED:
        raise RuntimeError('Frozen artifact write blocked: ' + str(path))
    is_test_source = path.is_relative_to(ROOT / 'data') and ('cs2_38' in path.name.lower() or path.name == 'calce_cs2_discharge_features.csv')
    if is_test_source:
        if not UNLOCKED:
            raise RuntimeError('CS2-38 locked until verified freeze receipt exists')
        if writing or path != TEST:
            raise RuntimeError('Only the individual read-only final-test source is authorized')
        if FIRST_ACCESS is None:
            FIRST_ACCESS = now()


sys.addaudithook(guard)


def load_functions(path, names, namespace, adapt_cell=False):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    if adapt_cell:
        class CellAdapter(ast.NodeTransformer):
            def visit_Constant(self, node):
                return ast.copy_location(ast.Constant('CS2-38'), node) if node.value == 'CS2-37' else node
        nodes = [CellAdapter().visit(n) for n in nodes]
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace


def helpers(cell):
    p = json.loads((ROOT / 'config/calce_experiment_protocol.json').read_text())
    ns = dict(np=np, pd=pd, ROOT=ROOT, sha=sha, config=lambda: p, CELLS=(cell,),
              average_precision_score=average_precision_score, roc_auc_score=roc_auc_score)
    load_functions(ROOT / 'scripts/build_calce_relative_features.py', ['build_relative', 'features'], ns)
    load_functions(ROOT / 'scripts/calce_replication.py', ['score', 'metrics', 'distribution', 'table', 'nasa_hashes', 'select_threshold'], ns)
    load_functions(ROOT / 'scripts/calce_replication.py', ['injected_copies'], ns, adapt_cell=cell == 'CS2-38')
    return ns


def write_once(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False))


def verify_freeze():
    receipt = json.loads((FINAL / 'freeze_receipt.json').read_text())
    for relative, expected in receipt['hashes'].items():
        if sha(ROOT / relative) != expected:
            raise RuntimeError('Frozen hash mismatch: ' + relative)
    return receipt


def freeze():
    if CONFIG.exists() or FINAL.exists():
        raise RuntimeError('Freeze is write-once; existing artifacts cannot be replaced. Use --evaluate to verify and resume.')
    h = helpers('CS2-37')
    evidence = pd.read_csv(DEV / 'thresholds.csv', float_precision='round_trip')
    percentile = h['select_threshold'](evidence[['seed', 'percentile', 'clean_fpr']])
    if percentile != 95:
        raise RuntimeError('Required all-seed P95 eligibility not verified; stop without test access')
    threshold = float(evidence.loc[evidence.seed.eq(42) & evidence.percentile.eq(95), 'threshold'].iloc[0])
    source = ROOT / 'models/development/calce_replication/DEVELOPMENT_CALCE_seed42.joblib'
    bundle = joblib.load(source)
    p = json.loads((ROOT / 'config/calce_experiment_protocol.json').read_text())
    assert bundle['features'] == h['features']() and bundle['seed'] == 42
    assert all(bundle['model'].get_params()[k] == v for k, v in p['model'].items())
    assert bundle['model'].random_state == 42
    ids = pd.DataFrame(bundle['training_ids'])
    assert ids.groupby('cell_id').size().to_dict() == {'CS2-35': 254, 'CS2-36': 281}
    assert all(11 <= r.global_cycle <= {'CS2-35': 264, 'CS2-36': 291}[r.cell_id] for r in ids.itertuples())
    nasa = h['nasa_hashes']()
    prior = json.loads((DEV / 'integrity_checks.json').read_text())['nasa_after']
    assert nasa == prior, 'NASA changed since development'
    sources = [ROOT / 'config/calce_experiment_protocol.json', ROOT / 'config/calce_anomaly_injection_protocol.json',
               ROOT / 'scripts/build_calce_relative_features.py', ROOT / 'scripts/calce_replication.py',
               ROOT / 'scripts/evaluate_final_calce.py', ROOT / 'data/processed/calce/calce_cs2_relative_features.csv',
               DEV / 'thresholds.csv', source]
    sources += [ROOT / f'data/processed/calce/CS2_{c}_discharge_features.csv' for c in [35, 36, 37]]
    hashes = {str(s.relative_to(ROOT)): sha(s) for s in sources}
    FINAL.mkdir(parents=True)
    shutil.copyfile(source, FINAL / 'model_bundle.joblib')
    joblib.dump(bundle['model'], FINAL / 'model.joblib')
    joblib.dump(bundle['scaler'], FINAL / 'scaler.joblib')
    for name in ['model_bundle.joblib', 'model.joblib', 'scaler.joblib']:
        path = FINAL / name
        hashes[str(path.relative_to(ROOT))] = sha(path)
    artifact = dict(version='1.0', frozen_at_utc=now(), status='FROZEN_BEFORE_FINAL_TEST_ACCESS',
        feature_representation='CALCE trajectory-relative measurement features', feature_names=bundle['features'],
        history_window=10, baseline='Previous ten cycles only, same cell, excluding current; no imputation',
        mad_scale=p['mad_scale'], epsilon=p['epsilon'], base_features=p['base_features'],
        model_hyperparameters=p['model'], random_state=42, threshold_percentile=95, threshold_value=threshold,
        score_definition='-IsolationForest.score_samples(StandardScaler.transform(X)); flag score > threshold',
        training_cells=p['training_cells'], nominal_fraction=.30, training_rows=ids.groupby('cell_id').size().to_dict(),
        scaler_provenance=dict(source_bundle=str(source.relative_to(ROOT)), training_matrix_sha256=bundle['training_matrix_sha256'],
                               fit_scope='Only 535 nominal CS2-35/36 relative rows; no refitting', mean=bundle['scaler'].mean_.tolist(), scale=bundle['scaler'].scale_.tolist()),
        selection_rationale='Seed 42 is the first predefined seed. P95 is first percentile meeting <=5% clean CS2-37 FPR for all three seeds. No synthetic metric or final-test data used.',
        development_clean_fpr_evidence=evidence.to_dict('records'),
        anomaly_protocol_version=json.loads((ROOT / 'config/calce_anomaly_injection_protocol.json').read_text())['version'],
        hashes=hashes, source_hash_scope='Development-only relative table plus three individual source tables. Combined source contains locked test data and is not read. CS2-38 hash recorded after unlock.',
        configuration_hash_location='models/final_calce/final_calce_model.sha256 and freeze_receipt.json (external digest avoids self-reference)')
    write_once(CONFIG, artifact)
    hashes = {**hashes, str(CONFIG.relative_to(ROOT)): sha(CONFIG)}
    with (FINAL / 'final_calce_model.sha256').open('x') as stream:
        stream.write(sha(CONFIG) + '  config/final_calce_model.json\n')
    write_once(FINAL / 'freeze_receipt.json', dict(frozen_at_utc=artifact['frozen_at_utc'], receipt_at_utc=now(), hashes=hashes, nasa_hashes=nasa, test_access_before_freeze=False))
    verify_freeze()
    print('FROZEN P95:', repr(threshold), 'configuration SHA256:', sha(CONFIG), flush=True)


def evaluate():
    global UNLOCKED
    receipt = verify_freeze()
    cfg = json.loads(CONFIG.read_text())
    h = helpers('CS2-38')
    assert h['nasa_hashes']() == receipt['nasa_hashes']
    PROTECTED.update((ROOT / p).resolve() for p in {**receipt['hashes'], **receipt['nasa_hashes']})
    PROTECTED.update(p.resolve() for p in FINAL.iterdir() if p.is_file())
    # Only after configuration, bundle and all pre-test hashes have been verified.
    UNLOCKED = True
    raw = pd.read_csv(TEST)
    source_hash = sha(TEST)
    PROTECTED.add(TEST.resolve())
    assert set(raw.cell_id) == {'CS2-38'}
    assert raw.global_cycle.tolist() == list(range(1, len(raw) + 1))
    assert pd.to_datetime(raw.start_timestamp).is_monotonic_increasing
    bundle = joblib.load(FINAL / 'model_bundle.joblib')
    assert bundle['features'] == cfg['feature_names']
    relative = h['build_relative'](raw)
    clean = relative.dropna(subset=cfg['feature_names']).copy()
    assert clean.global_cycle.tolist() == list(range(11, len(raw) + 1))
    values = h['score'](bundle, clean)
    threshold = cfg['threshold_value']
    flags = values > threshold
    for directory in [OUT, FIG]:
        directory.mkdir(parents=True, exist_ok=True)
    clean[['cell_id', 'global_cycle']].assign(score=values, flagged=flags).to_csv(OUT / 'clean_scores.csv', index=False)
    periods = []
    for name, indices in zip(['early', 'middle', 'late'], np.array_split(np.arange(len(clean)), 3)):
        periods.append(dict(period=name, first_cycle=int(clean.iloc[indices[0]].global_cycle), last_cycle=int(clean.iloc[indices[-1]].global_cycle),
                            **h['distribution'](values[indices]), flagged=int(flags[indices].sum()), clean_fpr=float(flags[indices].mean())))
    periods = pd.DataFrame(periods)
    periods.to_csv(OUT / 'clean_periods.csv', index=False)
    print('Held-out clean:', len(clean), 'flagged:', int(flags.sum()), 'FPR:', float(flags.mean()), flush=True)
    protocol = json.loads((ROOT / 'config/calce_anomaly_injection_protocol.json').read_text())
    print('Applying unchanged frozen protocol to isolated test copies...', flush=True)
    copies, counts = h['injected_copies'](raw, protocol)
    copies.to_csv(OUT / 'synthetic_evaluation_copies.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    counts.to_csv(OUT / 'synthetic_window_counts.csv', index=False)
    results = []
    score_groups = {}
    for (family, severity), group in copies.loc[copies.is_synthetic_anomaly].groupby(['anomaly_family', 'severity']):
        scores = h['score'](bundle, group)
        score_groups[(family, severity)] = scores
        results.append(dict(family=family, severity=severity, **h['metrics'](values, scores, threshold),
                            **{'score_' + k: v for k, v in h['distribution'](scores).items()}))
    results = pd.DataFrame(results)
    results.to_csv(OUT / 'anomaly_metrics.csv', index=False)
    dev = pd.read_csv(DEV / 'anomaly_metrics.csv')
    dev = dev.loc[dev.seed.eq(42)].copy()
    comparison = dev.merge(results, on=['family', 'severity'], suffixes=('_development', '_test'))
    comparison.to_csv(OUT / 'development_comparison.csv', index=False)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(clean.global_cycle, values, label='Clean CS2-38')
    ax.axhline(threshold, color='red', linestyle='--', label='Frozen P95')
    ax.scatter(clean.loc[flags, 'global_cycle'], values[flags], color='red', s=14)
    ax.set(xlabel='Global cycle', ylabel='Anomaly score (higher = more anomalous)'); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / 'cs2_38_clean_score_vs_cycle.png', dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    for ax, family in zip(axes, protocol['families']):
        for label, s in [('clean', values)] + [(severity, score_groups[(family, severity)]) for severity in ['mild', 'moderate', 'strong']]:
            x = np.sort(s); ax.plot(x, np.arange(1, len(x) + 1) / len(x), label=label)
        ax.axvline(threshold, color='black', linestyle='--'); ax.set(title=family, xlabel='Score', ylabel='Empirical CDF'); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / 'cs2_38_anomaly_score_distributions.png', dpi=160); plt.close(fig)
    for family in protocol['families']:
        fig, ax = plt.subplots(figsize=(8, 4))
        g = results.loc[results.family.eq(family)].set_index('severity').loc[['mild', 'moderate', 'strong']]
        for metric in ['precision', 'recall', 'f1', 'pr_auc', 'roc_auc']:
            ax.plot(g.index, g[metric], marker='o', label=metric)
        ax.set(ylim=(0, 1.05), title=family); ax.legend()
        fig.tight_layout(); fig.savefig(FIG / ('cs2_38_' + ('A2' if 'A2' in family else 'A4') + '_severity.png'), dpi=160); plt.close(fig)
    assert sha(TEST) == source_hash
    assert verify_freeze() == receipt
    assert h['nasa_hashes']() == receipt['nasa_hashes']
    assert FIRST_ACCESS > receipt['receipt_at_utc']
    integrity = dict(freeze_receipt_at_utc=receipt['receipt_at_utc'], first_test_access_at_utc=FIRST_ACCESS,
        completed_at_utc=now(), frozen_hashes_before=receipt['hashes'], frozen_hashes_after={p: sha(ROOT / p) for p in receipt['hashes']},
        nasa_hashes_unchanged=True, nasa_file_count=len(receipt['nasa_hashes']), test_source_sha256=source_hash,
        no_refit=True, no_retuning=True, threshold_unchanged=True, anomaly_protocol_and_magnitudes_unchanged=True,
        test_access_only_after_freeze=True, training_cells=cfg['training_cells'], final_configuration_sha256=sha(CONFIG))
    (OUT / 'integrity_checks.json').write_text(json.dumps(integrity, indent=2), encoding='utf-8')
    summary = dict(threshold=threshold, usable_cycles=len(clean), flagged=int(flags.sum()), clean_fpr=float(flags.mean()),
                   flagged_cycles=clean.loc[flags, 'global_cycle'].tolist(), score_distribution=h['distribution'](values))
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    columns = ['family', 'severity', 'precision', 'recall', 'f1', 'pr_auc', 'roc_auc']
    report = ['# Frozen CALCE final evaluation',
        '## Freeze and selection',
        f'Seed 42 is the first predefined seed, not selected by synthetic performance. P95 was the first clean-only all-seed eligible percentile. Exact threshold: {threshold!r}. Configuration SHA256: {sha(CONFIG)}. Freeze receipt: {receipt["receipt_at_utc"]}; first test-source access: {FIRST_ACCESS}. No fitting, recalibration or retuning occurred.',
        '## DEVELOPMENT — CS2-37', h['table'](pd.DataFrame(cfg['development_clean_fpr_evidence'])), h['table'](dev[columns]),
        '## FINAL HELD-OUT TEST — CS2-38', json.dumps(summary, indent=2), h['table'](periods), h['table'](results[columns]),
        '## Score separation independent of threshold', h['table'](results[['family', 'severity'] + [c for c in results if c.startswith('score_')]]),
        '## Frozen synthetic evaluation semantics',
        'The exact development function bodies are reused via AST, excluding the development entry point and all fitting/calibration functions. Only authorization/provenance cell literals change to CS2-38. The relative-feature cell allowlist permits the test cell after the freeze gate; its calculations are identical. Five-cycle A2 offsets and ten-cycle signed A4 ramps use frozen CS2-37 magnitudes. Each window begins with ten clean prior observations; prior injected observations adapt later baselines within that isolated copy. Current/future observations never enter their own baseline. A4 zero-offset onset is excluded from positive labels. Both drift signs are pooled. Physical guards reject whole windows; no magnitudes are clipped or recalculated.',
        'Precision, F1 and average precision (reported as PR-AUC) use 50% evaluation prevalence, matching development. Recall and ROC-AUC are class-conditional/unweighted. Overlapping scenarios are dependent synthetic copies, not independent real faults. Clean scores are never overwritten.', h['table'](counts),
        '## Integrity', f'All {len(receipt["nasa_hashes"])} frozen NASA hashes match. All pre-test CALCE hashes match after evaluation, including separate scaler/model, bundle, final configuration, source tables, feature code and anomaly protocol. The test-source hash was first computed after unlock and also matches after evaluation. The combined source table was never read; pre-freeze processed-source hashes cover the development-only relative table and three development source tables. The final configuration digest is external to avoid circular self-hashing. See calce_final_test/integrity_checks.json.']
    (ROOT / 'results/calce_final_test.md').write_text('\n\n'.join(report), encoding='utf-8')
    print(h['table'](results[columns]), flush=True)


if __name__ == '__main__':
    if '--evaluate' not in sys.argv:
        freeze()
    evaluate()
