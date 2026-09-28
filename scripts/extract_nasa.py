"""Extract discharge inspection features; this schema is not an ML feature set.

Indices are one-based. Timestamps retain the source's unspecified timezone.
capacity_trend_ah and rolling_capacity_slope are OFFLINE ANALYSIS ONLY:
Savitzky-Golay smoothing is non-causal, with interpolated edge values.
Current retains its measured sign; means are arithmetic sample means.
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"B0005": 168, "B0006": 168, "B0007": 168, "B0018": 132}
CUTOFF = {"B0005": 2.7, "B0006": 2.5, "B0007": 2.2, "B0018": 2.5}
COLUMNS = """cell_id cycle operation_index timestamp cutoff_voltage_target_v
capacity_ah soh_nominal capacity_retention delta_capacity_ah delta_soh_nominal
capacity_trend_ah rolling_capacity_slope capacity_rolling_median_5
capacity_slope_5 retention_slope_5 duration_s time_to_3_4v_s
mean_voltage_v min_voltage_v max_voltage_v mean_current_a ambient_temp_c
start_temp_c mean_temp_c max_temp_c delta_temp_c
rest_duration_before_discharge_h nasa_eol_reached""".split()


def require_fields(record, fields, context):
    if not isinstance(record, dict):
        raise ValueError(f"{context}: expected MATLAB structure")
    missing = set(fields) - record.keys()
    if missing:
        raise ValueError(f"{context}: missing required fields {sorted(missing)}")


def vector(value, context):
    values = np.asarray(value, dtype=float)
    if values.ndim > 1 or values.size == 0:
        raise ValueError(f"{context}: expected nonempty vector")
    values = values.reshape(-1)
    if not np.isfinite(values).all():
        raise ValueError(f"{context}: non-finite values")
    return values


def scalar(value, context):
    values = vector(value, context)
    if values.size != 1:
        raise ValueError(f"{context}: expected scalar")
    return float(values[0])


def matlab_timestamp(value):
    parts = vector(value, "timestamp")
    if len(parts) != 6 or not np.equal(parts[:5], np.floor(parts[:5])).all():
        raise ValueError("timestamp: expected six-element MATLAB date vector")
    if not 0 <= parts[5] < 60:
        raise ValueError("timestamp: invalid seconds")
    return datetime(*(int(v) for v in parts[:5])) + timedelta(seconds=float(parts[5]))


def rest_hours(start, previous):
    """Never substitute an earlier operation when the immediate predecessor fails."""
    if previous is None:
        return np.nan
    try:
        prior_start = matlab_timestamp(previous["time"])
        time = vector(previous["data"]["Time"], "previous operation Time")
        if time[0] < 0 or np.any(np.diff(time) < 0):
            return np.nan
        end = prior_start + timedelta(seconds=float(time[-1]))
        hours = (start - end).total_seconds() / 3600
        return hours if hours >= 0 else np.nan
    except (KeyError, TypeError, ValueError, OverflowError):
        return np.nan


def causal_capacity_features(frame):
    """One cell in cycle order; full trailing windows, available after discharge.

    Cycle indices must be consecutive. For five equally spaced cycles, centered
    regression x values are [-2, -1, 0, 1, 2] and sum(x**2) is 10.
    """
    if not np.all(np.diff(frame["cycle"].to_numpy()) == 1):
        raise ValueError("Causal features require consecutive increasing cycle indices")
    result = pd.DataFrame(index=frame.index)
    result["capacity_rolling_median_5"] = frame.capacity_ah.rolling(5, min_periods=5).median()
    weights = np.arange(-2, 3, dtype=float)
    for source, target in [("capacity_ah", "capacity_slope_5"),
                           ("capacity_retention", "retention_slope_5")]:
        result[target] = frame[source].rolling(5, min_periods=5).apply(
            lambda values: np.dot(weights, values) / 10.0, raw=True
        )
    return result


def extract_cell(path, cell_id):
    if not path.is_file():
        raise FileNotFoundError(f"Required MAT file missing: {path}")
    mat = loadmat(path, simplify_cells=True)
    require_fields(mat, [cell_id], str(path))
    battery = mat[cell_id]
    require_fields(battery, ["cycle"], cell_id)
    operations = battery["cycle"]
    if isinstance(operations, dict):
        operations = [operations]
    if not isinstance(operations, (list, np.ndarray)):
        raise ValueError(f"{cell_id}: invalid cycle array")
    rows = []
    for index, operation in enumerate(operations):
        context = f"{cell_id} operation {index + 1}"
        require_fields(operation, ["type"], context)
        if operation["type"] != "discharge":
            continue
        require_fields(operation, ["time", "ambient_temperature", "data"], context)
        data = operation["data"]
        fields = ["Voltage_measured", "Current_measured", "Temperature_measured", "Time"]
        require_fields(data, fields + ["Capacity"], context)
        voltage, current, temp, time = [vector(data[f], f"{context} {f}") for f in fields]
        if len({len(a) for a in (voltage, current, temp, time)}) != 1:
            raise ValueError(f"{context}: time-series array lengths disagree")
        if time[0] < 0 or np.any(np.diff(time) < 0):
            raise ValueError(f"{context}: Time must be nonnegative and nondecreasing")
        capacity = scalar(data["Capacity"], f"{context} Capacity")
        if capacity <= 0:
            raise ValueError(f"{context}: capacity must be positive")
        start = matlab_timestamp(operation["time"])
        crossing = np.flatnonzero(voltage <= 3.4)
        rows.append(dict(
            cell_id=cell_id, cycle=len(rows) + 1, operation_index=index + 1,
            timestamp=start, cutoff_voltage_target_v=CUTOFF[cell_id],
            capacity_ah=capacity, duration_s=time[-1] - time[0],
            time_to_3_4v_s=time[crossing[0]] - time[0] if crossing.size else np.nan,
            mean_voltage_v=voltage.mean(), min_voltage_v=voltage.min(),
            max_voltage_v=voltage.max(), mean_current_a=current.mean(),
            ambient_temp_c=scalar(operation["ambient_temperature"], f"{context} ambient temperature"),
            start_temp_c=temp[0], mean_temp_c=temp.mean(), max_temp_c=temp.max(),
            delta_temp_c=temp.max() - temp[0],
            rest_duration_before_discharge_h=rest_hours(start, operations[index - 1] if index else None),
            nasa_eol_reached=capacity <= 1.4,
        ))
    if len(rows) != EXPECTED[cell_id]:
        raise ValueError(f"{cell_id}: expected {EXPECTED[cell_id]} discharges, got {len(rows)}")
    frame = pd.DataFrame(rows)
    frame["soh_nominal"] = frame.capacity_ah / 2.0
    frame["capacity_retention"] = frame.capacity_ah / frame.capacity_ah.iloc[0]
    frame["delta_capacity_ah"] = frame.capacity_ah.diff()
    frame["delta_soh_nominal"] = frame.soh_nominal.diff()
    # OFFLINE ANALYSIS ONLY: these two columns include future observations.
    frame["capacity_trend_ah"] = savgol_filter(frame.capacity_ah, 5, 2, mode="interp")
    frame["rolling_capacity_slope"] = frame.capacity_trend_ah.diff()
    frame = frame.join(causal_capacity_features(frame))
    return frame[COLUMNS]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/nasa")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/nasa")
    args = parser.parse_args()
    # Validate the entire cohort before writing any outputs.
    for cell_id in EXPECTED:
        path = args.raw_dir / f"{cell_id}.mat"
        if not path.is_file():
            raise FileNotFoundError(f"Required MAT file missing: {path}")
    frames = {cell: extract_cell(args.raw_dir / f"{cell}.mat", cell) for cell in EXPECTED}
    combined = pd.concat(frames.values(), ignore_index=True)
    if len(combined) != 636:
        raise ValueError(f"Expected 636 combined rows, got {len(combined)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for cell, frame in frames.items():
        frame.to_csv(args.output_dir / f"{cell}_discharge_features.csv", index=False)
        print(f"\n{cell}: {len(frame)} discharges; capacity {frame.capacity_ah.iloc[0]:.6f} -> "
              f"{frame.capacity_ah.iloc[-1]:.6f} Ah; nominal SOH {frame.soh_nominal.iloc[0]:.6f} -> "
              f"{frame.soh_nominal.iloc[-1]:.6f}")
        print("Missing values per feature:")
        print(frame.drop(columns=["cell_id", "cycle", "operation_index"]).isna().sum().to_string())
    combined.to_csv(args.output_dir / "nasa_discharge_features.csv", index=False)
    print("\nPASS: required files, battery structures, discharge fields, per-cell counts, "
          "636 combined rows, finite positive capacities, matching array lengths.")
    print("PASS: finite measurement arrays and nonnegative, nondecreasing Time.")
    print("\nFirst five combined rows:")
    print(combined.head().to_string(index=False))


if __name__ == "__main__":
    main()
