"""Build deterministic cell-level splits and report metadata without scaling."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COUNTS = {"B0005": 168, "B0006": 168, "B0007": 168, "B0018": 132}


def build_splits(frame, protocol, fraction=None):
    """Return full train/validation/test frames plus a nominal training prefix.

    Sorting is by configured cell order, then discharge cycle within each cell.
    Only IDs, cycle order and recorded counts define membership, never features.
    """
    training = protocol["training_cells"]
    validation, test = protocol["validation_cell"], protocol["test_cell"]
    assignments = training + [validation, test]
    if len(assignments) != len(set(assignments)):
        raise ValueError("A cell cannot appear in more than one split")
    if set(training) != {"B0005", "B0006"} or validation != "B0007" or test != "B0018":
        raise ValueError("Protocol must train on B0005/B0006, validate on B0007, test on B0018")
    actual = set(frame.cell_id.unique())
    if actual != set(assignments):
        raise ValueError(f"Unexpected or missing cell IDs: observed {actual}, expected {set(assignments)}")
    fraction = protocol["nominal_training_fraction"] if fraction is None else fraction
    if not isinstance(fraction, (int, float)) or not math.isfinite(fraction) or not 0 < fraction <= 1:
        raise ValueError("Nominal fraction must lie in (0, 1]")
    if protocol.get("nominal_rounding") != "floor":
        raise ValueError("Supported nominal rounding rule is floor")
    groups = {}
    for cell in assignments:
        group = frame.loc[frame.cell_id == cell].sort_values("cycle").copy()
        if len(group) != EXPECTED_COUNTS[cell]:
            raise ValueError(f"{cell}: unexpected discharge count {len(group)}")
        if not np.array_equal(group.cycle.to_numpy(), np.arange(1, len(group) + 1)):
            raise ValueError(f"{cell}: cycle numbers must be unique and consecutive from 1")
        timestamps = pd.to_datetime(group.timestamp, errors="raise")
        if timestamps.isna().any() or not timestamps.is_monotonic_increasing:
            raise ValueError(f"{cell}: timestamps disagree with chronological cycle order")
        groups[cell] = group
    train = pd.concat([groups[cell] for cell in training], ignore_index=True)
    nominal = pd.concat([groups[cell].iloc[:math.floor(len(groups[cell]) * fraction)]
                         for cell in training], ignore_index=True)
    return {"train": train, "validation": groups[validation].reset_index(drop=True),
            "test": groups[test].reset_index(drop=True), "nominal_train": nominal}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/nasa/nasa_discharge_features.csv")
    parser.add_argument("--protocol", type=Path, default=ROOT / "config/nasa_experiment_protocol.json")
    parser.add_argument("--report", type=Path, default=ROOT / "results/nasa_split_summary.md")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    frame = pd.read_csv(args.input)
    splits = build_splits(frame, protocol)
    lines = ["# NASA split summary", "", f"Input: `{args.input}`", "",
             "Full splits preserve all columns and per-cell chronological order. No random mixing, scaling, imputation or training.", "",
             "| Split | Cells | Rows |", "| --- | --- | --- |"]
    for name in ["train", "validation", "test"]:
        part = splits[name]
        lines.append(f"| {name} | {', '.join(part.cell_id.unique())} | {len(part)} |")
    lines += ["", f"Default nominal fraction: {protocol['nominal_training_fraction']:.0%}; default nominal rows: {len(splits['nominal_train'])}.", "",
              "Nominal region = earliest floor(fraction × cell discharge count) cycles. The denominator is the fixed recorded trajectory length; no future capacity, SOH, EOL or scores determine membership. This is an early-life proxy, not verified healthy labels.", "",
              "| Fraction | Training cell | Nominal rows | Cycle range | Missing capacity_slope_5 |", "| --- | --- | --- | --- | --- |"]
    for fraction in protocol["nominal_sensitivity_fractions"]:
        nominal = build_splits(frame, protocol, fraction)["nominal_train"]
        for cell, group in nominal.groupby("cell_id", sort=False):
            lines.append(f"| {fraction:.0%} | {cell} | {len(group)} | {group.cycle.min()}–{group.cycle.max()} | {group.capacity_slope_5.isna().sum()} |")
    lines += ["", "Full validation/test trajectories remain available, including their initial causal-window NaNs. Missing-feature/model eligibility policy must be settled before fitting; these counts are not model-ready counts.", "",
              "Validation is for later design choices; test is held out from tuning. The callable build_splits API returns unscaled dataframes; only this metadata report is saved."]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
