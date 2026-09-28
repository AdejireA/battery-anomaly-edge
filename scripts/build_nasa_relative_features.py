"""Strict prior-cycle baselines, saved separately for development cells only."""

import numpy as np
import pandas as pd

try:
    from .nasa_development import ROOT, read_config, load_development_data
except ImportError:
    from nasa_development import ROOT, read_config, load_development_data

MANIFEST = 'nasa_relative_feature_manifest.json'


def build_relative_features(data, windows=None, *, allowed_cells=('B0005', 'B0006', 'B0007')):
    config = read_config(MANIFEST)
    windows = config['history_windows'] if windows is None else windows
    if not set(data.cell_id).issubset(set(allowed_cells)):
        raise ValueError('Cell outside explicitly authorized feature-build scope')
    frames = []
    for cell, source in data.groupby('cell_id', sort=False):
        source = source.sort_values('cycle').copy()
        if not np.array_equal(np.diff(source.cycle), np.ones(len(source)-1)):
            raise ValueError('Expected consecutive unique cycles per cell')
        additions = {}
        for k in windows:
            if k not in config['history_windows']:
                raise ValueError('Unplanned history window')
            for feature in config['base_features']:
                values = source[feature].to_numpy(dtype=float)
                if np.isinf(values).any():
                    raise ValueError('Infinite base feature')
                medians, mads = np.full(len(values), np.nan), np.full(len(values), np.nan)
                if len(values) > k:
                    # Row j covers j..j+k-1 and is assigned to current row j+k.
                    history = np.lib.stride_tricks.sliding_window_view(values, k)[:-1]
                    medians[k:] = np.median(history, axis=1)
                    mads[k:] = np.median(np.abs(history - medians[k:, None]), axis=1)
                median = pd.Series(medians, index=source.index)
                mad = pd.Series(mads, index=source.index)
                residual = source[feature] - median
                prefix = f'{feature}_prior{k}'
                additions[prefix + '_median'] = median
                additions[prefix + '_mad'] = mad
                additions[prefix + '_residual'] = residual
                additions[prefix + '_robust_residual'] = residual / (config['mad_scale'] * mad + config['epsilon'])
            additions[f'capacity_slope_change_prior{k}_ah_per_cycle'] = additions[f'capacity_slope_5_prior{k}_residual']
        frames.append(pd.concat([source, pd.DataFrame(additions, index=source.index)], axis=1))
    return pd.concat(frames, ignore_index=True)


def save_relative(data):
    frame = build_relative_features(data)
    output = ROOT / 'data/processed/nasa_relative'
    output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output / 'nasa_development_relative_features.csv', index=False)
    for cell, group in frame.groupby('cell_id'):
        group.to_csv(output / f'{cell}_relative_features.csv', index=False)
    return frame


if __name__ == '__main__':
    result = save_relative(load_development_data())
    print(f'Saved {len(result)} development rows, preserving original fields; no test-cell file opened.')
