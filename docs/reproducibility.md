# Reproducibility guide

This document provides a realistic, tiered overview of reproducibility for this repository. It specifies what can be verified directly from committed public assets, what requires external data downloads, and what historical artifacts remain archive-only.

## Reproducibility tiers

### Level 1: Inspect public evidence (Self-contained)
All final numerical results, threshold tables, score distribution summaries, synthetic anomaly recall matrices, and physical hardware replay benchmark logs are committed directly to this repository under:
- `results/`: Metric summaries, threshold tables, seed stability audits, and sanitized historical markdown reports.
- `deployment/pi/results/`: Benchmark logs, execution timing distributions, and playback validation receipts.
- `docs/artifact-manifest.md`: SHA-256 integrity manifest tracking the exact provenance of all committed public evidence.

No external downloads, model fitting, or hardware execution are required to audit Level 1 evidence.

### Level 2: Re-run pipeline from raw data (Data-dependent)
Researchers who obtain the external raw NASA Ames and CALCE datasets (see [docs/data-acquisition.md](data-acquisition.md)) can execute the extraction, relative feature engineering, and model fitting scripts. 
- Running extraction scripts regenerates `data/processed/nasa/` and `data/processed/calce/`.
- Running feature engineering scripts regenerates `data/processed/nasa_relative/` and `data/processed/calce/calce_cs2_relative_features.csv`.
- Running training scripts fits fresh `StandardScaler` and `IsolationForest` instances and recalculates thresholds.

*Important:* Re-running training scripts generates new model instances. Because scikit-learn tree construction can vary slightly across operating systems and library versions, re-running does not guarantee bit-for-bit identical decision scores, and future runs are not guaranteed to reproduce the historical clean-FPR outcome.

### Level 3: Historical binary verification (Archive-only)
In this initial public reconstruction, serialized model binaries (`.joblib`), full per-cycle raw observation tables, and full-resolution trajectory figures are excluded to maintain a clean, lightweight public distribution. Exact bitwise SHA-256 hash chains referencing historical `.joblib` model binaries can only be validated against the private archival workspace.

## Environment and dependencies

### Python environment
The research code was developed and verified on Python 3.13 and Python 3.14.
- Minimum public dependencies are specified in `requirements.txt`:
  ```
  numpy>=2.0.0
  scipy>=1.9
  pandas>=1.5
  matplotlib>=3.6
  scikit-learn>=1.3
  joblib>=1.3
  psutil>=5.9
  ```
- *NumPy note:* `numpy>=2.0.0` is required because `scripts/extract_calce_cs2_35.py` uses `np.trapezoid` (introduced in NumPy 2.0.0 to replace the deprecated `np.trapz`).
- *Raspberry Pi environment:* The physical hardware benchmark used Python 3.13.5 on Debian 13 (aarch64) with exact pinned dependencies recorded in `deployment/pi/requirements-pi.txt`.

## Pipeline execution order

The preserved entry points are research programs, not a one-command fresh-clone runner. Use a separate experimental checkout and output plan; changing only the shell working directory does not redirect scripts that derive ROOT from __file__. Do not overwrite committed evidence or frozen configuration.

The historical dependency sequence is: NASA extraction/audit and anomaly protocol; absolute development; cross-cell/burn-in analysis; relative feature construction and `validate_nasa_relative_features.py`; saved-output failure diagnostics; `finalize_nasa.py` freeze/evaluation; CALCE extraction/audit, relative construction and replication; `evaluate_final_calce.py` freeze/evaluation.

Write-once finalization refuses existing final configurations, and integrity checks reference archive-only inputs. Recreating the full experiment therefore needs an explicit independent run layout and dependency inventory. A newly trained model will not satisfy the frozen Pi runtime's exact artifact hash checks. This release provides inspectable source and compact evidence, not guaranteed fresh-clone end-to-end execution. See [workflow](workflow.md) and [artifact manifest](artifact-manifest.md).

## Test suite classification

The 13 actual modules are:

| Module | Scope |
|---|---|
| `test_calce_cs2_35_extraction.py` | Public-safe synthetic extraction fixtures (7 tests) |
| `test_nasa_causal_features.py` | Public-safe trailing five-cycle OLS/median and prefix-invariance fixtures (3 tests); current completed cycle is included in the causal slope, unlike prior-only relative baselines |
| `test_anomaly_protocol.py` | Processed NASA data and frozen calibration |
| `test_calce_cells.py` | Processed CALCE tables and extraction audit records |
| `test_nasa_splits.py` | Combined processed NASA table |
| `test_calce_replication.py` | Processed CALCE/model/result dependencies |
| `test_final_calce.py` | Frozen CALCE binaries and processed data |
| `test_nasa_burnin.py` | Processed NASA/development model dependencies |
| `test_nasa_final_evaluation.py` | Final NASA configuration and omitted hash-chain dependencies |
| `test_nasa_model_development.py` | Processed nominal/validation NASA data |
| `test_nasa_relative_features.py` | Processed NASA/development model dependencies |
| `test_pi_deployment.py` | Omitted frozen binaries and sample data |
| `test_nasa_failure_analysis.py` | Historical snapshot verification and safety guards |

The historical failure-analysis snapshot comparison has a known scope mismatch after later files were added. Do not silently update historical inventories to make it pass. Pytest marker declarations do not automatically mark or isolate these unchanged tests. Use the explicit public-safe selection below.

## Running public-safe tests

Run from the public repository root with dependencies installed:

```bash
python -B -m unittest tests.test_calce_cs2_35_extraction tests.test_nasa_causal_features
```

The Phase 3 baseline was 10 tests passed. Runtime depends on the environment; this selection does not validate omitted binaries or reproduce the research experiments.

