"""Independent CALCE development: fresh fitting, clean-only gate, no test access."""
import sys
sys.dont_write_bytecode=True
import os
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
READS=set()
PROTECTED=set()


def access_guard(event,args):
    if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
    path=Path(os.fsdecode(args[0])).resolve()
    if not path.is_relative_to(ROOT):return
    name=path.name.lower()
    if 'cs2_38' in name or name=='calce_cs2_discharge_features.csv':raise RuntimeError('CALCE final test/combined source remains locked')
    flags=args[2] if isinstance(args[2],int) else 0
    write=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if write and path in PROTECTED:raise RuntimeError('Protected artifact mutation blocked')
    if not write and not path.is_relative_to(ROOT/'.venv'):READS.add(str(path.relative_to(ROOT)))


sys.addaudithook(access_guard)
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score,roc_auc_score
from build_calce_relative_features import config,load_development,build_relative,features

OUT=ROOT/'results/calce_replication'
FIG=ROOT/'figures/calce/replication'
MODELS=ROOT/'models/development/calce_replication'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def nasa_hashes():
    paths=list((ROOT/'config').glob('*nasa*.json'))+[ROOT/'config/anomaly_injection_protocol.json']
    for directory in ['models/final_nasa','models/development','figures/nasa','data/processed/nasa','data/processed/nasa_relative']:
        paths += [p for p in (ROOT/directory).rglob('*') if p.is_file() and 'calce' not in p.as_posix().lower()]
    paths += list((ROOT/'scripts').glob('*nasa*.py'))
    for p in (ROOT/'results').glob('nasa*'):paths+=list(p.rglob('*')) if p.is_dir() else [p]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}


def table(d):
    def s(v):return f'{v:.6g}' if isinstance(v,(float,np.floating)) else str(v)
    return '\n'.join(['| '+' | '.join(d.columns)+' |','|'+'|'.join(['---']*len(d.columns))+'|']+['| '+' | '.join(map(s,r))+' |' for r in d.itertuples(index=False,name=None)])


def nominal(relative):
    p=config();parts=[]
    if any(c in relative for c in ['is_synthetic_anomaly','anomaly_family','severity']):raise ValueError('Synthetic labels forbidden in training')
    for cell in p['training_cells']:
        group=relative.loc[relative.cell_id.eq(cell)].sort_values('global_cycle')
        last=int(np.floor(len(group)*p['nominal_training_fraction']))
        parts.append(group.loc[group.global_cycle.le(last)])
    return pd.concat(parts).dropna(subset=features()).copy()


def fit_model(training,seed):
    if set(training.cell_id)!={'CS2-35','CS2-36'}:raise ValueError('Only nominal training cells allowed')
    if any(c in training for c in ['is_synthetic_anomaly','anomaly_family','severity']):raise ValueError('No synthetic training')
    limits={'CS2-35':264,'CS2-36':291}
    if not all(11<=r.global_cycle<=limits[r.cell_id] for r in training.itertuples()):raise ValueError('Outside frozen nominal windows')
    x=training[features()];assert np.isfinite(x.to_numpy()).all()
    scaler=StandardScaler();z=scaler.fit_transform(x)
    model=IsolationForest(**config()['model'],random_state=seed,n_jobs=1);model.fit(z)
    return dict(scaler=scaler,model=model,features=features(),seed=seed,training_ids=training[['cell_id','global_cycle']].to_dict('records'),training_matrix_sha256=hashlib.sha256(x.to_csv(index=False,float_format='%.17g').encode()).hexdigest(),scaler_mean=scaler.mean_.tolist(),scaler_scale=scaler.scale_.tolist(),status='CALCE_DEVELOPMENT_ONLY')


def score(bundle,data):return -bundle['model'].score_samples(bundle['scaler'].transform(data[bundle['features']]))


def select_threshold(clean):
    if set(clean.columns)!={'seed','percentile','clean_fpr'}:raise ValueError('Selection requires clean-only evidence')
    for p in [95,97.5,99]:
        g=clean.loc[clean.percentile.eq(p)]
        if len(g)!=3 or set(g.seed)!={42,123,2026}:raise ValueError('Missing seed evidence')
        if g.clean_fpr.le(.05).all():return p
    return None


