"""Deterministic synthetic mechanics demonstration; no research data or model."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import csv
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'deployment/pi'))
from features import BASE_FEATURES, CausalHistory


def synthetic_rows(cell, count, seed, perturb=False):
    """Invented units/scales and seeded noise, never source measurements."""
    rng = np.random.default_rng(seed)
    center = np.array([3000., 2400., 3.7, -1., 25., 29., 4.])
    scale = np.array([20., 18., .02, .01, .2, .3, .1])
    rows = []
    for cycle in range(1, count + 1):
        values = center + scale * rng.normal(size=7)
        if perturb and 21 <= cycle <= 23:
            values += scale * np.array([-30., -30., -30., 0., 30., 30., 30.])
        rows.append(dict(cell_id=cell, cycle=cycle,
                         **dict(zip(BASE_FEATURES, values))))
    return rows


def vectors(rows):
    state = CausalHistory()
    return [state.push(row)[2] for row in rows]


def run_demo():
    training = synthetic_rows('SYNTHETIC_TRAIN', 210, 42)
    x = np.stack([v for v in vectors(training) if v is not None])
    scaler = StandardScaler().fit(x)
    model = IsolationForest(n_estimators=100, random_state=42, n_jobs=1).fit(scaler.transform(x))
    threshold = float(np.percentile(-model.score_samples(scaler.transform(x)), 95))
    rows = synthetic_rows('SYNTHETIC_DEMO', 30, 123, perturb=True)
    predictions = []
    for row, vector in zip(rows, vectors(rows)):
        score = None if vector is None else float(-model.score_samples(scaler.transform(vector[None, :]))[0])
        predictions.append(dict(cell_id=row['cell_id'], cycle=row['cycle'],
            anomaly_score=score, threshold=threshold,
            prediction='INSUFFICIENT_HISTORY' if score is None else ('ALERT' if score > threshold else 'NORMAL')))
    return rows, predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, help='Optional directory for synthetic_input.csv and predictions.csv')
    args = parser.parse_args()
    rows, predictions = run_demo()
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, records in [('synthetic_input.csv', rows), ('predictions.csv', predictions)]:
            with (args.output_dir / name).open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(records[0]))
                writer.writeheader()
                writer.writerows(records)
    print('Synthetic-only fitted model; these scores are not research FPR results.')
    print('Input columns: ' + ', '.join(rows[0]))
    writer = csv.DictWriter(sys.stdout, fieldnames=list(predictions[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(predictions)


if __name__ == '__main__':
    main()
