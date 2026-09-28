# Research process

## Where the project started

Off-grid solar installations depend on battery energy storage to bridge intermittent generation and daily consumption cycles. In remote applications, premature battery failure risks complete system downtime, yet deploying complex, supervised deep learning models or cloud-dependent telemetry is impractical. Embedded microcontrollers and single-board computers operate under strict computation and memory limits, and field installations rarely provide labelled fault data.

This project began with a concrete research question: Can a lightweight unsupervised model learn normal battery degradation behaviour from historical measurements, detect deviations from that behaviour without fault labels, and run efficiently on Raspberry Pi-class edge hardware?

## Defining "anomaly"

Public battery ageing datasets provide cycle-by-cycle operational degradation under controlled laboratory conditions. However, they do not provide ground-truth binary labels demarcating "normal" operation from "faulty" operation. Capacity loss over hundreds of cycles is the expected physical reality of battery ageing, not an operational fault.

In this work, an anomaly is defined strictly as an unexpected operational deviation from a cell's own established degradation trajectory. This includes sudden premature capacity drops, early terminal voltage collapse during discharge, and unexpected thermal excursions. Normal, gradual capacity fade across hundreds of cycles is not considered anomalous.

## What label-free means here

"Label-free" means that no manually annotated operational fault examples were supplied to the anomaly detector during model fitting or threshold selection. The detector relies entirely on unsupervised learning to capture the distribution of nominal cycle characteristics.

Synthetic anomaly labels were constructed and used exclusively for offline sensitivity evaluation. At no point during training or threshold determination were these labels visible to the algorithm.

## Why controlled anomalies were introduced

Because public battery repositories do not contain verified natural field faults with precise timing annotations, evaluating detector sensitivity required a controlled experimental mechanism. Four synthetic anomaly mechanisms were implemented:

1. **A1 (Accelerated degradation):** Sustained capacity-retention decrease with a causal slope change; development-only for capacity-bearing representations.
2. **A2 (Premature voltage collapse):** Rapid voltage drop early in the discharge profile.
3. **A3 (Thermal excursion):** Uncharacteristically high operating temperatures during discharge.
4. **A4 (Gradual sensor drift):** Cumulative offset added to voltage or temperature readings over successive cycles.

These synthetic perturbations were injected at three severity levels (mild, moderate, and strong). They serve as controlled sensitivity benchmarks rather than naturally observed fault statistics.

## Preventing cycle-level leakage

To prevent data leakage, battery cells were segregated at the cell level. All cycles from a given battery were assigned exclusively to training, validation, or final evaluation. No single cell was split across training and testing partitions.

Furthermore, all feature transformations preserve temporal causality. For any cycle $t$, historical reference statistics depend solely on cycles strictly preceding $t$. Future observations and the current observation itself are excluded from the baseline.

## Qualification on "held-out"

In experimental machine learning, the term "held-out" is often used loosely to imply that test data was never inspected in any form. To maintain scientific precision, the access boundaries in this project are explicitly qualified:

- **Descriptive and extraction access:** Test cells (NASA B0018 and CALCE CS2-38) were parsed during initial dataset ingestion and schema inspection to ensure uniform extraction column formatting and verify data integrity.
- **Guarded fitting isolation:** B0018 and CS2-38 were excluded from guarded fitting and threshold selection. Recorded final evaluations verified the freeze first; earlier extraction/descriptive access means the files cannot establish that no prior human design decision was influenced by inspection.
- **Final evaluation access:** Recorded final evaluations scored the test cells against frozen models without refitting or retuning; this does not claim they were never previously inspected.

## Building the first NASA pipeline

The initial development pipeline focused on the NASA Ames Li-ion dataset (cells B0005, B0006, B0007, and B0018). The first model iteration extracted absolute summary statistics from each discharge cycle:
- Discharge capacity (Ah)
- Discharge cycle duration (s)
- Time to first sampled crossing of 3.4 V
- Mean and peak cell temperatures (°C)
- Mean operating voltage and current

An Isolation Forest was trained on absolute features from early cycles of training cells B0005 and B0006, and evaluated on validation cell B0007.

## First major failure

The absolute feature representation failed decisively. When the model trained on B0005 and B0006 was applied to B0007, clean validation FPR ranged from 21.43% to 73.81% across the absolute-feature configurations. The target operational design requirement was $\le 5\%$.

