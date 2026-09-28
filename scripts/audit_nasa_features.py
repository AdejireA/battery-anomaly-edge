"""Audit the candidate pool without selection, imputation, scaling or modeling."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CAUSAL = ["capacity_rolling_median_5", "capacity_slope_5", "retention_slope_5"]


def markdown_table(frame):
    """Render without an extra tabulate dependency."""
    def format_value(value):
        if isinstance(value, (float, np.floating)):
            return "NaN" if pd.isna(value) else f"{value:.6g}"
        return str(value)
    rows = ["| " + " | ".join(map(str, frame.columns)) + " |",
            "| " + " | ".join(["---"] * len(frame.columns)) + " |"]
    rows += ["| " + " | ".join(format_value(v) for v in row) + " |"
             for row in frame.itertuples(index=False, name=None)]
    return "\n".join(rows)


def make_plots(frame, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("capacity_ah", "Capacity (Ah)", "capacity_and_causal_trend.png"),
        ("capacity_slope_5", "Trailing 5-cycle capacity slope (Ah/cycle)", "capacity_slope_5_vs_cycle.png"),
        ("time_to_3_4v_s", "Time to first measured voltage <= 3.4 V (s)", "time_to_3_4v_vs_cycle.png"),
        ("duration_s", "Recorded discharge duration (s)", "duration_vs_cycle.png"),
        ("delta_temp_c", "Maximum minus starting temperature (°C)", "delta_temp_vs_cycle.png"),
    ]
    paths = []
    for feature, label, filename in specs:
        fig, ax = plt.subplots(figsize=(9, 5))
        for cell, group in frame.groupby("cell_id", sort=True):
            group = group.sort_values("cycle")
            line, = ax.plot(group.cycle, group[feature], linewidth=1.2,
                            alpha=0.5 if feature == "capacity_ah" else 1,
                            label=f"{cell} capacity" if feature == "capacity_ah" else cell)
            if feature == "capacity_ah":
                ax.plot(group.cycle, group.capacity_rolling_median_5,
                        color=line.get_color(), linestyle="--", linewidth=1.8,
                        label=f"{cell} trailing median (5)")
        if feature == "capacity_slope_5":
            ax.axhline(0, color="0.5", linewidth=0.8)
        ax.set(xlabel="Discharge cycle", ylabel=label, title="NASA discharge feature inspection")
        ax.grid(alpha=0.25)
        ax.legend(ncol=2 if feature == "capacity_ah" else 1, fontsize=8)
        fig.tight_layout()
        path = output_dir / filename
        fig.savefig(path, dpi=180)
        plt.close(fig)
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/nasa/nasa_discharge_features.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "config/nasa_feature_manifest.json")
    parser.add_argument("--report", type=Path, default=ROOT / "results/nasa_feature_audit.md")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "figures/nasa")
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    categories = ["metadata", "offline_analysis_only", "candidate_model_features", "health_analysis_features"]
    classified = [column for category in categories for column in manifest[category]]
    if len(classified) != len(set(classified)) or set(classified) != set(frame.columns):
        raise ValueError("Manifest must classify every CSV column exactly once")
    candidates = frame[manifest["candidate_model_features"]]
    if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in candidates.dtypes):
        raise ValueError("All candidate features must be numeric")
    if np.isinf(candidates.to_numpy(dtype=float)).any():
        raise ValueError("Candidate features contain infinities")
    stats = candidates.describe().T.rename(columns={"std": "standard deviation", "min": "minimum", "50%": "median", "max": "maximum"})
    stats.insert(1, "missing count", candidates.isna().sum())
    correlations = candidates.corr(method="pearson", min_periods=2)
    pairs = []
    for i, first in enumerate(candidates.columns):
        for second in candidates.columns[i + 1:]:
            value = correlations.loc[first, second]
            if pd.notna(value) and abs(value) >= 0.95:
                pairs.append((first, second, value, int(candidates[[first, second]].dropna().shape[0])))
    pair_frame = pd.DataFrame(pairs, columns=["feature 1", "feature 2", "Pearson r", "paired count"])
    missing = frame.groupby("cell_id")[CAUSAL].agg(lambda s: s.isna().sum())
    findings = []
    for feature in candidates:
        if candidates[feature].nunique(dropna=True) <= 1:
            findings.append(f"{feature} is constant; its Pearson correlations are undefined (NaN).")
    findings.append("Correlations pool all cells and use pairwise-complete observations; shared degradation and cell differences can influence them. No columns are removed.")
    findings.append("The first four rows per cell lack full causal windows; no values are imputed. Offline Savitzky-Golay columns are excluded from this audit's candidate statistics/correlations.")
    rest_missing = frame.groupby("cell_id").rest_duration_before_discharge_h.apply(lambda s: int(s.isna().sum()))
    findings.append(f"Unimputed rest-duration missing counts: {rest_missing.to_dict()}. This column remains metadata/experimental analysis only.")
    for feature in ["duration_s", "time_to_3_4v_s", "delta_temp_c", "mean_current_a"]:
        row = frame.loc[frame[feature].idxmax()]
        findings.append(f"Largest {feature}: {row[feature]:.6g}, {row.cell_id} cycle {int(row.cycle)}; see distributions and plots for context.")
    findings.append(f"Rows with nominal SOH > 1: {int((frame.soh_nominal > 1).sum())}; values are not clipped.")
    increases = int((frame.delta_capacity_ah > 0).sum())
    findings.append(f"Capacity increases in {increases} cycle transitions; largest increase is {frame.delta_capacity_ah.max():.6g} Ah. Positive causal slopes can reflect these observed increases; no monotonicity correction is applied.")
    below_cutoff = int((frame.min_voltage_v < frame.cutoff_voltage_target_v).sum())
    lowest = frame.loc[frame.min_voltage_v.idxmin()]
    findings.append(f"Measured minimum voltage is below the documented target in {below_cutoff} records; lowest is {lowest.min_voltage_v:.6g} V ({lowest.cell_id}, cycle {int(lowest.cycle)}, target {lowest.cutoff_voltage_target_v:.6g} V). Inspect raw traces/protocol before attributing this to an extraction error; records are not trimmed at cutoff.")
    bad_timing = (frame.duration_s < 0) | (frame.time_to_3_4v_s < 0) | (frame.time_to_3_4v_s > frame.duration_s)
    findings.append(f"Invalid duration/threshold timing relationships: {int(bad_timing.sum())} rows.")
    paths = make_plots(frame, args.figure_dir)
    report = ["# NASA candidate feature audit", f"Input: `{args.input}`. {len(frame)} observations, {len(frame.columns)} columns.",
              "Candidate pool only, NOT a final model feature set. No scaling, splitting, anomaly injection or training. Causal summaries are available after the current discharge completes.",
              "## Causal feature missing counts", markdown_table(missing.reset_index()),
              "## Candidate descriptive statistics", "Count means nonmissing observations; standard deviation uses ddof=1.",
              markdown_table(stats.rename_axis("feature").reset_index()),
              "## Pearson correlation matrix", markdown_table(correlations.rename_axis("feature").reset_index()),
              "## Highly correlated pairs (absolute r >= 0.95)", markdown_table(pair_frame),
              "## Distribution and data-quality observations", "\n".join(f"- {finding}" for finding in findings),
              "## Figures", "\n".join(f"- `{path}`" for path in paths)]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    print(missing.to_string())
    print("\nHighly correlated pairs:\n" + pair_frame.to_string(index=False))
    print("\n" + "\n".join(findings))
    print(f"\nSaved {args.report}")
    for path in paths:
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
