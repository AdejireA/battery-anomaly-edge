"""Shared CALCE CS2 extraction preserving the validated CS2-35 calculations."""
import sys
sys.dont_write_bytecode=True
import json
import re
from datetime import date
from collections import Counter
import numpy as np
import pandas as pd
import extract_calce_cs2_35 as base

ROOT=base.ROOT
CELLS=['CS2-35','CS2-36','CS2-37','CS2-38']
OUT=ROOT/'results/calce_cells'


def filename_date(path,cell):
    match=re.fullmatch(re.escape(cell.replace('-','_'))+r'_(\d{1,2})_(\d{1,2})_(\d{2,4})',path.stem)
    if not match:raise ValueError(f'Unexpected cell/filename: {path.name} for {cell}')
    m,d,y=map(int,match.groups());return date(y+2000 if y<100 else y,m,d)


def check_inputs():
    inventory={c:list((ROOT/'data/raw/calce'/c.replace('-','_')).glob('*.xlsx')) for c in CELLS}
    missing=[c for c,p in inventory.items() if not p]
    if missing:raise RuntimeError(f'Missing extracted workbook folders: {missing}; no search elsewhere')
    return inventory


def validate_output(data,cell):
    assert set(data.cell_id)=={cell}
    assert data.global_cycle.tolist()==list(range(1,len(data)+1))
    assert data.start_timestamp.is_monotonic_increasing
    assert (data.end_timestamp.shift()<data.start_timestamp).iloc[1:].all()
    assert data.capacity_ah.gt(0).all()
    assert data.source_step_index.eq(7).all()
    assert data.cutoff_final_voltage_v.le(2.7).all()
    assert not data.duplicated(['source_workbook','source_cycle_index']).any()
    # Review tolerance, not a capacity correction or an extra selection criterion.
    if data.capacity_integration_error_pct.abs().max()>.01:
        raise ValueError('Integration disagreement exceeds 0.01% CS2-35-validated review tolerance')