Clean FPR here is the alarm fraction on unmodified B0007 observations, not specificity against certified natural-fault negatives. These rates failed the predefined validation criterion.

## Why the detector was not immediately replaced

Rather than discarding the Isolation Forest in favor of more complex architectures (such as autoencoders or recurrent neural networks), the failure mechanism was investigated first. The decision was made to keep the estimator fixed and examine whether the input representation was the underlying cause of cross-cell failure.

## Cross-cell diagnosis

Clean feature and score diagnostics supported cross-cell operating-distribution differences and aging-related score drift. They do not establish manufacturing variation or a specific physical mechanism as the cause. The evidence motivated testing threshold adaptation and then relative features.

## Burn-in calibration experiment

Early B0007 fractions of 20%, 30% and 40% were used to calibrate P95/P97.5/P99 thresholds from saved models without refitting; evaluation used only later observations. Later-trajectory clean FPR ranged from 63.70% to 100%. None of 72 configuration/fraction/percentile groups met the <=5% clean-FPR condition across all seeds. Synthetic evaluation was withheld by the eligibility gate; loss of synthetic sensitivity is not an executed result of this phase. See the [historical report](../results/nasa_burnin_calibration.md).

## Changing representation rather than algorithm

The failure of absolute features pointed toward a clear architectural requirement: the model should evaluate whether a cycle is anomalous relative to the battery's own recent operating behavior, rather than relative to a universal absolute baseline.

This led to the design of causal history-relative residual features.

## Causal relative features

For each scorable cycle $t$, a historical baseline is computed from the preceding $k$ cycles:
$$\text{History}_t = \{x_{t-k}, x_{t-k+1}, \dots, x_{t-1}\}$$

From this history, two robust statistics are extracted for each measurement channel:
- **Baseline median:** $\tilde{\mu}_t = \text{median}(\text{History}_t)$
- **Baseline dispersion:** $\text{MAD}_t = \text{median}(|x_i - \tilde{\mu}_t|)$ for $x_i \in \text{History}_t$

The relative residual feature for cycle $t$ is defined as:
$$z_t = \frac{x_t - \tilde{\mu}_t}{1.4826\,\text{MAD}_t + \epsilon}$$
where $\epsilon$ is a small numerical stabilization constant ($10^{-9}$).

Strict temporal causality is enforced: cycle $t$ and all subsequent cycles are excluded from $\text{History}_t$. A cell requires a warmup period of $k$ cycles before scoring begins.

## History-window evaluation

Histories 5, 10 and 20 were evaluated. History 10 and RELATIVE_B were fixed as the reporting reference, not selected as the best synthetic performer or established as globally optimal. The artifacts document the tested representations and outcomes; they do not establish a stronger optimality rationale. See [final configuration](../config/final_nasa_model.json).

## Freezing NASA

With the relative feature formulation established (representation `RELATIVE_B`, 7 features), the NASA pipeline was frozen under a guarded protocol:
- Estimator: `IsolationForest(n_estimators=100, max_features=1.0, max_samples='auto', contamination='auto', random_state=42)`
- Training set: B0005 and B0006 nominal cycles (cycles 1-50, with cycles 1-10 serving as history; cycles 11-50 supply 40 rows per cell and 80 fitted rows total).
- Threshold: 95th percentile of anomaly scores on clean training data ($0.554868$).
- Validation cell B0007 achieved 3 false alarms across 158 scorable cycles, yielding a clean FPR of $1.90\%$, well within the $\le 5\%$ design target.

## Final B0018 evaluation

Once frozen, the model was evaluated on guarded test cell B0018:
- Total usable scorable cycles: 122 (cycles 11 to 132).
- Clean cycles flagged: 5 (cycles 46, 47, 106, 107, 108).
- Clean FPR: $4.10\%$.

The result confirmed that the causal relative representation successfully maintained low false-alarm rates on a cell excluded from guarded fitting and threshold selection, after its initial history window.

## Synthetic NASA evaluation