def distribution(values):
    x=np.asarray(values);return dict(count=len(x),mean=float(x.mean()),std=float(x.std(ddof=1)),p05=float(np.quantile(x,.05)),median=float(np.median(x)),p95=float(np.quantile(x,.95)),minimum=float(x.min()),maximum=float(x.max()))


def anomaly_protocol(clean):
    if set(clean.cell_id)!={'CS2-37'}:raise ValueError('Anomaly calibration restricted to validation')
    stats={}
    for feature in config()['base_features']:
        x=clean[feature].dropna();median=float(x.median());mad=float((x-median).abs().median())
        stats[feature]=dict(median=median,MAD=mad,p05=float(x.quantile(.05)),p95=float(x.quantile(.95)),minimum=float(x.min()),maximum=float(x.max()))
    cv=max(stats[b]['MAD']/stats[b]['median'] for b in ['duration_s','time_to_3_4v_s'])
    severities={}
    for severity,m in [('mild',1.5),('moderate',3.),('strong',5.)]:
        factor=1/(1+m*cv)
        severities[severity]=dict(multiplier=m,timing_factor=factor,duration_reduction_at_median_s=stats['duration_s']['median']*(1-factor),crossing_reduction_at_median_s=stats['time_to_3_4v_s']['median']*(1-factor),voltage_offset_v=m*stats['mean_voltage_v']['MAD'])
    return dict(version='1.0',status='CALCE_VALIDATION_DERIVED_NO_TEST_ACCESS',calibration_cell='CS2-37',calibration_rows=len(clean),source_sha256=sha(ROOT/'data/processed/calce/CS2_37_discharge_features.csv'),statistics=stats,severity=severities,families={'CALCE_A2_EARLY_VOLTAGE_COLLAPSE':dict(window_cycles=5,affected_features=['duration_s','time_to_3_4v_s','mean_voltage_v'],directions='timing multiplied by shared factor; mean voltage reduced by offset'),'CALCE_A4_VOLTAGE_SENSOR_DRIFT':dict(window_cycles=10,affected_features=['mean_voltage_v'],directions='separate positive and negative linear ramps from zero to total offset')},timing_redesign='Use factor=1/(1+m*max(MAD/median of both timing features)) instead of subtracting m*MAD: guarantees positive times and preserves crossing<=duration. No fitted/test-derived magnitudes.',physical_guard='Reject whole scenario if mean voltage leaves original observed min/max voltage envelope, duration/crossing becomes nonpositive or crossing exceeds duration. No clipping.',baseline_rule='Fresh scenario context; prior injected samples influence later baselines only within that scenario. Current/future excluded.',protected='All columns except explicitly affected raw features remain unchanged; no capacity or metadata changes')


def injected_copies(clean,protocol):
    if set(clean.cell_id)!={'CS2-37'}:raise ValueError('Synthetic generation restricted to validation')
    copies=[];counts=[]
    for family,spec in protocol['families'].items():
        length=spec['window_cycles'];signs=[-1,1] if 'A4' in family else [0]
        for severity,params in protocol['severity'].items():
            for sign in signs:
                accepted=rejected=0
                for start in range(10,len(clean)-length+1):
                    original=clean.iloc[start:start+length].copy();modified=original.copy(deep=True)
                    if 'A2' in family:
                        modified['duration_s']*=params['timing_factor'];modified['time_to_3_4v_s']*=params['timing_factor'];modified['mean_voltage_v']-=params['voltage_offset_v']
                    else:modified['mean_voltage_v']+=sign*params['voltage_offset_v']*np.arange(length)/(length-1)
                    good=modified.mean_voltage_v.between(modified.min_voltage_v,modified.max_voltage_v).all() and modified.time_to_3_4v_s.gt(0).all() and modified.time_to_3_4v_s.le(modified.duration_s).all()
                    if not good:rejected+=1;continue
                    protected=[c for c in original if c not in spec['affected_features']]
                    pd.testing.assert_frame_equal(original[protected],modified[protected])
                    context=pd.concat([clean.iloc[start-10:start],modified],ignore_index=True)
                    rel=build_relative(context).iloc[10:].copy()
                    rel['source_cell']='CS2-37';rel['source_cycle']=modified.global_cycle.to_numpy();rel['anomaly_family']=family;rel['severity']=severity;rel['drift_sign']=sign;rel['scenario_id']=f'{family}_{severity}_{sign}_{start+1}'
                    rel['is_synthetic_anomaly']=True
                    if 'A4' in family:rel.iloc[0,rel.columns.get_loc('is_synthetic_anomaly')]=False
                    copies.append(rel);accepted+=1
                counts.append(dict(family=family,severity=severity,sign=sign,accepted_windows=accepted,rejected_windows=rejected))
    return pd.concat(copies,ignore_index=True) if copies else pd.DataFrame(),pd.DataFrame(counts)


