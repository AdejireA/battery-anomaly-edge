"""Phase 4C: prior-only relative features, frozen IF grid, clean-only selection."""

import hashlib
import itertools
import json
import platform

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

try:
    from .nasa_development import (ROOT, read_config, load_development_data, nominal_training, validate_nominal,
                                   feature_matrix, anomaly_scores, clean_training_thresholds, threshold_review)
    from .build_nasa_relative_features import MANIFEST, build_relative_features, save_relative
    from .inject_nasa_anomalies import perturb_window
    from .nasa_burnin import protected_hashes
    from .train_nasa_isolation_forest import md_table, distribution, aggregate_seeds, evaluation_metrics
except ImportError:
    from nasa_development import (ROOT, read_config, load_development_data, nominal_training, validate_nominal,
                                  feature_matrix, anomaly_scores, clean_training_thresholds, threshold_review)
    from build_nasa_relative_features import MANIFEST, build_relative_features, save_relative
    from inject_nasa_anomalies import perturb_window
    from nasa_burnin import protected_hashes
    from train_nasa_isolation_forest import md_table, distribution, aggregate_seeds, evaluation_metrics

OUT = ROOT / 'results/nasa_relative_features'
FIG = ROOT / 'figures/nasa/relative_features'
MODELS = ROOT / 'models/development/relative_features'
KEYS = ['feature_set','history_window','n_estimators','max_features']
ABSOLUTE = {'RELATIVE_A':'degradation_aware', 'RELATIVE_B':'measurement_oriented'}


def fit_relative(nominal, fs, k, trees, mf, seed):
    validate_nominal(nominal)
    config = read_config('nasa_model_development.json')
    if trees not in config['n_estimators'] or mf not in config['max_features'] or seed not in config['seeds']:
        raise ValueError('Outside frozen IF grid')
    features = read_config(MANIFEST)['feature_sets'][str(k)][fs]
    matrix, keep = feature_matrix(nominal, features)
    expected = 2 * (50-k-(4 if fs == 'RELATIVE_A' else 0))
    if len(matrix) != expected:
        raise ValueError(f'Unexpected effective count {len(matrix)}, expected {expected}')
    scaler = StandardScaler()
    transformed = scaler.fit_transform(matrix)
    model = IsolationForest(n_estimators=trees, max_features=mf, max_samples='auto', contamination='auto', random_state=seed, n_jobs=1)
    model.fit(transformed)  # No y; feature whitelist excludes all synthetic labels/metadata.
    provenance = {'status':'DEVELOPMENT_ONLY','feature_set':fs,'history_window':k,'training_rows':len(matrix),
                  'training_ids':nominal.loc[keep,['cell_id','cycle']].to_dict('records'),
                  'training_sha256':hashlib.sha256(matrix.to_csv(index=False,float_format='%.17g').encode()).hexdigest(),
                  'scaler_mean':scaler.mean_.tolist(),'scaler_var':scaler.var_.tolist(),'scaler_scale':scaler.scale_.tolist(),
                  'n_estimators':trees,'max_features':mf,'seed':seed,'features':features}
    return {'scaler':scaler,'model':model,'features':features,'provenance':provenance,'final_threshold':None}


def review_relative(thresholds):
    allowed = KEYS + ['seed','percentile','clean_fpr']
    if set(thresholds.columns) != set(allowed):
        raise ValueError('Only clean FPR/configuration fields permitted in selection')
    result = []
    for key, group in thresholds.groupby(KEYS):
        advice = threshold_review(group[['seed','percentile','clean_fpr']])
        for percentile, rows in group.groupby('percentile'):
            result.append(dict(zip(KEYS,key)) | {'percentile':percentile,'clean_fpr_mean':rows.clean_fpr.mean(),
                                                 'clean_fpr_std':rows.clean_fpr.std(), 'clean_fpr_max':rows.clean_fpr.max(),
                                                 'eligible':bool(rows.clean_fpr.le(.05).all()),
                                                 'recommended_percentile_for_review':advice['recommended_percentile_for_review'],
                                                 'final_threshold':None})
    return pd.DataFrame(result)