Controlled anomaly sensitivity was evaluated in eligible independent scenario copies of B0018, with dependent overlapping windows:
- **A2 (Premature voltage collapse):** Recall scaled from 51.69% (mild) to 82.37% (moderate) and 92.54% (strong).
- **A1 (Accelerated degradation):** Inapplicable to the final measurement-only RELATIVE_B model; no final A1 recall is reported.
- **A3 (Thermal excursion):** Recall scaled from 5.76% (mild) to 21.53% (moderate) and 46.10% (strong).

## Gradual-drift weakness

In contrast to abrupt profile anomalies, gradual sensor drift (A4) was poorly detected:
- Mild drift recall: 4.50%
- Moderate drift recall: 4.55%
- Strong drift recall: 4.67%

A4 uses ten-cycle drift windows. Adaptive baselines absorb part of the drift; detector/representation and operating-point limitations also contribute. The diagnostics do not establish baseline adaptation as the sole cause.

## Why CALCE was added

To verify whether the relative feature approach was specific to the NASA dataset or applicable more broadly, an independent replication was conducted on the CALCE CS2 battery dataset (University of Maryland).

The CALCE experiment was an independent methodological replication, not a direct model transfer. A new Isolation Forest model was fitted from scratch using CALCE training data.

## CALCE data engineering

CALCE data presented different characteristics from NASA:
- Accepted complete discharges were CS2-35: 880, CS2-36: 970, CS2-37: 1,036, and CS2-38: 1,025.
- Operating temperature channels were not recorded in the raw data files.
- Cutoff criteria differed from NASA protocols.

Consequently, the CALCE feature set was reduced to 4 relative residual features: `duration_s`, `time_to_3_4v_s`, `mean_voltage_v`, and `mean_current_a`. History window $k=10$ was retained.

## CALCE validation and final evaluation

The CALCE partitioning assigned CS2-35 and CS2-36 to training, CS2-37 to validation, and CS2-38 to final evaluation:
- **Validation (CS2-37):** 26 flagged cycles out of 1,026 usable cycles, yielding a clean FPR of $2.53\%$ for the reference seed 42 model (mean across seeds 42, 123, 2026 was $3.15\%$). The frozen threshold was $0.595563$.
- **Final evaluation (CS2-38):** 32 flagged cycles out of 1,015 usable cycles, yielding a clean FPR of $3.15\%$.

Across more than 1,000 continuous cycles, clean false-positive rates remained comfortably below the $5\%$ limit.

## What the two datasets support

The empirical evidence supports the following restrained claim: the causal history-relative anomaly detection methodology produced low clean false-positive rates ($\le 5\%$) across independently fitted models on two distinct laboratory battery ageing datasets.

The evidence does not support claims of universal "cross-chemistry generalization" or direct zero-shot model transfer between different battery types.

## From research model to edge package

To evaluate edge deployment viability, the frozen NASA model, scaler, and feature extraction pipeline were packaged into a standalone deployment bundle under `deployment/pi/`:
- `features.py`: Standalone causal rolling history buffer and MAD residual calculation.
- `infer.py`: Single-cycle inference CLI accepting historical context and returning score, threshold, and alarm status.
- `benchmark.py`: Timing and memory instrumentation runner using `psutil`.

## Playback before benchmark

Before running performance benchmarks, numerical prediction equivalence was verified. Test cell B0018 observations were replayed through the edge package, and outputs were compared against the original research pipeline:
- Mismatches: 0 out of 122 cycles.
- Maximum absolute score discrepancy: 0.0.
- Exactly the same 5 cycles (46, 47, 106, 107, 108) were flagged.

## Physical Raspberry Pi execution

The package was transferred to a physical Raspberry Pi 3B+ (ARM Cortex-A53, 4 cores @ 1.2 GHz, 905 MiB RAM, running Debian 13 trixie, Python 3.13.5).

A 1,000-iteration timed benchmark produced:
- Feature computation latency: Median 0.76 ms (P95: 0.85 ms).
- Model scoring latency: Median 63.00 ms (P95: 64.17 ms).
- Total cycle latency: Median 63.77 ms (P95: 64.94 ms).
- Throughput: 15.64 cycles/second.
- Process RSS: Approximately 130 MB.

The saved before-run RSS/peak counters are 129,765,376/129,392,640 bytes; after-run counters are 130,093,056/129,785,856 bytes. The reported peaks are below instantaneous RSS. The cause is unverified, and the peaks are not reliable upper bounds. Values remain unchanged.

## Meaning of edge-deployed in this project

