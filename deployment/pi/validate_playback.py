"""Compare streaming playback to copied frozen held-out scores; no tuning."""
import argparse
import csv
import json
from pathlib import Path
from infer import HERE, FrozenRunner, read_rows


def validate(input_path, expected_path, tolerance=1e-12):
    with Path(expected_path).open(newline='', encoding='utf-8') as stream:
        expected = {(r['cell_id'], int(r['cycle'])): r for r in csv.DictReader(stream)}
    runner = FrozenRunner()  # One runner for the entire sequential playback.
    actual = [runner.observe(r) for r in read_rows(input_path)]
    usable = [r for r in actual if r['anomaly_score'] is not None]
    if {(r['cell_id'], r['cycle']) for r in usable} != set(expected):
        raise AssertionError('Usable cycle IDs differ from frozen reference')
    differences, mismatches = [], 0
    for row in usable:
        reference = expected[(row['cell_id'], row['cycle'])]
        differences.append(abs(row['anomaly_score'] - float(reference['score'])))
        mismatches += (row['prediction'] == 'ALERT') != (reference['flagged'].lower() == 'true')
    maximum = max(differences, default=0.)
    if maximum > tolerance or mismatches:
        raise AssertionError(f'Playback mismatch: max difference={maximum}, predictions={mismatches}')
    return dict(usable_cycles=len(usable), warmup_cycles=len(actual) - len(usable), mismatch_count=mismatches,
                max_score_difference=maximum, tolerance=tolerance,
                flagged_cycles=[r['cycle'] for r in usable if r['prediction'] == 'ALERT'], passed=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE / 'sample_data/B0018_cycles.csv')
    parser.add_argument('--expected', type=Path, default=HERE / 'sample_data/B0018_expected.csv')
    parser.add_argument('--output', type=Path, default=HERE / 'results/playback_validation.json')
    args = parser.parse_args()
    result = validate(args.input, args.expected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
