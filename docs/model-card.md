# Research model card: Causal history-relative Isolation Forest

This model card documents the lightweight unsupervised anomaly detection models developed for battery discharge cycle monitoring.

## Model purpose

The models score lithium-ion battery discharge cycles to detect unexpected deviations from established normal degradation behavior. Scoring operates on aggregated cycle-level summary features rather than sub-second continuous telemetry.

## Intended use

- **Research and benchmarking:** Investigating unsupervised anomaly detection, representation design, and edge inference feasibility for battery degradation monitoring.
- **Cycle-level health auditing:** Offline or post-cycle scoring of completed battery discharge cycles.
- **Comparative research:** Evaluating lightweight tree-based anomaly detection against deep learning or parametric physical degradation models.

## Out-of-scope use

The models in this repository are **NOT** designed, certified, or intended for:
- Safety-critical battery protection (e.g., thermal runaway prevention, over-current cutoff, or emergency isolation).
- Real-time certified Battery Management System (BMS) control.
- Medical, aviation, or high-consequence energy storage applications.
- Direct remaining-useful-life (RUL) estimation or state-of-health (SOH) regression.
- Live, unvalidated field deployment without human supervision.
- Sub-cycle instantaneous fault detection (inference requires cycle completion).

## Training methodology

- **Estimator:** scikit-learn `IsolationForest`.
- **Learning paradigm:** Unsupervised fitting on an early-life nominal operational proxy.
- **Label-free:** No labelled operational fault examples were provided during model training or threshold selection.
- **Data normalization:** `StandardScaler` fitted exclusively on the nominal training split.
- **Early-life proxy:** Training uses the earliest 30% of each training trajectory before history exclusion: NASA cycles 1-50, CALCE cycles 1-264/1-291. History-10 exclusion leaves 80 NASA and 535 CALCE fitted rows. This is a retrospective nominal proxy, not a knee-point rule.

## NASA reference configuration

- **Feature representation:** `RELATIVE_B` (7 features).
  - `duration_s` (discharge duration)
  - `time_to_3_4v_s` (time to reach 3.4 V)
  - `mean_voltage_v` (mean discharge voltage)
  - `mean_current_a` (mean discharge current)
  - `mean_temp_c` (mean cell temperature)
  - `max_temp_c` (maximum cell temperature)
  - `delta_temp_c` (maximum minus starting temperature)
- **History window:** $k=10$ prior cycles.
- **Isolation Forest hyperparameters:**
  - `n_estimators`: 100
  - `max_features`: 1.0
  - `max_samples`: 'auto' (80 effective samples for the 80-row NASA fit)
  - `contamination`: 'auto'
  - `random_state`: 42
- **Decision threshold:** $0.5548682376720724$ (95th percentile of clean training anomaly scores).

## CALCE replication configuration

- **Feature representation:** 4 features (temperature channels unavailable in source workbooks).
  - `duration_s`
  - `time_to_3_4v_s`
  - `mean_voltage_v`
  - `mean_current_a`
- **History window:** $k=10$ prior cycles.
- **Isolation Forest hyperparameters:** Same structure as NASA (`n_estimators=100`, `max_features=1.0`, reporting seed 42).
- **Decision threshold:** $0.595563163424274$ (95th percentile of clean nominal CALCE training scores).
- **Note:** The CALCE model is an independent replication fitted from scratch; it is not the NASA model transferred across datasets.

## Input representation

For cycle $t$, each feature is computed as a dimensionless residual normalized against the cell's own prior $k$ cycles:
$$z_t = \frac{x_t - \text{median}(x_{t-k \dots t-1})}{1.4826\,\text{MAD}(x_{t-k \dots t-1}) + 10^{-9}}$$
where MAD is the median absolute deviation. This transformation expresses deviations relative to recent same-cell history; it can also absorb gradual abnormalities.

## Thresholding strategy

Thresholds are established using a clean-nominal calibration rule:
$$\text{Threshold} = \text{Percentile}_{95}(\{- \text{score\_samples}(\text{StandardScaler.transform}(z_i)) \mid i \in \text{Nominal Training}\})$$
An alarm is flagged if $\text{Score}(z_t) > \text{Threshold}$.

## Evaluation results

### Clean false-positive rates (Target: $\le 5\%$)
- NASA validation (B0007): 3 / 158 flagged = 1.90%
- NASA final test (B0018): 5 / 122 flagged = 4.10%
- CALCE validation (CS2-37): 26 / 1,026 flagged = 2.53% (seed 42 reference; 3-seed mean: 3.15%)
- CALCE final test (CS2-38): 32 / 1,015 flagged = 3.15%

### Controlled anomaly sensitivity (B0018 synthetic recall)
- A2 (Premature voltage collapse): Mild: 51.69% | Moderate: 82.37% | Strong: 92.54%
- A1 (Accelerated degradation): Not applicable to frozen RELATIVE_B; no final A1 result.
- A3 (Thermal excursion): Mild: 5.76% | Moderate: 21.53% | Strong: 46.10%
- A4 (Gradual sensor drift): Mild: 4.50% | Moderate: 4.55% | Strong: 4.67%

## Hardware evaluation

- **Hardware:** Raspberry Pi 3B+ (ARM Cortex-A53, 4 cores @ 1.2 GHz, 905 MiB RAM, Debian 13).
- **Execution mode:** Replay of 122 scorable B0018 cycle contexts.
- **Latency (1,000 iterations):** Median 63.77 ms, P95 64.94 ms.
- **Throughput:** 15.64 observations/second.
- **Memory footprint:** ~130 MB RSS.

## Known limitations

1. **Vulnerability to gradual drift:** Sliding-window baselines adapt to slow sensor calibration drift. As a result, gradual drift anomalies (A4) achieved recall $< 5\%$.
2. **Warmup requirement:** The model cannot score the first $k$ cycles of a battery because no baseline exists.
3. **Laboratory data scope:** The models were trained and tested on constant-current laboratory discharge profiles. Performance under irregular solar charge-discharge duty cycles is unverified.
4. **No fault classification:** The model outputs a continuous anomaly score and binary alarm flag; it does not diagnose the physical root cause of a detected anomaly.

## Artifact availability

Final frozen model binaries (`.joblib`) are released in v0.2; see the [manifest](../artifacts/manifest.json) and [reproduction guide](reproduction.md). Development model collections remain excluded. Load only trusted joblib files after hash verification; deserialization can execute code.

## Interpretation and sources

History 10 is the selected reporting reference, not a global optimum. B0018/CS2-38 were excluded from guarded fitting and threshold selection but appeared earlier during extraction/descriptive auditing. P95 was the first of P95/P97.5/P99 satisfying <=5% validation clean FPR for all three seeds, without synthetic metrics in selection. No live sensor integration, field deployment or cross-chemistry generalization is demonstrated. Logged Pi peak RSS is below current RSS; its cause is unverified. See [NASA configuration](../config/final_nasa_model.json), [CALCE configuration](../config/final_calce_model.json), [NASA metrics](../results/nasa_final_test/anomaly_metrics.csv) and [Pi benchmark](../deployment/pi/results/pi_benchmark.json).
