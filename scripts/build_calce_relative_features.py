"""CALCE development-only prior-ten-cycle features; test cell remains locked."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/calce_experiment_protocol.json'
CELLS=('CS2-35','CS2-36','CS2-37')


def config():return json.loads(CONFIG.read_text())


def load_development():
    frames=[]
    for cell in CELLS:
        d=pd.read_csv(ROOT/f'data/processed/calce/{cell.replace("-","_")}_discharge_features.csv')
        if set(d.cell_id)!={cell}:raise ValueError('Incorrect source cell')
        if d.global_cycle.tolist()!=list(range(1,len(d)+1)):raise ValueError('Incorrect cycle ordering')
        if not pd.to_datetime(d.start_timestamp).is_monotonic_increasing:raise ValueError('Nonchronological source')
        frames.append(d)
    return pd.concat(frames,ignore_index=True)


def features():return [f'{b}_prior10_robust_residual' for b in config()['base_features']]


def build_relative(data):
    if not set(data.cell_id).issubset(CELLS):raise ValueError('Non-development cell forbidden')
    p=config();outputs=[]
    for _,source in data.groupby('cell_id',sort=False):
        source=source.sort_values('global_cycle').copy()
        if not np.all(np.diff(source.global_cycle)==1):raise ValueError('History requires consecutive cycles')
        for base in p['base_features']:
            x=source[base].to_numpy(float);median=np.full(len(x),np.nan);mad=median.copy()
            if np.isinf(x).any():raise ValueError('Infinite base measurement')
            if len(x)>10:
                history=np.lib.stride_tricks.sliding_window_view(x,10)[:-1]
                median[10:]=np.median(history,axis=1)
                mad[10:]=np.median(np.abs(history-median[10:,None]),axis=1)
            source[f'{base}_prior10_median']=median;source[f'{base}_prior10_mad']=mad
            source[f'{base}_prior10_robust_residual']=(x-median)/(p['mad_scale']*mad+p['epsilon'])
        outputs.append(source)
    return pd.concat(outputs,ignore_index=True)


if __name__=='__main__':
    result=build_relative(load_development())
    result.to_csv(ROOT/'data/processed/calce/calce_cs2_relative_features.csv',index=False)
    print(f'{len(result)} development rows only; CS2-38 excluded without reading it.')