def relative_copy(clean, injected, k):
    """Each scenario gets isolated history; preceding synthetic values adapt its baseline.

    Only the injected window is emitted. Prior clean observations are read-only;
    no tail is appended after A1, hence no artificial recovery is introduced.
    """
    start, end = int(injected.source_cycle.min()), int(injected.source_cycle.max())
    context = clean.loc[clean.cycle.between(max(1,start-k),end)].copy().reset_index(drop=True)
    fields = read_config(MANIFEST)['base_features']
    mask = context.cycle.between(start,end)
    context.loc[mask,fields] = injected[fields].to_numpy()
    result = build_relative_features(context, [k])
    result = result.loc[result.cycle.between(start,end)].reset_index(drop=True)
    for column in injected.columns:
        # Preserve full altered raw rows/provenance, including companion temperature fields.
        result[column] = injected[column].to_numpy()
    return result


def generate_relative_copies(clean,k,applicable_sets,protocol):
    """Only start scenarios when the relevant model has sufficient causal history."""
    outputs, counts = [], []
    for family,spec in protocol['families'].items():
        sets = [fs for fs in applicable_sets if ABSOLUTE[fs] in spec['feature_sets']]
        if not sets:
            continue
        # Generate union of eligible sources. Model-specific complete-case filtering
        # below requires a full usable window, never a partial injected segment.
        minimum = min(k + (4 if fs=='RELATIVE_A' else 0) for fs in sets)
        if family.startswith('A1'):
            minimum = max(minimum,4)
        variants = [(c,s) for c in spec['primary_channels'] for s in [-1,1]] if family.startswith('A4') else [('',0)]
        for severity in spec['severity']:
            for channel,sign in variants:
                accepted,rejected=0,0
                for start in range(minimum, len(clean)-spec.get('window_cycles',5)+1):
                    try:
                        injection=perturb_window(clean,family,severity,start,protocol,channel,sign)
                    except ValueError:
                        rejected+=1
                        continue
                    outputs.append(relative_copy(clean,injection,k))
                    accepted+=1
                counts.append(dict(history_window=k,anomaly_family=family,severity=severity,channel=channel or 'joint',
                                   drift_sign=sign,first_start_cycle=minimum+1,accepted_windows=accepted,rejected_windows=rejected))
    return pd.concat(outputs,ignore_index=True),pd.DataFrame(counts)


def shifts_and_numerics(relative, manifest):
    rows,numeric=[] , []
    nominal=nominal_training(relative)
    clean=relative.loc[relative.cell_id.eq('B0007')]
    for k in manifest['history_windows']:
        for fs,features in manifest['feature_sets'][str(k)].items():
            train,_=feature_matrix(nominal,features)
            validation,keep=feature_matrix(clean,features)
            for feature in features:
                a,b=train[feature],validation[feature]
                ma=(a-a.median()).abs().median(); mb=(b-b.median()).abs().median()
                rows.append(dict(feature_set=fs,history_window=k,feature=feature,training_median=a.median(),validation_median=b.median(),
                                 training_MAD=ma,validation_MAD=mb,median_shift=b.median()-a.median(),
                                 standardized_shift=(b.median()-a.median())/ma if ma>0 else np.nan))
                base=feature.replace(f'_prior{k}_robust_residual','')
                for region,frame in [('training',nominal.loc[train.index]),('B0007',clean.loc[keep])]:
                    numeric.append(dict(feature_set=fs,history_window=k,feature=feature,region=region,
                                        zero_history_mad=int(frame[f'{base}_prior{k}_mad'].eq(0).sum()),
                                        max_absolute_robust_residual=float(frame[feature].abs().max())))
    shifts=pd.DataFrame(rows)
    shifts['absolute_standardized_shift']=shifts.standardized_shift.abs()
    return shifts.sort_values(['feature_set','history_window','absolute_standardized_shift'],ascending=[True,True,False]),pd.DataFrame(numeric)


