"""Descriptive four-cell CALCE audit; no model fitting or relative features."""
import sys
sys.dont_write_bytecode=True
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from extract_calce import ROOT,OUT,CELLS,base

FEATURES=['capacity_ah','capacity_retention','duration_s','time_to_3_4v_s','mean_voltage_v','mean_current_a']


def main():
    before=base.nasa_hashes()
    d=pd.read_csv(ROOT/'data/processed/calce/calce_cs2_discharge_features.csv')
    assert set(d.cell_id)==set(CELLS)
    summaries=[json.loads((OUT/c.replace('-','_')/'summary.json').read_text()) for c in CELLS]
    distributions=[];life=[];correlations=[];boundaries=[]
    for cell,g in d.groupby('cell_id',sort=True):
        g=g.sort_values('global_cycle');n=max(1,int(len(g)*.1))
        boundary=g.source_workbook.ne(g.source_workbook.shift());boundary.iloc[0]=False
        for feature in FEATURES:
            s=g[feature];delta=s.diff().abs()
            distributions.append(dict(cell_id=cell,feature=feature,missing=int(s.isna().sum()),**s.describe(percentiles=[.05,.25,.5,.75,.95]).to_dict()))
            correlations.append(dict(cell_id=cell,feature=feature,pearson_with_retention=s.corr(g.capacity_retention)))
            for region,part in [('early',g.head(n)),('late',g.tail(n))]:
                life.append(dict(cell_id=cell,region=region,feature=feature,rows=n,median=part[feature].median(),mean=part[feature].mean(),std=part[feature].std()))
            b=delta.loc[boundary];w=delta.loc[~boundary].dropna()
            ratio=b.median()/w.median() if w.median()>0 else np.nan
            boundaries.append(dict(cell_id=cell,feature=feature,boundary_transitions=len(b),within_transitions=len(w),boundary_median_absolute_change=b.median(),within_median_absolute_change=w.median(),median_change_ratio=ratio,max_boundary_absolute_change=b.max()))
    distributions=pd.DataFrame(distributions);life=pd.DataFrame(life);correlations=pd.DataFrame(correlations);boundaries=pd.DataFrame(boundaries)
    for name,frame in [('feature_distributions',distributions),('early_late_features',life),('retention_correlations',correlations),('boundary_feature_changes',boundaries)]:frame.to_csv(OUT/(name+'.csv'),index=False)
    figdir=ROOT/'figures/calce/cross_cell';figdir.mkdir(parents=True,exist_ok=True)
    for feature,name in [('capacity_ah','capacity_vs_cycle'),('capacity_retention','capacity_retention_vs_cycle'),('duration_s','duration_vs_cycle'),('time_to_3_4v_s','time_to_3_4v_vs_cycle'),('mean_voltage_v','mean_voltage_vs_cycle'),('capacity_change','capacity_change_vs_cycle')]:
        fig,ax=plt.subplots(figsize=(12,5))
        for cell,g in d.groupby('cell_id'):
            g=g.sort_values('global_cycle');y=g.capacity_ah.diff() if feature=='capacity_change' else g[feature]
            ax.plot(g.global_cycle,y,label=cell,lw=.9,alpha=.85)
        ax.set(xlabel='Accepted chronological discharge cycle',ylabel='Cycle-to-cycle capacity change (Ah)' if feature=='capacity_change' else feature,title='CALCE CS2 comparison — descriptive, not fault labels');ax.legend();ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(figdir/(name+'.png'),dpi=160);plt.close(fig)
    columns=['cell_id','workbooks','retained_workbooks','unique_candidate_discharges','accepted','rejected','first_capacity','final_capacity','final_retention','capacity_min','capacity_max','mean_discharge_current_a','integration_median_abs_pct','integration_max_abs_pct','largest_positive_change_ah','largest_negative_change_ah']
    report=['# CALCE cross-cell audit',base.md(pd.DataFrame(summaries)[columns]),
            '## Method and comparability','All four cells pass the shared extraction checks: near-1C sustained discharge in step 7, observed cutoff cluster immediately below 2.7 V, transition to step 8, positive counter increments and small integration disagreement. All use the same 17-column channel schema; supplementary worksheet names/counts are reported below. CS2-35 output was checked against its validated table without rewriting its bytes. No temperature measurements, relative features, model fitting or EOL labels were created.',
            'Early/late summaries use the first/last floor(10% of accepted cycles) separately for each cell. These are observed trajectory regions, not matched calendar ages or train/test splits. Correlations are descriptive Pearson correlations within each cell; serial dependence and common ageing trends preclude causal interpretations. Capacity retention is normalized to each cell’s first accepted complete discharge.',
            '## Observed cross-cell differences',
            'All four trajectories show broadly declining capacity, duration and time to 3.4 V, with temporary dips/recovery and workbook-associated jumps. Their rates and terminal observed retention differ; recording length is not a matched end-of-life criterion. CS2-36 and CS2-37 finish at lower normalized capacities than CS2-35 and CS2-38. Early median retention is similar (about 0.939–0.954), but late-region medians span about 0.185–0.376.',
            'CS2-38 has an early mean-voltage median near 3.621 V, compared with about 3.652–3.654 V for the other cells (roughly 30–34 mV lower). Mean discharge currents are all approximately -1.1 A; cross-cell offsets are below about 0.5 mA and should not be confused with major operating-current changes. These are descriptive offsets, not faults.',
            'Median absolute capacity changes at workbook boundaries are 2.60–3.91 times within-workbook changes; corresponding time-to-3.4 V ratios are 3.87–6.12. This shows substantial boundary association for timing/capacity variables, confounded by rest intervals and ageing. The largest absolute capacity boundary jump is CS2-36: +0.130568 Ah (+14.62%) entering CS2_36_10_21_10.xlsx. Large current-change ratios have very small absolute denominators and do not alone establish practically large current offsets. All values are retained without correction.',
            '## Per-cell structural and rejection evidence',*[f'### {s["cell_id"]}\n\n'+json.dumps({k:s[k] for k in ['sheet_names','duplicate_workbooks','rejection_reasons','dominant_step','complete_final_voltage','largest_boundary_jump','missing_values']},indent=2) for s in summaries],
            '## Feature distributions',base.md(distributions),'## Early and late differences',base.md(life),'## Correlation with capacity retention',base.md(correlations),
            '## Workbook-boundary dependence',base.md(boundaries),
            'Boundary effects are assessed by comparing absolute one-cycle changes at workbook boundaries with changes inside workbooks. Ratios above one indicate larger typical boundary transitions; they do not establish that acquisition boundaries caused the changes. Boundary events are fewer, differ in rest gaps, and occur at different ageing stages. Every boundary jump remains uncorrected. Raw cycle-to-cycle dips and recovery are plotted without fault labels or smoothing.',
            '## Scope','A common CALCE extraction pipeline is supported for these four cells. This does not establish identical electrochemical histories or a common feature distribution. Compare first/final retention and the trajectories rather than interpreting recording lengths as equal cycle-life endpoints. Early characterization cycles are retained when complete; initial-charge-state differences and long recording gaps remain limitations.',
            '## Files','Per-cell tables and combined table: data/processed/calce/. Per-cell extraction validation reports and rejected-cycle CSVs: results/. Detailed schemas, duplicates, candidate records, completion rules, capacity changes and summaries: results/calce_cells/. Six cross-cell figures: figures/calce/cross_cell/.']
    (ROOT/'results/calce_cross_cell_audit.md').write_text('\n\n'.join(report),encoding='utf-8')
    compatibility='''# NASA–CALCE feature compatibility

The NASA study is frozen. This is a new comparison document, not a change to NASA artifacts. The final NASA RELATIVE_B model uses seven prior-10 robust residuals of duration, time to 3.4 V, mean voltage, mean current, mean/max temperature and temperature rise. CALCE outputs here are absolute cycle summaries; no trajectory-relative features have been generated.

| Concept | NASA available | CALCE available | Directly comparable? | Caveat |
|---|---|---|---|---|
| duration_s | Yes | Yes | Related, not exactly identical | NASA measures last minus first recorded sample; CALCE includes inferred step onset before the first sample. Cutoff and operating protocols differ. |
| time_to_3_4v_s | Yes | Yes | Related, not exactly identical | Frozen NASA uses first sampled crossing relative to first sample; CALCE linearly interpolates relative to step onset. Sampling cadence differs. |
| mean_voltage_v | Yes | Yes | Same unit/concept, protocol dependent | Arithmetic sample means depend on current, cutoff, sampling and starting charge state. |
| mean_current_a | Yes | Yes | Same unit/concept, different operating distribution | CALCE main discharge is around -1.1 A; NASA conditions differ. Do not treat a cell-specific operating offset as a fault. |
| temperature-derived features | Yes | No | No | CALCE workbooks lack measured temperature traces; auxiliary mapping metadata is not temperature data. No temperature values are invented. |
| capacity_retention | Yes | Yes | Related normalization, different capacity measurement | Both normalize to the first included discharge. NASA uses supplied discharge capacity; CALCE differences cumulative counters at verified step boundaries. Initial characterization/charge states differ. Not an input to final NASA RELATIVE_B. |

The feature spaces are not identical. The frozen NASA model cannot simply receive these CALCE columns: three required thermal concepts are unavailable and no relative representation has been built. A common CALCE replication design must be developed independently; no feature set or model is selected here.
'''
    (ROOT/'results/nasa_calce_feature_compatibility.md').write_text(compatibility,encoding='utf-8')
    for path,value in before.items():assert base.sha(ROOT/path)==value
    print(base.md(pd.DataFrame(summaries)[columns]))


if __name__=='__main__':main()
