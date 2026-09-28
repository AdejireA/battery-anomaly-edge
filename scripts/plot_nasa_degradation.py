"""Scientific inspection plots from the processed NASA discharge CSV."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/nasa/nasa_discharge_features.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "figures/nasa")
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plots = [
        ("capacity_ah", "Discharge capacity (Ah)", "capacity_vs_cycle.png", 1.4),
        ("soh_nominal", "Nominal SOH (capacity / 2.0 Ah)", "soh_vs_cycle.png", 0.7),
        ("capacity_retention", "Capacity retention (relative to first discharge)", "capacity_retention_vs_cycle.png", None),
    ]
    for feature, label, filename, threshold in plots:
        fig, ax = plt.subplots(figsize=(8, 5))
        for cell, group in frame.groupby("cell_id", sort=True):
            group = group.sort_values("cycle")
            ax.plot(group.cycle, group[feature], label=cell, linewidth=1.4)
        if threshold is not None:
            ax.axhline(threshold, color="0.4", linestyle="--", linewidth=1, label="NASA EOL (30% nominal fade)")
        ax.set(xlabel="Discharge cycle", ylabel=label, title="NASA battery degradation")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        path = args.output_dir / filename
        fig.savefig(path, dpi=180)
        plt.close(fig)
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