In this work, "edge-deployed" denotes cycle-level inference execution and latency profiling of a pre-trained model on physical Raspberry Pi hardware using recorded laboratory inputs.

It does not denote live sensor acquisition, real-time BMS control, physical battery protection, or continuous operating field deployment.

## What failed

The negative results of this investigation include:
1. Standard absolute feature representations failed the validation tolerance (FPR 21.43%-73.81%).
2. Burn-in threshold adaptation failed the later-trajectory clean-FPR gate; synthetic sensitivity was withheld.
3. Causal sliding-window representations had weak gradual sensor drift sensitivity (pooled final recall below 5%).

## What changed because of those failures

These failures directly shaped the final system architecture:
- Abandoned absolute physical units in favor of dimensionless normalized historical residuals ($z$-scores relative to median/MAD).
- Shifted the reference frame from "population-level normal" to "cell-specific recent normal".
- Recognized the fundamental trade-off between drift robustness and tracking normal battery ageing.

## What I would do differently

Reflecting on the research progression:
1. **Initial representation choice:** I would begin with relative temporal residuals immediately rather than spending effort attempting to force absolute physical measurements to generalize across cells.
2. **Dual-timescale baselines:** To address the gradual drift vulnerability, I would investigate dual-timescale tracking: maintaining both a short-term sliding baseline (10 cycles) and a long-term anchored baseline from early life.
3. **Continuous-time streaming:** I would design the data extraction pipeline around streaming intra-cycle voltage curves rather than aggregated per-cycle summary statistics.

## Current limitations

- Laboratory datasets use constant-current cycling protocols under stable ambient temperatures; off-grid solar storage experiences erratic solar charging and variable load profiles.
- Evaluation relies on synthetic anomaly injection due to the lack of labelled operational faults in public data.
- The 10-cycle warmup window leaves the initial 10 cycles of any new battery unmonitored by the relative model.
- Inference occurs at cycle completion rather than detecting faults in real time during an ongoing discharge.

## Future work

Promising directions for extending this research include:
1. Evaluating the pipeline on unconstrained, variable-load solar battery field logs.
2. Exploring dual-timescale residual architectures to detect slow sensor calibration drift.
3. Implementing streaming intra-cycle anomaly detection directly on raw voltage and current time-series.
4. Profiling active hardware power draw during inference on edge microcontrollers.

## Reproducibility map

All supporting scripts and configs are structured as follows:
- Data extraction: `scripts/extract_nasa.py`, `scripts/extract_calce.py`
- Relative feature engineering: `scripts/build_nasa_relative_features.py`, `scripts/build_calce_relative_features.py`
- Training and validation: `scripts/train_nasa_isolation_forest.py` (absolute), `scripts/validate_nasa_relative_features.py` (relative), `scripts/calce_replication.py`
- Final evaluation: `scripts/finalize_nasa.py`, `scripts/evaluate_final_calce.py`
- Edge deployment: `deployment/pi/benchmark.py`, `deployment/pi/infer.py`

## Dataset acquisition and redistribution

Raw datasets are not redistributed in this repository. Researchers must obtain the raw files from the original repositories as documented in [docs/data-acquisition.md](data-acquisition.md).

## Artifact integrity

All executed historical metrics and receipts are inventoried in [docs/artifact-manifest.md](artifact-manifest.md). SHA-256 hashes confirm bitwise equivalence with original execution artifacts.

## Development and AI-assistance record

AI-assisted tools were used during research script development and public repository reconstruction. The scientific narrative and reported numbers are grounded in executed outputs.

## Closing record

This research demonstrates that lightweight unsupervised anomaly detection on resource-constrained edge hardware is computationally feasible (median 63.77 ms and p95 64.94 ms warm combined inference on a Raspberry Pi 3B+; maximum 88.63 ms) and achieves low false-alarm rates ($\le 5\%$) across different cells when framed around causal, history-relative degradation residuals.

Factual sources: [NASA final report](../results/nasa_final_test.md), [CALCE replication](../results/calce_replication_validation.md), [CALCE final report](../results/calce_final_test.md), [feature manifest](../config/nasa_relative_feature_manifest.json), and [Pi benchmark](../deployment/pi/results/pi_benchmark.json). Future-work reflections above are proposals, not executed experiments.