def process_cell(cell,paths):
    output=OUT/cell.replace('-','_');output.mkdir(parents=True,exist_ok=True)
    workbooks=[];structures=[]
    for path in paths:
        print(f'{cell}: {path.name}',flush=True)
        dated=filename_date(path,cell);channels=[]
        for name,d,meta in base.read_sheets(path):
            structures.append(dict(workbook=path.name,sheet=name,rows=len(d),columns=json.dumps(d.columns.tolist()),header_row=meta['header_row']))
            if meta.get('cycling_data'):channels.append((name,d))
        if len(channels)!=1:raise ValueError(f'{path.name}: expected exactly one channel trace; found {len(channels)}')
        name,d=channels[0];d=d.reset_index(drop=True)
        if list(d.columns)!=base.FINGERPRINT_COLUMNS:raise ValueError(f'{path.name}: channel schema differs from CS2-35')
        if d.isna().any().any():raise ValueError(f'{path.name}: missing channel values need review')
        if not d.Date_Time.is_monotonic_increasing or not d['Test_Time(s)'].is_monotonic_increasing:raise ValueError(f'{path.name}: nonchronological source')
        workbooks.append(dict(path=path,date=dated,frame=d))
    pd.DataFrame(structures).to_csv(output/'workbook_structure.csv',index=False)
    kept,wa=base.order_and_deduplicate(workbooks)
    wa.to_csv(output/'workbook_audit.csv',index=False)
    rows=[];missing=[]
    for w in kept:
        d=w['frame'];seen=set()
        for g,near in base.candidate_segments(d):
            r,_,_=base.segment_record(d,g,w['path'].name,near,cell_id=cell)
            if r['source_cycle_index'] in seen:raise ValueError('Repeated discharge segments within a local cycle')
            seen.add(r['source_cycle_index']);rows.append(r)
        for cycle in sorted(set(d.Cycle_Index)-seen):
            g=d.loc[d.Cycle_Index.eq(cycle)]
            missing.append(dict(cell_id=cell,source_workbook=w['path'].name,source_cycle_index=int(cycle),source_step_index=int(g.Step_Index.iloc[-1]),start_timestamp=g.Date_Time.iloc[0],end_timestamp=g.Date_Time.iloc[-1],sample_count=len(g),candidate_main_discharge=False,rejection_reason='no_main_discharge_segment_in_local_cycle;unfinished_workbook_tail' if cycle==d.Cycle_Index.iloc[-1] else 'no_main_discharge_segment_in_local_cycle'))
    candidates=pd.DataFrame(rows)
    candidates.to_csv(output/'candidate_discharge_audit.csv',index=False)
    steps=candidates.loc[candidates.near_1c,'source_step_index'].value_counts().to_dict()
    if set(steps)!={7}:raise ValueError(f'Near-1C current occurs in unexpected steps: {steps}')
    rule=base.completion_rule(candidates);rule['cell_id']=cell
    for idx,r in candidates.iterrows():
        reasons=r.rejection_reason.split(';') if r.rejection_reason else []
        if r.cutoff_final_voltage_v>rule['completion_upper_voltage_v']:reasons.append('final_voltage_above_empirical_cutoff_cluster')
        if r.next_step_index!=8:reasons.append('no_observed_transition_to_post_discharge_rest')
        candidates.loc[idx,'rejection_reason']=';'.join(reasons)
    candidates.to_csv(output/'candidate_discharge_audit.csv',index=False)
    accepted=candidates.loc[candidates.rejection_reason.eq('')].sort_values(['start_timestamp','end_timestamp','source_workbook','source_cycle_index']).reset_index(drop=True).copy()
    rejected=pd.concat([candidates.loc[candidates.rejection_reason.ne('')],pd.DataFrame(missing)],ignore_index=True)
    accepted.insert(1,'global_cycle',np.arange(1,len(accepted)+1))
    accepted['capacity_retention']=accepted.capacity_ah/accepted.capacity_ah.iloc[0]
    accepted['soh_nominal']=accepted.capacity_ah/1.1;accepted['nominal_capacity_ah']=1.1
    accepted=accepted.drop(columns=['rejection_reason','candidate_main_discharge','near_1c','end_of_file','next_step_index'])
    validate_output(accepted,cell)
    target=ROOT/'data/processed/calce'/f'{cell.replace("-","_")}_discharge_features.csv'
    if cell=='CS2-35':
        previous=pd.read_csv(target,parse_dates=['start_timestamp','end_timestamp','first_sample_timestamp'])
        pd.testing.assert_frame_equal(previous,accepted,check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-12)
        # Preserve validated CS2-35 file bytes once numerical/schema equality is proved.
    else:accepted.to_csv(target,index=False)
    rejected.to_csv(ROOT/'results'/f'calce_{cell.lower().replace("-","_")}_rejected_cycles.csv',index=False)
    (output/'completion_rule.json').write_text(json.dumps(rule,indent=2),encoding='utf-8')
    delta=accepted.capacity_ah.diff();boundary=accepted.source_workbook.ne(accepted.source_workbook.shift())&delta.notna()
    changes=accepted[['global_cycle','source_workbook','source_cycle_index','capacity_ah']].copy()
    changes['delta_capacity_ah']=delta;changes['delta_capacity_pct']=accepted.capacity_ah.pct_change()*100;changes['workbook_boundary']=boundary
    changes.to_csv(output/'capacity_changes.csv',index=False)
    absolute_error=accepted.capacity_integration_error_pct.abs()
    summary=dict(cell_id=cell,workbooks=len(workbooks),retained_workbooks=len(kept),duplicate_workbooks=wa.loc[~wa.included,['source_workbook','duplicate_of']].to_dict('records'),unique_candidate_discharges=len(candidates),accepted=len(accepted),rejected=len(rejected),rejected_candidates=int(candidates.rejection_reason.ne('').sum()),cycles_without_discharge=len(missing),rejection_reasons=dict(Counter(x for s in rejected.rejection_reason for x in s.split(';'))),dominant_step=7,near_1c_step_counts=steps,mean_discharge_current_a=float(accepted.mean_current_a.mean()),complete_final_voltage=accepted.cutoff_final_voltage_v.describe(percentiles=[.05,.5,.95]).to_dict(),capacity_min=float(accepted.capacity_ah.min()),capacity_max=float(accepted.capacity_ah.max()),first_capacity=float(accepted.capacity_ah.iloc[0]),final_capacity=float(accepted.capacity_ah.iloc[-1]),first_retention=1.,final_retention=float(accepted.capacity_retention.iloc[-1]),integration_median_abs_pct=float(absolute_error.median()),integration_max_abs_pct=float(absolute_error.max()),largest_positive_change_ah=float(delta.max()),largest_negative_change_ah=float(delta.min()),largest_boundary_jump=changes.loc[changes.workbook_boundary].iloc[changes.loc[changes.workbook_boundary,'delta_capacity_ah'].abs().argmax()].to_dict(),missing_values=accepted.isna().sum().to_dict(),sheet_names=pd.DataFrame(structures).sheet.value_counts().to_dict(),integration_review_tolerance_pct=.01)
    (output/'summary.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    report=[f'# {cell} extraction validation',json.dumps(summary,indent=2,default=str),'## Rejected local cycles',base.md(rejected[['source_workbook','source_cycle_index','source_step_index','rejection_reason']]),'## Method', 'Shared validated CS2-35 calculations: timestamp-first workbook order; canonical 17-column fingerprints; within-workbook pre-step counter subtraction; current trapezoidal integration including initial sample gap; observed 2.7 V cluster with transition to step 8; no counter replacement, temperature, smoothing, fault/EOL labeling, trajectory-relative features or ML. Small step/test-clock onset offsets remain audited. Integration review tolerance 0.01% exceeds the validated CS2-35 maximum 0.00393%; any violation stops output publication for that cell. The initial three characterization cycles are retained when complete.']
    (ROOT/'results'/f'calce_{cell.lower().replace("-","_")}_extraction_validation.md').write_text('\n\n'.join(report),encoding='utf-8')
    print(f'{cell}: accepted {len(accepted)}, rejected {len(rejected)}',flush=True)
    return accepted,summary


def main():
    inventory=check_inputs();OUT.mkdir(parents=True,exist_ok=True)
    before=base.nasa_hashes();raw_before={str(p.relative_to(ROOT)):base.sha(p) for paths in inventory.values() for p in paths}
    frames=[];summaries=[];failures={}
    for cell,paths in inventory.items():
        try:
            data,summary=process_cell(cell,paths);frames.append(data);summaries.append(summary)
        except Exception as error:
            failures[cell]=f'{type(error).__name__}: {error}';print(f'{cell}: STOPPED: {error}',flush=True)
    after=base.nasa_hashes();assert before==after
    assert raw_before=={str(p.relative_to(ROOT)):base.sha(p) for paths in inventory.values() for p in paths}
    record=dict(nasa_before=before,nasa_after=after,nasa_unchanged=True,raw_hashes=raw_before,raw_unchanged=True,failures=failures,summaries=summaries,no_ml=True)
    (OUT/'extraction_integrity.json').write_text(json.dumps(record,indent=2,default=str),encoding='utf-8')
    if failures:
        (ROOT/'results/calce_extraction_discrepancies.md').write_text('# CALCE assumption discrepancies\n\n'+json.dumps(failures,indent=2),encoding='utf-8')
        raise RuntimeError('Cell assumptions failed; see results/calce_extraction_discrepancies.md; no combined table published')
    pd.concat(frames,ignore_index=True).to_csv(ROOT/'data/processed/calce/calce_cs2_discharge_features.csv',index=False)
    print(json.dumps([dict(cell_id=s['cell_id'],accepted=s['accepted'],rejected=s['rejected']) for s in summaries],indent=2))


if __name__=='__main__':main()
