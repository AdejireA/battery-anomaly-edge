# Research workflow and pipeline map

This document maps each stage of the research workflow to its corresponding scripts, configuration files, and result directories.

## Pipeline overview

The project comprises two parallel research tracks:
1. **NASA track (Primary development):** Exploration of absolute feature limitations, cross-cell diagnosis, burn-in calibration experiments, transition to causal relative features, guarded model freezing, and physical Raspberry Pi replay benchmarking.
2. **CALCE track (Independent replication):** Independent data engineering and methodological replication across more than 1,000 cycles on prismatic lithium cobalt oxide cells.

---

## 1. NASA research pipeline

### Stage 1: Dataset inspection and extraction
- **Objective:** Parse raw NASA Ames `.mat` files, inspect cycle cutoffs, and segment discharge cycles.
- **Scripts:**
  - `scripts/inspect_nasa.py`: Inspects variable names, structures, and cycle counts.
  - `scripts/inspect_voltage_cutoff.py`: Documents cell-specific discharge voltage cutoff thresholds (2.7 V, 2.5 V, 2.2 V, 2.5 V).
  - `scripts/extract_nasa.py`: Extracts per-cycle physical features.
- **Inputs:** `data/raw/nasa/` (`B0005.mat`, `B0006.mat`, `B0007.mat`, `B0018.mat`). *(External, not committed)*
- **Outputs:** `data/processed/nasa/*.csv`. *(Excluded from public release)*

### Stage 2: Feature auditing and partition definition
- **Objective:** Verify physical measurement ranges, check correlations, and formalize cell splits.
- **Scripts:**
  - `scripts/audit_nasa_features.py`: Audits ranges, missingness, and collinearity.
  - `scripts/build_nasa_splits.py`: Establishes training (B0005, B0006), validation (B0007), and guarded test (B0018) definitions.
- **Configurations:**
  - `config/nasa_feature_manifest.json`: Feature definitions and valid measurement ranges.
  - `config/nasa_experiment_protocol.json`: Formal partition protocol and cell roles.

### Stage 3: Absolute-feature model development
- **Objective:** Train initial Isolation Forest models on raw physical features and evaluate cross-cell transfer.
- **Scripts:**
  - `scripts/train_nasa_isolation_forest.py`: Fits models across hyperparameter grid and computes validation scores.
- **Configurations:**
  - `config/nasa_model_development.json`: Grid search parameters (`n_estimators`, `max_features`, contamination settings).
- **Results:**
  - `results/nasa_model_validation/`: Documents the initial failure (validation clean FPR 21.43%-73.81%).
  - `results/nasa_model_validation.md`: Historical report analyzing cross-cell transfer failure.

### Stage 4: Cross-cell diagnosis and burn-in experiment
- **Objective:** Diagnose cause of high false alarms and test target-cell burn-in threshold adaptation.
- **Scripts:**
  - `scripts/analyze_cross_cell_shift.py`: Evaluates feature distribution drift between training and validation cells.
  - `scripts/nasa_burnin.py`: Implements burn-in threshold calibration logic.
  - `scripts/evaluate_nasa_burnin.py`: Evaluates burn-in thresholds on later clean validation; synthetic evaluation is gated and was withheld because no configuration qualified.
- **Results:**
  - `results/nasa_burnin_calibration/`: Evidence of 63.70%-100% later clean FPR and zero all-seed eligible groups.
  - `results/nasa_burnin_calibration.md`: Historical report documenting the rejection of burn-in calibration.

### Stage 5: Causal relative-feature development
- **Objective:** Transform features into causal residuals normalized by sliding-window median and MAD.
- **Scripts:**
  - `scripts/build_nasa_relative_features.py`: Computes causal historical residuals for windows $k \in \{5, 10, 20\}$.
  - `scripts/validate_nasa_relative_features.py`: Evaluates clean FPR and seed stability across relative representations.
- **Configurations:**
  - `config/nasa_relative_feature_manifest.json`: Relative feature formulas, residual definitions, and parameter bounds.
- **Results:**
  - `results/nasa_relative_features/`: Selection of `RELATIVE_B` with history $k=10$ as the reporting reference.
  - `results/nasa_relative_feature_validation.md`: Historical validation report confirming clean FPR $< 5\%$.

### Stage 6: Anomaly protocol and failure analysis
- **Objective:** Formulate controlled synthetic anomaly injection protocols and evaluate detector sensitivity limits.
- **Scripts:**
  - `scripts/inject_nasa_anomalies.py`: Injects synthetic anomalies A1 (sustained accelerated degradation), A2 (voltage collapse), A3 (thermal spike), A4 (sensor drift).
  - `scripts/analyze_anomaly_ranges.py`: Calibrates synthetic magnitudes from B0007 measurement distributions before model evaluation.
  - `scripts/diagnose_nasa_failures.py`: Examines failure modes, notably weak gradual sensor drift detection.
