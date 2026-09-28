"""Read-only Phase 4C diagnostics. Writes only a new report, tables and figures."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import itertools
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/nasa_failure_analysis'
FIG = ROOT / 'figures/nasa/failure_analysis'
REPORT = ROOT / 'results/nasa_failure_analysis.md'
READS = set()


def access_guard(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    if not path.is_relative_to(ROOT):
        return
    rel = path.relative_to(ROOT).as_posix()
    if 'b0018' in rel.lower() or rel == 'data/processed/nasa/nasa_discharge_features.csv' or rel.startswith('data/raw/'):
        raise RuntimeError('Forbidden data access')
    flags = args[2] if isinstance(args[2], int) else 0
    writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if writing and not (path.is_relative_to(OUT) or path.is_relative_to(FIG) or path == REPORT):
        raise RuntimeError(f'Experimental artifact write forbidden: {rel}')
    if not writing and not rel.startswith('.venv/'):
        READS.add(rel)


sys.addaudithook(access_guard)
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from nasa_burnin import prohibit_fitting

SOURCE = ROOT / 'results/nasa_relative_features'
KEYS = ['feature_set', 'history_window', 'n_estimators', 'max_features']
SEEDS = [42, 123, 2026]


def hashes():
    paths = list((ROOT / 'models/development').rglob('*.joblib'))
    paths += list((ROOT / 'config').glob('*.json'))
    paths += list(SOURCE.glob('*'))
    for cell in ['B0005', 'B0006', 'B0007']:
        paths += [ROOT / f'data/processed/nasa/{cell}_discharge_features.csv',
                  ROOT / f'data/processed/nasa_relative/{cell}_relative_features.csv']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def table(df):
    if df.empty:
        return '(No rows.)'
    f = df.copy()
    for c in f.select_dtypes(include='number'):
        f[c] = f[c].map(lambda v: f'{v:.5g}')
    return '| ' + ' | '.join(f.columns) + ' |\n|' + '|'.join(['---']*len(f.columns)) + '|\n' + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in f.itertuples(index=False, name=None))


def model(fs, k, trees=100, mf=1.0, seed=42):
    return joblib.load(ROOT / f'models/development/relative_features/DEVELOPMENT_{fs}_k{k}_trees{trees}_features{mf}_seed{seed}.joblib')


def score(bundle, frame):
    x = frame[bundle['features']]
    assert x.notna().all().all()
    return -bundle['model'].score_samples(bundle['scaler'].transform(x))


def valid(frame, bundle):
    ok = frame[bundle['features']].notna().all(axis=1)
    if 'scenario_id' in frame:
        ok = ok.groupby(frame.scenario_id).transform('all')
    return frame.loc[ok].copy()


def summarize(values, prefix):
    return {prefix+'_'+n: float(v) for n,v in zip(['p05','median','p95'],np.percentile(values,[5,50,95]))} | {prefix+'_mean':float(np.mean(values)), prefix+'_std':float(np.std(values,ddof=1))}


def adaptation(clean, copies):
    rows, trajectories = [], []
    shared = set.intersection(*(set(d.scenario_id) for d in copies.values()))
    for k, data in copies.items():
        data = data.loc[data.scenario_id.isin(shared) & data.anomaly_family.str.startswith(('A1','A4'))]
        for scenario, g in data.groupby('scenario_id', sort=False):
            g = g.sort_values('offset_in_window')
            c = clean.loc[g.source_cycle].reset_index(drop=True)
            g = g.reset_index(drop=True)
            bases = ['capacity_retention','capacity_slope_5'] if g.anomaly_family.iloc[0].startswith('A1') else [g.channel.iloc[0]]
            for base in bases:
                pre = f'{base}_prior{k}_'
                raw_delta = g[base]-c[base]
                residual_delta = g[pre+'residual']-c[pre+'residual']
                z_delta = g[pre+'robust_residual']-c[pre+'robust_residual']
                baseline_delta = g[pre+'median']-c[pre+'median']
                ratio = residual_delta / raw_delta.where(raw_delta.abs()>1e-12)
                # Diagnostic clean range, NOT a new decision threshold.
                lo, hi = clean[pre+'robust_residual'].dropna().quantile([.05,.95])
                outside = ((g[pre+'robust_residual']<lo)|(g[pre+'robust_residual']>hi)).to_numpy()
                excursion = np.flatnonzero(outside)
                returned = np.nan
                if len(excursion):
                    for j in range(excursion[0]+1,len(g)-2):
                        if not outside[j:j+3].any():
                            returned = j-int(excursion[0]); break
                stable_return = np.nan
                if len(excursion):
                    for j in range(excursion[0]+1,len(g)-2):
                        if not outside[j:].any():
                            stable_return=j-int(excursion[0]);break
                info = dict(history_window=k,scenario_id=scenario,anomaly_family=g.anomaly_family.iloc[0],severity=g.severity.iloc[0],channel=g.channel.iloc[0],drift_sign=g.drift_sign.iloc[0],base_feature=base,window_start_cycle=int(g.source_cycle.iloc[0]))
                rows.append(info | dict(window_cycles=len(g),raw_effect_final=raw_delta.iloc[-1],raw_effect_peak=raw_delta.abs().max(),residual_effect_first=residual_delta.iloc[0],residual_effect_peak=residual_delta.abs().max(),residual_effect_final=residual_delta.iloc[-1],z_effect_peak=z_delta.abs().max(),z_effect_final=z_delta.iloc[-1],remaining_fraction_final=ratio.iloc[-1],absorbed_percent_final=100*(1-ratio.iloc[-1]),mad_ratio_final=g[pre+'mad'].iloc[-1]/c[pre+'mad'].iloc[-1],ever_outside_clean_p05_p95=bool(len(excursion)),return_cycles_after_first_excursion=returned,return_observed=bool(np.isfinite(returned)),injected_z_final=g[pre+'robust_residual'].iloc[-1],clean_z_final=c[pre+'robust_residual'].iloc[-1]))
                rows[-1].update(injected_residual_first=g[pre+'residual'].iloc[0],injected_residual_peak_abs=g[pre+'residual'].abs().max(),injected_residual_final=g[pre+'residual'].iloc[-1],stable_return_cycles=stable_return,stable_return_observed=bool(np.isfinite(stable_return)),onset_already_outside=bool(outside[0]))
                for j in range(len(g)):
                    trajectories.append(info | dict(offset=j,raw_effect=raw_delta.iloc[j],residual_effect=residual_delta.iloc[j],z_effect=z_delta.iloc[j],baseline_effect=baseline_delta.iloc[j],absorbed_percent=100*(1-ratio.iloc[j])))
    return pd.DataFrame(rows),pd.DataFrame(trajectories)


def plot_adaptation(clean, copies, thresholds, severity='strong'):
    # Fixed source onset 50, fixed reference 100 trees / full features / seed 42.
    # This is an illustration, not a model/configuration selection.
    for family, filename, fs in [('A1','a1_baseline_absorption.png','RELATIVE_A'),('A4','a4_drift_absorption.png','RELATIVE_B')]:
        if family=='A4' and severity!='strong':continue
        if severity!='strong':filename=filename.replace('.png',f'_{severity}.png')
        if family=='A1':
            fig,axes=plt.subplots(8,3,figsize=(17,25))
            cases=[('capacity_retention','capacity_slope_5')]*3
            columns=[5,10,20]
        else:
            fig,axes=plt.subplots(4,6,figsize=(24,13))
            columns=[5,10,20,5,10,20]
            cases=[('mean_voltage_v',)]*3+[('mean_temp_c',)]*3
        for col,(k,bases) in enumerate(zip(columns,cases)):
            d=copies[k]
            mask=d.anomaly_family.str.startswith(family)&d.window_start_cycle.eq(50)&d.severity.eq(severity)
            if family=='A4':mask &= d.channel.eq(bases[0])&d.drift_sign.eq(1)
            g=d.loc[mask].sort_values('offset_in_window')
            assert g.scenario_id.nunique()==1
            c=clean.loc[g.source_cycle]
            x=g.offset_in_window.to_numpy()
            for b,base in enumerate(bases):
                pre=f'{base}_prior{k}_'; r=b*3
                axes[r,col].plot(x,c[base],label='clean');axes[r,col].plot(x,g[base],label='injected')
                axes[r,col].plot(x,g[pre+'median'],'--',label='injected prior median')
                axes[r,col].plot(x,c[pre+'median'],':',label='clean prior median')
                axes[r,col].set_title(f'{base}, k={k}')
                axes[r+1,col].plot(x,c[pre+'residual'],label='clean residual')
                axes[r+1,col].plot(x,g[pre+'residual'],label='injected residual');axes[r+1,col].set_ylabel('Residual (base units)')
                axes[r+2,col].plot(x,c[pre+'robust_residual'],label='clean z')
                axes[r+2,col].plot(x,g[pre+'robust_residual'],label='injected z');axes[r+2,col].set_ylabel('Robust residual z')
            bundle=model(fs,k)
            ax=axes[6 if family=='A1' else 3,col]
            ax.plot(x,score(bundle,c),label='clean score');ax.plot(x,score(bundle,g),label='injected score')
            tt=thresholds.loc[thresholds.feature_set.eq(fs)&thresholds.history_window.eq(k)&thresholds.n_estimators.eq(100)&thresholds.max_features.eq(1)&thresholds.seed.eq(42)]
            for _,t in tt.iterrows():ax.axhline(t.threshold,ls=':',alpha=.5,label=f'existing P{t.percentile:g}')
            ax.set_ylabel('Anomaly score')
            if family=='A1':
                raw=g.capacity_retention.to_numpy()-c.capacity_retention.to_numpy()
                rem=g[f'capacity_retention_prior{k}_residual'].to_numpy()-c[f'capacity_retention_prior{k}_residual'].to_numpy()
                axes[7,col].plot(x,100*(1-np.divide(rem,raw,out=np.full_like(raw,np.nan),where=np.abs(raw)>1e-12)))
                axes[7,col].set_ylabel('Retention effect absorbed (%)')
        for ax in axes.flat:
            if ax.get_legend_handles_labels()[0]:ax.legend(fontsize=6)
            ax.grid(alpha=.2);ax.set_xlabel('Offset from source cycle 50')
        fig.suptitle(f'{family} {severity}: saved independent scenario; reference model only',fontsize=15)
        fig.tight_layout(rect=(0,0,1,.98));fig.savefig(FIG/filename,dpi=140);plt.close(fig)


def seed_analysis(clean,copies,eligible,thresholds):
    rows,corrs,plotdata=[],[],{}
    configurations=eligible.loc[eligible.feature_set.eq('RELATIVE_B')&eligible.history_window.eq(10)]
    for (trees,mf),config in configurations.groupby(['n_estimators','max_features']):
        for family in ['A2','A3']:
            for severity in ['mild','moderate','strong']:
                d=copies[10]
                d=d.loc[d.anomaly_family.str.startswith(family)&d.severity.eq(severity)]
                store={}
                for seed in SEEDS:
                    bundle=model('RELATIVE_B',10,int(trees),mf,seed)
                    c=valid(clean,bundle);g=valid(d,bundle)
                    g=g.loc[g.is_synthetic_anomaly].sort_values(['scenario_id','source_cycle'])
                    cs=score(bundle,c);ss=score(bundle,g)
                    store[seed]=(cs,ss)
                    if trees==100 and mf==1 and family=='A2':plotdata[(severity,seed)]=(cs,ss)
                    tt=thresholds.loc[thresholds.feature_set.eq('RELATIVE_B')&thresholds.history_window.eq(10)&thresholds.n_estimators.eq(trees)&thresholds.max_features.eq(mf)&thresholds.seed.eq(seed)&thresholds.percentile.isin(config.percentile)]
                    for _,t in tt.iterrows():
                        rows.append(dict(n_estimators=trees,max_features=mf,seed=seed,anomaly_family=family,severity=severity,percentile=t.percentile,threshold=t.threshold,clean_rows=len(cs),synthetic_rows=len(ss),recall=float(np.mean(ss>t.threshold)),clean_fpr=float(np.mean(cs>t.threshold)),threshold_clean_percentile=100*float(np.mean(cs<=t.threshold)),threshold_synthetic_percentile=100*float(np.mean(ss<=t.threshold)),threshold_clean_z=(t.threshold-np.median(cs))/np.std(cs,ddof=1),synthetic_within_001_threshold=float(np.mean(np.abs(ss-t.threshold)<=.01)),synthetic_in_clean_p05_p95=float(np.mean((ss>=np.percentile(cs,5))&(ss<=np.percentile(cs,95)))),**summarize(cs,'clean'),**summarize(ss,'synthetic')))
                for a,b in itertools.combinations(SEEDS,2):
                    for region,idx in [('clean',0),('synthetic',1),('pooled',2)]:
                        x=store[a][idx] if idx<2 else np.concatenate(store[a]);y=store[b][idx] if idx<2 else np.concatenate(store[b])
                        corrs.append(dict(n_estimators=trees,max_features=mf,anomaly_family=family,severity=severity,seed_a=a,seed_b=b,region=region,spearman=float(spearmanr(x,y).statistic)))
    return pd.DataFrame(rows),pd.DataFrame(corrs),plotdata


def seed_plots(detail,plotdata):
    fig,axes=plt.subplots(2,2,figsize=(14,9))
    for i,sev in enumerate(['moderate','strong']):
        for seed in SEEDS:
            cs,ss=plotdata[(sev,seed)]
            for ax,values in [(axes[i,0],cs),(axes[i,1],ss)]:
                v=np.sort(values);ax.plot(v,np.arange(1,len(v)+1)/len(v),label=str(seed))
            t=detail.loc[detail.n_estimators.eq(100)&detail.max_features.eq(1)&detail.anomaly_family.eq('A2')&detail.severity.eq(sev)&detail.seed.eq(seed)&detail.percentile.eq(97.5)].iloc[0]
            for ax in axes[i]:ax.axvline(t.threshold,ls='--',alpha=.6)
        axes[i,0].set_title(f'Clean B0007 ({sev} comparison)');axes[i,1].set_title(f'A2 {sev}; dashed existing P97.5 thresholds')
    for ax in axes.flat:ax.set(xlabel='Anomaly score',ylabel='Empirical cumulative fraction');ax.legend(title='Seed');ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/'a2_seed_score_distributions.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    for ax,sev in zip(axes,['moderate','strong']):
        for j,seed in enumerate(SEEDS):
            cs,ss=plotdata[(sev,seed)]
            for values,dy,color,label in [(cs,-.13,'tab:blue','clean'),(ss,.13,'tab:orange','A2')]:
                q=np.percentile(values,[5,25,50,75,95]);ax.plot([q[0],q[-1]],[j+dy]*2,color=color,lw=2)
                ax.plot([q[1],q[3]],[j+dy]*2,color=color,lw=7,label=label if j==0 else None);ax.scatter(q[2],j+dy,color='black',s=15)
            t=detail.loc[detail.n_estimators.eq(100)&detail.max_features.eq(1)&detail.anomaly_family.eq('A2')&detail.severity.eq(sev)&detail.seed.eq(seed)&detail.percentile.eq(97.5)].iloc[0]
            ax.scatter(t.threshold,j,marker='x',color='red',s=80,label='existing P97.5' if j==0 else None)
        ax.set(yticks=range(3),yticklabels=SEEDS,xlabel='Anomaly score',title=f'A2 {sev}: 5–95% / 25–75% intervals');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/'a2_threshold_overlap.png',dpi=160);plt.close(fig)


def main():
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    before=hashes()
    clean=pd.read_csv(ROOT/'data/processed/nasa_relative/B0007_relative_features.csv').set_index('cycle',drop=False)
    assert set(clean.cell_id)=={'B0007'}
    copies={k:pd.read_csv(SOURCE/f'B0007_relative_injected_prior{k}.csv.gz') for k in [5,10,20]}
    assert all(set(d.source_cell)=={'B0007'} for d in copies.values())
    thresholds=pd.read_csv(SOURCE/'thresholds.csv');eligible=pd.read_csv(SOURCE/'eligible_configurations.csv')
    metrics=pd.read_csv(SOURCE/'eligible_anomaly_metrics.csv')
    with prohibit_fitting():
        adaptation_rows,trajectories=adaptation(clean,copies)
        plot_adaptation(clean,copies,thresholds)
        plot_adaptation(clean,copies,thresholds,'mild')
        plot_adaptation(clean,copies,thresholds,'moderate')
        detail,corrs,plotdata=seed_analysis(clean,copies,eligible,thresholds)
        seed_plots(detail,plotdata)
    adaptation_rows.to_csv(OUT/'baseline_adaptation_by_scenario.csv',index=False)
    trajectories.to_csv(OUT/'baseline_adaptation_over_time.csv',index=False)
    detail.to_csv(OUT/'seed_score_and_threshold_diagnostics.csv',index=False)
    corrs.to_csv(OUT/'seed_rank_correlations.csv',index=False)
    groups=['anomaly_family','history_window','severity','base_feature','drift_sign']
    summary=adaptation_rows.groupby(groups).agg(scenarios=('scenario_id','size'),raw_peak_median=('raw_effect_peak','median'),residual_peak_median=('residual_effect_peak','median'),z_peak_median=('z_effect_peak','median'),remaining_final_median=('remaining_fraction_final','median'),absorbed_final_percent_median=('absorbed_percent_final','median'),mad_ratio_final_median=('mad_ratio_final','median'),ever_outside_fraction=('ever_outside_clean_p05_p95','mean'),return_observed_fraction=('return_observed','mean'),return_cycles_median=('return_cycles_after_first_excursion','median')).reset_index()
    summary.to_csv(OUT/'adaptation_summary.csv',index=False)
    recovery=adaptation_rows.loc[adaptation_rows.anomaly_family.str.startswith('A1')].groupby(['history_window','severity','base_feature']).agg(stable_return_fraction=('stable_return_observed','mean'),stable_return_cycles_median=('stable_return_cycles','median'),onset_already_outside_fraction=('onset_already_outside','mean')).reset_index()
    recovery.to_csv(OUT/'a1_sustained_return_diagnostics.csv',index=False)
    reference=metrics.loc[metrics.n_estimators.eq(100)&metrics.max_features.eq(1)&metrics.percentile.eq(97.5)&metrics.variant.eq('pooled')]
    metric_summary=reference.groupby(['feature_set','history_window','anomaly_family','severity'])[['recall','pr_auc','roc_auc']].agg(['mean','std'])
    metric_summary.columns=['_'.join(c) for c in metric_summary.columns];metric_summary=metric_summary.reset_index()
    metric_summary.to_csv(OUT/'reference_existing_metrics.csv',index=False)
    after=hashes();assert before==after,'Protected artifact changed'
    assert not any('b0018' in p.lower() for p in READS)
    integrity=dict(protected_files=len(before),sha256_before=before,sha256_after=after,all_protected_files_unchanged=True,model_and_embedded_scaler_unchanged=True,thresholds_unchanged=True,anomaly_protocol_unchanged=True,permitted_processed_sources_unchanged=True,fit_methods_blocked=True,test_cell_accessed=False,accessed_repository_files=sorted(READS),final_model=None,final_threshold=None)
    (OUT/'integrity_checks.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
    text=['# Phase 4C read-only failure analysis','',
          'Only existing saved Phase 4C models, embedded scalers, thresholds, B0007 relative data and synthetic copies were used. No injection, feature recomputation, fitting, calibration, selection or protocol modification occurred. Higher score means more anomalous. All tables refer to development diagnostics.',
          '\n## Diagnosis',
          '| Family | Ranking quality | Thresholded detection | Main failure mechanism | Implication |\n|---|---|---|---|---|\n| A1 | Near chance (AP approximately 0.46–0.49 at the reference) | Almost absent | Baseline adaptation / representation failure | A sustained change in degradation rate becomes the new local reference |\n| A4 | Weak to moderate; voltage better than temperature | Very low | Baseline adaptation plus detector/representation limitations and conservative operating point | Preserving physical drift does not guarantee separation in this multivariate detector |\n| A2 | Excellent clean/anomaly separation; high cross-seed rank correlation | Strongly seed-sensitive | Operating-point calibration instability with score-scale changes | Stable ranking does not imply stable decisions at clean-derived thresholds |\n| A3 | Severity dependent, strong substantially better than mild | Low relative to strong-anomaly ranking quality | Mainly operating point for strong anomalies, with genuine score overlap | This is not the near-total signal loss seen for A1 |',
          'A1: all matched saved ramps span 91 cycles. The median final retention effect remaining is 3.33%, 6.11%, and 11.67% for histories 5, 10, and 20 (absorption 96.67%, 93.89%, 88.33%). The added slope effect is completely absorbed at the endpoint for all histories. For a locally linear ramp, the median-baseline lag is approximately (k+1)/2 cycles, so retained ramp effect scales as (k+1)/(2×90). Longer histories retain more physical residual and slow adaptation, but do not preserve the cumulative loss as a lasting anomaly. The strong-retention MAD grows by median factors 2.70, 3.16, and 4.11, further normalizing away the altered trend. Very large peak Δz for k=5 can reflect a large clean residual becoming smaller, not stronger injected abnormality; it is not interchangeable with injected |z|.',
          'A4: the first drift sample has zero injected offset, so its incremental residual is exactly zero although its existing clean residual need not be zero. At the final strong-drift sample, k=5 retains 33.3% of raw drift; k=10 retains approximately 61%; k=20 retains 95.6–99.2% for voltage and 89.4–90.7% for temperature. This is a material window-length effect over the finite 10-cycle sequence, not evidence of long-term resistance to drift. At k=10, strong voltage drift inflates final MAD roughly 15–17 fold, versus approximately 2 fold at k=20. Nevertheless k=20 voltage recall at the fixed reference P97.5 is only 0.24–1.44%, despite AP 0.68–0.76 / ROC-AUC 0.79–0.85. Temperature ranks less well. Thus short-window adaptation is important, but does not by itself explain the remaining weak detection; the multivariate representation/detector and unchanged high operating point also limit sensitivity. These diagnostics cannot causally separate detector architecture from feature representation without a new experiment, which was not performed.',
          'A2: for RELATIVE_B/k=10/100 trees/full features, strong recall at the existing P97.5 is 47.92%, 95.32%, and 66.36% for seeds 42, 123, and 2026; moderate recall is 46.49%, 92.86%, and 64.16%. Strong-anomaly medians are 0.5871, 0.6209, and 0.5945, while thresholds are 0.5898, 0.6004, and 0.5885. The thresholds lie at the 52.08th, 4.68th, and 33.64th percentiles of strong A2 scores, even though each is near the 98th–99th percentile of clean B0007 scores. Between 19.5% and 47.5% of strong scores are within 0.01 of the corresponding threshold. Strong-anomaly Spearman correlations are 0.898–0.923, clean correlations 0.967–0.983, and pooled correlations 0.935–0.953. Ranking is comparatively stable but operating-point calibration is unstable. Rank differences are not zero; the dominant evidence is seed-dependent anomaly score placement relative to the clean tail, rather than collapse of clean/anomaly ranking. It is not just a common affine rescaling, since that alone would preserve threshold decisions.',
          'A3 quick check: at the same k=10 reference, strong AP/ROC-AUC average 0.917/0.938, but recall averages 19.83%. About 27–31% of strong scores lie within the clean P5–P95 interval, and the thresholds are at the 75th–89th percentiles of strong scores. This supports a restrictive operating point plus real overlap, rather than wholesale representation failure. Mild anomalies rank substantially worse (AP about 0.662 / ROC-AUC 0.697), so the strong-anomaly conclusion should not be extended to every severity.',
          '\n## Definitions and comparison controls',
          'For a matched source cycle, d = injected raw value − clean raw value; Δr = injected unstandardized residual − clean residual; Δb = injected prior median − clean prior median. Thus d = Δr + Δb. The signed retained fraction is Δr/d and absorption is 100(1−Δr/d). Zero-effect onset is undefined, not zero absorption. Values are not clipped: negative/>100% values can arise from nonlinear medians and pre-existing trajectory variation. Actual Δz is reported separately; it also includes changes in the MAD denominator and is not a physical-unit absorption percentage.',
          'Adaptation comparisons use only scenario IDs present at all three history lengths, avoiding different source-onset mixtures. Each saved sequence retains its own evolving injected history; no clean copy is contaminated. No observations beyond the saved sequence are fabricated. Near-clean is the descriptive clean-B0007 z P5–P95 band (not a detector threshold). Return time is the number of cycles after the first excursion until three consecutive samples are inside that band. Never-excursing sequences and right-censored nonreturns have no return time; medians of observed returns alone cannot establish recovery.',
          'Figures use the fixed source onset cycle 50, strong severity, 100 trees / max_features=1 / seed 42. This illustrative reference is not a winning-model selection. A4 figures show positive drift; tables cover both signs and both channels. A1 tables cover all severities and both retention and slope. A2/A3 score diagnostics cover every eligible RELATIVE_B history-10 grid/percentile combination and all three seeds.',
          '\n## A1 and A4 matched-window adaptation',table(summary),
          '\n## A1 return-time qualification',table(recovery),
          'The first-three-inside return times in the adaptation table can be temporary. This additional table requires all remaining saved samples to stay inside the clean range, with at least three remaining samples. Onset-already-outside flags reveal clean outliers present before any injected offset; return times are descriptive trajectory timings, not proof that injection caused every excursion. Sequences without an observed sustained return remain censored. No post-ramp recovery is inferred.',
          '\n## A2 moderate/strong seed diagnostics: fixed 100-tree/full-feature reference',
          table(detail.loc[detail.n_estimators.eq(100)&detail.max_features.eq(1)&detail.anomaly_family.eq('A2')&detail.severity.isin(['moderate','strong'])&detail.percentile.eq(97.5),['severity','seed','threshold','clean_median','clean_p95','synthetic_median','synthetic_p05','synthetic_p95','recall','threshold_clean_percentile','threshold_synthetic_percentile','threshold_clean_z','synthetic_within_001_threshold']]),
          'Threshold-to-distribution positions are empirical percentages at or below the unchanged threshold. Synthetic score multiplicity reflects the original overlapping windows; these are not independent biological replicates. The ±0.01 score band is descriptive only, in model-specific score units.',
          '\n## Rank stability on identical observations',table(corrs.loc[corrs.anomaly_family.eq('A2')&corrs.severity.isin(['moderate','strong'])]),
          'Synthetic rows are aligned by scenario ID and source cycle; clean rows are aligned by cycle. Pooled rank correlation is also supplied because within-anomaly rankings and clean-versus-anomaly separation answer different questions. Ties are handled by Spearman average ranks.',
          '\n## Existing eligible reference metrics',table(metric_summary),
          'PR-AUC is the saved class-balanced average precision (50/50 class weight), not raw prevalence-weighted AP. ROC-AUC uses the saved evaluation. The full score/threshold CSV includes A3 overlap: fraction of injected scores in clean P5–P95. No supervised metrics were used to choose a configuration or threshold.',
          '\n## Integrity verification',f'All {len(before)} protected files have identical before/after SHA-256 digests. This includes 96 development model/scaler bundles, the frozen configuration files, existing relative-result artifacts (including thresholds and synthetic copies), and explicitly named B0005/B0006/B0007 processed files. B0018 and the combined source CSV were never opened, including for hashing. A runtime audit guard blocked forbidden data paths and writes outside the new diagnostic outputs. Scaler fit/partial_fit and Isolation Forest fit were blocked during scoring. Full evidence: `results/nasa_failure_analysis/integrity_checks.json`.',
          '\n## Outputs','New diagnostic source: `scripts/diagnose_nasa_failures.py`. Report: `results/nasa_failure_analysis.md`. Diagnostic tables and integrity evidence: `results/nasa_failure_analysis/`. Figures: `figures/nasa/failure_analysis/a1_baseline_absorption.png`, `a4_drift_absorption.png`, `a2_seed_score_distributions.png`, `a2_threshold_overlap.png`. No experimental artifact was modified.']
    REPORT.write_text('\n\n'.join(text),encoding='utf-8')
    append_detail_tables()
    print(summary.to_string(index=False))
    print(detail.loc[detail.n_estimators.eq(100)&detail.max_features.eq(1)&detail.percentile.eq(97.5)&detail.anomaly_family.eq('A2'),['severity','seed','threshold','recall','threshold_clean_z','synthetic_within_001_threshold']].to_string(index=False))
    print(f'Integrity passed: {len(before)} unchanged artifacts.')


def append_detail_tables():
    """Render additional diagnostics from existing diagnostic tables only."""
    a=pd.read_csv(OUT/'baseline_adaptation_by_scenario.csv')
    a4=a.loc[a.anomaly_family.str.startswith('A4')]
    columns=['residual_effect_first','residual_effect_peak','residual_effect_final','injected_residual_first','injected_residual_peak_abs','injected_residual_final','remaining_fraction_final']
    summary=a4.groupby(['history_window','severity','base_feature','drift_sign'])[columns].median().reset_index()
    summary.to_csv(OUT/'a4_residual_summary.csv',index=False)
    m=pd.read_csv(SOURCE/'eligible_anomaly_metrics.csv')
    variants=m.loc[m.feature_set.eq('RELATIVE_B')&m.n_estimators.eq(100)&m.max_features.eq(1)&m.percentile.eq(97.5)&m.history_window.isin([10,20])&m.severity.eq('strong')&m.anomaly_family.str.startswith('A4')]
    variants=variants.groupby(['history_window','variant'])[['recall','pr_auc','roc_auc']].mean().reset_index()
    content=REPORT.read_text(encoding='utf-8').split('\n\n## Additional residual detail')[0]
    content+='\n\n## Additional residual detail\n\nRetention is a dimensionless fraction; capacity slope is Ah/cycle; voltage is V; temperature is degrees Celsius; robust residual z is dimensionless. Effect columns compare the injected value with its identical clean source cycle. Injected-residual columns give the actual residual rather than its change. Medians below are across matched scenarios, separately by sign.\n\n'+table(summary)
    content+='\n\n### A4 channel-specific existing metrics\n\nSeed means at the fixed reference P97.5, for already eligible configurations only.\n\n'+table(variants)
    content+='\n\nAdditional diagnostic safety tests: `tests/test_nasa_failure_analysis.py`. No protocol changes are recommended or selected in this diagnostic report.\n'
    REPORT.write_text(content,encoding='utf-8')


if __name__=='__main__':
    main()