def metrics(clean,synthetic,threshold):
    fpr=float(np.mean(clean>threshold));recall=float(np.mean(synthetic>threshold));precision=recall/(recall+fpr) if recall+fpr else 0
    y=np.r_[np.zeros(len(clean)),np.ones(len(synthetic))];scores=np.r_[clean,synthetic];weights=np.r_[np.full(len(clean),.5/len(clean)),np.full(len(synthetic),.5/len(synthetic))]
    return dict(precision=precision,recall=recall,f1=2*precision*recall/(precision+recall) if precision+recall else 0,pr_auc=average_precision_score(y,scores,sample_weight=weights),roc_auc=roc_auc_score(y,scores),clean_fpr=fpr)


def main():
    before=nasa_hashes();PROTECTED.update((ROOT/p).resolve() for p in before)
    sources=[ROOT/f'data/processed/calce/{c}_discharge_features.csv' for c in ['CS2_35','CS2_36','CS2_37']]
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources};PROTECTED.update(p.resolve() for p in sources)
    for directory in [OUT,FIG,MODELS]:directory.mkdir(parents=True,exist_ok=True)
    raw=load_development();relative=build_relative(raw)
    relative.to_csv(ROOT/'data/processed/calce/calce_cs2_relative_features.csv',index=False)
    training=nominal(relative);validation=relative.loc[relative.cell_id.eq('CS2-37')].dropna(subset=features()).copy()
    clean_raw=raw.loc[raw.cell_id.eq('CS2-37')].reset_index(drop=True)
    models={};thresholds=[];scores=[];distributions=[];drift=[];shifts=[]
    for feature in features():
        a=training[feature];b=validation[feature];mad=float((a-a.median()).abs().median())
        shifts.append(dict(feature=feature,training_median=a.median(),validation_median=b.median(),training_MAD=mad,validation_MAD=(b-b.median()).abs().median(),shift_in_training_MAD=(b.median()-a.median())/mad if mad else np.nan))
    for seed in config()['seeds']:
        bundle=fit_model(training,seed);models[seed]=bundle;joblib.dump(bundle,MODELS/f'DEVELOPMENT_CALCE_seed{seed}.joblib')
        ts=score(bundle,training);vs=score(bundle,validation)
        for region,frame,values in [('nominal_training',training,ts),('CS2-37',validation,vs)]:
            distributions.append(dict(seed=seed,region=region,**distribution(values)))
            scores.extend(dict(seed=seed,region=region,cell_id=r.cell_id,global_cycle=r.global_cycle,score=float(v)) for r,v in zip(frame.itertuples(),values))
        n=len(vs)//3;drift.append(dict(seed=seed,early_mean=vs[:n].mean(),late_mean=vs[-n:].mean(),late_minus_early=vs[-n:].mean()-vs[:n].mean(),early_median=np.median(vs[:n]),late_median=np.median(vs[-n:])))
        for percentile in [95,97.5,99]:
            threshold=float(np.percentile(ts,percentile))
            thresholds.append(dict(seed=seed,percentile=percentile,threshold=threshold,clean_fpr=float(np.mean(vs>threshold)),training_rows=len(ts),validation_rows=len(vs),threshold_source='clean_nominal_CALCE_training_only'))
    thresholds=pd.DataFrame(thresholds);eligible=select_threshold(thresholds[['seed','percentile','clean_fpr']])
    scores=pd.DataFrame(scores);shifts=pd.DataFrame(shifts);drift=pd.DataFrame(drift);distributions=pd.DataFrame(distributions)
    for name,d in [('thresholds',thresholds),('clean_scores',scores),('relative_feature_shifts',shifts),('score_drift',drift),('score_distributions',distributions)]:d.to_csv(OUT/f'{name}.csv',index=False)
    protocol=anomaly_protocol(clean_raw)
    (ROOT/'config/calce_anomaly_injection_protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    results=[];counts=pd.DataFrame()
    if eligible is not None:
        copies,counts=injected_copies(clean_raw,protocol)
        copies.to_csv(OUT/'CS2_37_synthetic_evaluation_copies.csv.gz',index=False,compression={'method':'gzip','mtime':0})
        counts.to_csv(OUT/'synthetic_window_counts.csv',index=False)
        for seed,bundle in models.items():
            clean_scores=score(bundle,validation);threshold=float(thresholds.loc[thresholds.seed.eq(seed)&thresholds.percentile.eq(eligible),'threshold'].iloc[0])
            for (family,severity),g in copies.loc[copies.is_synthetic_anomaly].groupby(['anomaly_family','severity']):
                values=score(bundle,g)
                results.append(dict(seed=seed,family=family,severity=severity,percentile=eligible,synthetic_rows=len(g),**metrics(clean_scores,values,threshold),**{'score_'+k:v for k,v in distribution(values).items()}))
    results=pd.DataFrame(results)
    if len(results):results.to_csv(OUT/'anomaly_metrics.csv',index=False)
    fig,axes=plt.subplots(4,2,figsize=(13,12))
    for i,base in enumerate(config()['base_features']):
        v=relative.loc[relative.cell_id.eq('CS2-37')]
        axes[i,0].plot(v.global_cycle,v[base],label='raw');axes[i,0].plot(v.global_cycle,v[base+'_prior10_median'],label='prior median');axes[i,0].set_ylabel(base);axes[i,0].legend()
        axes[i,1].plot(v.global_cycle,v[base+'_prior10_robust_residual']);axes[i,1].set_ylabel('robust residual')
    fig.tight_layout();fig.savefig(FIG/'relative_feature_examples.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,4))
    for seed,g in scores.loc[scores.region.eq('CS2-37')].groupby('seed'):ax.plot(g.global_cycle,g.score,label=str(seed),alpha=.7)
    ax.set(xlabel='CS2-37 cycle',ylabel='Anomaly score',title='Clean validation: higher score is more anomalous');ax.legend();fig.tight_layout();fig.savefig(FIG/'clean_score_vs_cycle.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,4))
    for ax,seed in zip(axes,config()['seeds']):
        for region,g in scores.loc[scores.seed.eq(seed)].groupby('region'):
            s=np.sort(g.score);ax.plot(s,np.arange(1,len(s)+1)/len(s),label=region)
        ax.set(title=f'Seed {seed}',xlabel='Score',ylabel='Empirical CDF');ax.legend()
    fig.tight_layout();fig.savefig(FIG/'training_vs_validation_scores.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4))
    for seed,g in thresholds.groupby('seed'):ax.plot(g.percentile,g.clean_fpr*100,marker='o',label=str(seed))
    ax.axhline(5,c='black',ls='--');ax.set(xlabel='Clean training percentile',ylabel='CS2-37 FPR (%)');ax.legend();fig.tight_layout();fig.savefig(FIG/'clean_fpr_thresholds.png',dpi=160);plt.close(fig)
    if len(results):
        fig,axes=plt.subplots(1,2,figsize=(12,4))
        for ax,(family,g) in zip(axes,results.groupby('family')):
            for metric in ['recall','pr_auc','roc_auc']:
                s=g.groupby('severity')[metric].agg(['mean','std']).reindex(['mild','moderate','strong']);ax.errorbar(s.index,s['mean'],yerr=s['std'],marker='o',label=metric)
            ax.set(title=family,ylim=(0,1.05));ax.legend()
        fig.tight_layout();fig.savefig(FIG/'anomaly_severity_response.png',dpi=160);plt.close(fig)
    after=nasa_hashes();assert before==after
    assert all(sha(ROOT/p)==h for p,h in source_hashes.items())
    integrity=dict(nasa_before=before,nasa_after=after,nasa_unchanged=True,development_source_hashes=source_hashes,test_cell_accessed=False,repository_reads=sorted(READS),eligible_percentile=eligible,training_counts=training.groupby('cell_id').size().to_dict(),validation_rows=len(validation),no_NASA_model_reuse=True)
    (OUT/'integrity_checks.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
    stability=thresholds.groupby('percentile').clean_fpr.agg(['mean','std','min','max']).reset_index();stability.to_csv(OUT/'threshold_seed_stability.csv',index=False)
    report=['# Independent CALCE replication validation',f'Train: CS2-35/36; validation: CS2-37; CS2-38 remains locked. Effective training rows: {training.groupby("cell_id").size().to_dict()} ({len(training)} total). Nominal boundaries are cycles 264 and 291; cycles 1–10 are dropped after applying those boundaries. Usable validation: {len(validation)} (cycles 11–1036). The separate relative table contains only the three development cells, not the held-out cell.',
            'Fresh StandardScaler and Isolation Forest fits use only four prior-10 robust residuals on nominal training rows. No NASA fitted artifact, threshold or anomaly magnitude is reused. Capacity and metadata never enter fitting. Scores are minus score_samples; decisions use score > threshold. No imputation or burn-in recalibration occurs.',
            '## Clean-only thresholds',table(thresholds),'## Seed stability',table(stability),f'First all-seed eligible percentile: {eligible}. '+('FAILURE: no percentile meets the <=5% clean FPR rule; synthetic evaluation was not run and development stops here.' if eligible is None else 'Eligible for development review only. No final configuration or test access is authorized automatically.'),
            '## Training versus validation scores',table(distributions),'## Early-to-late validation score drift',table(drift),'First/last thirds use usable chronological rows. Small or negative drift is not proof of stationarity; transient clean spikes remain visible.',
            '## Remaining robust feature shift',table(shifts),'Shift is (validation median − training median)/training MAD, calculated per relative feature. Near-zero local MAD can create large residual tails; no clipping is performed.',
            '## CALCE-only controlled-anomaly design',json.dumps(protocol,indent=2),'Magnitudes use only CS2-37 raw feature MADs, with 1.5/3/5 multipliers. Shared positive timing contraction preserves crossing<=duration; its nonlinear formulation avoids impossible negative times at large spreads. Voltage offsets use literal m×MAD. Raw-value envelope guards reject whole scenarios, never clip or change magnitudes. Timing reductions at the observed median and observed ranges are recorded above. A4 is a signed monotonic ten-cycle drift, not independent noise. No capacity or metadata modifications are allowed.',
            '## Eligible synthetic evaluation',table(results) if len(results) else 'Not run: clean-only eligibility failed.',table(counts) if len(counts) else '',
            'Precision/F1 and average precision (PR-AUC) use 50% evaluation prevalence. ROC-AUC and recall are unweighted within class. A4 variants are pooled across both drift signs. Zero-offset onset rows are not labeled anomalous. Each scenario has isolated causal history; prior injected values can adapt its baseline. Overlapping windows are dependent copies, not independent battery failures. Synthetic deviations are not claimed to be naturally observed faults. None of these metrics enters fitting or threshold choice.',
            f'## Integrity\n\nAll {len(before)} NASA hashes and all three permitted CALCE source hashes match before/after. A runtime audit blocks CS2-38 and the combined raw feature table, and blocks writes to protected artifacts. Only development models are saved under models/development/calce_replication/. Test-cell access did not occur.']
    (ROOT/'results/calce_replication_validation.md').write_text('\n\n'.join(report),encoding='utf-8')
    print(table(thresholds));print('Eligible:',eligible);print(table(drift));print(table(shifts))


if __name__=='__main__':main()
