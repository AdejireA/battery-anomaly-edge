"""Inspect selected raw NASA discharge traces without altering extraction."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat

from extract_nasa import CUTOFF, EXPECTED, vector
from audit_nasa_features import markdown_table

ROOT = Path(__file__).resolve().parents[1]


def inspect(raw_dir, processed, figure_dir):
    rows = []
    figure_dir.mkdir(parents=True, exist_ok=True)
    for cell, count in EXPECTED.items():
        operations = loadmat(raw_dir / f"{cell}.mat", simplify_cells=True)[cell]["cycle"]
        discharges = [(i + 1, op) for i, op in enumerate(operations) if op["type"] == "discharge"]
        if len(discharges) != count:
            raise ValueError(f"{cell}: unexpected discharge count")
        selected = [1, 24, 50, count] if cell == "B0007" else [1, 50, count]
        for cycle in selected:
            operation_index, operation = discharges[cycle - 1]
            data = operation["data"]
            time = vector(data["Time"], "Time")
            terminal = vector(data["Voltage_measured"], "Voltage_measured")
            current = vector(data["Current_measured"], "Current_measured")
            load = vector(data["Voltage_load"], "Voltage_load") if "Voltage_load" in data else None
            if any(len(values) != len(time) for values in [terminal, current] + ([] if load is None else [load])):
                raise ValueError(f"{cell} cycle {cycle}: mismatched trace lengths")
            elapsed = time - time[0]
            crossing = np.flatnonzero(terminal < CUTOFF[cell])
            first = int(crossing[0]) if crossing.size else None
            minimum = int(np.argmin(terminal))
            source = processed.loc[(processed.cell_id == cell) & (processed.cycle == cycle)]
            if len(source) != 1:
                raise ValueError("Expected one processed row per selected cycle")
            source = source.iloc[0]
            match = (int(source.operation_index) == operation_index
                     and np.isclose(source.min_voltage_v, terminal.min(), rtol=0, atol=1e-9)
                     and np.isclose(source.duration_s, elapsed[-1], rtol=0, atol=1e-9))
            rows.append({"cell": cell, "cycle": cycle, "target_v": CUTOFF[cell],
                         "min_terminal_v": terminal.min(), "final_terminal_v": terminal[-1],
                         "min_load_v": np.nan if load is None else load.min(),
                         "final_load_v": np.nan if load is None else load[-1],
                         "first_below_cutoff_s": np.nan if first is None else elapsed[first],
                         "duration_s": elapsed[-1],
                         "samples_after_crossing": 0 if first is None else len(time) - first - 1,
                         "samples_below_cutoff": len(crossing),
                         "current_at_min_v_a": current[minimum], "final_current_a": current[-1],
                         "processed_matches_raw": match})
            fig, (ax, current_ax) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                               gridspec_kw={"height_ratios": [2, 1]})
            ax.plot(elapsed, terminal, label="Measured terminal voltage", linewidth=1.2)
            if load is not None:
                ax.plot(elapsed, load, label="Load voltage", linewidth=1, alpha=0.7)
            ax.axhline(CUTOFF[cell], color="0.4", linestyle="--", label="Documented cutoff")
            if first is not None:
                ax.axvline(elapsed[first], color="red", linestyle=":", label="First sample below cutoff")
            ax.set(ylabel="Voltage (V)", title=f"{cell}: discharge cycle {cycle}")
            ax.legend(fontsize=8)
            current_ax.plot(elapsed, current, color="tab:green")
            current_ax.set(xlabel="Elapsed time from first sample (s)", ylabel="Measured current (A)")
            for axis in (ax, current_ax):
                axis.grid(alpha=0.25)
            fig.tight_layout()
            fig.savefig(figure_dir / f"{cell}_cycle_{cycle:03d}.png", dpi=180)
            plt.close(fig)
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/nasa")
    parser.add_argument("--processed", type=Path, default=ROOT / "data/processed/nasa/nasa_discharge_features.csv")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "figures/nasa/cutoff_inspection")
    parser.add_argument("--report", type=Path, default=ROOT / "results/nasa_cutoff_inspection.md")
    args = parser.parse_args()
    table = inspect(args.raw_dir, pd.read_csv(args.processed), args.figure_dir)
    recovered = (table.final_terminal_v > table.target_v) & (table.final_current_a.abs() < 0.01)
    endings = table.loc[table.samples_after_crossing == 0]
    notes = ["# NASA raw voltage-cutoff inspection", markdown_table(table),
             f"Observed: {int((table.samples_below_cutoff == 1).sum())}/{len(table)} selected traces have exactly one below-cutoff sample. {int(recovered.sum())}/{len(table)} end above the target with absolute measured current below 0.01 A. Traces ending at the crossing without later samples: {', '.join(f'{r.cell} cycle {r.cycle}' for r in endings.itertuples())}. All selected minimum-voltage samples occur under approximately -2 A load; load-voltage minima are zero in all selected records.",
             "Crossing means the first measured terminal-voltage sample strictly below the documented target, with no interpolation. Time is elapsed from the first Time sample. Samples after crossing exclude the crossing sample; below-cutoff sample count is reported separately. Final voltage is the last recorded sample, not necessarily the loaded endpoint. Load voltage zeros are retained as recorded and are not interpreted as battery terminal voltage.",
             f"Selected processed operation indices, minimum voltages and durations match raw traces: {bool(table.processed_matches_raw.all())}. This checks these selected values, not every possible parser behavior. The extractor is unchanged.",
             "Interpretation: inspect terminal voltage together with measured current and load voltage. A below-target dip while current is still negative, followed by current near zero and voltage recovery, is consistent with a loaded cutoff followed by relaxation samples. This supports a protocol/sampling explanation; the exact controller timing and reason for undershoot cannot be established from these traces alone.",
             f"Plots: `{args.figure_dir}` (one per selected cycle)."]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n\n".join(notes) + "\n", encoding="utf-8")
    print(table.to_string(index=False))
    print(f"Saved {args.report}; {len(table)} plots in {args.figure_dir}")
    if not table.processed_matches_raw.all():
        raise ValueError("Selected processed values disagree with raw traces")


if __name__ == "__main__":
    main()
