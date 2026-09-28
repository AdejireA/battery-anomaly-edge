"""Independent CS2-35 complete-main-discharge reconstruction; no NASA changes."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import hashlib
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from inspect_calce_workbooks import ROOT,RAW,read_sheets,workbook_date,protected_hashes,sha,md

OUT=ROOT/'results/calce_cs2_35'
FIG=ROOT/'figures/calce/cs2_35'
PROCESSED=ROOT/'data/processed/calce/CS2_35_discharge_features.csv'
NOMINAL_AH=1.1
EXPECTED_CUTOFF=2.7
FINGERPRINT_COLUMNS=['Data_Point','Test_Time(s)','Date_Time','Step_Time(s)','Step_Index','Cycle_Index','Current(A)','Voltage(V)','Charge_Capacity(Ah)','Discharge_Capacity(Ah)','Charge_Energy(Wh)','Discharge_Energy(Wh)','dV/dt(V/s)','Internal_Resistance(Ohm)','Is_FC_Data','AC_Impedance(Ohm)','ACI_Phase_Angle(Deg)']


def nasa_hashes():
    result=protected_hashes()
    for directory in [ROOT/'data/processed/nasa',ROOT/'data/processed/nasa_relative']:
        for p in directory.rglob('*'):
            if p.is_file():result[str(p.relative_to(ROOT))]=sha(p)
    for p in (ROOT/'scripts').glob('*.py'):
        if 'nasa' in p.name:result[str(p.relative_to(ROOT))]=sha(p)
    return result


def fingerprint(frame):
    payload=frame[FINGERPRINT_COLUMNS].to_csv(index=False,float_format='%.17g',date_format='%Y-%m-%dT%H:%M:%S.%f',lineterminator='\n')
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def order_and_deduplicate(workbooks):
    ordered=sorted(workbooks,key=lambda w:(w['frame'].Date_Time.iloc[0],w['date'] or pd.Timestamp.max.date(),w['path'].name))
    seen={};audit=[];kept=[]
    for w in ordered:
        key=fingerprint(w['frame']);duplicate=seen.get(key)
        audit.append(dict(source_workbook=w['path'].name,filename_date=str(w['date']),measurement_first=w['frame'].Date_Time.iloc[0],measurement_last=w['frame'].Date_Time.iloc[-1],rows=len(w['frame']),channel_fingerprint=key,raw_file_sha256=sha(w['path']),duplicate_of=duplicate or '',included=duplicate is None))
        if duplicate is None:seen[key]=w['path'].name;kept.append(w)
    return kept,pd.DataFrame(audit)


def candidate_segments(frame):
    runs=(frame.Cycle_Index.ne(frame.Cycle_Index.shift())|frame.Step_Index.ne(frame.Step_Index.shift())|frame['Step_Time(s)'].diff().lt(0)).cumsum()
    for _,g in frame.groupby(runs,sort=False):
        current=g['Current(A)'].median()
        near_1c=-1.21<=current<=-.99  # ±10% neighborhood for identifying the observed 1.1 A mode, not completion.
        if near_1c or int(g.Step_Index.iloc[0])==7:
            yield g,near_1c


def segment_record(frame,g,filename,near_1c,*,cell_id='CS2-35'):
    start,end=int(g.index[0]),int(g.index[-1])
    time=g['Test_Time(s)'].to_numpy(float);current=g['Current(A)'].to_numpy(float)
    elapsed=time-(time[0]-float(g['Step_Time(s)'].iloc[0]))
    prev=frame.iloc[start-1] if start>0 else None
    initial=float(prev['Discharge_Capacity(Ah)']) if prev is not None else np.nan
    q=float(g['Discharge_Capacity(Ah)'].iloc[-1])-initial
    integrated=abs(float(np.trapezoid(np.r_[current[0],current],np.r_[0.,elapsed])))/3600
    finite=np.isfinite(g[['Test_Time(s)','Step_Time(s)','Voltage(V)','Current(A)','Discharge_Capacity(Ah)']].to_numpy(float)).all()
    prior_ok=prev is not None and prev.Cycle_Index==g.Cycle_Index.iloc[0] and prev.Step_Index!=g.Step_Index.iloc[0]
    onset=time[0]-elapsed[0]
    prior_gap=onset-float(prev['Test_Time(s)']) if prev is not None else np.nan
    v=g['Voltage(V)'].to_numpy(float)
    below=np.flatnonzero(v<=3.4)
    crossing=np.nan
    if len(below):
        j=int(below[0])
        if j>0:
            crossing=float(elapsed[j-1]+(3.4-v[j-1])*(elapsed[j]-elapsed[j-1])/(v[j]-v[j-1]))
        elif v[0]==3.4:crossing=float(elapsed[0])
        # If first voltage already below 3.4 V, crossing is left-censored; never invent it.
    reasons=[]
    if len(g)<3:reasons.append('too_few_samples_for_curve_and_integration')
    if not finite:reasons.append('missing_or_nonfinite_measurement')
    if not prior_ok:reasons.append('missing_same_cycle_pre_discharge_counter')
    if not near_1c:reasons.append('current_not_in_observed_main_discharge_mode')
    if int(g.Step_Index.iloc[0])!=7:reasons.append('unexpected_main_discharge_step_requires_review')
    if not np.all(np.diff(time)>0):reasons.append('non_increasing_test_time')
    if not np.all(np.diff(g['Discharge_Capacity(Ah)'].to_numpy(float))>0):reasons.append('non_increasing_discharge_capacity_counter')
    if not (v[-1]<v[0]):reasons.append('voltage_does_not_fall_over_segment')
    if not (np.isfinite(q) and q>0 and elapsed[-1]>0):reasons.append('nonpositive_or_invalid_duration_capacity')
    if elapsed[0]<0 or (np.abs(elapsed-g['Step_Time(s)'].to_numpy(float))>1e-3).any():reasons.append('inconsistent_step_and_test_time')
    # Step and test clocks have observed +/-30 ms transition offsets. Preserve
    # that discrepancy, but validate the recorded ordering instead of rejecting
    # an inferred onset that precedes the prior sample by a few milliseconds.
    if prior_ok and float(prev['Test_Time(s)'])>=time[0]:reasons.append('non_increasing_time_at_pre_step_boundary')
    # A constant-current physical envelope, with a numerical 1 micro-Ah allowance.
    low=max(0.,-float(current.max()))*elapsed[-1]/3600
    high=max(0.,-float(current.min()))*elapsed[-1]/3600
    if q<low-1e-6 or q>high+1e-6:reasons.append('capacity_outside_observed_current_duration_envelope')
    eof=end==len(frame)-1
    if eof and current[-1]<-.5:reasons.append('end_of_file_while_discharging')
    record=dict(cell_id='CS2-35',source_workbook=filename,source_cycle_index=int(g.Cycle_Index.iloc[0]),source_step_index=int(g.Step_Index.iloc[0]),start_timestamp=pd.Timestamp(g.Date_Time.iloc[0])-pd.to_timedelta(elapsed[0],unit='s'),end_timestamp=g.Date_Time.iloc[-1],capacity_ah=q,capacity_from_current_ah=integrated,capacity_integration_error_pct=100*(integrated-q)/q if q>0 else np.nan,duration_s=float(elapsed[-1]),time_to_3_4v_s=crossing,mean_voltage_v=float(v.mean()),min_voltage_v=float(v.min()),max_voltage_v=float(v.max()),mean_current_a=float(current.mean()),min_current_a=float(current.min()),max_current_a=float(current.max()),cutoff_final_voltage_v=float(v[-1]),sample_count=len(g),capacity_counter_initial_ah=initial,capacity_counter_final_ah=float(g['Discharge_Capacity(Ah)'].iloc[-1]),first_sample_timestamp=g.Date_Time.iloc[0],first_sample_elapsed_s=float(elapsed[0]),pre_step_to_onset_gap_s=prior_gap,discharge_onset_test_time_s=float(onset),starting_voltage_v=float(v[0]),next_step_index=int(frame.Step_Index.iloc[end+1]) if not eof else np.nan,end_of_file=eof,near_1c=bool(near_1c),candidate_main_discharge=True,rejection_reason=';'.join(reasons))
    record['cell_id']=cell_id
    return record,elapsed,v


def completion_rule(candidates):
    """Inspect observed terminal-voltage cluster before choosing a tolerance."""
    reference=candidates.loc[candidates.next_step_index.eq(8)&candidates.near_1c,'cutoff_final_voltage_v']
    if len(reference)<10:raise RuntimeError('Insufficient step-transition evidence for completion interpretation')
    # No positive tolerance invented: validate the observed cluster against 2.7 V.
    if not (reference.le(EXPECTED_CUTOFF).all() and reference.min()>2.69):
        raise RuntimeError('Observed completion endpoints do not support the expected cutoff; manual review required')
    others=candidates.loc[~candidates.index.isin(reference.index),'cutoff_final_voltage_v']
    return dict(cell_id='CS2-35',main_step=7,nominal_capacity_ah=1.1,nominal_capacity_role='metadata and nominal-capacity-normalized SOH only; no EOL label',reference_complete_segments=len(reference),reference_min_v=float(reference.min()),reference_max_v=float(reference.max()),reference_quantiles=reference.quantile([0,.01,.05,.5,.95,.99,1]).to_dict(),observed_other_endpoints_v=sorted(others.unique().tolist()),completion_upper_voltage_v=2.7,positive_voltage_tolerance_v=0.,rationale='Observed step-7-to-step-8 endpoints form a tight cluster immediately below 2.7 V. Therefore use the documented 2.7 V endpoint with no positive tolerance. End-of-file discharge remains rejected even if its final voltage is low.',completion_transition='require next step 8; reject end-of-file under discharge current',minimum_samples=3,capacity_definition='final cumulative discharge counter minus last pre-step counter in the same local cycle/workbook',current_integration='trapezoidal over Test_Time relative to step onset, with first measured current held over the initial unsampled interval',numerical_capacity_envelope_allowance_ah=1e-6,pre_step_boundary_validation='Same local cycle, preceding non-discharge sample, strictly increasing recorded Test_Time; inferred step-onset clock offsets are retained as measurement diagnostics rather than completeness failures',nominal_current_identification_band_a=[-1.21,-.99])


def plots(accepted,curves):
    FIG.mkdir(parents=True,exist_ok=True)
    for column,name,ylabel in [('capacity_ah','capacity_vs_global_cycle','Capacity (Ah)'),('capacity_retention','capacity_retention_vs_global_cycle','Retention relative to first accepted discharge'),('duration_s','duration_vs_global_cycle','Discharge duration (s)'),('time_to_3_4v_s','time_to_3_4v_vs_global_cycle','First 3.4 V crossing (s)')]:
        fig,ax=plt.subplots(figsize=(11,4));ax.plot(accepted.global_cycle,accepted[column],lw=1)
        ax.set(xlabel='Chronological complete discharge number',ylabel=ylabel,title='CALCE CS2-35');ax.grid(alpha=.2)
        fig.tight_layout();fig.savefig(FIG/f'{name}.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for label,index in [('early',0),('middle',len(accepted)//2),('late',len(accepted)-1)]:
        row=accepted.iloc[index];time,v=curves[(row.source_workbook,int(row.source_cycle_index))]
        ax.plot(time,v,label=f'{label}: global {row.global_cycle} ({row.source_workbook}, local {row.source_cycle_index})')
        single,sax=plt.subplots(figsize=(9,4))
        sax.plot(time,v);sax.axhline(2.7,c='gray',ls='--')
        sax.set(xlabel='Seconds from discharge-step onset',ylabel='Terminal voltage (V)',title=f'CS2-35 {label}: global cycle {row.global_cycle}, local {row.source_cycle_index}')
        sax.grid(alpha=.2);single.tight_layout();single.savefig(FIG/f'{label}_discharge_curve.png',dpi=160);plt.close(single)
    ax.axhline(2.7,c='gray',ls='--');ax.set(xlabel='Seconds from discharge-step onset',ylabel='Terminal voltage (V)',title='Representative accepted CS2-35 discharges');ax.legend(fontsize=7);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/'representative_discharge_curves.png',dpi=160);plt.close(fig)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    before=nasa_hashes();raw_before={p.name:sha(p) for p in RAW.glob('*.xlsx')}
    workbooks=[]
    for path in RAW.glob('*.xlsx'):
        print(f'Reading {path.name}',flush=True)
        channels=[d for name,d,meta in read_sheets(path) if meta.get('cycling_data')]
        if len(channels)!=1:raise RuntimeError(f'{path.name}: expected one validated channel sheet')
        d=channels[0].reset_index(drop=True)
        if d.Date_Time.isna().any() or not d.Date_Time.is_monotonic_increasing:raise RuntimeError('Missing/backward timestamps')
        if not d['Test_Time(s)'].is_monotonic_increasing:raise RuntimeError('Test clock reset within workbook')
        workbooks.append(dict(path=path,date=workbook_date(path),frame=d))
    kept,workbook_audit=order_and_deduplicate(workbooks)
    candidates=[];missing=[];curves={};raw_candidates=sum(sum(1 for _ in candidate_segments(w['frame'])) for w in workbooks)
    for w in kept:
        d=w['frame'];seen=set()
        for g,near in candidate_segments(d):
            row,time,v=segment_record(d,g,w['path'].name,near)
            if row['source_cycle_index'] in seen:raise RuntimeError('Multiple main-discharge segments in one local cycle; review required')
            seen.add(row['source_cycle_index']);candidates.append(row);curves[(w['path'].name,row['source_cycle_index'])]=(time,v)
        for cycle in sorted(set(d.Cycle_Index)-seen):
            g=d.loc[d.Cycle_Index.eq(cycle)]
            missing.append(dict(cell_id='CS2-35',source_workbook=w['path'].name,source_cycle_index=int(cycle),source_step_index=int(g.Step_Index.iloc[-1]),start_timestamp=g.Date_Time.iloc[0],end_timestamp=g.Date_Time.iloc[-1],sample_count=len(g),candidate_main_discharge=False,rejection_reason='no_main_discharge_segment_in_local_cycle;unfinished_workbook_tail' if cycle==d.Cycle_Index.iloc[-1] else 'no_main_discharge_segment_in_local_cycle'))
    candidates=pd.DataFrame(candidates)
    print('Observed endpoints before completion rule:\n'+candidates.cutoff_final_voltage_v.describe(percentiles=[.01,.05,.5,.95,.99]).to_string(),flush=True)
    rule=completion_rule(candidates)
    for idx,row in candidates.iterrows():
        reasons=row.rejection_reason.split(';') if row.rejection_reason else []
        if row.cutoff_final_voltage_v>rule['completion_upper_voltage_v']:reasons.append('final_voltage_above_empirical_cutoff_cluster')
        if row.next_step_index!=8:reasons.append('no_observed_transition_to_post_discharge_rest')
        candidates.loc[idx,'rejection_reason']=';'.join(reasons)
    accepted=candidates.loc[candidates.rejection_reason.eq('')].sort_values(['start_timestamp','end_timestamp','source_workbook','source_cycle_index']).copy().reset_index(drop=True)
    rejected=pd.concat([candidates.loc[candidates.rejection_reason.ne('')],pd.DataFrame(missing)],ignore_index=True)
    if accepted.empty:raise RuntimeError('No accepted discharges')
    accepted.insert(1,'global_cycle',np.arange(1,len(accepted)+1))
    accepted['capacity_retention']=accepted.capacity_ah/accepted.capacity_ah.iloc[0]
    accepted['soh_nominal']=accepted.capacity_ah/NOMINAL_AH
    accepted['nominal_capacity_ah']=NOMINAL_AH
    # Preserve useful boundary evidence, but keep rejection-only bookkeeping out of accepted features.
    accepted=accepted.drop(columns=['rejection_reason','candidate_main_discharge','near_1c','end_of_file','next_step_index'])
    assert accepted.global_cycle.tolist()==list(range(1,len(accepted)+1))
    assert not accepted.duplicated(['source_workbook','source_cycle_index']).any()
    assert accepted.source_step_index.eq(7).all()
    assert accepted.start_timestamp.is_monotonic_increasing
    assert (accepted.end_timestamp.shift()<accepted.start_timestamp).iloc[1:].all()
    assert accepted.source_workbook.isin(workbook_audit.loc[workbook_audit.included,'source_workbook']).all()
    boundaries=[]
    for i in range(1,len(accepted)):
        a,b=accepted.iloc[i-1],accepted.iloc[i]
        if a.source_workbook!=b.source_workbook:
            boundaries.append(dict(previous_workbook=a.source_workbook,next_workbook=b.source_workbook,previous_global_cycle=int(a.global_cycle),next_global_cycle=int(b.global_cycle),gap_hours=(b.start_timestamp-a.end_timestamp).total_seconds()/3600,previous_capacity_ah=a.capacity_ah,next_capacity_ah=b.capacity_ah,capacity_jump_ah=b.capacity_ah-a.capacity_ah,capacity_jump_pct=100*(b.capacity_ah/a.capacity_ah-1)))
    boundaries=pd.DataFrame(boundaries)
    PROCESSED.parent.mkdir(parents=True,exist_ok=True);accepted.to_csv(PROCESSED,index=False)
    rejected.to_csv(ROOT/'results/calce_cs2_35_rejected_cycles.csv',index=False)
    workbook_audit.to_csv(OUT/'workbook_audit.csv',index=False);candidates.to_csv(OUT/'candidate_discharge_audit.csv',index=False);boundaries.to_csv(OUT/'workbook_boundary_audit.csv',index=False)
    (OUT/'completion_rule.json').write_text(json.dumps(rule,indent=2),encoding='utf-8')
    plots(accepted,curves)
    after=nasa_hashes();assert before==after
    assert raw_before=={p.name:sha(p) for p in RAW.glob('*.xlsx')}
    integrity=dict(nasa_artifacts_unchanged=True,nasa_before=before,nasa_after=after,raw_workbook_hashes=raw_before,raw_workbooks_unchanged=True,accepted_rows=len(accepted),unique_global_cycles=True,no_duplicate_source_cycles=True,chronological_nonoverlapping_discharge_intervals=True,no_models_trained=True)
    (OUT/'integrity_checks.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
    statscols=['starting_voltage_v','cutoff_final_voltage_v','mean_current_a','duration_s','capacity_ah','capacity_integration_error_pct','sample_count','first_sample_elapsed_s','pre_step_to_onset_gap_s']
    stats=candidates[statscols].describe(percentiles=[.01,.05,.5,.95,.99]).T.reset_index(names='quantity')
    counts=Counter(reason for reasons in rejected.rejection_reason for reason in reasons.split(';'))
    error=accepted.capacity_integration_error_pct.abs()
    report=['# Independent CALCE CS2-35 discharge extraction',
            f'Workbooks: {len(workbooks)}. Unique channel datasets retained: {len(kept)}. Raw candidate main-discharge segments: {raw_candidates}; after duplicate exclusion: {len(candidates)}. Accepted complete discharges: {len(accepted)}. Rejected candidates: {int(candidates.rejection_reason.ne("").sum())}; additional local cycles without a main-discharge segment: {len(missing)}; total rejected/incomplete local cycles: {len(rejected)}.',
            '## Chronology and duplicates','Workbooks are ordered primarily by first channel measurement timestamp. Exact timestamp ties are resolved by filename date, then filename. Content fingerprints are SHA-256 of a canonical serialization of all 17 channel columns in original measurement order, not workbook bytes. Thus the earlier dated copy is kept when duplicate acquisitions have identical measurement intervals. Raw workbooks are never deleted. No global cycle offsets are inferred from reset local indices.',md(workbook_audit),
            '## Identification and empirical completion',f'All near-1C candidate segments have step distribution: {candidates.loc[candidates.near_1c,"source_step_index"].value_counts().to_dict()}. Main discharge is confirmed and locked to step 7 for this CS2-35 reconstruction, corroborated by current near -1.1 A, falling voltage and increasing counter. The ±10% current neighborhood is only a mode-identification check; the actual distribution is reported below. Tiny negative diagnostic currents at steps 6/9 are not candidates.',md(stats),json.dumps(rule,indent=2),
            'Completion selection was made after inspecting all candidate endpoints. The reference step-7-to-step-8 cluster lies immediately below the documented 2.7 V cutoff; therefore no positive voltage tolerance is needed. Above-cluster endpoints and missing post-discharge transitions are rejected. End-of-file under discharge current is rejected independently of final voltage. At least three samples are required to characterize a curve and integrate more than one interval. Missing/nonfinite measurements, nonpositive counter increments, nonpositive duration/capacity, inconsistent within-step clocks or physically inconsistent current-duration/capacity envelopes are rejected. The 1 micro-Ah envelope allowance is numerical, not a capacity-replacement rule.',
            '## Capacity and timing definitions','capacity_ah = final cumulative discharge counter − last pre-step counter from the same local cycle and workbook. This baseline includes charge delivered before the first discharge sample. Counters are never differenced across files, and statistics sheets are not used for capacity extraction. Current capacity is |integral I(t) dt|/3600 using trapezoidal integration over the monotonic Test_Time clock. The first observed current is held from the step onset to the first sample; this explicit constant-current assumption is cross-checked against the independent counter. No counter capacity is automatically replaced.',
            'duration_s runs from inferred step onset (first Test_Time minus first Step_Time) to the last discharge sample. start_timestamp is the first wall-clock timestamp minus its Step_Time, so onset is inferred at the wall-clock clock resolution, not an exactly observed timestamp. end_timestamp and first_sample_timestamp retain recorded dates. Wall-clock and test clocks may differ slightly; elapsed features/integration use the test clock. time_to_3_4v_s uses the first bracketing voltage samples with linear interpolation; an already-below-threshold first sample is left-censored (NaN). Voltage/current means are arithmetic sample means; no temperature features are constructed.',
            f'Transition-clock diagnostic: inferred onset minus preceding recorded Test_Time ranges from {candidates.pre_step_to_onset_gap_s.min():.9g} to {candidates.pre_step_to_onset_gap_s.max():.9g} seconds. A preliminary 1 ms negative-offset check incorrectly flagged otherwise complete traces; it was replaced by validating strictly increasing recorded Test_Time and the same-cycle pre-step provenance. These observed approximately +/-30 ms clock offsets are retained, not imputed or corrected. Their maximum conservative current-capacity effect on accepted records is {(accepted.pre_step_to_onset_gap_s.abs()*accepted.min_current_a.abs()/3600).max():.9g} Ah; the independent integration agreement below supports treating them as timing uncertainty, not incomplete discharge.',
            f'First accepted capacity: {accepted.capacity_ah.iloc[0]:.12g} Ah; final: {accepted.capacity_ah.iloc[-1]:.12g} Ah. Capacity range: {accepted.capacity_ah.min():.12g}–{accepted.capacity_ah.max():.12g} Ah. First/final retention: {accepted.capacity_retention.iloc[0]:.12g}/{accepted.capacity_retention.iloc[-1]:.12g}; range {accepted.capacity_retention.min():.12g}–{accepted.capacity_retention.max():.12g}. Retention is normalized to the first accepted complete discharge after ordering. soh_nominal = capacity_ah/1.1 is nominal-capacity-normalized SOH, not an EOL label. 1.1 Ah is retained as nominal metadata only.',
            f'Counter/current absolute percentage disagreement: median {error.median():.9g}%, P95 {error.quantile(.95):.9g}%, maximum {error.max():.9g}%. Signed error is 100×(integrated−counter)/counter. Missing 3.4 V crossing times among accepted cycles: {accepted.time_to_3_4v_s.isna().sum()}.',
            '## Rejected/incomplete cycles',md(pd.DataFrame(counts.items(),columns=['reason','count'])),md(rejected[['source_workbook','source_cycle_index','source_step_index','candidate_main_discharge','rejection_reason']]),
            '## Workbook-boundary discontinuities',md(boundaries),'Every boundary is reported without smoothing or automatic correction. Differences can reflect storage/rest recovery, changed acquisition conditions or interruptions; this extraction does not assign causal explanations or splice separate acquisitions into one discharge. The original source indices and workbook names remain available.',
            '## Limitations and validation','The earliest three single-cycle acquisitions are included because they satisfy the same discharge criteria; whether a later study excludes them as characterization runs is a separate protocol decision. Duplicate channel data are removed regardless of workbook-byte differences. No unavailable cycles are invented across recording gaps. A full discharge means an observed termination meeting this empirical rule, not independent certification of a particular electrochemical health state. The unsampled initial current interval and wall-clock precision remain explicit measurement limitations.',
            'The capacity trajectory also contains isolated downward dips followed by recovery within workbooks. These cycles remain included when they reach the cutoff, transition to rest and pass counter/current checks. Their cause (for example prior charging or operating conditions) is unresolved. Completion does not establish identical initial charge state, and no outlier smoothing, fault labeling or exclusion based solely on low capacity was performed. Counter/current agreement is a numerical consistency check on the recorded trace, not independent electrochemical ground truth.',
            f'All {len(before)} NASA model/configuration/result/feature-definition/processed-data artifact hashes match before/after extraction; all {len(raw_before)} raw CALCE hashes match. Unique continuous global indices, unique source cycles, chronological nonoverlapping intervals, expected step and duplicate exclusion assertions passed. NASA data were accessed only for integrity hashing; no NASA artifact was modified. No training, relative features, other CALCE cells, temperature data or EOL classification were produced.',
            '## Files','scripts/extract_calce_cs2_35.py; data/processed/calce/CS2_35_discharge_features.csv; results/calce_cs2_35_extraction.md; results/calce_cs2_35_rejected_cycles.csv; results/calce_cs2_35/ (workbook/candidate/boundary audits, empirical rule, integrity hashes); figures/calce/cs2_35/ (four trajectory figures and representative early/middle/late discharge curves).']
    (ROOT/'results/calce_cs2_35_extraction.md').write_text('\n\n'.join(report),encoding='utf-8')
    print(json.dumps(dict(accepted=len(accepted),candidates=len(candidates),rejected=len(rejected),duplicate_workbooks=int((~workbook_audit.included).sum()),capacity_min=accepted.capacity_ah.min(),capacity_max=accepted.capacity_ah.max(),first_capacity=accepted.capacity_ah.iloc[0],final_capacity=accepted.capacity_ah.iloc[-1],retention_min=accepted.capacity_retention.min(),retention_max=accepted.capacity_retention.max(),integration_median_abs_pct=error.median(),integration_max_abs_pct=error.max(),nasa_hashes_unchanged=len(before)),indent=2),flush=True)


if __name__=='__main__':main()
