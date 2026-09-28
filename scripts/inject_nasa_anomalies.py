"""Evaluation-only copies of B0007; frozen protocol, no calibration or fitting."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .nasa_development import ROOT, load_development_data, read_config
except ImportError:
    from nasa_development import ROOT, load_development_data, read_config


def thermal_valid(frame):
    fields = ['start_temp_c', 'mean_temp_c', 'max_temp_c', 'delta_temp_c']
    return (np.isfinite(frame[fields].to_numpy()).all()
            and frame.max_temp_c.ge(frame.mean_temp_c).all()
            and frame.max_temp_c.ge(frame.start_temp_c).all()
            and np.allclose(frame.delta_temp_c, frame.max_temp_c - frame.start_temp_c, atol=1e-8))


def perturb_window(clean, family, severity, start, protocol, channel='', sign=0, *, authorized_cell='B0007'):
    """Return a copied window or raise ValueError on a frozen physical guard.

    A1 computes only required history plus ramp. No post-ramp observations are
    emitted, so endpoint loss is not followed by a synthetic recovery.
    """
    if set(clean.cell_id) != {authorized_cell}:
        raise ValueError('Cell outside explicitly authorized injection scope')
    spec = protocol['families'][family]
    length = spec.get('window_cycles', 5)
    if start < 0 or start + length > len(clean):
        raise ValueError('Incomplete window')
    source = clean.iloc[start:start + length]
    window = source.copy(deep=True)
    params = spec['severity'][severity]
    if window[spec['affected_features']].isna().any().any():
        raise ValueError('Missing required anomaly feature')
    if family.startswith('A1_'):
        if start < 4:
            raise ValueError('A1 needs four prior cycles')
        history = clean.iloc[start - 4:start + length].capacity_retention.to_numpy(copy=True)
        history[4:] -= params['retention_total_decrease'] * np.arange(length) / (length - 1)
        if not np.isfinite(history).all() or (history <= 0).any():
            raise ValueError('Nonpositive/missing A1 retention')
        window['capacity_retention'] = history[4:]
        capacity = history * clean.capacity_ah.iloc[0]
        slopes = np.array([np.dot(np.arange(-2, 3), capacity[j:j + 5]) / 10 for j in range(length)])
        # Zero-offset onset is an exact clean observation, not a floating-point anomaly.
        slopes[0] = source.capacity_slope_5.iloc[0]
        window['capacity_slope_5'] = slopes
    elif family.startswith('A2_'):
        cols = list(params)
        if (source[cols] <= 0).any().any() or (source.time_to_3_4v_s > source.duration_s).any():
            raise ValueError('Invalid source timing or voltage')
        for feature, values in params.items():
            window[feature] *= values['factor']
        if (window.time_to_3_4v_s > window.duration_s).any():
            raise ValueError('Crossing after discharge end')
        if not window.mean_voltage_v.between(window.min_voltage_v, window.max_voltage_v).all():
            raise ValueError('Voltage outside source envelope')
    elif family.startswith('A3_'):
        if not thermal_valid(source):
            raise ValueError('Invalid source thermal relationships')
        for feature, amount in params.items():
            window[feature] += amount
        if not thermal_valid(window):
            raise ValueError('Invalid altered thermal relationships')
    elif family.startswith('A4_'):
        if channel not in spec['primary_channels'] or sign not in [-1, 1]:
            raise ValueError('A4 requires one frozen primary channel and sign')
        offset = sign * params[channel] * np.arange(length) / (length - 1)
        if channel == 'mean_voltage_v':
            window[channel] += offset
            if not window.mean_voltage_v.between(window.min_voltage_v, window.max_voltage_v).all():
                raise ValueError('Voltage drift outside source envelope')
        else:
            if not thermal_valid(source):
                raise ValueError('Invalid source thermal relationships')
            for feature in ['start_temp_c', 'mean_temp_c', 'max_temp_c']:
                window[feature] += offset
            if not thermal_valid(window):
                raise ValueError('Invalid altered thermal relationships')
    else:
        raise ValueError('Unknown anomaly family')
    pd.testing.assert_frame_equal(window[protocol['protected_fields']], source[protocol['protected_fields']])
    window['source_cell'] = source.cell_id
    window['source_cycle'] = source.cycle
    window['anomaly_family'] = family
    window['severity'] = severity
    window['channel'] = channel or 'joint'
    window['drift_sign'] = sign
    window['scenario_id'] = f'{family}_{severity}_{channel or "joint"}_{sign}_{int(source.cycle.iloc[0]):03d}'
    window['window_start_cycle'] = int(source.cycle.iloc[0])
    window['offset_in_window'] = np.arange(length)
    window['is_synthetic_anomaly'] = True
    if family.startswith(('A1_', 'A4_')):
        window.loc[window.index[0], 'is_synthetic_anomaly'] = False
    return window


def generate_validation_copies(clean, protocol, min_source_cycle=1):
    """Optionally restrict entire emitted windows to post-calibration cycles.

    Earlier clean A1 history is read only to compute the causal slope; it is
    never perturbed or emitted. Default preserves the original Phase 4 run.
    """
    if set(clean.cell_id) != {'B0007'} or clean.cycle.tolist() != list(range(1, 169)):
        raise ValueError('Injection requires the complete ordered clean B0007 trajectory')
    original = clean.copy(deep=True)
    if not isinstance(min_source_cycle, int) or not 1 <= min_source_cycle <= len(clean):
        raise ValueError('Invalid first evaluation source cycle')
    copies, counts = [], []
    for family, spec in protocol['families'].items():
        variants = [(c, s) for c in spec['primary_channels'] for s in [-1, 1]] if family.startswith('A4_') else [('', 0)]
        for severity in spec['severity']:
            for channel, sign in variants:
                rejected = {}
                accepted = 0
                for start in range(min_source_cycle - 1, len(clean) - spec.get('window_cycles', 5) + 1):
                    try:
                        copied = perturb_window(clean, family, severity, start, protocol, channel, sign)
                    except ValueError as error:
                        rejected[str(error)] = rejected.get(str(error), 0) + 1
                        continue
                    copies.append(copied)
                    accepted += 1
                counts.append({'anomaly_family': family, 'severity': severity, 'channel': channel or 'joint',
                               'drift_sign': sign, 'accepted_windows': accepted, 'rejected_windows': sum(rejected.values()),
                               'rejection_reasons': json.dumps(rejected, sort_keys=True)})
    pd.testing.assert_frame_equal(clean, original)
    return pd.concat(copies, ignore_index=True), pd.DataFrame(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results/nasa_model_validation')
    args = parser.parse_args()
    data = load_development_data()
    clean = data.loc[data.cell_id.eq('B0007')].reset_index(drop=True)
    copies, counts = generate_validation_copies(clean, read_config('anomaly_injection_protocol.json'))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    copies.to_csv(args.output_dir / 'B0007_synthetic_evaluation_copies.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    counts.to_csv(args.output_dir / 'injection_window_counts.csv', index=False)
    print(counts.to_string(index=False))
    print(f'Saved {len(copies)} evaluation-only rows; clean source unchanged.')


if __name__ == '__main__':
    main()
