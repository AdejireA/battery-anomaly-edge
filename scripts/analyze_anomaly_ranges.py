"""Freeze a B0007-only analytical anomaly protocol; never create injected data."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['capacity_retention', 'capacity_slope_5', 'duration_s', 'time_to_3_4v_s',
            'mean_voltage_v', 'mean_current_a', 'start_temp_c', 'mean_temp_c',
            'max_temp_c', 'delta_temp_c']
MULTIPLIERS = {'mild': 1.5, 'moderate': 3.0, 'strong': 5.0}
UNITS = dict(zip(FEATURES, ['fraction', 'Ah/cycle', 's', 's', 'V', 'A', 'degC', 'degC', 'degC', 'degC']))


def validation_rows(frame):
    # Filter before computing any statistic or provenance hash.
    validation = frame.loc[frame.cell_id.eq('B0007')].sort_values('cycle').copy()
    if len(validation) != 168 or validation.cycle.tolist() != list(range(1, 169)):
        raise ValueError('Expected B0007 cycles 1 through 168 exactly once')
    return validation


def summarize(validation):
    result = {}
    for feature in FEATURES:
        values = validation[feature].dropna()
        if values.empty or not np.isfinite(values).all():
            raise ValueError(f'Invalid calibration values: {feature}')
        median = float(values.median())
        result[feature] = {'count': int(len(values)), 'median': median,
                           'MAD': float((values - median).abs().median()),
                           'mean': float(values.mean()), 'std': float(values.std(ddof=1)),
                           'min': float(values.min()), 'max': float(values.max()),
                           **{f'p{p}': float(values.quantile(p / 100)) for p in [5, 25, 75, 95]}}
        if result[feature]['MAD'] <= 0:
            raise ValueError(f'Zero MAD requires explicit redesign: {feature}')
    return result


def build_protocol(frame):
    v = validation_rows(frame)
    stats = summarize(v)
    raw = {f: {level: k * stats[f]['MAD'] for level, k in MULTIPLIERS.items()} for f in FEATURES}
    initial_capacity = float(v.capacity_ah.iloc[0])
    # Minimum integer duration keeping steady ramp slope <= its own MAD proposal.
    ramp_intervals = math.ceil(initial_capacity * stats['capacity_retention']['MAD'] / stats['capacity_slope_5']['MAD'])
    families = {}
    families['A1_ACCELERATED_DEGRADATION'] = {
        'feature_sets': ['degradation_aware'],
        'affected_features': ['capacity_retention', 'capacity_slope_5'],
        'directions': {'capacity_retention': -1, 'capacity_slope_5': -1},
        'window_cycles': ramp_intervals + 1,
        'rule': 'Retention offset is -a*j/(L-1), j=0..L-1. Recompute causal capacity slope using C0 times altered retention. Persist endpoint loss after the ramp; no artificial recovery. Only ramp cycles are evaluated in this scenario.',
        'severity': {level: {'retention_total_decrease': raw['capacity_retention'][level],
                             'steady_slope_decrease_ah_per_cycle': initial_capacity * raw['capacity_retention'][level] / ramp_intervals}
                     for level in MULTIPLIERS},
        'adjustment': 'Independent slope offsets replaced by slope implied by retention ramp. Ramp duration comes from ratio of validation retention/capacity-slope MADs. At onset the five-cycle slope transitions causally; full decrement applies once all five samples lie on the ramp.',
        'application_guard': 'Use the target cell initial capacity to recompute slope, never its spread to recalibrate severity. Reject windows with nonpositive altered retention or unavailable five-cycle history. Preserve metadata and source health columns; use a temporary calculation array for slope, not an overwritten capacity_ah column.'}
    a2_features = ['time_to_3_4v_s', 'duration_s', 'mean_voltage_v']
    severity = {}
    for level, k in MULTIPLIERS.items():
        severity[level] = {}
        for f in a2_features:
            exponent = k * stats[f]['MAD'] / stats[f]['median']
            factor = math.exp(-exponent)
            severity[level][f] = {'factor': factor, 'decrease_at_validation_median': stats[f]['median'] * (1 - factor),
                                  'decrease_range': [stats[f]['min'] * (1 - factor), stats[f]['max'] * (1 - factor)],
                                  'result_range': [stats[f]['min'] * factor, stats[f]['max'] * factor]}
        if severity[level]['time_to_3_4v_s']['factor'] > severity[level]['duration_s']['factor']:
            raise ValueError('A2 would not guarantee crossing time <= duration')
    families['A2_EARLY_VOLTAGE_COLLAPSE'] = {
        'feature_sets': ['degradation_aware', 'measurement_oriented'], 'affected_features': a2_features,
        'directions': dict.fromkeys(a2_features, -1), 'severity': severity,
        'rule': 'x_prime = x * exp(-k*MAD_validation(x)/median_validation(x)); fixed factor per severity/channel.',
        'adjustment': 'Strong raw additive timing proposal gives negative time_to_3_4v_s. Redesign all three A2 channels with a positive exponential response, whose small-offset limit is the original k*MAD at the median. Time factor <= duration factor preserves time <= duration. No clipping.',
        'application_guard': 'Require positive source duration, voltage and crossing time, and crossing time <= duration. Reject invalid/missing windows. Modified summary voltage must remain between source measured min and max; reject rather than silently clip.'}
    thermal_shared = max(stats['max_temp_c']['MAD'], stats['delta_temp_c']['MAD'])
    families['A3_THERMAL_ABNORMALITY'] = {
        'feature_sets': ['degradation_aware', 'measurement_oriented'],
        'affected_features': ['mean_temp_c', 'max_temp_c', 'delta_temp_c'],
        'directions': dict.fromkeys(['mean_temp_c', 'max_temp_c', 'delta_temp_c'], 1),
        'severity': {level: {'mean_temp_c': k * stats['mean_temp_c']['MAD'],
                             'max_temp_c': k * thermal_shared, 'delta_temp_c': k * thermal_shared}
                     for level, k in MULTIPLIERS.items()},
        'rule': 'Add mean offset; add identical max/delta offsets; hold start temperature fixed.',
        'adjustment': 'Use max(MAD(max_temp), MAD(delta_temp)) for both max and delta to preserve delta=max-start and the proposed heating direction.',
        'application_guard': 'Require max >= mean and max >= start, and delta=max-start before and after. These summary constraints do not establish thermal safety or a physical trace model.'}
    families['A4_SENSOR_DRIFT'] = {
        'feature_sets': ['measurement_oriented', 'degradation_aware'],
        'primary_channels': ['mean_voltage_v', 'mean_temp_c'],
        'affected_features': ['mean_voltage_v', 'mean_temp_c', 'start_temp_c', 'max_temp_c'],
        'directions': {'mean_voltage_v': 'separate positive and negative scenarios', 'mean_temp_c': 'separate positive and negative scenarios'},
        'window_cycles': 10, 'window_rationale': 'Design duration of two five-cycle feature windows; fixed sensitivity scenario, not a measured fault duration.',
        'rule': 'Choose one primary channel and sign per scenario. Offset d_j = sign*a*j/(L-1), j=0..L-1. Temperature drift shifts start/mean/max equally and leaves delta unchanged. Voltage drift affects the mean-voltage summary channel only, not the raw trace or crossing time. No independent noise.',
        'severity': {level: {f: raw[f][level] for f in ['mean_voltage_v', 'mean_temp_c']} for level in MULTIPLIERS},
        'application_guard': 'Reject voltage-summary windows crossing the unchanged raw min/max envelope. Temperature offsets must preserve ordering and delta identity. This is summary-telemetry drift, not a full raw voltage sensor simulation.'}
    fingerprint_columns = ['cell_id', 'cycle', 'capacity_ah', 'min_voltage_v', 'max_voltage_v'] + FEATURES
    fingerprint = hashlib.sha256(v[fingerprint_columns].to_csv(index=False, float_format='%.17g', lineterminator='\n').encode()).hexdigest()
    return {'protocol_version': '1.0', 'status': 'frozen_design_only_no_injection',
            'calibration_cells': ['B0007'], 'calibration_row_count': len(v), 'calibration_sha256': fingerprint,
            'statistics': stats, 'units': UNITS, 'mad_definition': 'median(abs(x-median(x))), unscaled; NaNs omitted per feature; ddof=1 std; linear quantiles',
            'severity_multipliers': MULTIPLIERS, 'raw_mad_proposals': raw,
            'protected_fields': ['cell_id', 'cycle', 'operation_index', 'timestamp', 'cutoff_voltage_target_v', 'nasa_eol_reached', 'rest_duration_before_discharge_h'],
            'held_out_policy': 'B0018 is not a calibration source; no injection or tuning on it in this phase.',
            'scenario_policy': 'Separate family/severity/channel/sign scenarios; no combinations. Later evaluate all eligible contiguous windows independently, never stitch overlapping copies. A1 uses its derived ramp length, A4 uses 10 cycles, A2/A3 use 5-cycle constant-offset/factor windows. First zero-offset ramp sample is not an injected positive. Missing inputs remain missing and make a window ineligible; no imputation. Reject any invalid window and report rejected counts; do not select windows using scores or labels.',
            'families': families}


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(f'{x:.8g}' if isinstance(x, float) else str(x) for x in row) + ' |' for row in rows])


def report(protocol, validation):
    stats = protocol['statistics']
    fields = ['count', 'median', 'MAD', 'mean', 'std', 'min', 'max', 'p5', 'p25', 'p75', 'p95']
    parts = ['# B0007 anomaly range analysis',
             'B0007 only; no B0018 statistics were computed. Raw MAD is unscaled. Robust range means P5–P95 (not a hard physical boundary). Standard deviation uses ddof=1; NaNs are omitted per feature.',
             f"Validation-only canonical data SHA256: `{protocol['calibration_sha256']}`",
             table(['feature'] + fields, [[f] + [stats[f][s] for s in fields] for f in FEATURES]),
             '## Raw MAD proposals (physical units)',
             table(['feature', 'unit', 'mild', 'moderate', 'strong', 'strong / P5–P95 width'],
                   [[f, UNITS[f]] + list(protocol['raw_mad_proposals'][f].values()) + [protocol['raw_mad_proposals'][f]['strong'] / (stats[f]['p95']-stats[f]['p5'])] for f in FEATURES]),
             'Proposals for current and starting temperature are reference spreads only, not independent anomaly channels.',
             '## Final magnitudes and adjustments']
    for name, family in protocol['families'].items():
        parts += [f'### {name}', family['rule'], family.get('adjustment', 'No MAD amplitude adjustment; coherent sensor channel coupling as specified.'),
                  '```json\n' + json.dumps(family['severity'], indent=2) + '\n```']
    minimum_raw_time = stats['time_to_3_4v_s']['min'] - protocol['raw_mad_proposals']['time_to_3_4v_s']['strong']
    parts += ['## Analytical physical checks (no anomalous dataset generated)',
              f'Raw strong A2 crossing-time minimum would be {minimum_raw_time:.6f} s: impossible. Exponential redesign preserves positivity and crossing-before-end for all B0007 rows.',
              'No clipping is used. Values outside observed P5–P95 or min–max are flagged as extrapolation, not automatically impossible. No unverified temperature safety ceiling is imposed.']
    a1 = protocol['families']['A1_ACCELERATED_DEGRADATION']
    parts += [f"A1 ramp length: {a1['window_cycles']} cycles. Conservative minimum retention at strong endpoint: {stats['capacity_retention']['min'] - a1['severity']['strong']['retention_total_decrease']:.8g} (>0). Independent slope adjustment avoided."]
    for level, changes in protocol['families']['A3_THERMAL_ABNORMALITY']['severity'].items():
        parts.append(f"A3 {level}: mean range [{stats['mean_temp_c']['min']+changes['mean_temp_c']:.6f}, {stats['mean_temp_c']['max']+changes['mean_temp_c']:.6f}] degC; max range [{stats['max_temp_c']['min']+changes['max_temp_c']:.6f}, {stats['max_temp_c']['max']+changes['max_temp_c']:.6f}] degC. Max/delta coupling preserves identity; heating extends beyond baseline range.")
    for level, changes in protocol['families']['A4_SENSOR_DRIFT']['severity'].items():
        amp = changes['mean_voltage_v']
        # Endpoint-envelope checks only; do not construct or save perturbed observations.
        bad = int(((validation.mean_voltage_v - amp < validation.min_voltage_v) | (validation.mean_voltage_v + amp > validation.max_voltage_v)).sum())
        parts.append(f'A4 {level}: voltage-summary endpoint envelope violations on B0007 = {bad}; total +/- drift is {amp:.8g} V or {changes["mean_temp_c"]:.8g} degC. Temperature companion channels shift equally, so delta is invariant.')
    parts += ['## Limitations', 'These are feature-summary counterfactuals, not simulated electrochemistry or natural fault labels. Full-trajectory validation MAD includes aging and operating variation, not just sensor noise. A1 has gradual onset; A2 exponential reductions differ from raw additive MAD targets; A3 preserves summary identities but does not generate a thermal trace; A4 voltage summary drift is not raw sensor bias. No scaling, injection, or training was performed.']
    return '\n\n'.join(parts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/processed/nasa/nasa_discharge_features.csv')
    parser.add_argument('--report', type=Path, default=ROOT / 'results/nasa_anomaly_range_analysis.md')
    parser.add_argument('--protocol', type=Path, default=ROOT / 'config/anomaly_injection_protocol.json')
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    protocol = build_protocol(frame)
    args.protocol.parent.mkdir(parents=True, exist_ok=True)
    args.protocol.write_text(json.dumps(protocol, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report(protocol, validation_rows(frame)), encoding='utf-8')
    print(f'Saved {args.protocol}\nSaved {args.report}\nCalibration: B0007 only, 168 rows; no injected dataset created.')


if __name__ == '__main__':
    main()
