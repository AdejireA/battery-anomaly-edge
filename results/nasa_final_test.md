> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/nasa_final_test.md`  
> **Archival SHA-256:** `dbfa5353e8f879964f0f2788ea5973d8f72a9f2085fbe29ccdd6296f23c75834`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# NASA final held-out evaluation

The user fixed the predeclared reporting-reference configuration before final-test access. No model, scaler, feature definition, history, threshold, protocol or magnitude was retuned after opening B0018. This report distinguishes development from held-out evidence; synthetic deviations are evaluation-only and are not claimed to be naturally observed faults.

## Freeze and selection

RELATIVE_B, 10 prior cycles, 100 trees, max_features=1.0, max_samples=auto, contamination=auto, seed=42. Scaler and model were copied from development, trained on 80 rows (cycles 11–50 from B0005 and B0006). P95 was the first eligible percentile under the all-three-seed clean B0007 FPR <=5% rule. Exact seed-42 threshold: 0.5548682376720724. Flag score > threshold; score = −score_samples. No synthetic metric was read for selection.

| seed | percentile | threshold | clean_fpr |
| --- | --- | --- | --- |
| 42 | 95.00000000 | 0.55486824 | 0.01898734 |
| 42 | 97.50000000 | 0.58979009 | 0.01898734 |
| 42 | 99.00000000 | 0.62609897 | 0.00632911 |
| 123 | 95.00000000 | 0.53713069 | 0.03797468 |
| 123 | 97.50000000 | 0.60043217 | 0.01898734 |
| 123 | 99.00000000 | 0.61021620 | 0.00632911 |
| 2026 | 95.00000000 | 0.55178268 | 0.01898734 |
| 2026 | 97.50000000 | 0.58846307 | 0.01265823 |
| 2026 | 99.00000000 | 0.62907031 | 0.00000000 |

Configuration SHA-256: fd4747b45ef8edfae3674fd284209b8df7b2aa4520906ca7ba9799eda46cde21. Freeze receipt was persisted before the first test-source open. The pre-freeze processed source hash covers the development-only snapshot; hashing the combined four-cell CSV before freeze would itself access the locked test data. The B0018 source hash is recorded separately after unlock: 52bdf14d6100b768111e4a74cc80ce04608e2a254271da33c924717f023b8d9b. Canonical configuration-payload and complete-file hashes are both recorded; no circular self-hash is claimed.

## DEVELOPMENT RESULTS — B0007

| anomaly_family | severity | precision | recall | f1 | pr_auc | roc_auc |
| --- | --- | --- | --- | --- | --- | --- |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.9777 | 0.8325 | 0.8993 | 0.9582 | 0.9751 |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.9808 | 0.9701 | 0.9754 | 0.9681 | 0.9839 |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.9812 | 0.9935 | 0.9873 | 0.9693 | 0.9846 |
| A3_THERMAL_ABNORMALITY | mild | 0.8041 | 0.0779 | 0.1421 | 0.6605 | 0.6964 |
| A3_THERMAL_ABNORMALITY | moderate | 0.9292 | 0.2494 | 0.3932 | 0.8262 | 0.8603 |
| A3_THERMAL_ABNORMALITY | strong | 0.9647 | 0.5195 | 0.6753 | 0.9122 | 0.9375 |
| A4_SENSOR_DRIFT | mild | 0.5940 | 0.0278 | 0.0531 | 0.5474 | 0.5774 |
| A4_SENSOR_DRIFT | moderate | 0.6240 | 0.0315 | 0.0600 | 0.5843 | 0.6282 |
| A4_SENSOR_DRIFT | strong | 0.6474 | 0.0349 | 0.0662 | 0.6125 | 0.6656 |

| count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 158 | 0.3936 | 0.0626 | 0.3278 | 0.3351 | 0.3706 | 0.5250 | 0.6353 |

| period | first_cycle | last_cycle | count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 11 | 63 | 53 | 0.4072 | 0.0610 | 0.3295 | 0.3367 | 0.3929 | 0.4910 | 0.6219 |
| middle | 64 | 116 | 53 | 0.3817 | 0.0633 | 0.3298 | 0.3332 | 0.3530 | 0.5294 | 0.6123 |
| late | 117 | 168 | 52 | 0.3919 | 0.0621 | 0.3278 | 0.3376 | 0.3693 | 0.5174 | 0.6353 |

## FINAL HELD-OUT TEST — B0018

Usable clean cycles: 122 (11–132); first 10 excluded for unavailable history. Flagged: 5; clean FPR: 4.098361%. False-positive cycles: [46, 47, 106, 107, 108].

| count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 122 | 0.3835 | 0.0588 | 0.3305 | 0.3371 | 0.3655 | 0.5033 | 0.6526 |

| period | first_cycle | last_cycle | flagged | fpr | count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| early | 11 | 51 | 2 | 0.0488 | 41 | 0.3883 | 0.0638 | 0.3305 | 0.3322 | 0.3660 | 0.5291 | 0.6109 |
| middle | 52 | 92 | 0 | 0.0000 | 41 | 0.3647 | 0.0238 | 0.3324 | 0.3375 | 0.3604 | 0.4088 | 0.4247 |
| late | 93 | 132 | 3 | 0.0750 | 40 | 0.3979 | 0.0733 | 0.3371 | 0.3407 | 0.3673 | 0.5762 | 0.6526 |

### Controlled anomalies

| anomaly_family | severity | precision | recall | f1 | pr_auc | roc_auc |
| --- | --- | --- | --- | --- | --- | --- |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.9265 | 0.5169 | 0.6636 | 0.8860 | 0.9414 |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.9526 | 0.8237 | 0.8835 | 0.9205 | 0.9640 |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.9576 | 0.9254 | 0.9412 | 0.9280 | 0.9682 |
| A3_THERMAL_ABNORMALITY | mild | 0.5844 | 0.0576 | 0.1049 | 0.7171 | 0.7768 |
| A3_THERMAL_ABNORMALITY | moderate | 0.8401 | 0.2153 | 0.3427 | 0.8356 | 0.9004 |
| A3_THERMAL_ABNORMALITY | strong | 0.9184 | 0.4610 | 0.6139 | 0.8978 | 0.9482 |
| A4_SENSOR_DRIFT | mild | 0.5233 | 0.0450 | 0.0828 | 0.5720 | 0.5968 |
| A4_SENSOR_DRIFT | moderate | 0.5260 | 0.0455 | 0.0837 | 0.6222 | 0.6593 |
| A4_SENSOR_DRIFT | strong | 0.5326 | 0.0467 | 0.0859 | 0.6579 | 0.7015 |

Precision = recall/(recall + clean FPR), corresponding to 50% evaluation prevalence. F1 uses this precision; PR-AUC is class-balanced non-interpolated average precision. ROC-AUC and recall are independent of that balancing. Raw instance metrics are also saved. Clean baseline observations are compared with all accepted synthetic windows; overlapping windows are dependent observations, not independent biological replicates. Zero-offset A4 onset rows are excluded from positive labels. No A1 evaluation applies to RELATIVE_B.

Every synthetic scenario starts after sufficient clean history. Within a scenario, earlier altered observations affect later causal medians/MADs; current/future observations never enter their own baseline. Different scenarios have isolated histories. All original physical guards remain active; rejected windows are logged, without clipping or changing magnitudes.

| anomaly_family | severity | channel | drift_sign | accepted_windows | rejected_windows | reasons |
| --- | --- | --- | --- | --- | --- | --- |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | joint | 0 | 118 | 0 | {} |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | joint | 0 | 118 | 0 | {} |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | joint | 0 | 118 | 0 | {} |
| A3_THERMAL_ABNORMALITY | mild | joint | 0 | 118 | 0 | {} |
| A3_THERMAL_ABNORMALITY | moderate | joint | 0 | 118 | 0 | {} |
| A3_THERMAL_ABNORMALITY | strong | joint | 0 | 118 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_voltage_v | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_voltage_v | 1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_temp_c | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_temp_c | 1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v | 1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_temp_c | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_temp_c | 1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_voltage_v | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_voltage_v | 1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_temp_c | -1 | 113 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_temp_c | 1 | 113 | 0 | {} |

### Score-distribution separation (independent of threshold)

| anomaly_family | severity | variant | count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLEAN | clean | pooled | 122 | 0.3835 | 0.0588 | 0.3305 | 0.3371 | 0.3655 | 0.5033 | 0.6526 |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 590 | 0.5435 | 0.0546 | 0.3252 | 0.4294 | 0.5569 | 0.6084 | 0.6664 |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 590 | 0.5756 | 0.0372 | 0.3620 | 0.5177 | 0.5769 | 0.6362 | 0.6946 |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 590 | 0.5842 | 0.0290 | 0.4483 | 0.5461 | 0.5815 | 0.6479 | 0.6946 |
| A3_THERMAL_ABNORMALITY | mild | pooled | 590 | 0.4374 | 0.0647 | 0.3317 | 0.3510 | 0.4308 | 0.5585 | 0.6256 |
| A3_THERMAL_ABNORMALITY | moderate | pooled | 590 | 0.4957 | 0.0693 | 0.3451 | 0.3742 | 0.5048 | 0.5970 | 0.6575 |
| A3_THERMAL_ABNORMALITY | strong | pooled | 590 | 0.5403 | 0.0597 | 0.3625 | 0.4291 | 0.5496 | 0.6188 | 0.6865 |
| A4_SENSOR_DRIFT | mild | pooled | 4068 | 0.3964 | 0.0606 | 0.3265 | 0.3375 | 0.3806 | 0.5310 | 0.6785 |
| A4_SENSOR_DRIFT | mild | mean_temp_c_-1 | 1017 | 0.3800 | 0.0626 | 0.3269 | 0.3345 | 0.3602 | 0.5310 | 0.6785 |
| A4_SENSOR_DRIFT | mild | mean_temp_c_1 | 1017 | 0.3915 | 0.0583 | 0.3291 | 0.3359 | 0.3733 | 0.5268 | 0.6503 |
| A4_SENSOR_DRIFT | mild | mean_voltage_v_-1 | 1017 | 0.4021 | 0.0540 | 0.3294 | 0.3448 | 0.3892 | 0.5118 | 0.6424 |
| A4_SENSOR_DRIFT | mild | mean_voltage_v_1 | 1017 | 0.4122 | 0.0624 | 0.3265 | 0.3459 | 0.3962 | 0.5565 | 0.6688 |
| A4_SENSOR_DRIFT | moderate | pooled | 4068 | 0.4066 | 0.0611 | 0.3236 | 0.3397 | 0.3930 | 0.5377 | 0.6785 |
| A4_SENSOR_DRIFT | moderate | mean_temp_c_-1 | 1017 | 0.3844 | 0.0631 | 0.3236 | 0.3341 | 0.3638 | 0.5319 | 0.6785 |
| A4_SENSOR_DRIFT | moderate | mean_temp_c_1 | 1017 | 0.3981 | 0.0581 | 0.3290 | 0.3430 | 0.3816 | 0.5283 | 0.6503 |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v_-1 | 1017 | 0.4153 | 0.0547 | 0.3305 | 0.3464 | 0.4076 | 0.5284 | 0.6379 |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v_1 | 1017 | 0.4288 | 0.0588 | 0.3269 | 0.3612 | 0.4214 | 0.5565 | 0.6688 |
| A4_SENSOR_DRIFT | strong | pooled | 4068 | 0.4151 | 0.0620 | 0.3262 | 0.3417 | 0.4045 | 0.5464 | 0.6785 |
| A4_SENSOR_DRIFT | strong | mean_temp_c_-1 | 1017 | 0.3915 | 0.0647 | 0.3262 | 0.3343 | 0.3681 | 0.5330 | 0.6785 |
| A4_SENSOR_DRIFT | strong | mean_temp_c_1 | 1017 | 0.4060 | 0.0597 | 0.3293 | 0.3479 | 0.3878 | 0.5420 | 0.6567 |
| A4_SENSOR_DRIFT | strong | mean_voltage_v_-1 | 1017 | 0.4240 | 0.0560 | 0.3305 | 0.3475 | 0.4226 | 0.5378 | 0.6402 |
| A4_SENSOR_DRIFT | strong | mean_voltage_v_1 | 1017 | 0.4388 | 0.0567 | 0.3341 | 0.3690 | 0.4383 | 0.5575 | 0.6688 |

## Generalization comparison

Clean FPR transferred at the predeclared aggregate criterion: B0007 seed-42 FPR was 1.90% (3/158), versus B0018 4.10% (5/122), both below 5%. This is one held-out cell, not a population-level guarantee.

A2 ranking transferred with some deterioration: strong AP/ROC-AUC changed from 0.969/0.985 on B0007 to 0.928/0.968 on B0018; strong recall declined from 99.35% to 92.54%. Mild A2 recall declined more, from 83.25% to 51.69%.

A3 ranking broadly transferred: strong AP/ROC-AUC was 0.912/0.937 in development and 0.898/0.948 on test. Strong recall was 51.95% versus 46.10%; mild/moderate detection remains limited.

A4 remained weak despite modestly better ranking on test: strong AP/ROC-AUC 0.658/0.702 with only 4.67% recall, close to the clean FPR of 4.10%. The principal persisting failure is drift detection, rather than a newly discovered wholesale generalization collapse.

Clean score medians were 0.366, 0.360, and 0.367 across early/middle/late thirds. There is no large sustained upward median drift. The late third nevertheless has 7.5% FPR and larger score spikes; all false positives are clustered at cycles 46-47 and 106-108. The aggregate target passes while local false-positive burden is uneven. No configuration or threshold was changed in response. All planned synthetic windows passed the existing physical guards; no magnitude adjustments or rejection-driven changes were made.

| anomaly_family | severity | precision_B0007 | recall_B0007 | f1_B0007 | pr_auc_B0007 | roc_auc_B0007 | precision_B0018 | recall_B0018 | f1_B0018 | pr_auc_B0018 | roc_auc_B0018 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.9777 | 0.8325 | 0.8993 | 0.9582 | 0.9751 | 0.9265 | 0.5169 | 0.6636 | 0.8860 | 0.9414 |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.9808 | 0.9701 | 0.9754 | 0.9681 | 0.9839 | 0.9526 | 0.8237 | 0.8835 | 0.9205 | 0.9640 |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.9812 | 0.9935 | 0.9873 | 0.9693 | 0.9846 | 0.9576 | 0.9254 | 0.9412 | 0.9280 | 0.9682 |
| A3_THERMAL_ABNORMALITY | mild | 0.8041 | 0.0779 | 0.1421 | 0.6605 | 0.6964 | 0.5844 | 0.0576 | 0.1049 | 0.7171 | 0.7768 |
| A3_THERMAL_ABNORMALITY | moderate | 0.9292 | 0.2494 | 0.3932 | 0.8262 | 0.8603 | 0.8401 | 0.2153 | 0.3427 | 0.8356 | 0.9004 |
| A3_THERMAL_ABNORMALITY | strong | 0.9647 | 0.5195 | 0.6753 | 0.9122 | 0.9375 | 0.9184 | 0.4610 | 0.6139 | 0.8978 | 0.9482 |
| A4_SENSOR_DRIFT | mild | 0.5940 | 0.0278 | 0.0531 | 0.5474 | 0.5774 | 0.5233 | 0.0450 | 0.0828 | 0.5720 | 0.5968 |
| A4_SENSOR_DRIFT | moderate | 0.6240 | 0.0315 | 0.0600 | 0.5843 | 0.6282 | 0.5260 | 0.0455 | 0.0837 | 0.6222 | 0.6593 |
| A4_SENSOR_DRIFT | strong | 0.6474 | 0.0349 | 0.0662 | 0.6125 | 0.6656 | 0.5326 | 0.0467 | 0.0859 | 0.6579 | 0.7015 |

Early/middle/late statistics are three nearly equal chronological portions of usable cycles, as declared before test access. Comparisons are descriptive for one held-out cell; no uncertainty claim based on treating overlapping windows as independent samples is made.

## Integrity and outputs

All frozen hashes matched before/after evaluation, including separate scaler/model serializations, original bundle, configuration, feature manifests, protocol, magnitudes and implementation files. Fitting was blocked. The evaluation start marker is exclusive: running the evaluation command again refuses to reopen the test experiment. Tests also exercise write rejection for frozen configuration and clean-only threshold selection.

Artifacts: config/final_nasa_model.json; models/final_nasa/ (bundle, scaler, model, source snapshot and hash receipts); results/nasa_final_test/ (scores, metrics, rejection counts, temporal statistics and integrity receipt); figures/nasa/final_test/ (five requested figures).

## Verification completion

All 8 final freeze/evaluation safety tests passed after evaluation, with no skipped tests. The 8 existing relative-feature tests passed before freeze. All 22 protected file hashes matched before/after the held-out run. Frozen configuration, separate model/scaler files, anomaly protocol and threshold were reverified after report generation. Five output figures passed image-integrity checks.

Implementation files: new scripts/finalize_nasa.py and tests/test_nasa_final_evaluation.py; existing scripts/build_nasa_relative_features.py and scripts/inject_nasa_anomalies.py gained explicit cell-authorization parameters before freeze, without changing any feature or perturbation calculation. Their original development-only defaults remain in place. No frozen implementation file was modified after freeze.
