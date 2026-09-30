# Reproduction, v0.2

There are three practical levels: a synthetic executable demonstration, verification of released scientific artifacts, and a separate full experiment using independently obtained data. The release does not redistribute NASA/CALCE observations or promise bitwise retraining equivalence.

## Environment

Use Python **3.14.6** for the tested workstation environment. Create a local environment and install the exact scientific subset:

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# POSIX shell: source .venv/bin/activate
python -m pip install -r requirements-lock.txt
```

`requirements.txt` lists direct source dependencies; `requirements-lock.txt` pins the scientific packages and runtime dependencies tested-compatible for v0.2 reproduction on Python 3.14.6 (Windows x86_64). Exact historical provenance differs across packages: NumPy 2.5.3, pandas 3.0.6, and scikit-learn 1.9.1 are historically recorded at model freeze in the NASA freeze configuration (`config/final_nasa_model.json`). SciPy 1.18.1, joblib 1.6.0, and threadpoolctl 3.7.0 are historically recorded in the edge deployment runtime (`deployment/pi/requirements-pi.txt` and `deployment/pi/infer.py`); SciPy 1.18.1, joblib 1.6.0, and matplotlib 3.11.2 are also corroborated by development validation records (`results/nasa_model_validation/run_provenance.json`). The transitive pins and matplotlib were verified in the surviving workstation environment and tested-compatible for v0.2 reproduction; a fresh network installation was not tested. This is not a claim that unpinned or newer library versions can safely deserialize the frozen models.

The historical physical Pi used Python **3.13.5**, Debian 13/aarch64 and [requirements-pi.txt](../deployment/pi/requirements-pi.txt). The recovered conversational history reports psutil 7.2.2 on the physical Pi. The checked saved environment and benchmark records do not independently preserve its exact version; requirements-pi.txt specifies a version range. psutil was absent from the workstation environment used for v0.2 validation. It is required for benchmarking, not the demo or artifact checks. No new Pi benchmark was performed. CALCE XLSX reading uses the repository's ZIP/XML implementation, so an Excel engine is not required. Tests use standard-library `unittest`.

## Level 1: synthetic demo (no external data)

From the release root:

```bash
python -B demo/run_demo.py
python -B demo/run_demo.py --output-dir output/demo
python -B -m unittest tests.test_calce_cs2_35_extraction tests.test_nasa_causal_features tests.test_v02_reproducibility -v
```

The demo creates observations from invented constants and seeded noise, fits a separate synthetic scaler/model and prints 30 predictions: ten history warmup rows followed by twenty scored rows. The optional files show the exact input schema and resulting scores. The demo uses the deployed prior-ten-cycle implementation, computes `(current - median(prior)) / (1.4826 * MAD(prior) + 1e-9)`, standardizes, negates Isolation Forest `score_samples` and compares against synthetic training P95. No current/future observation enters its own baseline. See [demo details](../demo/README.md). Synthetic alerts demonstrate mechanics, not physical fault validity or the study FPRs.

## Level 2: released models, figures and hashes

```bash
python -B scripts/verify_artifacts.py
python -B scripts/verify_artifacts.py --load-models
```

Expected: **114 released artifacts verified**, with the second command also loading the eight binary files after all hashes pass. The standard-library-only first command needs no scientific packages. Inspect [manifest.json](../artifacts/manifest.json), [artifact notes](../artifacts/README.md) and [historical evidence inventory](artifact-manifest.md). Only load trusted joblib files: deserialization can execute code, and a hash match alone does not authenticate an unknown publisher.

The final NASA/CALCE directories each contain estimator, scaler and the exact selected bundle. The Pi directory contains identical NASA estimator/scaler copies so its preserved hash-enforcing runner works. The NASA bundle's `final_threshold=None` and CALCE bundle's development status are historical metadata; final decisions use the frozen configuration, not those fields. The final configurations specify seed 42, 100 trees, full feature sampling, `max_samples='auto'`, `contamination='auto'` and strict `score > threshold`.

| Dataset | Train nominal proxy | Validation | Final test | Features / history | Frozen P95 |
|---|---|---|---|---|---|
| NASA | B0005/B0006 cycles 1–50; 80 fitted rows after history exclusion | B0007 | B0018 | Seven measurement-relative residuals / 10 | 0.5548682376720724 |
| CALCE | CS2-35/CS2-36 earliest 30%; 535 fitted rows after history exclusion | CS2-37 | CS2-38 | Four measurement-relative residuals / 10 | 0.595563163424274 |

NASA includes duration, time to 3.4 V, mean voltage/current and mean/max/delta temperature. CALCE has the first four channels only and uses its own separately fitted model. Early life is a nominal proxy, not a certified fault-free period. History 10 is the reporting reference, not a global optimum.

The six [figures](../artifacts/figures/) are unchanged surviving research plots, identified individually in the manifest. Two are clean B0007 validation summaries; four show final clean B0018/CS2-38 or B0018 synthetic results. Formal publication placement is unknown. A4 precision/F1/AP use 50% evaluation prevalence, and plot label `pr_auc` means average precision. The score-drift comparison has model-specific score scales and one differing thermal input, so it is not an isolated causal ablation.

## Level 3: independent full experiment

Obtain **B0005, B0006, B0007, B0018** from NASA Ames PCoE and **CS2-35, CS2-36, CS2-37, CS2-38** from the University of Maryland CALCE Battery Research Group. [Data acquisition](data-acquisition.md) records provider names, file formats and placement. No verified download URL survives in the released acquisition guide; none is invented here. The external provider's terms and exact workbook set must be checked independently.

Prepare an isolated run layout, because research scripts derive their root from their own file location and can overwrite results. Simply changing the shell directory is insufficient:

```bash
python -B scripts/prepare_reproduction.py
cd output/reproduction
```

The helper refuses an existing destination and only creates a subdirectory under release `output/`. It copies source, tests and non-final configurations; it does not copy historical results, frozen models, data, virtual environments or Git state. It intentionally omits both final configurations so write-once freezing can create new records. All commands below run in this new directory with the environment activated. Preparation was tested; the external-data pipeline was not rerun for this upgrade.

Place raw NASA MATLAB files at `data/raw/nasa/B0005.mat`, `B0006.mat`, `B0007.mat`, `B0018.mat`. Place each CALCE cell's XLSX workbooks under `data/raw/calce/CS2_35/`, `CS2_36/`, `CS2_37/`, `CS2_38/`, preserving workbook filenames and all test intervals. Extraction performs descriptive access to all four cells. The guarded development/finalization boundary follows extraction; it does not mean B0018/CS2-38 were never opened earlier.

### NASA preprocessing and development

```bash
python -B scripts/extract_nasa.py
python -B scripts/audit_nasa_features.py
python -B scripts/build_nasa_splits.py
python -B scripts/inspect_voltage_cutoff.py
python -B scripts/analyze_anomaly_ranges.py
python -B scripts/inject_nasa_anomalies.py
python -B scripts/train_nasa_isolation_forest.py
python -B scripts/analyze_cross_cell_shift.py
python -B scripts/evaluate_nasa_burnin.py
python -B scripts/build_nasa_relative_features.py
python -B scripts/validate_nasa_relative_features.py
python -B scripts/diagnose_nasa_failures.py
```

Extraction creates per-cell discharge summaries and the combined NASA table under `data/processed/nasa/`. Completed-cycle causal summaries include trailing capacity slope; the later history-relative baseline is strictly prior-only. Keep the frozen feature and anomaly definitions intact. The guarded loaders use individual development-cell files. Relative construction writes development-only tables under `data/processed/nasa_relative/`; validation fits StandardScaler/IsolationForest on nominal B0005/B0006 rows, compares clean B0007 FPR across predefined seeds and computes synthetic sensitivity only for eligible configurations. The absolute-model phase supplies comparison scores consumed by relative validation. Intermediate source-derived tables and model collections are local outputs, not release assets.

### Freeze before NASA final evaluation

```bash
python -B scripts/finalize_nasa.py freeze
python -B scripts/finalize_nasa.py evaluate
```

Freezing checks clean-only percentile eligibility across seeds 42/123/2026, selects the predefined seed-42 RELATIVE_B/history-10 reference and records input/model/configuration hashes before the guarded B0018 unlock. Evaluation prohibits fitting and retuning. Outputs include a new `config/final_nasa_model.json`, `models/final_nasa/` and `results/nasa_final_test/`, including clean scores, temporal statistics, synthetic metrics and integrity receipts. A new run has new timestamps/hash chains; never overwrite the released receipts to make new hashes match.

### Separate CALCE replication and final evaluation

```bash
python -B scripts/inspect_calce_workbooks.py
python -B scripts/extract_calce_cs2_35.py
python -B scripts/extract_calce.py
python -B scripts/audit_calce_cells.py
python -B scripts/build_calce_relative_features.py
python -B scripts/calce_replication.py
python -B scripts/evaluate_final_calce.py
```

CALCE preprocessing orders and deduplicates workbooks and selects complete main discharges, retaining qualifying initial characterization cycles. Outputs include `data/processed/calce/CS2_35_discharge_features.csv` and equivalents, the combined table, and a development-only relative table. Independent fitting uses CS2-35/36 and validates on CS2-37. The final command freezes once and then evaluates CS2-38; `--evaluate` is only for an already-created valid local freeze. Generated results go to `results/calce_replication/` and `results/calce_final_test/`, with a new final configuration/model directory. No NASA fitted model is transferred.

### Synthetic evaluation and expected scientific outputs

The preserved NASA final evaluator uses A2/A3 five-cycle windows and A4 ten-cycle ramps; CALCE uses A2/A4 without thermal channels. Each scenario starts with clean prior context and evolves independently. Earlier injected values enter later baselines, zero-offset drift onset is excluded from positive labels, and physical guards reject whole invalid windows. Magnitudes come from validation-only protocols. Labels denote synthetic perturbations, not observed battery faults; overlapping scenarios are dependent. A1 has no frozen RELATIVE_B final result. Gradual drift remains difficult.

| Clean result | Historical reference |
|---|---|
| B0007 validation, seed 42 | 3/158 = 1.90% |
| B0018 final test | 5/122 = 4.10% |
| CS2-37 validation, seed 42 P95 | 26/1026 = 2.53% |
| CS2-37 validation P95 mean, seeds 42/123/2026 | 3.15% |
| CS2-38 final test | 32/1015 = 3.15% |

Compare counts, thresholds, feature order and metrics with the released evidence. A changed workbook set, preprocessing result, runtime or numerical backend can change fitted trees and scores; investigate differences rather than forcing the historical percentages. Full raw-data execution and bitwise retraining equivalence remain unverified in v0.2.

### Physical Pi replay

The released NASA binaries allow the unchanged `deployment/pi/infer.py` to load in its pinned environment. To reproduce recorded replay, independently regenerate B0018 cycle features and matching workstation expected scores, including ten initial history rows and 122 scorable predictions. `validate_playback.py` requires expected columns `cell_id`, `cycle`, `score`, `flagged` (true/false), containing only scorable cycles; keys must match the replay exactly. Use its implementation as the comparison contract. From the release root, after creating the local inputs:

```bash
python -B deployment/pi/infer.py --input output/B0018_cycles.csv --output output/B0018_predictions.csv
python -B deployment/pi/validate_playback.py --input output/B0018_cycles.csv --expected output/B0018_expected.csv --output output/local_playback_validation.json
python -B deployment/pi/benchmark.py --input output/B0018_cycles.csv --output-prefix output/local_pi_benchmark --label "physical Raspberry Pi 3B+ replay"
```

Use the last command on actual Pi hardware with its optional benchmark dependencies installed; a workstation run is not a Pi measurement. These commands require locally reconstructed inputs, not files promised in the public release. Historical reference: 122 scorable B0018 predictions, zero mismatches, warm median 63.77 ms, P95 64.94 ms, throughput 15.64 observations/s. Timing excludes input and context preparation. Saved peak RSS is below instantaneous RSS; the cause remains unknown. This was recorded cycle-level replay, not live sensing, field deployment, BMS integration or autonomous control.

## Test scope

The Level 1 command is self-contained. Existing research tests remain unchanged and many require excluded processed data/development models. Full `unittest discover -s tests -v` on the release is not expected to be green: the baseline already contained missing-input errors and two archive inventory comparisons that do not describe the public subset. Artifact verification checks only the released subset and never rewrites historical receipts. See [v0.2 validation record](v02-validation.md) for exact observed results and remaining limitations.
