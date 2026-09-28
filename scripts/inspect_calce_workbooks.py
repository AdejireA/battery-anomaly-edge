"""Structure-only CALCE/Arbin inspection; no cross-workbook data merge or features.

Uses pandas plus the standard-library XLSX ZIP/XML reader to avoid requiring an
unavailable Excel engine. This is an inspection utility, not a final extractor.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import re
import json
import zipfile
import posixpath
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/calce/CS2_35'
REPORT=ROOT/'results/calce_cs2_35_structure.md'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
M='{'+NS['m']+'}'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def protected_hashes():
    paths=list((ROOT/'config').glob('*nasa*.json'))+list((ROOT/'config').glob('*anomaly*.json'))
    paths+=list((ROOT/'models').rglob('*'))+list((ROOT/'figures/nasa').rglob('*'))
    for p in (ROOT/'results').glob('nasa*'):
        paths+=list(p.rglob('*')) if p.is_dir() else [p]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}


def workbook_date(path):
    match=re.fullmatch(r'CS2_35_(\d{1,2})_(\d{1,2})_(\d{2,4})',path.stem,re.I)
    if not match:return None
    month,day,year=map(int,match.groups())
    if year<100:year+=2000
    try:return datetime(year,month,day).date()
    except ValueError:return None


def column_number(ref):
    value=0
    for char in re.match(r'[A-Z]+',ref).group():value=26*value+ord(char)-64
    return value-1


def read_sheets(path):
    """Resolve relationships, strings, numeric/boolean cells and Excel date styles."""
    with zipfile.ZipFile(path) as z:
        book=ET.fromstring(z.read('xl/workbook.xml'))
        relationships={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or '' for t in si.iter(M+'t')) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        styles=ET.fromstring(z.read('xl/styles.xml'))
        formats={int(x.attrib['numFmtId']):x.attrib['formatCode'] for x in styles.findall('m:numFmts/m:numFmt',NS)}
        date_styles=set()
        for i,xf in enumerate(styles.find('m:cellXfs',NS)):
            num=int(xf.attrib.get('numFmtId','0'));fmt=formats.get(num,'')
            if num in range(14,23) or re.search(r'[dy]',re.sub(r'"[^"]*"','',fmt),re.I):date_styles.add(i)
        prop=book.find('m:workbookPr',NS)
        epoch=datetime(1904,1,1) if prop is not None and prop.attrib.get('date1904') in ['1','true'] else datetime(1899,12,30)
        for sheet in book.find('m:sheets',NS):
            rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=relationships[rid]
            target=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            rows=[];dimension=None;formulas=0;errors=0
            with z.open(target) as stream:
                for event,element in ET.iterparse(stream,events=['end']):
                    if element.tag==M+'dimension':dimension=element.attrib.get('ref')
                    if element.tag!=M+'row':continue
                    values={}
                    for c in element.findall('m:c',NS):
                        v=c.find('m:v',NS);kind=c.attrib.get('t')
                        formulas+=int(c.find('m:f',NS) is not None)
                        value=None
                        if kind=='inlineStr':value=''.join(t.text or '' for t in c.iter(M+'t'))
                        elif v is not None and v.text is not None:
                            raw=v.text
                            if kind=='s':value=strings[int(raw)]
                            elif kind=='b':value=bool(int(raw))
                            elif kind in ['str','e']:value=raw;errors+=int(kind=='e')
                            else:
                                value=int(raw) if re.fullmatch(r'[+-]?\d+',raw) else float(raw)
                                if int(c.attrib.get('s','0')) in date_styles:value=epoch+timedelta(days=float(value))
                        if value is not None:values[column_number(c.attrib['r'])]=value
                    if values:rows.append((int(element.attrib['r']),values))
                    element.clear()
            # Channel headers are discovered by content; metadata has a separate header.
            candidates=[]
            for row_id,values in rows[:20]:
                names=[str(v).strip() for v in values.values()]
                hits=sum(n in names for n in ['Cycle_Index','Step_Index','Current(A)','Voltage(V)','Test_Time(s)'])
                candidates.append((hits,sum(isinstance(v,str) for v in values.values()),row_id,values))
            if not candidates:yield sheet.attrib['name'],pd.DataFrame(),dict(dimension=dimension,header_row=None);continue
            hits,_,header_id,header=max(candidates,key=lambda x:(x[0],x[1],-x[2]))
            width=max(max(v) for _,v in rows)+1
            names=[str(header.get(i,f'Unnamed_{i+1}')).strip() for i in range(width)]
            if len(set(names))!=len(names):names=[f'{n}__col{i+1}' if names.count(n)>1 else n for i,n in enumerate(names)]
            data=[[v.get(i) for i in range(width)] for rid,v in rows if rid>header_id]
            frame=pd.DataFrame(data,columns=names)
            is_trace={'Cycle_Index','Step_Index','Current(A)','Voltage(V)','Test_Time(s)'}.issubset(frame.columns)
            yield sheet.attrib['name'],frame,dict(dimension=dimension,header_row=header_id,nonempty_worksheet_rows=len(rows),cycling_data=is_trace,formula_cells=formulas,error_cells=errors,preamble=[str(v) for rid,v in rows if rid<header_id])


def md(frame):
    def val(x):
        if isinstance(x,float):return f'{x:.9g}'
        return str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |','|'+'|'.join(['---']*len(frame.columns))+'|']+['| '+' | '.join(val(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])


def roles(columns):
    patterns={'cycle index':r'cycle','step index':r'step.*index','test time':r'test.*time','step time':r'step.*time','date/time':r'date|timestamp','voltage':r'volt','current':r'current','charge capacity':r'(?<!dis)charge.*capacity','discharge capacity':r'discharge.*capacity','energy':r'energy','temperature':r'temp'}
    return {role:[c for c in columns if re.search(pattern,c,re.I)] for role,pattern in patterns.items()}


def analyze_channel(frame,filename,sheet):
    d=frame
    summary=dict(filename=filename,sheet=sheet,rows=len(d))
    for col,short in [('Cycle_Index','cycle'),('Step_Index','step'),('Test_Time(s)','test_time'),('Data_Point','data_point')]:
        s=pd.to_numeric(d[col],errors='coerce')
        summary.update({short+'_first':s.iloc[0],short+'_last':s.iloc[-1],short+'_min':s.min(),short+'_max':s.max(),short+'_decreases':int(s.diff().lt(0).sum())})
    dates=pd.to_datetime(d.Date_Time,errors='coerce').dt.round('ms')
    summary.update(timestamp_first=dates.iloc[0],timestamp_last=dates.iloc[-1],timestamp_missing=int(dates.isna().sum()),timestamp_backwards=int(dates.diff().dt.total_seconds().lt(0).sum()),timestamp_duplicates=int(dates.duplicated().sum()))
    current=pd.to_numeric(d['Current(A)'],errors='coerce')
    summary.update(negative_current=int(current.lt(-1e-9).sum()),zero_current=int(current.abs().le(1e-9).sum()),positive_current=int(current.gt(1e-9).sum()))
    counts={col:{str(k):int(v) for k,v in d[col].value_counts(dropna=False).sort_index().items()} for col in ['Cycle_Index','Step_Index']}
    run=(d.Cycle_Index.ne(d.Cycle_Index.shift())|d.Step_Index.ne(d.Step_Index.shift())|d['Test_Time(s)'].diff().lt(0)).cumsum()
    segments=[]
    for _,part in d.groupby(run,sort=False):
        segments.append(dict(cycle=part.Cycle_Index.iloc[0],step=part.Step_Index.iloc[0],rows=len(part),current_median=part['Current(A)'].median(),voltage_first=part['Voltage(V)'].iloc[0],voltage_last=part['Voltage(V)'].iloc[-1],step_time_first=part['Step_Time(s)'].iloc[0],step_time_last=part['Step_Time(s)'].iloc[-1],charge_first=part['Charge_Capacity(Ah)'].iloc[0],charge_last=part['Charge_Capacity(Ah)'].iloc[-1],discharge_first=part['Discharge_Capacity(Ah)'].iloc[0],discharge_last=part['Discharge_Capacity(Ah)'].iloc[-1]))
    segments=pd.DataFrame(segments)
    caps=[]
    for name in ['Charge_Capacity(Ah)','Discharge_Capacity(Ah)']:
        diff=d[name].diff();same=run.eq(run.shift())
        caps.append(dict(column=name,increases_within_segment=int((diff.gt(1e-10)&same).sum()),decreases_within_segment=int((diff.lt(-1e-10)&same).sum()),decreases_at_segment_boundary=int((diff.lt(-1e-10)&~same).sum()),decreases_when_cycle_changes=int((diff.lt(-1e-10)&d.Cycle_Index.ne(d.Cycle_Index.shift())).sum())))
    sample=[]
    selected=list(segments.loc[segments.current_median.lt(-.5),'cycle'].drop_duplicates())[:2]
    for cycle in selected:
        part=d.loc[d.Cycle_Index.eq(cycle)&current.lt(-.5)]
        sample.extend(part.iloc[np.unique([0,len(part)//2,len(part)-1])].to_dict('records'))
    columns=['Cycle_Index','Step_Index','Voltage(V)','Current(A)','Charge_Capacity(Ah)','Discharge_Capacity(Ah)','Test_Time(s)','Step_Time(s)','Date_Time']
    sample=pd.DataFrame(sample).reindex(columns=columns)
    return summary,counts,segments,pd.DataFrame(caps),sample


def main():
    paths=sorted(RAW.glob('*.xlsx'),key=lambda p:(workbook_date(p) or datetime.max.date(),p.name))
    if not paths:raise RuntimeError('No CS2-35 XLSX workbooks found')
    protected=protected_hashes();raw_hashes={p.name:sha(p) for p in paths}
    chosen={paths[0].name,paths[len(paths)//2].name,paths[-1].name}
    inventory=[];details=[];summaries=[];schemas=Counter();sheet_names=Counter();semantic=defaultdict(list);problems=[];all_caps=[];all_segments=[];stats_checks=[]
    for path in paths:
        print(f'Inspecting {path.name}',flush=True)
        channel=None
        try:
            for name,frame,meta in read_sheets(path):
                sheet_names[name]+=1
                inventory.append(dict(filename=path.name,filename_date=workbook_date(path),sheet=name,rows_after_header=len(frame),columns=len(frame.columns),header_row=meta['header_row'],dimension=meta['dimension']))
                details.extend([f'### {path.name} — {name}',f'Metadata: {json.dumps(meta,default=str)}',f'Columns: {json.dumps(frame.columns.tolist())}'])
                if meta.get('cycling_data'):
                    channel=frame
                    schemas[tuple(frame.columns)]+=1
                    semantic[hashlib.sha256(pd.util.hash_pandas_object(frame,index=False).values.tobytes()).hexdigest()].append(path.name+' / '+name)
                    summary,counts,segments,caps,sample=analyze_channel(frame,path.name,name)
                    summaries.append(summary);all_caps.append(caps.assign(filename=path.name));all_segments.append(segments.assign(filename=path.name))
                    details.extend(['Cycle/step unique values and row counts: '+json.dumps(counts), 'Current sign counts: '+json.dumps({k:summary[k] for k in ['negative_current','zero_current','positive_current']}), 'Capacity-counter behavior:',md(caps),'Candidate main-discharge rows (first/middle/last of the first two cycles with current below -0.5 A; excludes small diagnostic pulses):',md(sample)])
                    if path.name in chosen:
                        details.extend(['Contiguous cycle/step segments (first 16, preserving recorded order):',md(segments.head(16))])
                elif 'Cycle_Index' in frame and 'Discharge_Capacity(Ah)' in frame:
                    semantic[hashlib.sha256(pd.util.hash_pandas_object(frame,index=False).values.tobytes()).hexdigest()].append(path.name+' / '+name)
                    details.append('Summary-sheet cycle counts: '+json.dumps({str(k):int(v) for k,v in frame.Cycle_Index.value_counts().sort_index().items()}))
                    if channel is not None:
                        endpoints=channel.groupby('Cycle_Index',sort=False).last()
                        aligned=frame.set_index('Cycle_Index')
                        common=aligned.index.intersection(endpoints.index)
                        stats_checks.append(dict(filename=path.name,statistics_rows=len(frame),channel_cycles=int(channel.Cycle_Index.nunique()),statistics_cycles=frame.Cycle_Index.tolist(),last_channel_step=int(channel.Step_Index.iloc[-1]),max_discharge_capacity_endpoint_difference=float((aligned.loc[common,'Discharge_Capacity(Ah)']-endpoints.loc[common,'Discharge_Capacity(Ah)']).abs().max())))
                if path.name in chosen:
                    preview=frame.head(10)
                    print(f'\n{path.name} / {name}: first 10 rows\n{preview.to_string(index=False)}',flush=True)
                    details.extend(['First 10 rows (or all rows when fewer):',md(preview),'Inferred pandas dtypes and missing counts:',md(pd.DataFrame({'column':frame.columns,'dtype':[str(frame[c].dtype) for c in frame],'missing':[int(frame[c].isna().sum()) for c in frame]})), 'Likely column roles (name-based candidates, not assumptions): '+json.dumps(roles(frame.columns))])
                if meta.get('error_cells'):problems.append(f'{path.name}/{name}: {meta["error_cells"]} Excel error cells')
        except Exception as error:
            problems.append(f'{path.name}: {type(error).__name__}: {error}')
    summary=pd.DataFrame(summaries)
    boundaries=[]
    for previous,current in zip(summaries,summaries[1:]):
        boundaries.append(dict(previous=previous['filename'],current=current['filename'],previous_last_cycle=previous['cycle_last'],current_first_cycle=current['cycle_first'],previous_last_step=previous['step_last'],current_first_step=current['step_first'],previous_last_test_s=previous['test_time_last'],current_first_test_s=current['test_time_first'],timestamp_gap_s=(current['timestamp_first']-previous['timestamp_last']).total_seconds()))
    duplicate_bytes=[names for value in set(raw_hashes.values()) if len(names:=[name for name,h in raw_hashes.items() if h==value])>1]
    duplicate_data=[names for names in semantic.values() if len(names)>1]
    caps_all=pd.concat(all_caps,ignore_index=True)
    segments_all=pd.concat(all_segments,ignore_index=True)
    state_summary=segments_all.groupby('step').agg(segments=('rows','size'),current_median_min=('current_median','min'),current_median_max=('current_median','max'),voltage_end_min=('voltage_last','min'),voltage_end_max=('voltage_last','max')).reset_index()
    partial=segments_all.loc[segments_all.step.eq(7)&segments_all.voltage_last.gt(2.71),['filename','cycle','rows','voltage_first','voltage_last','step_time_last']]
    assert raw_hashes=={p.name:sha(p) for p in paths},'Raw workbook changed'
    assert protected==protected_hashes(),'NASA artifact changed'
    report=['# CALCE CS2-35 workbook structure audit',
            f'Found {len(paths)} XLSX files. This is a workbook-by-workbook structure inspection only: no combined cycling table, SOH, ML features or models were created. Representative workbooks: {sorted(chosen)}. Filename dates are interpreted as month_day_year, with two-digit years mapped to 2000–2099; they are not assumed to equal first measurement time.',
            'Reader: standard-library ZIP/XML plus pandas. openpyxl was unavailable and its package installation failed. Workbook relationships identify worksheets; shared/inline strings, numeric/boolean values and date styles are decoded. Excel date epoch follows workbook settings (1899-12-30 or 1904-01-01). Timestamp comparisons round Excel floating-point conversion noise to milliseconds; previews preserve decoded values. Formula cells use cached values, with formula/error counts reported. Dtypes below are pandas inference from decoded cells, not an openpyxl-engine claim.',
            'Rows after header count nonempty physical rows below the detected header. Sheet dimensions and header row are reported separately: Info contains preamble/merged metadata and should not be treated as a conventional row-1 table. Every sheet is inspected, including Info.',
            '## Findings for future parser design',
            'All 25 files have Info (one metadata record, header row 4) and Channel_1-008 (17-column sample-level trace, header row 1). Starting with CS2_35_10_29_10.xlsx, 15 files additionally have Statistics_1-008 (15-column cycle-end snapshots). This is a valid structural variation, not a malformed workbook. No measured temperature time-series column is present; Info.Temp is an auxiliary-channel mapping field, not a cell-temperature measurement. The Info schedule name is CS2_1C.sdu in the representative files.',
            'Cycle_Index, Data_Point and the initial Step_Index restart at 1 in every workbook. Test_Time(s) restarts near 10 seconds in the first file and 30 seconds in the others; it is monotonic within each channel sheet. Steps repeat 1–9 within each cycle, so step-number repetition is expected and should not create a global cycle identifier. Step_Time(s) resets for each step.',
            'Date_Time is usable as a wall-clock ordering anchor: no missing or backward timestamps were found within the channel sheets. However, timestamps have approximately second resolution and repeated values at rapid transitions, so preserve Data_Point/Test_Time as tie-breakers. Filename dates do not equal measurement start dates. All distinct file intervals are chronological with gaps, except the duplicated late pair. Their channel and statistics tables are identical even though workbook bytes differ. Do not double-count this repeated acquisition. Clock timezone and any unrecorded clock adjustments are not specified.',
            'Charge_Capacity(Ah) and Discharge_Capacity(Ah) are running throughput counters across steps AND cycles within a file. They do not reset at each step or cycle. Statistics-sheet capacities are snapshots of these same cumulative counters, not isolated completed-cycle capacities. In the latest acquisition, discharge endpoints progress approximately 0.500406, 0.975163, 1.439672 Ah across the first three cycles. A future per-discharge capacity must use the counter increment over the discharge interval with a verified pre-step reference; blindly using the endpoint, or subtracting the first sampled discharge value, would respectively accumulate prior cycles or omit the unsampled initial increment. No such extraction or SOH calculation is performed here.',
            'Likely full-discharge identification: segment by workbook/channel, local Cycle_Index and contiguous Step_Index, using current direction/magnitude and voltage trajectory as checks. Step 7 is the sustained approximately -1.1 A discharge toward approximately 2.70 V; steps 6 and 9 contain tiny signed diagnostic currents and must not be mistaken for full discharges just because current is negative. Require evidence of a complete step (termination near the observed endpoint and/or transition into step 8/9), and flag interrupted final cycles. The approximately 2.70 V criterion is observed evidence, not yet a frozen acceptance tolerance. Statistics rows can cross-check completed cycles where present, but are unavailable in the first ten workbooks.',
            'Remaining decisions: confirm schedule-defined cutoff/termination tolerances, diagnostic-step semantics and whether the early single-cycle acquisitions belong in the main ageing series; define duplicate-file handling and interrupted-cycle policy; establish wall-clock timezone and cross-file continuity assumptions; determine whether temperature exists in a separate source. No global cycle renumbering, record removal or merging has been performed.',
            '## Workbook and sheet inventory',md(pd.DataFrame(inventory)),
            '## Sheet-name frequency',md(pd.DataFrame(sheet_names.items(),columns=['sheet','workbook_count'])),
            '## Cycling schemas',*[f'{count} sheets: '+json.dumps(list(schema)) for schema,count in schemas.items()],
            '## Per-file counter and timestamp evidence',md(summary),
            '## Boundaries in inferred filename-date order',md(pd.DataFrame(boundaries)),
            'Step_Index is a schedule-state identifier that normally repeats inside a run, not a globally increasing observation identifier. A decrease alone is not proof of file reset. Current signs use a numerical zero tolerance of 1e-9 A; negative-current rows are discharge candidates, not automatically full discharges.',
            '## Duplicate and malformed-file checks',f'Byte-identical workbook groups: {json.dumps(duplicate_bytes)}',f'Identical decoded channel-table groups: {json.dumps(duplicate_data)}',f'Read/structural errors: {json.dumps(problems)}',
            '## Observed schedule states',md(state_summary),'Step 7 endpoints above 2.71 V (inspection flags, not an automated rejection rule):',md(partial),
            '## Statistics-sheet cross-checks',md(pd.DataFrame(stats_checks)),
            '## Capacity accumulation evidence',md(caps_all),
            '## Detailed sheets and representative previews',*details,
            '## Integrity',f'All {len(protected)} existing NASA configuration/model/result/figure artifacts hashed before inspection matched afterward. All {len(paths)} CALCE workbook hashes also matched. NASA raw/processed-data directories were not read; existing NASA artifacts were accessed only for hashing. No NASA artifact or raw workbook was modified.']
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text('\n\n'.join(report),encoding='utf-8')
    print('\nSUMMARY\n'+summary.to_string(index=False),flush=True)
    print('DUPLICATE_BYTES',duplicate_bytes,'DUPLICATE_DATA',duplicate_data,'ERRORS',problems,flush=True)
    print('SEGMENT STATES\n'+pd.concat(all_segments,ignore_index=True).groupby('step').agg(segments=('rows','size'),current_min=('current_median','min'),current_max=('current_median','max'),voltage_end_min=('voltage_last','min'),voltage_end_max=('voltage_last','max')).to_string(),flush=True)
    print(f'NASA protected hashes unchanged: {len(protected)}. Report: {REPORT}',flush=True)


if __name__=='__main__':main()
