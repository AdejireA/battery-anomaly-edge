> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/calce_final_test.md`  
> **Archival SHA-256:** `7cb1cc7ef999aee1403dc414fde13aeea8e838021802650fdb34815acbc6fabc`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# Frozen CALCE final evaluation

## Descriptive generalization assessment

Clean transfer met the predefined requirement: CS2-38 FPR is 32/1015 = 3.1527%, compared with 2.5341% on CS2-37 for the frozen seed-42 model. The increase is 0.6186 percentage points, and both remain below 5%. Test scores have mean 0.37890, median 0.34623 and P95 0.54948, versus development mean 0.36750, median 0.33968 and P95 0.52346. There is a modest score-distribution shift but no failure of the clean-FPR criterion.

A2 ranking transferred with modest degradation: development versus final-test PR-AUC is 0.8460 versus 0.8205 (mild), 0.9054 versus 0.8882 (moderate), and 0.9380 versus 0.9259 (strong). ROC-AUC is 0.8779 versus 0.8553, 0.9273 versus 0.9102, and 0.9533 versus 0.9406. The increasing severity response transferred in recall, F1, PR-AUC and ROC-AUC. Test recall is 20.26%, 35.51%, and 49.44%; useful ranking does not imply high thresholded sensitivity, and even strong A2 misses approximately half of injected observations.

A4 remains weak. Test recall is 2.92%, 3.25%, and 3.61%, close to the 3.15% clean FPR. Its PR-AUC is 0.5413, 0.5723, and 0.6014, lower than development 0.5582, 0.5970, and 0.6319. ROC-AUC is 0.5856, 0.6372, and 0.6776 versus development 0.6072, 0.6687, and 0.7144. This reproduces the weak drift sensitivity rather than revealing a new successful drift detector.

No sustained upward late-life mean-score drift appears: early/middle/late means are 0.37902/0.38274/0.37495 and FPRs are 2.95%/4.73%/1.78%. Late median 0.34623 is slightly above early median 0.34469; transient score spikes and clustered flags remain. These summaries are descriptive, not proof of stationarity. There is no major unexpected aggregate generalization failure; limited A2 recall and weak A4 detection remain material limitations. Nothing was retuned after opening CS2-38.

## Verification and generated files

All seven tests in `tests/test_final_calce.py` pass. They verify the access gate, write-once configuration, pre/post hashes and access timestamps, clean-only selection and training provenance, exact feature/injection adapter equivalence, no-fit scoring, and equality of serialized final components with the original development model. All 260 NASA artifact hashes match the development integrity record.

New files: `scripts/evaluate_final_calce.py`, `tests/test_final_calce.py`, `config/final_calce_model.json`; the bundle, separate scaler/model, SHA256 sidecar and freeze receipt under `models/final_calce/`; this report; clean scores, period statistics, summary, synthetic copies/window counts, anomaly metrics, development comparison and integrity records under `results/calce_final_test/`. Original development scripts, protocols, data and NASA artifacts were not modified.

Figures under `figures/calce/final_test/`: `cs2_38_clean_score_vs_cycle.png`, `cs2_38_anomaly_score_distributions.png`, `cs2_38_A2_severity.png`, `cs2_38_A4_severity.png`.

## Freeze and selection

Seed 42 is the first predefined seed, not selected by synthetic performance. P95 was the first clean-only all-seed eligible percentile. Exact threshold: 0.595563163424274. Configuration SHA256: 571fb85db6aba717bee1c7a1353a9ca20ac1fe9eab578d8f34740a2160bb00fe. Freeze receipt: 2026-09-20T02:13:19.750825+00:00; first test-source access: 2026-09-20T02:13:20.513911+00:00. No fitting, recalibration or retuning occurred.

## DEVELOPMENT — CS2-37

| seed | percentile | threshold | clean_fpr | training_rows | validation_rows | threshold_source |
|---|---|---|---|---|---|---|
| 42 | 95 | 0.595563 | 0.0253411 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 42 | 97.5 | 0.663556 | 0.0136452 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 42 | 99 | 0.707657 | 0.00487329 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 123 | 95 | 0.594081 | 0.0341131 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 123 | 97.5 | 0.668308 | 0.0155945 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 123 | 99 | 0.708086 | 0.00389864 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 2026 | 95 | 0.580072 | 0.0350877 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 2026 | 97.5 | 0.663818 | 0.0136452 | 535 | 1026 | clean_nominal_CALCE_training_only |
| 2026 | 99 | 0.705646 | 0.00487329 | 535 | 1026 | clean_nominal_CALCE_training_only |

| family | severity | precision | recall | f1 | pr_auc | roc_auc |
|---|---|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.876965 | 0.180626 | 0.299554 | 0.846042 | 0.877926 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.922667 | 0.302348 | 0.45545 | 0.90543 | 0.92734 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.948296 | 0.464775 | 0.62381 | 0.937956 | 0.953251 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 0.45224 | 0.0209221 | 0.039994 | 0.558212 | 0.607189 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 0.492398 | 0.0245821 | 0.0468265 | 0.597018 | 0.668727 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 0.526587 | 0.0281875 | 0.0535106 | 0.631858 | 0.714355 |

## FINAL HELD-OUT TEST — CS2-38

{
  "threshold": 0.595563163424274,
  "usable_cycles": 1015,
  "flagged": 32,
  "clean_fpr": 0.03152709359605911,
  "flagged_cycles": [
    69,
    88,
    137,
    138,
    228,
    237,
    238,
    239,
    240,
    241,
    355,
    356,
    357,
    358,
    359,
    492,
    494,
    495,
    544,
    545,
    592,
    595,
    656,
    660,
    661,
    662,
    712,
    755,
    757,
    829,
    835,
    888
  ],
  "score_distribution": {
    "count": 1015,
    "mean": 0.3789018358983376,
    "std": 0.07908959588434779,
    "p05": 0.322785860686818,
    "median": 0.3462273346578459,
    "p95": 0.5494789708830135,
    "minimum": 0.3208663901378803,
    "maximum": 0.7934279687532505
  }
}

| period | first_cycle | last_cycle | count | mean | std | p05 | median | p95 | minimum | maximum | flagged | clean_fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| early | 11 | 349 | 339 | 0.379018 | 0.0790957 | 0.322875 | 0.34469 | 0.563587 | 0.321266 | 0.706808 | 10 | 0.0294985 |
| middle | 350 | 687 | 338 | 0.382741 | 0.0861118 | 0.322541 | 0.347455 | 0.590306 | 0.320866 | 0.793428 | 16 | 0.0473373 |
| late | 688 | 1025 | 338 | 0.374946 | 0.0714196 | 0.323234 | 0.346231 | 0.519272 | 0.321236 | 0.77696 | 6 | 0.0177515 |

| family | severity | precision | recall | f1 | pr_auc | roc_auc |
|---|---|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.865326 | 0.202572 | 0.328291 | 0.820532 | 0.855347 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.918455 | 0.355094 | 0.512172 | 0.888168 | 0.910241 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.94005 | 0.494362 | 0.647966 | 0.925886 | 0.940577 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 0.480484 | 0.0291584 | 0.0549803 | 0.541308 | 0.585621 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 0.507806 | 0.0325271 | 0.061138 | 0.572292 | 0.637196 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 0.533924 | 0.0361166 | 0.0676567 | 0.601437 | 0.677557 |

## Score separation independent of threshold

| family | severity | score_count | score_mean | score_std | score_p05 | score_median | score_p95 | score_minimum | score_maximum |
|---|---|---|---|---|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 5055 | 0.505769 | 0.113246 | 0.355361 | 0.473666 | 0.745512 | 0.320427 | 0.811891 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 5055 | 0.557406 | 0.114332 | 0.393482 | 0.542053 | 0.790214 | 0.32528 | 0.811891 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 5055 | 0.596543 | 0.111449 | 0.420595 | 0.593389 | 0.793965 | 0.332503 | 0.812991 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 18108 | 0.388032 | 0.0759941 | 0.324845 | 0.359162 | 0.556417 | 0.320283 | 0.793428 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 18108 | 0.396234 | 0.0764575 | 0.32803 | 0.368426 | 0.562107 | 0.320417 | 0.793428 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 18108 | 0.405272 | 0.0776095 | 0.330585 | 0.378546 | 0.570024 | 0.321136 | 0.797734 |

## Frozen synthetic evaluation semantics

The exact development function bodies are reused via AST, excluding the development entry point and all fitting/calibration functions. Only authorization/provenance cell literals change to CS2-38. The relative-feature cell allowlist permits the test cell after the freeze gate; its calculations are identical. Five-cycle A2 offsets and ten-cycle signed A4 ramps use frozen CS2-37 magnitudes. Each window begins with ten clean prior observations; prior injected observations adapt later baselines within that isolated copy. Current/future observations never enter their own baseline. A4 zero-offset onset is excluded from positive labels. Both drift signs are pooled. Physical guards reject whole windows; no magnitudes are clipped or recalculated.

Precision, F1 and average precision (reported as PR-AUC) use 50% evaluation prevalence, matching development. Recall and ROC-AUC are class-conditional/unweighted. Overlapping scenarios are dependent synthetic copies, not independent real faults. Clean scores are never overwritten.

| family | severity | sign | accepted_windows | rejected_windows |
|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 0 | 1011 | 0 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0 | 1011 | 0 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 0 | 1011 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | -1 | 1006 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 1 | 1006 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | -1 | 1006 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 1 | 1006 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | -1 | 1006 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 1 | 1006 | 0 |

## Integrity

All 260 frozen NASA hashes match. All pre-test CALCE hashes match after evaluation, including separate scaler/model, bundle, final configuration, source tables, feature code and anomaly protocol. The test-source hash was first computed after unlock and also matches after evaluation. The combined source table was never read; pre-freeze processed-source hashes cover the development-only relative table and three development source tables. The final configuration digest is external to avoid circular self-hashing. See calce_final_test/integrity_checks.json.