- **Configurations:**
  - `config/anomaly_injection_protocol.json`: Injection magnitudes and perturbation formulas.
- **Results:**
  - `results/nasa_failure_analysis/`: Diagnostic summaries and rank correlation statistics.
  - `results/nasa_failure_analysis.md`: Historical analysis documenting weak detection of gradual drift.

### Stage 7: Guarded NASA finalization and test evaluation
- **Objective:** Permanently freeze NASA model parameters and evaluate on guarded test cell B0018.
- **Scripts:**
  - `scripts/finalize_nasa.py`: Freezes model, verifies integrity hashes, unlocks B0018, and calculates final test metrics.
- **Configurations:**
  - `config/final_nasa_model.json`: Frozen configuration specification and threshold ($0.554868$).
- **Results:**
  - `results/nasa_final_test/`: Final test metrics (122 scorable cycles, 5 flagged, clean FPR $4.10\%$).
  - `results/nasa_final_test.md`: Final test report.

### Stage 8: Edge packaging and physical Raspberry Pi benchmark
- **Objective:** Package inference code, verify prediction equivalence on edge runtime, and measure physical inference latency.
- **Scripts:**
  - `deployment/pi/validate_playback.py`: Verifies zero prediction discrepancies on B0018 replay.
  - `deployment/pi/benchmark.py`: Runs 1,000 timed observations with latency and memory profiling.
- **Artifacts & Results:**
  - `deployment/pi/artifacts/final_nasa_model.json`: Frozen model metadata and threshold.
  - `deployment/pi/results/pi_benchmark.json`: Execution latency (median 63.77 ms) and throughput logs.
  - `deployment/pi/results/playback_validation.json`: Verification receipt confirming 0 prediction mismatches.
  - `deployment/pi/results/pi_environment.txt`: Hardware system information (Debian 13, Python 3.13.5).

---

## 2. CALCE replication pipeline

### Stage 1: Workbook inspection and segmentation validation
- **Objective:** Inspect CALCE multi-sheet Excel files and validate complete-discharge cycle extraction.
- **Scripts:**
  - `scripts/inspect_calce_workbooks.py`: Parses workbook metadata and step indices.
  - `scripts/extract_calce_cs2_35.py`: Validates cycle segmentation on cell CS2-35.

### Stage 2: Full CALCE extraction and auditing
- **Objective:** Extract all four CALCE cells and audit feature distributions across 1,000+ cycles.
- **Scripts:**
  - `scripts/extract_calce.py`: Processes cells CS2-35, CS2-36, CS2-37, and CS2-38.
  - `scripts/audit_calce_cells.py`: Audits extraction integrity and validates absence of thermal channels.
- **Outputs:** `data/processed/calce/*.csv`. *(Excluded from public release)*

### Stage 3: CALCE relative feature engineering
- **Objective:** Construct 4-channel relative residual features (`duration_s`, `time_to_3_4v_s`, `mean_voltage_v`, `mean_current_a`).
- **Scripts:**
  - `scripts/build_calce_relative_features.py`: Generates causal relative tables for CS2 cells.
- **Outputs:** `data/processed/calce/calce_cs2_relative_features.csv`. *(Excluded from public release)*

### Stage 4: CALCE replication training and validation
- **Objective:** Fit independent Isolation Forest on CS2-35/36 and validate clean FPR on CS2-37.
- **Scripts:**
  - `scripts/calce_replication.py`: Fits model from scratch, establishes P95 threshold ($0.595563$), and validates on CS2-37.
- **Configurations:**
  - `config/calce_experiment_protocol.json`: Partition roles and cell parameters.
  - `config/calce_anomaly_injection_protocol.json`: CALCE synthetic anomaly configurations.
- **Results:**
  - `results/calce_replication/`: Validation metrics (CS2-37 clean FPR $2.53\%$ on seed 42 reference; 3-seed mean $3.15\%$).
  - `results/calce_replication_validation.md`: Historical replication report.

### Stage 5: CALCE final evaluation
- **Objective:** Evaluate the frozen CALCE model on guarded final cell CS2-38 across 1,015 scorable cycles.
- **Scripts:**
  - `scripts/evaluate_final_calce.py`: Evaluates frozen CALCE model on CS2-38.
- **Configurations:**
  - `config/final_calce_model.json`: Frozen CALCE model metadata and decision threshold.
- **Results:**
  - `results/calce_final_test/`: Final test metrics (1,015 scorable cycles, 32 flagged, clean FPR $3.15\%$).
  - `results/calce_final_test.md`: Historical final evaluation report.

Protocol calibration precedes synthetic evaluation even though the supporting scripts are grouped by topic above. B0018 and CS2-38 appeared in extraction/descriptive audits but were excluded from guarded fitting/threshold selection. History 10 is the selected reporting reference, not a global optimum. Paths marked excluded describe research outputs, not promised release contents.