def make_figures(relative, thresholds, scores, shifts, drift, manifest):
    FIG.mkdir(parents=True,exist_ok=True)
    reference=scores.loc[scores.n_estimators.eq(100)&scores.max_features.eq(1.0)&scores.region.eq('B0007')]
    fig,axes=plt.subplots(1,2,figsize=(13,4.5))
    old=pd.read_csv(ROOT/'results/nasa_model_validation/clean_scores.csv')
    if not set(old.cell_id).issubset({'B0007'}):raise ValueError('Unexpected absolute score source')
    for ax,fs in zip(axes,['RELATIVE_A','RELATIVE_B']):
        abs_rows=old.loc[old.feature_set.eq(ABSOLUTE[fs])&old.n_estimators.eq(100)&old.max_features.eq(1.0)]
        mean=abs_rows.groupby('cycle').anomaly_score.mean()
        ax.plot(mean.index,mean,linestyle='--',color='black',label='Absolute reference')
        for k,part in reference.loc[reference.feature_set.eq(fs)].groupby('history_window'):
            values=part.groupby('cycle').score.agg(['mean','std'])
            ax.plot(values.index,values['mean'],label=f'Prior {k}')
            ax.fill_between(values.index,values['mean']-values['std'],values['mean']+values['std'],alpha=.12)
        ax.set(title=fs,xlabel='B0007 cycle',ylabel='Anomaly score (model-specific scale)')
        ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('100 trees / max_features=1.0, seed mean; within-model drift is the relevant comparison')
    fig.tight_layout();fig.savefig(FIG/'absolute_vs_relative_score_drift.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(16,8))
    for row,fs in enumerate(['RELATIVE_A','RELATIVE_B']):
        for col,k in enumerate(manifest['history_windows']):
            ax=axes[row,col];part=shifts.loc[shifts.feature_set.eq(fs)&shifts.history_window.eq(k)].iloc[::-1]
            labels=part.feature.str.replace(f'_prior{k}_robust_residual','',regex=False)
            ax.barh(labels,part.standardized_shift);ax.axvline(0,color='black',linewidth=.7)
            ax.set(title=f'{fs}, prior {k}',xlabel='Median shift / training MAD');ax.tick_params(axis='y',labelsize=7)
    fig.tight_layout();fig.savefig(FIG/'relative_feature_shift_summary.png',dpi=160);plt.close(fig)
    summary=aggregate_seeds(thresholds,KEYS+['percentile'],['clean_fpr'])
    fig,axes=plt.subplots(2,3,figsize=(14,8),sharey=True)
    for row,fs in enumerate(['RELATIVE_A','RELATIVE_B']):
        for col,p in enumerate([95.,97.5,99.]):
            ax=axes[row,col]
            for (trees,mf),part in summary.loc[summary.feature_set.eq(fs)&summary.percentile.eq(p)].groupby(['n_estimators','max_features']):
                ax.errorbar(part.history_window,part.clean_fpr_mean,yerr=part.clean_fpr_std,marker='o',capsize=3,label=f'{trees}, features={mf}')
            ax.axhline(.05,color='red',linestyle='--',label='5% tolerance')
            ax.set(title=f'{fs}, train P{p:g}',xlabel='Prior history cycles',ylabel='Clean B0007 FPR');ax.set_xticks([5,10,20]);ax.grid(alpha=.2)
            if col==0:ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(FIG/'clean_fpr_by_history_window.png',dpi=160);plt.close(fig)
    clean=relative.loc[relative.cell_id.eq('B0007')]
    for base in ['duration_s','time_to_3_4v_s','delta_temp_c','capacity_retention']:
        fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
        axes[0].plot(clean.cycle,clean[base],color='black',label='Raw current observation')
        for k in manifest['history_windows']:
            axes[0].plot(clean.cycle,clean[f'{base}_prior{k}_median'],label=f'Prior {k} median',alpha=.8)
            axes[1].plot(clean.cycle,clean[f'{base}_prior{k}_robust_residual'],label=f'Prior {k}',alpha=.8)
        axes[0].set(title=f'B0007 {base}',ylabel='Base feature units');axes[1].set(xlabel='Discharge cycle',ylabel='Robust residual')
        for ax in axes:ax.legend(fontsize=8);ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(FIG/f'trajectory_{base}.png',dpi=160);plt.close(fig)


def main():
    before=protected_hashes()
    manifest=read_config(MANIFEST);config=read_config('nasa_model_development.json');protocol=read_config('anomaly_injection_protocol.json')
    OUT.mkdir(parents=True,exist_ok=True);MODELS.mkdir(parents=True,exist_ok=True)
    data=load_development_data();relative=save_relative(data)
    nominal=nominal_training(relative);clean=relative.loc[relative.cell_id.eq('B0007')].reset_index(drop=True)
    original_clean=data.loc[data.cell_id.eq('B0007')].reset_index(drop=True)
    shifts,numerics=shifts_and_numerics(relative,manifest)
    shifts.to_csv(OUT/'relative_feature_shifts.csv',index=False);numerics.to_csv(OUT/'denominator_diagnostics.csv',index=False)
    thresholds,score_rows,distributions,drifts,provenances,counts=[],[],[],[],[],[]
    absolute=pd.read_csv(ROOT/'results/nasa_model_validation/clean_scores.csv')
    if set(absolute.cell_id)!={'B0007'}:raise ValueError('Unexpected source in absolute comparison')
    for k,fs,trees,mf,seed in itertools.product(manifest['history_windows'],['RELATIVE_A','RELATIVE_B'],config['n_estimators'],config['max_features'],config['seeds']):
        info=dict(feature_set=fs,history_window=k,n_estimators=trees,max_features=mf,seed=seed)
        bundle=fit_relative(nominal,fs,k,trees,mf,seed)
        ts=clean_training_thresholds(bundle,nominal)
        train_score,_=anomaly_scores(bundle,nominal);validation_score,keep=anomaly_scores(bundle,clean)
        for t in ts:thresholds.append(dict(info,**t,clean_fpr=float((validation_score>t['threshold']).mean()),validation_rows=len(validation_score)))
        for region,frame,scores in [('training',nominal,train_score),('B0007',clean,validation_score)]:
            distributions.append(dict(info,region=region,**distribution(scores)))
            for index,value in scores.items():score_rows.append(dict(info,region=region,cell_id=frame.loc[index,'cell_id'],cycle=int(frame.loc[index,'cycle']),score=value))
        eligible_cycles=clean.loc[keep,'cycle']
        old=absolute.loc[absolute.feature_set.eq(ABSOLUTE[fs])&absolute.n_estimators.eq(trees)&absolute.max_features.eq(mf)&absolute.seed.eq(seed)&absolute.cycle.isin(eligible_cycles)]
        current=pd.DataFrame({'cycle':eligible_cycles.to_numpy(),'score':validation_score.to_numpy()})
        for representation,frame,column in [('relative',current,'score'),('absolute_matched_cycles',old,'anomaly_score')]:
            early=frame.loc[frame.cycle<=50,column];late=frame.loc[frame.cycle>50,column]
            drifts.append(dict(info,representation=representation,early_count=len(early),late_count=len(late),
                               early_mean=early.mean(),late_mean=late.mean(),late_minus_early=late.mean()-early.mean()))
        bundle['threshold_candidates']=ts
        joblib.dump(bundle,MODELS/f'DEVELOPMENT_{fs}_k{k}_trees{trees}_features{mf}_seed{seed}.joblib',compress=3)
        provenances.append(bundle['provenance'])
        if trees==100 and mf==.75 and seed==42:counts.append(dict(feature_set=fs,history_window=k,training_rows=len(train_score),per_training_cell=len(train_score)//2,validation_rows=len(validation_score)))
        print(f'{fs} prior{k}: trees={trees}, features={mf}, seed={seed}; training={len(train_score)}, validation={len(validation_score)}',flush=True)
    thresholds=pd.DataFrame(thresholds);scores=pd.DataFrame(score_rows);drift=pd.DataFrame(drifts)
    reviews=review_relative(thresholds[KEYS+['seed','percentile','clean_fpr']]);eligible=reviews.loc[reviews.eligible]
    stability=aggregate_seeds(thresholds,KEYS+['percentile'],['threshold','clean_fpr'])
    drift_stability=aggregate_seeds(drift,KEYS+['representation'],['early_mean','late_mean','late_minus_early'])
    for name,frame in [('thresholds',thresholds),('clean_scores',scores),('score_distributions',pd.DataFrame(distributions)),('score_drift',drift),('score_drift_seed_stability',drift_stability),('threshold_seed_stability',stability),('eligibility_review',reviews),('eligible_configurations',eligible),('sample_counts',pd.DataFrame(counts))]:frame.to_csv(OUT/f'{name}.csv',index=False)
    (OUT/'training_provenance.json').write_text(json.dumps(provenances,indent=2)+'\n')
    # Gating is complete and saved before any synthetic generation or scoring.
    metrics,window_counts=[],[]
    for k in eligible.history_window.unique():
        applicable=eligible.loc[eligible.history_window.eq(k),'feature_set'].unique()
        synthetic,windows=generate_relative_copies(original_clean,int(k),applicable,protocol)
        window_counts.append(windows)
        synthetic.to_csv(OUT/f'B0007_relative_injected_prior{k}.csv.gz',index=False,compression={'method':'gzip','mtime':0})
        for key,group in eligible.loc[eligible.history_window.eq(k)].groupby(KEYS):
            fs,k,trees,mf=key
            for seed in config['seeds']:
                bundle=joblib.load(MODELS/f'DEVELOPMENT_{fs}_k{k}_trees{trees}_features{mf}_seed{seed}.joblib')
                allowed=[f for f,s in protocol['families'].items() if ABSOLUTE[fs] in s['feature_sets']]
                source=synthetic.loc[synthetic.anomaly_family.isin(allowed)]
                # Entire scenario must have usable model history at onset.
                complete=source[bundle['features']].notna().all(axis=1).groupby(source.scenario_id).all()
                source=source.loc[source.scenario_id.isin(complete.index[complete])&source.is_synthetic_anomaly]
                positive,keep=anomaly_scores(bundle,source);source=source.loc[keep].copy();source['score']=positive
                negative,_=anomaly_scores(bundle,clean)
                selected=thresholds.loc[(thresholds.feature_set==fs)&(thresholds.history_window==k)&(thresholds.n_estimators==trees)&(thresholds.max_features==mf)&(thresholds.seed==seed)&thresholds.percentile.isin(group.percentile)]
                for (family,severity),part in source.groupby(['anomaly_family','severity']):
                    variants=[('pooled',part)]
                    if family.startswith('A4'):variants += [(f'{ch}_{sign}',sub) for (ch,sign),sub in part.groupby(['channel','drift_sign'])]
                    for variant,subset in variants:
                        for values in evaluation_metrics(negative,subset.score,selected[['percentile','threshold']].to_dict('records')):
                            metrics.append(dict(feature_set=fs,history_window=k,n_estimators=trees,max_features=mf,seed=seed,anomaly_family=family,severity=severity,variant=variant,**values))
        print(f'Completed eligible synthetic evaluation for prior{k}',flush=True)
    metric_columns=KEYS+['seed','anomaly_family','severity','variant','percentile','threshold','precision','recall','f1','clean_fpr','pr_auc','roc_auc','raw_precision','raw_f1','raw_pr_auc','clean_rows','synthetic_rows']
    metrics=pd.DataFrame(metrics,columns=metric_columns);metrics.to_csv(OUT/'eligible_anomaly_metrics.csv',index=False)
    if len(metrics):
        aggregate_seeds(metrics,KEYS+['anomaly_family','severity','variant','percentile'],['precision','recall','f1','pr_auc','roc_auc']).to_csv(OUT/'eligible_anomaly_seed_stability.csv',index=False)
    if window_counts:pd.concat(window_counts).to_csv(OUT/'injection_window_counts.csv',index=False)
    make_figures(relative,thresholds,scores,shifts,drift,manifest)
    report(manifest,counts,stability,drift_stability,shifts,numerics,eligible,metrics,pd.DataFrame(distributions))
    if protected_hashes()!=before:raise AssertionError('Frozen/source/absolute-model artifact changed')
    (OUT/'run_integrity.json').write_text(json.dumps({'protected_sha256':before,'unchanged':True,'python':platform.python_version(),
                                                  'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,
                                                  'relative_models':72,'eligible_configurations':len(eligible),'test_cell_accessed':False,
                                                  'final_model':None,'final_threshold':None,
                                                  'new_source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'config'/MANIFEST,ROOT/'scripts/build_nasa_relative_features.py',ROOT/'scripts/validate_nasa_relative_features.py']}},indent=2)+'\n')
    print(stability.groupby(['feature_set','history_window','percentile']).clean_fpr_mean.agg(['min','max']).to_string())
    print(f'Eligible combinations: {len(eligible)}; no finalization; test cell untouched.')


def report(manifest,counts,stability,drift,shifts,numerics,eligible,metrics,distributions):
    reference=stability.loc[stability.n_estimators.eq(100)&stability.max_features.eq(1.)]
    reference_drift=drift.loc[drift.n_estimators.eq(100)&drift.max_features.eq(1.)]
    if len(metrics):
        metric_summary=aggregate_seeds(metrics,KEYS+['anomaly_family','severity','variant','percentile'],['precision','recall','f1','pr_auc','roc_auc'])
        displayed=metric_summary.loc[metric_summary.n_estimators.eq(100)&metric_summary.max_features.eq(1.)&metric_summary.percentile.eq(97.5)&metric_summary.variant.eq('pooled')]
    else:
        displayed=pd.DataFrame()
    parts=['# Phase 4C causal trajectory-relative feature validation',
           'DEVELOPMENT ONLY. Only individual B0005/B0006/B0007 processed files are loaded. Original data, frozen absolute feature sets, injection protocol and previous models are preserved. No per-cell burn-in is used.',
           '## Findings for review',
           f'{len(eligible)} of 72 configuration/window/threshold combinations meet <=5% clean B0007 FPR for every seed. This demonstrates improved clean transfer on this validation cell, not a final fault detector or test-cell generalization result.',
           'In the reporting reference (100 trees, max_features=1.0), matched-cycle late-minus-early score drift changes from approximately +0.126 to +0.153 for absolute models to -0.039 to -0.014 for relative models. Drift magnitude is reduced but not eliminated; the small negative drift is also a change in score distribution.',
           'Sensitivity trade-off: A1 is mostly absorbed by the adaptive trajectory baseline, with near-chance ranking and very low recall. A4 remains weak at eligible thresholds even where its ranking improves. A2 is much better ranked at 10/20-cycle histories, and A3 ranking improves with severity, but high PR-AUC does not imply high recall at the clean-only threshold. No configuration is chosen using these metrics.',
           'After normalization the largest absolute robust standardized feature-median shift is below 1 (about 0.946 for duration, RELATIVE_B/prior20). This uses the full usable B0007 distribution, so it is not directly comparable with the earlier early-life-only shift audit. There are no zero-MAD windows in the clean model-eligible samples, but the prior5 current residual reaches about 1,140 from a very small nonzero local MAD; it is retained without clipping.',
           '## Feature definition and causality',
           'For each base feature x and k=5/10/20, baseline median and raw MAD use exactly cycles t-k through t-1 from the same cell. The current cycle is excluded. Residual=x_t-median; robust residual=residual/(1.4826*MAD+1e-9). Epsilon is 1e-9 in the base feature units, solely a zero-denominator guard; no clipping or imputation. Every prior window entry must be available. Current capacity_slope_5 itself is causal and includes the current discharge; its historical baseline excludes it. Its unstandardized residual is saved as capacity_slope_change_prior{k}_ah_per_cycle; RELATIVE_A uses the robust slope residual. No absolute values enter model features.',
           'Relative sets are in `config/nasa_relative_feature_manifest.json`. Separate processed output is `data/processed/nasa_relative/` (504 development observations retaining all original columns).',
           '## Training/evaluation counts',md_table(pd.DataFrame(counts)),
           'First 50 cycles per training cell define the nominal region before dropping initial history NaNs. RELATIVE_A starts at cycle k+5 because capacity_slope_5 has four initial NaNs; RELATIVE_B starts at k+1. StandardScaler and IsolationForest fit only complete nominal training features, without labels. Grid remains 100/200 trees x 0.75/1.0 max_features x seeds 42/123/2026, max_samples=auto, contamination=auto (72 models across six representations).',
           '## Clean-only thresholds and eligibility',
           'Higher score=-score_samples. P95/P97.5/P99 are linear percentiles of clean nominal TRAINING scores only; strict score>threshold is anomalous. These are in-sample calibration distributions, not calibrated transfer guarantees. A configuration/percentile is eligible only if clean B0007 FPR <=5% for every seed. No synthetic metric is used to choose history, feature set, model or threshold. No automatic final model/threshold.',
           f'Eligible configuration/window/percentile combinations: {len(eligible)}.',
           md_table(eligible) if len(eligible) else 'No representation satisfies the all-seed requirement; synthetic evaluation is withheld and failure is reported without final-test access.',
           '### Predeclared display reference: 100 trees, max_features=1.0',md_table(reference),
           '### Full-grid seed means and sample SD',md_table(stability),
           '## Early-to-late clean score drift',
           'Early=usable cycles <=50; late=cycles >50. Absolute counterparts are compared on exactly the same usable cycles per history window and seed/configuration. For RELATIVE_B the absolute measurement-oriented set includes start_temp while relative B does not (as requested), so this is not a perfectly controlled change-of-representation ablation. Score scales differ across models; compare within-model late-minus-early changes, not raw score levels as calibrated probabilities. Shorter trajectories and different nominal sample sizes can also affect models.',
           md_table(reference_drift),
           'Full matched-cycle drift comparisons: score_drift.csv and score_drift_seed_stability.csv.',
           '## Cross-cell shift after normalization',
           'Training nominal distribution versus ALL usable clean B0007, not only early B0007. Raw training MAD defines standardized median shift; zero MAD produces NaN. Complete-case eligibility is feature-set-specific.',
           md_table(shifts),
           '## Numerical diagnostics',
           'Zero local MAD can create extreme robust residuals because epsilon is not a statistically meaningful scale floor. These values are not clipped; denominator_diagnostics.csv reports affected counts and maxima. This limitation can distort StandardScaler and is not silently corrected using validation labels.',md_table(numerics),
           '## Training and clean validation score distributions',md_table(distributions),
           '## Controlled deviations: eligible configurations only',
           'Each frozen window is injected into a fresh isolated copy. Its preceding clean k-cycle context is included only for baseline calculation. Within an A1/A4 sequence, earlier altered observations enter subsequent prior baselines, so sustained deviations can be adapted away; the current observation never enters its own baseline. The baseline is NOT frozen at pre-event values. No synthetic baseline is shared across unrelated copies. A1 derives altered slopes from its own capacity history; only the ramp is evaluated and no recovery tail is added. A2/A3 prior injected samples also enter later window baselines. Scenario onset must have sufficient model history; whole unusable windows are excluded. Zero-offset onset rows remain negative and are not counted as synthetic positives.',
           'A1 is applicable only to RELATIVE_A. Severity magnitudes/durations are frozen and unchanged. Metrics use the established equal-class-weight 50% evaluation prevalence; PR-AUC means average precision. ROC-AUC is reported where both classes exist. Repeated overlapping windows are dependent, not independent trials. No synthetic F1 optimization.',
           '### Eligible reference results, P97.5 (display convention only; not a selected threshold)',
           md_table(displayed) if len(displayed) else 'No eligible reference rows at this display percentile.',
           'The display uses all eligible history windows for the predeclared 100-tree/max_features=1.0 reference. RELATIVE_B/prior5/P97.5 is not shown because it fails the all-seed clean-FPR gate despite its mean being below 5%. Full results for every eligible configuration, seed, family, severity, threshold and A4 channel/sign are in `results/nasa_relative_features/eligible_anomaly_metrics.csv`; cross-seed means and sample SD are in `eligible_anomaly_seed_stability.csv`. Precision/F1/AP use 50% evaluation prevalence, not a real deployment prevalence.',
           '## Artifacts',
           'Detailed results: `results/nasa_relative_features/`. DEVELOPMENT models: `models/development/relative_features/`. Figures: `figures/nasa/relative_features/`. Reproduce with `scripts/validate_nasa_relative_features.py`; standalone builder: `scripts/build_nasa_relative_features.py`. No final-test evaluation or deployment.']
    (ROOT/'results/nasa_relative_feature_validation.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')


if __name__=='__main__':main()
