"""Two-stage, write-once NASA freeze followed by one authorized held-out evaluation."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import shutil

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'config/final_nasa_model.json'
FINAL = ROOT/'models/final_nasa'
OUT = ROOT/'results/nasa_final_test'
FIG = ROOT/'figures/nasa/final_test'
UNLOCKED = False
TEST_READS = []
PROTECTED = set()


def now():
    return datetime.now(timezone.utc).isoformat()


def guard(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    p=Path(os.fsdecode(args[0])).resolve()
    flags=args[2] if isinstance(args[2],int) else 0
    writing=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing and p in PROTECTED:
        raise RuntimeError('Frozen artifact writes are forbidden during final evaluation')
    test_data=('b0018' in p.name.lower() or p.name=='nasa_discharge_features.csv') and p.is_relative_to(ROOT/'data')
    if test_data:
        if not UNLOCKED:
            raise RuntimeError('Final test data is locked until freeze verification')
        if writing:
            raise RuntimeError('Final source data is read-only')
        TEST_READS.append(dict(path=str(p.relative_to(ROOT)),utc=now()))


sys.addaudithook(guard)
import numpy as np
import pandas as pd
import joblib
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nasa_burnin import prohibit_fitting
from build_nasa_relative_features import build_relative_features
from inject_nasa_anomalies import perturb_window
from train_nasa_isolation_forest import evaluation_metrics, distribution, md_table


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT)).replace('\\','/')


def write_once(path,obj):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,indent=2,allow_nan=False)
        f.write('\n')


def select_threshold(evidence):
    # Deliberately accepts ONLY clean evidence, never synthetic metrics.
    required={'seed','percentile','threshold','clean_fpr'}
    if set(evidence.columns)!=required:
        raise ValueError('Threshold selection accepts clean evidence only')
    for percentile in [95.,97.5,99.]:
        part=evidence.loc[evidence.percentile.eq(percentile)]
        if len(part)!=3 or set(part.seed)!={42,123,2026}:
            raise ValueError('Incomplete all-seed evidence')
        if part.clean_fpr.le(.05).all():
            return percentile,float(part.loc[part.seed.eq(42),'threshold'].iloc[0])
    raise RuntimeError('No eligible threshold: final configuration cannot be frozen')


def freeze():
    if CONFIG.exists() or (FINAL/'freeze_receipt.json').exists():
        raise RuntimeError('Freeze is write-once; existing freeze cannot be replaced')
    evidence_path=ROOT/'results/nasa_relative_features/thresholds.csv'
    evidence=pd.read_csv(evidence_path,float_precision='round_trip')
    evidence=evidence.loc[evidence.feature_set.eq('RELATIVE_B')&evidence.history_window.eq(10)&evidence.n_estimators.eq(100)&evidence.max_features.eq(1),['seed','percentile','threshold','clean_fpr']]
    percentile,threshold=select_threshold(evidence)
    source=ROOT/'models/development/relative_features/DEVELOPMENT_RELATIVE_B_k10_trees100_features1.0_seed42.joblib'
    bundle=joblib.load(source)
    provenance=bundle['provenance']
    assert provenance['training_rows']==80
    assert {r['cell_id'] for r in provenance['training_ids']}=={'B0005','B0006'}
    assert all(11<=r['cycle']<=50 for r in provenance['training_ids'])
    manifest=json.loads((ROOT/'config/nasa_relative_feature_manifest.json').read_text())
    assert bundle['features']==manifest['feature_sets']['10']['RELATIVE_B']
    params=dict(n_estimators=100,max_features=1.0,max_samples='auto',contamination='auto',random_state=42)
    assert all(bundle['model'].get_params()[k]==v for k,v in params.items())
    FINAL.mkdir(parents=True,exist_ok=True)
    bundle_path=FINAL/'model_bundle.joblib'
    # No model fit/clone: exact byte copy of the predeclared reporting reference.
    with bundle_path.open('xb') as f:f.write(source.read_bytes())
    for key in ['scaler','model']:
        with (FINAL/f'{key}.joblib').open('xb') as f:joblib.dump(bundle[key],f)
    sources=[ROOT/f'data/processed/nasa/{cell}_discharge_features.csv' for cell in ['B0005','B0006','B0007']]
    frames=[pd.read_csv(p) for p in sources]
    assert [set(f.cell_id) for f in frames]==[{'B0005'},{'B0006'},{'B0007'}]
    snapshot=FINAL/'development_source_table.csv'
    pd.concat(frames,ignore_index=True).to_csv(snapshot,index=False,mode='x')
    locked=[ROOT/'config/nasa_relative_feature_manifest.json',ROOT/'config/nasa_feature_manifest.json',ROOT/'config/nasa_experiment_protocol.json',ROOT/'config/anomaly_injection_protocol.json',ROOT/'config/nasa_model_development.json',evidence_path,source,bundle_path,FINAL/'scaler.joblib',FINAL/'model.joblib',snapshot,*sources,
            ROOT/'scripts/build_nasa_relative_features.py',ROOT/'scripts/inject_nasa_anomalies.py',ROOT/'scripts/finalize_nasa.py',ROOT/'scripts/train_nasa_isolation_forest.py',ROOT/'scripts/nasa_burnin.py']
    config=dict(version='1.0',status='FROZEN_FINAL_NASA_CONFIGURATION',frozen_at_utc=now(),feature_set='RELATIVE_B',representation='trajectory_measurement_oriented',history_window=10,features=bundle['features'],model_family='IsolationForest',hyperparameters=params,random_seed=42,training_cells=['B0005','B0006'],nominal_fraction=.30,nominal_cycles_per_training_cell=50,effective_training_rows=80,scaler_provenance=provenance,threshold_percentile=percentile,threshold_value=threshold,threshold_source='Seed-42 in-sample clean nominal B0005/B0006 scores; exact saved Phase 4C value',score_convention='-IsolationForest.score_samples(StandardScaler.transform(X)); higher is more anomalous; flag score > threshold',selection_rationale='User-fixed predeclared reporting reference, not best synthetic result. First of P95/P97.5/P99 meeting clean B0007 FPR <=5% for ALL seeds 42/123/2026. No synthetic metrics used.',development_clean_fpr_evidence=evidence.to_dict('records'),anomaly_protocol_version=json.loads((ROOT/'config/anomaly_injection_protocol.json').read_text())['protocol_version'],source_table_scope='Development-only B0005/B0006/B0007 snapshot; combined NASA table contains locked test data and is deliberately not opened before freeze. Test source hash will be recorded in a separate post-freeze receipt.',clean_temporal_statistics_rule='Split chronologically ordered usable cycles into three nearly equal contiguous parts with numpy.array_split',synthetic_evaluation_rule='Frozen A2/A3 five-cycle and A4 ten-cycle windows at every valid onset after 10 prior cycles; both A4 signs/channels; independent scenario histories; exclude zero-offset onset from positive class; preserve physical guards; class-balanced 50% evaluation prevalence',hashes={relative(p):digest(p) for p in locked},software_versions=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__),configuration_hash_rule='configuration_payload_sha256 hashes canonical sorted compact JSON excluding that field. Detached final_nasa_model.sha256 hashes the complete file bytes.')
    config['configuration_payload_sha256']=hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    write_once(CONFIG,config)
    file_hash=digest(CONFIG)
    with (FINAL/'final_nasa_model.sha256').open('x') as f:f.write(file_hash+'  config/final_nasa_model.json\n')
    write_once(FINAL/'freeze_receipt.json',dict(stage='FREEZE_COMPLETE_TEST_DATA_STILL_LOCKED',utc=now(),configuration_sha256=file_hash,model_bundle_sha256=digest(bundle_path),test_accesses_before_freeze=TEST_READS))
    assert not TEST_READS
    print(json.dumps(dict(percentile=percentile,threshold=threshold,configuration_sha256=file_hash,clean_evidence=evidence.to_dict('records')),indent=2))


def verify_freeze():
    config=json.loads(CONFIG.read_text())
    receipt=json.loads((FINAL/'freeze_receipt.json').read_text())
    actual=digest(CONFIG)
    assert actual==receipt['configuration_sha256']==(FINAL/'final_nasa_model.sha256').read_text().split()[0]
    content=dict(config);expected=content.pop('configuration_payload_sha256')
    assert expected==hashlib.sha256(json.dumps(content,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    for path,value in config['hashes'].items():assert digest(ROOT/path)==value,path
    assert receipt['test_accesses_before_freeze']==[]
    return config


def predict(bundle,frame):
    x=frame[bundle['features']]
    assert np.isfinite(x.to_numpy()).all()
    return -bundle['model'].score_samples(bundle['scaler'].transform(x))


def injected_relative(clean,injected):
    start,end=int(injected.source_cycle.min()),int(injected.source_cycle.max())
    context=clean.loc[clean.cycle.between(start-10,end)].copy().reset_index(drop=True)
    fields=json.loads((ROOT/'config/nasa_relative_feature_manifest.json').read_text())['base_features']
    context.loc[context.cycle.between(start,end),fields]=injected[fields].to_numpy()
    result=build_relative_features(context,[10],allowed_cells=('B0018',))
    result=result.loc[result.cycle.between(start,end)].reset_index(drop=True)
    for column in injected.columns:result[column]=injected[column].to_numpy()
    return result


def figures(clean,synthetic,metrics,threshold):
    FIG.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(12,4))
    ax.plot(clean.cycle,clean.score,label='Clean B0018');flagged=clean.loc[clean.flagged]
    ax.scatter(flagged.cycle,flagged.score,c='red',label='Flagged');ax.axhline(threshold,c='black',ls='--',label='Frozen threshold')
    ax.set(xlabel='Discharge cycle',ylabel='Anomaly score',title='FINAL HELD-OUT TEST — B0018');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/'b0018_clean_score_vs_cycle.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(16,5))
    for ax,family in zip(axes,['A2','A3','A4']):
        for label,values in [('clean',clean.score)]+[(s,synthetic.loc[synthetic.anomaly_family.str.startswith(family)&synthetic.severity.eq(s),'score']) for s in ['mild','moderate','strong']]:
            if len(values):
                v=np.sort(values);ax.plot(v,np.arange(1,len(v)+1)/len(v),label=label)
        ax.axvline(threshold,c='black',ls='--');ax.set(title=family,xlabel='Anomaly score',ylabel='Cumulative fraction');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/'b0018_anomaly_score_distributions.png',dpi=160);plt.close(fig)
    for family in ['A2','A3','A4']:
        part=metrics.loc[metrics.anomaly_family.str.startswith(family)&metrics.variant.eq('pooled')].set_index('severity').reindex(['mild','moderate','strong'])
        fig,ax=plt.subplots(figsize=(8,4))
        for metric in ['precision','recall','f1','pr_auc','roc_auc']:ax.plot(part.index,part[metric],marker='o',label=metric)
        ax.set(ylim=(0,1.03),title=f'FINAL HELD-OUT TEST — {family}',ylabel='Metric (50% evaluation prevalence for precision/F1/AP)');ax.legend();ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(FIG/f'b0018_{family}_severity.png',dpi=160);plt.close(fig)


def evaluate():
    global UNLOCKED
    config=verify_freeze()
    PROTECTED.update((ROOT/p).resolve() for p in config['hashes'])
    PROTECTED.update([CONFIG.resolve(),(FINAL/'freeze_receipt.json').resolve(),(FINAL/'final_nasa_model.sha256').resolve()])
    OUT.mkdir(parents=True,exist_ok=True)
    # Exclusive marker prevents an accidental repeat of final-test evaluation.
    write_once(OUT/'evaluation_started.json',dict(utc=now(),configuration_sha256=digest(CONFIG),freeze_verified=True))
    before={relative(p):digest(p) for p in PROTECTED}
    UNLOCKED=True
    clean_path=ROOT/'data/processed/nasa/B0018_discharge_features.csv'
    clean=pd.read_csv(clean_path).sort_values('cycle').reset_index(drop=True)
    assert set(clean.cell_id)=={'B0018'} and clean.cycle.tolist()==list(range(1,133))
    source_hash=digest(clean_path)
    bundle=joblib.load(FINAL/'model_bundle.joblib')
    protocol=json.loads((ROOT/'config/anomaly_injection_protocol.json').read_text())
    threshold=config['threshold_value']
    with prohibit_fitting():
        relative_clean=build_relative_features(clean,[10],allowed_cells=('B0018',))
        usable=relative_clean.loc[relative_clean[bundle['features']].notna().all(axis=1)].copy()
        assert usable.cycle.tolist()==list(range(11,133))
        usable['score']=predict(bundle,usable);usable['flagged']=usable.score.gt(threshold)
        temporal=[]
        for name,indices in zip(['early','middle','late'],np.array_split(np.arange(len(usable)),3)):
            part=usable.iloc[indices]
            temporal.append(dict(period=name,first_cycle=int(part.cycle.min()),last_cycle=int(part.cycle.max()),flagged=int(part.flagged.sum()),fpr=float(part.flagged.mean()),**distribution(part.score)))
        copies=[];counts=[]
        for family,spec in protocol['families'].items():
            if family.startswith('A1'):continue
            assert 'measurement_oriented' in spec['feature_sets']
            variants=[(c,s) for c in spec['primary_channels'] for s in [-1,1]] if family.startswith('A4') else [('',0)]
            for severity in ['mild','moderate','strong']:
                for channel,sign in variants:
                    accepted=0;rejections={}
                    for start in range(10,len(clean)-spec.get('window_cycles',5)+1):
                        try:
                            inj=perturb_window(clean,family,severity,start,protocol,channel,sign,authorized_cell='B0018')
                        except ValueError as error:
                            reason=str(error);rejections[reason]=rejections.get(reason,0)+1;continue
                        rel=injected_relative(clean,inj)
                        assert rel[bundle['features']].notna().all().all()
                        copies.append(rel);accepted+=1
                    counts.append(dict(anomaly_family=family,severity=severity,channel=channel or 'joint',drift_sign=sign,accepted_windows=accepted,rejected_windows=sum(rejections.values()),reasons=json.dumps(rejections)))
        all_copies=pd.concat(copies,ignore_index=True)
        all_copies['score']=predict(bundle,all_copies)
    positive=all_copies.loc[all_copies.is_synthetic_anomaly].copy()
    metrics=[];distributions=[dict(anomaly_family='CLEAN',severity='clean',variant='pooled',**distribution(usable.score))]
    for (family,severity),group in positive.groupby(['anomaly_family','severity']):
        variants=[('pooled',group)]
        if family.startswith('A4'):variants += [(f'{c}_{s}',part) for (c,s),part in group.groupby(['channel','drift_sign'])]
        for variant,part in variants:
            record=dict(anomaly_family=family,severity=severity,variant=variant)
            metrics.append(record|evaluation_metrics(usable.score,part.score,[dict(percentile=config['threshold_percentile'],threshold=threshold)])[0])
            distributions.append(record|distribution(part.score))
    metrics=pd.DataFrame(metrics);distributions=pd.DataFrame(distributions);temporal=pd.DataFrame(temporal)
    development=pd.read_csv(ROOT/'results/nasa_relative_features/eligible_anomaly_metrics.csv')
    development=development.loc[development.feature_set.eq('RELATIVE_B')&development.history_window.eq(10)&development.n_estimators.eq(100)&development.max_features.eq(1)&development.seed.eq(42)&development.percentile.eq(config['threshold_percentile'])&development.variant.eq('pooled')]
    dev_scores=pd.read_csv(ROOT/'results/nasa_relative_features/clean_scores.csv')
    dev_scores=dev_scores.loc[dev_scores.feature_set.eq('RELATIVE_B')&dev_scores.history_window.eq(10)&dev_scores.n_estimators.eq(100)&dev_scores.max_features.eq(1)&dev_scores.seed.eq(42)&dev_scores.region.eq('B0007')].sort_values('cycle')
    dev_temporal=[]
    for name,indices in zip(['early','middle','late'],np.array_split(np.arange(len(dev_scores)),3)):
        part=dev_scores.iloc[indices];dev_temporal.append(dict(period=name,first_cycle=int(part.cycle.min()),last_cycle=int(part.cycle.max()),**distribution(part.score)))
    pd.DataFrame(dev_temporal).to_csv(OUT/'development_temporal_scores.csv',index=False)
    usable.to_csv(OUT/'B0018_clean_relative_scores.csv',index=False)
    all_copies.to_csv(OUT/'B0018_synthetic_relative_scores.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    metrics.to_csv(OUT/'anomaly_metrics.csv',index=False);distributions.to_csv(OUT/'score_distributions.csv',index=False)
    temporal.to_csv(OUT/'clean_temporal_statistics.csv',index=False);pd.DataFrame(counts).to_csv(OUT/'injection_window_counts.csv',index=False)
    development.to_csv(OUT/'development_comparison_metrics.csv',index=False)
    figures(usable,positive,metrics,threshold)
    after={relative(p):digest(p) for p in PROTECTED}
    assert before==after and digest(clean_path)==source_hash
    verify_freeze()
    integrity=dict(freeze_preceded_test_access=True,freeze_receipt=json.loads((FINAL/'freeze_receipt.json').read_text()),test_access_log=TEST_READS,configuration_sha256=digest(CONFIG),before_hashes=before,after_hashes=after,all_frozen_artifacts_unchanged=True,source_table_sha256=source_hash,source_table=relative(clean_path),threshold_before=threshold,threshold_after=json.loads(CONFIG.read_text())['threshold_value'],fitting_blocked=True,no_test_rows_in_fitting=all(r['cell_id'] in ['B0005','B0006'] for r in bundle['provenance']['training_ids']),no_test_metrics_in_selection=True,completed_utc=now())
    write_once(OUT/'integrity_receipt.json',integrity)
    pooled=metrics.loc[metrics.variant.eq('pooled')]
    cols=['anomaly_family','severity','precision','recall','f1','pr_auc','roc_auc']
    report=['# NASA final held-out evaluation',
            'The user fixed the predeclared reporting-reference configuration before final-test access. No model, scaler, feature definition, history, threshold, protocol or magnitude was retuned after opening B0018. This report distinguishes development from held-out evidence; synthetic deviations are evaluation-only and are not claimed to be naturally observed faults.',
            '## Freeze and selection',f'RELATIVE_B, 10 prior cycles, 100 trees, max_features=1.0, max_samples=auto, contamination=auto, seed=42. Scaler and model were copied from development, trained on 80 rows (cycles 11–50 from B0005 and B0006). P{config["threshold_percentile"]:g} was the first eligible percentile under the all-three-seed clean B0007 FPR <=5% rule. Exact seed-42 threshold: {threshold!r}. Flag score > threshold; score = −score_samples. No synthetic metric was read for selection.',md_table(pd.DataFrame(config['development_clean_fpr_evidence']),digits=8),
            f'Configuration SHA-256: {digest(CONFIG)}. Freeze receipt was persisted before the first test-source open. The pre-freeze processed source hash covers the development-only snapshot; hashing the combined four-cell CSV before freeze would itself access the locked test data. The B0018 source hash is recorded separately after unlock: {source_hash}. Canonical configuration-payload and complete-file hashes are both recorded; no circular self-hash is claimed.',
            '## DEVELOPMENT RESULTS — B0007',md_table(development[cols]),md_table(pd.DataFrame([distribution(dev_scores.score)])),md_table(pd.DataFrame(dev_temporal)),
            '## FINAL HELD-OUT TEST — B0018',f'Usable clean cycles: {len(usable)} (11–132); first 10 excluded for unavailable history. Flagged: {int(usable.flagged.sum())}; clean FPR: {usable.flagged.mean():.6%}. False-positive cycles: {usable.loc[usable.flagged,"cycle"].tolist()}.',md_table(pd.DataFrame([distribution(usable.score)])),md_table(temporal),
            '### Controlled anomalies',md_table(pooled[cols]),
            'Precision = recall/(recall + clean FPR), corresponding to 50% evaluation prevalence. F1 uses this precision; PR-AUC is class-balanced non-interpolated average precision. ROC-AUC and recall are independent of that balancing. Raw instance metrics are also saved. Clean baseline observations are compared with all accepted synthetic windows; overlapping windows are dependent observations, not independent biological replicates. Zero-offset A4 onset rows are excluded from positive labels. No A1 evaluation applies to RELATIVE_B.',
            'Every synthetic scenario starts after sufficient clean history. Within a scenario, earlier altered observations affect later causal medians/MADs; current/future observations never enter their own baseline. Different scenarios have isolated histories. All original physical guards remain active; rejected windows are logged, without clipping or changing magnitudes.',md_table(pd.DataFrame(counts)),
            '### Score-distribution separation (independent of threshold)',md_table(distributions),
            '## Generalization comparison',md_table(development[cols].merge(pooled[cols],on=['anomaly_family','severity'],suffixes=('_B0007','_B0018'))),
            'Early/middle/late statistics are three nearly equal chronological portions of usable cycles, as declared before test access. Comparisons are descriptive for one held-out cell; no uncertainty claim based on treating overlapping windows as independent samples is made.',
            '## Integrity and outputs','All frozen hashes matched before/after evaluation, including separate scaler/model serializations, original bundle, configuration, feature manifests, protocol, magnitudes and implementation files. Fitting was blocked. The evaluation start marker is exclusive: running the evaluation command again refuses to reopen the test experiment. Tests also exercise write rejection for frozen configuration and clean-only threshold selection.',
            'Artifacts: config/final_nasa_model.json; models/final_nasa/ (bundle, scaler, model, source snapshot and hash receipts); results/nasa_final_test/ (scores, metrics, rejection counts, temporal statistics and integrity receipt); figures/nasa/final_test/ (five requested figures).']
    (ROOT/'results/nasa_final_test.md').write_text('\n\n'.join(report),encoding='utf-8')
    print(json.dumps(dict(usable=len(usable),flagged=int(usable.flagged.sum()),fpr=float(usable.flagged.mean()),cycles=usable.loc[usable.flagged,'cycle'].tolist()),indent=2))
    print(pooled[cols].to_string(index=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['freeze','evaluate']);args=parser.parse_args()
    with prohibit_fitting():
        freeze() if args.stage=='freeze' else evaluate()
