> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/nasa_burnin_calibration.md`  
> **Archival SHA-256:** `329815a6db56fd21ab7ceadd881a3f1f6c491cbdb6e1170ed49fb99cd816a019`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# Label-free B0007 burn-in calibration

Validation experiment only: no final model/threshold selection and no final-test access. All 24 saved development models are loaded read-only; StandardScaler.fit/partial_fit and IsolationForest.fit are disabled at runtime. No scaler/model refitting or frozen magnitude/feature changes.

Result: 0 of 72 configuration/fraction/percentile combinations meet the all-seed clean-FPR requirement. Individual-run FPR spans 63.70%–100.00%. The tested early per-cell burn-in calibration does not solve the later clean-trajectory threshold shift.

### Calibration/evaluation row counts

| feature_set | calibration_fraction | boundary_cycle | calibration_rows | post_calibration_clean_rows |
| --- | --- | --- | --- | --- |
| degradation_aware | 0.2000 | 33 | 29 | 135 |
| degradation_aware | 0.3000 | 50 | 46 | 118 |
| degradation_aware | 0.4000 | 67 | 63 | 101 |
| measurement_oriented | 0.2000 | 33 | 33 | 135 |
| measurement_oriented | 0.3000 | 50 | 50 | 118 |
| measurement_oriented | 0.4000 | 67 | 67 | 101 |

### Predeclared reference (100 trees, max_features=1.0): mean and seed SD

| feature_set | n_estimators | max_features | calibration_fraction | percentile | threshold_mean | threshold_std | post_calibration_clean_fpr_mean | post_calibration_clean_fpr_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 1.0000 | 0.2000 | 95.0000 | 0.5559 | 0.0167 | 0.7679 | 0.0238 |
| degradation_aware | 100 | 1.0000 | 0.2000 | 97.5000 | 0.5616 | 0.0189 | 0.7457 | 0.0373 |
| degradation_aware | 100 | 1.0000 | 0.2000 | 99.0000 | 0.5628 | 0.0198 | 0.7457 | 0.0373 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 95.0000 | 0.5489 | 0.0099 | 0.8983 | 0.0085 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 97.5000 | 0.5596 | 0.0170 | 0.8644 | 0.0369 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 99.0000 | 0.5624 | 0.0193 | 0.8503 | 0.0382 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 95.0000 | 0.5595 | 0.0120 | 0.9967 | 0.0057 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 97.5000 | 0.5644 | 0.0088 | 0.9868 | 0.0057 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 99.0000 | 0.5680 | 0.0084 | 0.9769 | 0.0229 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 95.0000 | 0.5993 | 0.0091 | 0.7235 | 0.0238 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 97.5000 | 0.6133 | 0.0106 | 0.6840 | 0.0308 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 99.0000 | 0.6207 | 0.0078 | 0.6642 | 0.0280 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 95.0000 | 0.6081 | 0.0094 | 0.7825 | 0.0353 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 97.5000 | 0.6204 | 0.0045 | 0.7571 | 0.0176 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 99.0000 | 0.6331 | 0.0047 | 0.7316 | 0.0176 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 95.0000 | 0.6009 | 0.0079 | 0.9439 | 0.0375 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 97.5000 | 0.6152 | 0.0080 | 0.9010 | 0.0357 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 99.0000 | 0.6298 | 0.0033 | 0.8548 | 0.0206 |

## Predeclared policy

Fractions 20%, 30%, 40% use floor(fraction*168), ending at cycles 33, 50, 67. The boundary is set before feature-NaN dropping. Calibration uses only required-feature-complete CLEAN B0007 observations up to that boundary; clean evaluation uses only later cycles. Scores are -score_samples. Thresholds are linear P95/P97.5/P99 of burn-in scores only; alarm iff score > threshold. No synthetic labels enter threshold calculation.

Eligibility requires post-calibration clean FPR <=5% for EACH of seeds 42/123/2026, not just their mean. Eligible rows are ordered by shorter calibration fraction first, then the lowest satisfying percentile. All eligible model configurations remain for review; no synthetic metric is a selection criterion and no automatic finalization occurs.

## Counts and thresholds for every seed/configuration

| feature_set | n_estimators | max_features | seed | calibration_fraction | boundary_cycle | percentile | calibration_rows | post_calibration_clean_rows | threshold | post_calibration_clean_fpr | threshold_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | 42 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5607 | 0.7630 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5637 | 0.7556 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5643 | 0.7556 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5567 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5625 | 0.8644 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5641 | 0.8644 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5626 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5651 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 42 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5658 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5688 | 0.7778 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5697 | 0.7778 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5699 | 0.7778 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5663 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5693 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5698 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5710 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5748 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 123 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5774 | 0.9703 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5686 | 0.7704 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5728 | 0.7481 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5760 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5631 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5699 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5747 | 0.8559 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5704 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5712 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 0.7500 | 2026 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5738 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5672 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5726 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5734 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5568 | 0.8983 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5706 | 0.8220 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5731 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5636 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5688 | 0.9802 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 42 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5728 | 0.9505 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5366 | 0.7852 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5397 | 0.7852 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5399 | 0.7852 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5378 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5400 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5401 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5460 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5543 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 123 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5583 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5637 | 0.7778 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5724 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5751 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5521 | 0.9068 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5683 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5740 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5689 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5700 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 100 | 1.0000 | 2026 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5729 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5662 | 0.7704 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5700 | 0.7481 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5704 | 0.7481 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5590 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5687 | 0.8644 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5702 | 0.8559 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5684 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5692 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 42 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5701 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5664 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5673 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5673 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5607 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5670 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5673 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5658 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5666 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 123 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5673 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5727 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5754 | 0.7333 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5770 | 0.7259 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5699 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5738 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5764 | 0.8390 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5683 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5721 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 0.7500 | 2026 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5757 | 0.9802 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5761 | 0.7185 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5803 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5815 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5691 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5783 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5810 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5670 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5748 | 0.9802 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 42 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5805 | 0.9505 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5456 | 0.7778 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5505 | 0.7704 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5514 | 0.7704 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5379 | 0.8983 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5485 | 0.8898 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5510 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5516 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5530 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 123 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5554 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.2000 | 33 | 95.0000 | 29 | 135 | 0.5666 | 0.7333 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.2000 | 33 | 97.5000 | 29 | 135 | 0.5743 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.2000 | 33 | 99.0000 | 29 | 135 | 0.5761 | 0.7111 | clean_B0007_cycles_1_to_33_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.3000 | 50 | 95.0000 | 46 | 118 | 0.5552 | 0.8814 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.3000 | 50 | 97.5000 | 46 | 118 | 0.5710 | 0.8305 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.3000 | 50 | 99.0000 | 46 | 118 | 0.5754 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.4000 | 67 | 95.0000 | 63 | 101 | 0.5567 | 0.9901 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.4000 | 67 | 97.5000 | 63 | 101 | 0.5645 | 0.9802 | clean_B0007_cycles_1_to_67_required_features_complete |
| degradation_aware | 200 | 1.0000 | 2026 | 0.4000 | 67 | 99.0000 | 63 | 101 | 0.5747 | 0.9505 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6190 | 0.7259 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6307 | 0.7037 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6371 | 0.6889 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6212 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6384 | 0.7712 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6419 | 0.7627 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6120 | 0.9703 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6327 | 0.9208 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 42 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6417 | 0.8911 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5857 | 0.7926 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6002 | 0.7333 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6147 | 0.6741 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.5943 | 0.8475 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6175 | 0.7627 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6304 | 0.7288 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.5934 | 1.0000 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6048 | 0.9505 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 123 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6284 | 0.8515 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5955 | 0.7037 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6095 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6123 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6029 | 0.7627 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6128 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6433 | 0.6441 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.5935 | 0.9208 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6103 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 0.7500 | 2026 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6336 | 0.8317 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5993 | 0.7333 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6196 | 0.6741 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6278 | 0.6444 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6115 | 0.7712 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6234 | 0.7627 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6294 | 0.7373 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6004 | 0.9604 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6195 | 0.8911 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 42 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6281 | 0.8614 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6084 | 0.6963 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6193 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6220 | 0.6519 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6154 | 0.7542 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6226 | 0.7373 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6384 | 0.7119 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6091 | 0.9010 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6201 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 123 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6336 | 0.8317 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5902 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6010 | 0.7185 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6124 | 0.6963 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.5975 | 0.8220 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6152 | 0.7712 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6313 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.5932 | 0.9703 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6060 | 0.9406 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 100 | 1.0000 | 2026 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6276 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6045 | 0.7259 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6200 | 0.6815 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6247 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6158 | 0.7797 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6256 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6325 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6077 | 0.9406 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6214 | 0.9010 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 42 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6310 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5932 | 0.7259 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6044 | 0.6963 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6154 | 0.6667 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.5952 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6176 | 0.7542 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6259 | 0.7288 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.5894 | 0.9703 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6078 | 0.9010 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 123 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6249 | 0.8515 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6107 | 0.7185 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6239 | 0.6741 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6322 | 0.6519 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6239 | 0.7542 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6352 | 0.7373 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6517 | 0.6610 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6156 | 0.9109 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6305 | 0.8614 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 0.7500 | 2026 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6470 | 0.8218 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6053 | 0.7185 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6235 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6350 | 0.6370 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6138 | 0.7797 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6269 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6361 | 0.7288 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6043 | 0.9406 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6224 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 42 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6338 | 0.8614 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.6212 | 0.6593 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6324 | 0.6519 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6358 | 0.6370 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6244 | 0.7458 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6365 | 0.7203 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6429 | 0.7119 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.6157 | 0.9010 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6335 | 0.8614 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 123 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6413 | 0.8317 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.2000 | 33 | 95.0000 | 33 | 135 | 0.5886 | 0.7407 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.2000 | 33 | 97.5000 | 33 | 135 | 0.6012 | 0.7259 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.2000 | 33 | 99.0000 | 33 | 135 | 0.6091 | 0.6963 | clean_B0007_cycles_1_to_33_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.3000 | 50 | 95.0000 | 50 | 118 | 0.6012 | 0.8136 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.3000 | 50 | 97.5000 | 50 | 118 | 0.6120 | 0.7797 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.3000 | 50 | 99.0000 | 50 | 118 | 0.6320 | 0.7373 | clean_B0007_cycles_1_to_50_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.4000 | 67 | 95.0000 | 67 | 101 | 0.5932 | 0.9703 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.4000 | 67 | 97.5000 | 67 | 101 | 0.6075 | 0.9406 | clean_B0007_cycles_1_to_67_required_features_complete |
| measurement_oriented | 200 | 1.0000 | 2026 | 0.4000 | 67 | 99.0000 | 67 | 101 | 0.6261 | 0.8713 | clean_B0007_cycles_1_to_67_required_features_complete |

## Seed stability for every configuration

| feature_set | n_estimators | max_features | calibration_fraction | percentile | threshold_mean | threshold_std | post_calibration_clean_fpr_mean | post_calibration_clean_fpr_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | 0.2000 | 95.0000 | 0.5660 | 0.0046 | 0.7704 | 0.0074 |
| degradation_aware | 100 | 0.7500 | 0.2000 | 97.5000 | 0.5687 | 0.0046 | 0.7605 | 0.0154 |
| degradation_aware | 100 | 0.7500 | 0.2000 | 99.0000 | 0.5701 | 0.0058 | 0.7580 | 0.0186 |
| degradation_aware | 100 | 0.7500 | 0.3000 | 95.0000 | 0.5621 | 0.0049 | 0.8842 | 0.0049 |
| degradation_aware | 100 | 0.7500 | 0.3000 | 97.5000 | 0.5672 | 0.0041 | 0.8785 | 0.0129 |
| degradation_aware | 100 | 0.7500 | 0.3000 | 99.0000 | 0.5695 | 0.0053 | 0.8701 | 0.0176 |
| degradation_aware | 100 | 0.7500 | 0.4000 | 95.0000 | 0.5680 | 0.0047 | 0.9967 | 0.0057 |
| degradation_aware | 100 | 0.7500 | 0.4000 | 97.5000 | 0.5704 | 0.0049 | 0.9934 | 0.0057 |
| degradation_aware | 100 | 0.7500 | 0.4000 | 99.0000 | 0.5723 | 0.0059 | 0.9868 | 0.0151 |
| degradation_aware | 100 | 1.0000 | 0.2000 | 95.0000 | 0.5559 | 0.0167 | 0.7679 | 0.0238 |
| degradation_aware | 100 | 1.0000 | 0.2000 | 97.5000 | 0.5616 | 0.0189 | 0.7457 | 0.0373 |
| degradation_aware | 100 | 1.0000 | 0.2000 | 99.0000 | 0.5628 | 0.0198 | 0.7457 | 0.0373 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 95.0000 | 0.5489 | 0.0099 | 0.8983 | 0.0085 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 97.5000 | 0.5596 | 0.0170 | 0.8644 | 0.0369 |
| degradation_aware | 100 | 1.0000 | 0.3000 | 99.0000 | 0.5624 | 0.0193 | 0.8503 | 0.0382 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 95.0000 | 0.5595 | 0.0120 | 0.9967 | 0.0057 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 97.5000 | 0.5644 | 0.0088 | 0.9868 | 0.0057 |
| degradation_aware | 100 | 1.0000 | 0.4000 | 99.0000 | 0.5680 | 0.0084 | 0.9769 | 0.0229 |
| degradation_aware | 200 | 0.7500 | 0.2000 | 95.0000 | 0.5684 | 0.0037 | 0.7506 | 0.0171 |
| degradation_aware | 200 | 0.7500 | 0.2000 | 97.5000 | 0.5709 | 0.0041 | 0.7407 | 0.0074 |
| degradation_aware | 200 | 0.7500 | 0.2000 | 99.0000 | 0.5716 | 0.0050 | 0.7383 | 0.0113 |
| degradation_aware | 200 | 0.7500 | 0.3000 | 95.0000 | 0.5632 | 0.0059 | 0.8757 | 0.0245 |
| degradation_aware | 200 | 0.7500 | 0.3000 | 97.5000 | 0.5698 | 0.0035 | 0.8531 | 0.0098 |
| degradation_aware | 200 | 0.7500 | 0.3000 | 99.0000 | 0.5713 | 0.0046 | 0.8475 | 0.0085 |
| degradation_aware | 200 | 0.7500 | 0.4000 | 95.0000 | 0.5675 | 0.0015 | 0.9934 | 0.0057 |
| degradation_aware | 200 | 0.7500 | 0.4000 | 97.5000 | 0.5693 | 0.0027 | 0.9934 | 0.0057 |
| degradation_aware | 200 | 0.7500 | 0.4000 | 99.0000 | 0.5710 | 0.0043 | 0.9901 | 0.0099 |
| degradation_aware | 200 | 1.0000 | 0.2000 | 95.0000 | 0.5627 | 0.0156 | 0.7432 | 0.0308 |
| degradation_aware | 200 | 1.0000 | 0.2000 | 97.5000 | 0.5684 | 0.0158 | 0.7309 | 0.0342 |
| degradation_aware | 200 | 1.0000 | 0.2000 | 99.0000 | 0.5697 | 0.0161 | 0.7309 | 0.0342 |
| degradation_aware | 200 | 1.0000 | 0.3000 | 95.0000 | 0.5541 | 0.0157 | 0.8757 | 0.0259 |
| degradation_aware | 200 | 1.0000 | 0.3000 | 97.5000 | 0.5660 | 0.0155 | 0.8446 | 0.0400 |
| degradation_aware | 200 | 1.0000 | 0.3000 | 99.0000 | 0.5691 | 0.0159 | 0.8362 | 0.0391 |
| degradation_aware | 200 | 1.0000 | 0.4000 | 95.0000 | 0.5585 | 0.0078 | 0.9967 | 0.0057 |
| degradation_aware | 200 | 1.0000 | 0.4000 | 97.5000 | 0.5641 | 0.0109 | 0.9868 | 0.0114 |
| degradation_aware | 200 | 1.0000 | 0.4000 | 99.0000 | 0.5702 | 0.0131 | 0.9670 | 0.0286 |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 95.0000 | 0.6001 | 0.0171 | 0.7407 | 0.0463 |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 97.5000 | 0.6135 | 0.0156 | 0.6988 | 0.0373 |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 99.0000 | 0.6213 | 0.0137 | 0.6741 | 0.0148 |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 95.0000 | 0.6061 | 0.0138 | 0.8079 | 0.0427 |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 97.5000 | 0.6229 | 0.0136 | 0.7599 | 0.0129 |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 99.0000 | 0.6385 | 0.0071 | 0.7119 | 0.0611 |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 95.0000 | 0.5996 | 0.0107 | 0.9637 | 0.0400 |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 97.5000 | 0.6159 | 0.0148 | 0.9142 | 0.0400 |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 99.0000 | 0.6345 | 0.0067 | 0.8581 | 0.0302 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 95.0000 | 0.5993 | 0.0091 | 0.7235 | 0.0238 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 97.5000 | 0.6133 | 0.0106 | 0.6840 | 0.0308 |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 99.0000 | 0.6207 | 0.0078 | 0.6642 | 0.0280 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 95.0000 | 0.6081 | 0.0094 | 0.7825 | 0.0353 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 97.5000 | 0.6204 | 0.0045 | 0.7571 | 0.0176 |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 99.0000 | 0.6331 | 0.0047 | 0.7316 | 0.0176 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 95.0000 | 0.6009 | 0.0079 | 0.9439 | 0.0375 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 97.5000 | 0.6152 | 0.0080 | 0.9010 | 0.0357 |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 99.0000 | 0.6298 | 0.0033 | 0.8548 | 0.0206 |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 95.0000 | 0.6028 | 0.0089 | 0.7235 | 0.0043 |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 97.5000 | 0.6161 | 0.0103 | 0.6840 | 0.0113 |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 99.0000 | 0.6241 | 0.0084 | 0.6593 | 0.0074 |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 95.0000 | 0.6116 | 0.0148 | 0.7825 | 0.0298 |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 97.5000 | 0.6262 | 0.0088 | 0.7458 | 0.0085 |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 99.0000 | 0.6367 | 0.0134 | 0.7119 | 0.0448 |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 95.0000 | 0.6043 | 0.0134 | 0.9406 | 0.0297 |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 97.5000 | 0.6199 | 0.0114 | 0.8878 | 0.0229 |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 99.0000 | 0.6343 | 0.0114 | 0.8482 | 0.0249 |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 95.0000 | 0.6050 | 0.0163 | 0.7062 | 0.0421 |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 97.5000 | 0.6190 | 0.0161 | 0.6790 | 0.0408 |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 99.0000 | 0.6266 | 0.0152 | 0.6568 | 0.0342 |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 95.0000 | 0.6131 | 0.0116 | 0.7797 | 0.0339 |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 97.5000 | 0.6251 | 0.0124 | 0.7486 | 0.0298 |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 99.0000 | 0.6370 | 0.0055 | 0.7260 | 0.0129 |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 95.0000 | 0.6044 | 0.0113 | 0.9373 | 0.0348 |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 97.5000 | 0.6211 | 0.0130 | 0.8911 | 0.0432 |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 99.0000 | 0.6337 | 0.0076 | 0.8548 | 0.0206 |

## Eligibility review

| feature_set | n_estimators | max_features | calibration_fraction | percentile | clean_fpr_mean | clean_fpr_std | clean_fpr_max | eligible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | 0.2000 | 95.0000 | 0.7704 | 0.0074 | 0.7778 | False |
| degradation_aware | 100 | 0.7500 | 0.2000 | 97.5000 | 0.7605 | 0.0154 | 0.7778 | False |
| degradation_aware | 100 | 0.7500 | 0.2000 | 99.0000 | 0.7580 | 0.0186 | 0.7778 | False |
| degradation_aware | 100 | 0.7500 | 0.3000 | 95.0000 | 0.8842 | 0.0049 | 0.8898 | False |
| degradation_aware | 100 | 0.7500 | 0.3000 | 97.5000 | 0.8785 | 0.0129 | 0.8898 | False |
| degradation_aware | 100 | 0.7500 | 0.3000 | 99.0000 | 0.8701 | 0.0176 | 0.8898 | False |
| degradation_aware | 100 | 0.7500 | 0.4000 | 95.0000 | 0.9967 | 0.0057 | 1.0000 | False |
| degradation_aware | 100 | 0.7500 | 0.4000 | 97.5000 | 0.9934 | 0.0057 | 1.0000 | False |
| degradation_aware | 100 | 0.7500 | 0.4000 | 99.0000 | 0.9868 | 0.0151 | 1.0000 | False |
| degradation_aware | 100 | 1.0000 | 0.2000 | 95.0000 | 0.7679 | 0.0238 | 0.7852 | False |
| degradation_aware | 100 | 1.0000 | 0.2000 | 97.5000 | 0.7457 | 0.0373 | 0.7852 | False |
| degradation_aware | 100 | 1.0000 | 0.2000 | 99.0000 | 0.7457 | 0.0373 | 0.7852 | False |
| degradation_aware | 100 | 1.0000 | 0.3000 | 95.0000 | 0.8983 | 0.0085 | 0.9068 | False |
| degradation_aware | 100 | 1.0000 | 0.3000 | 97.5000 | 0.8644 | 0.0369 | 0.8898 | False |
| degradation_aware | 100 | 1.0000 | 0.3000 | 99.0000 | 0.8503 | 0.0382 | 0.8898 | False |
| degradation_aware | 100 | 1.0000 | 0.4000 | 95.0000 | 0.9967 | 0.0057 | 1.0000 | False |
| degradation_aware | 100 | 1.0000 | 0.4000 | 97.5000 | 0.9868 | 0.0057 | 0.9901 | False |
| degradation_aware | 100 | 1.0000 | 0.4000 | 99.0000 | 0.9769 | 0.0229 | 0.9901 | False |
| degradation_aware | 200 | 0.7500 | 0.2000 | 95.0000 | 0.7506 | 0.0171 | 0.7704 | False |
| degradation_aware | 200 | 0.7500 | 0.2000 | 97.5000 | 0.7407 | 0.0074 | 0.7481 | False |
| degradation_aware | 200 | 0.7500 | 0.2000 | 99.0000 | 0.7383 | 0.0113 | 0.7481 | False |
| degradation_aware | 200 | 0.7500 | 0.3000 | 95.0000 | 0.8757 | 0.0245 | 0.8898 | False |
| degradation_aware | 200 | 0.7500 | 0.3000 | 97.5000 | 0.8531 | 0.0098 | 0.8644 | False |
| degradation_aware | 200 | 0.7500 | 0.3000 | 99.0000 | 0.8475 | 0.0085 | 0.8559 | False |
| degradation_aware | 200 | 0.7500 | 0.4000 | 95.0000 | 0.9934 | 0.0057 | 1.0000 | False |
| degradation_aware | 200 | 0.7500 | 0.4000 | 97.5000 | 0.9934 | 0.0057 | 1.0000 | False |
| degradation_aware | 200 | 0.7500 | 0.4000 | 99.0000 | 0.9901 | 0.0099 | 1.0000 | False |
| degradation_aware | 200 | 1.0000 | 0.2000 | 95.0000 | 0.7432 | 0.0308 | 0.7778 | False |
| degradation_aware | 200 | 1.0000 | 0.2000 | 97.5000 | 0.7309 | 0.0342 | 0.7704 | False |
| degradation_aware | 200 | 1.0000 | 0.2000 | 99.0000 | 0.7309 | 0.0342 | 0.7704 | False |
| degradation_aware | 200 | 1.0000 | 0.3000 | 95.0000 | 0.8757 | 0.0259 | 0.8983 | False |
| degradation_aware | 200 | 1.0000 | 0.3000 | 97.5000 | 0.8446 | 0.0400 | 0.8898 | False |
| degradation_aware | 200 | 1.0000 | 0.3000 | 99.0000 | 0.8362 | 0.0391 | 0.8814 | False |
| degradation_aware | 200 | 1.0000 | 0.4000 | 95.0000 | 0.9967 | 0.0057 | 1.0000 | False |
| degradation_aware | 200 | 1.0000 | 0.4000 | 97.5000 | 0.9868 | 0.0114 | 1.0000 | False |
| degradation_aware | 200 | 1.0000 | 0.4000 | 99.0000 | 0.9670 | 0.0286 | 1.0000 | False |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 95.0000 | 0.7407 | 0.0463 | 0.7926 | False |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 97.5000 | 0.6988 | 0.0373 | 0.7333 | False |
| measurement_oriented | 100 | 0.7500 | 0.2000 | 99.0000 | 0.6741 | 0.0148 | 0.6889 | False |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 95.0000 | 0.8079 | 0.0427 | 0.8475 | False |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 97.5000 | 0.7599 | 0.0129 | 0.7712 | False |
| measurement_oriented | 100 | 0.7500 | 0.3000 | 99.0000 | 0.7119 | 0.0611 | 0.7627 | False |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 95.0000 | 0.9637 | 0.0400 | 1.0000 | False |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 97.5000 | 0.9142 | 0.0400 | 0.9505 | False |
| measurement_oriented | 100 | 0.7500 | 0.4000 | 99.0000 | 0.8581 | 0.0302 | 0.8911 | False |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 95.0000 | 0.7235 | 0.0238 | 0.7407 | False |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 97.5000 | 0.6840 | 0.0308 | 0.7185 | False |
| measurement_oriented | 100 | 1.0000 | 0.2000 | 99.0000 | 0.6642 | 0.0280 | 0.6963 | False |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 95.0000 | 0.7825 | 0.0353 | 0.8220 | False |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 97.5000 | 0.7571 | 0.0176 | 0.7712 | False |
| measurement_oriented | 100 | 1.0000 | 0.3000 | 99.0000 | 0.7316 | 0.0176 | 0.7458 | False |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 95.0000 | 0.9439 | 0.0375 | 0.9703 | False |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 97.5000 | 0.9010 | 0.0357 | 0.9406 | False |
| measurement_oriented | 100 | 1.0000 | 0.4000 | 99.0000 | 0.8548 | 0.0206 | 0.8713 | False |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 95.0000 | 0.7235 | 0.0043 | 0.7259 | False |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 97.5000 | 0.6840 | 0.0113 | 0.6963 | False |
| measurement_oriented | 200 | 0.7500 | 0.2000 | 99.0000 | 0.6593 | 0.0074 | 0.6667 | False |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 95.0000 | 0.7825 | 0.0298 | 0.8136 | False |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 97.5000 | 0.7458 | 0.0085 | 0.7542 | False |
| measurement_oriented | 200 | 0.7500 | 0.3000 | 99.0000 | 0.7119 | 0.0448 | 0.7458 | False |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 95.0000 | 0.9406 | 0.0297 | 0.9703 | False |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 97.5000 | 0.8878 | 0.0229 | 0.9010 | False |
| measurement_oriented | 200 | 0.7500 | 0.4000 | 99.0000 | 0.8482 | 0.0249 | 0.8713 | False |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 95.0000 | 0.7062 | 0.0421 | 0.7407 | False |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 97.5000 | 0.6790 | 0.0408 | 0.7259 | False |
| measurement_oriented | 200 | 1.0000 | 0.2000 | 99.0000 | 0.6568 | 0.0342 | 0.6963 | False |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 95.0000 | 0.7797 | 0.0339 | 0.8136 | False |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 97.5000 | 0.7486 | 0.0298 | 0.7797 | False |
| measurement_oriented | 200 | 1.0000 | 0.3000 | 99.0000 | 0.7260 | 0.0129 | 0.7373 | False |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 95.0000 | 0.9373 | 0.0348 | 0.9703 | False |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 97.5000 | 0.8911 | 0.0432 | 0.9406 | False |
| measurement_oriented | 200 | 1.0000 | 0.4000 | 99.0000 | 0.8548 | 0.0206 | 0.8713 | False |

Eligible configuration/fraction/percentile combinations: **0**.

None satisfies the clean-FPR requirement across all three seeds. No winner is proposed.

## Controlled anomalies — clean-FPR gate

Part 4 and the requested completion report require synthetic performance only after the clean-FPR condition is satisfied. All configurations are first evaluated on clean post-calibration data; synthetic evaluation is then run only for eligible configurations. It is not used to rescue an ineligible threshold.

When eligible, whole synthetic windows must start after the boundary, not merely have their late rows filtered from a window that began during calibration. A1 may read the four preceding CLEAN observations and original initial capacity for its frozen causal calculation; these rows are neither perturbed nor emitted. Zero-offset ramp onsets are not synthetic positives. Precision/F1/AP retain the Phase 4 equal-class-weight 50% evaluation prevalence; PR-AUC is average precision. Overlapping windows are dependent.

No eligible configurations: synthetic metrics are intentionally withheld, and no new synthetic datasets were generated in this run. A4 performance after burn-in cannot be claimed or compared under this gate. Prior Phase 4 weakness is not evidence that calibration fixes or worsens A4.

## Interpretation

Post-calibration clean FPR across all individual runs: 63.70%–100.00%.

Early clean burn-in calibrates the initial cell score distribution; it does not guarantee control during later trajectory evolution. A full clean aging trajectory is not a stationary negative population or independently verified fault-free ground truth. Clean-FPR eligibility is a validation-screening result, not an out-of-sample guarantee. Seed SD quantifies forest randomness, not uncertainty from independent batteries. Windows differ in evaluation length, so fraction comparisons do not hold the evaluated cycles fixed.

## Artifacts

Detailed CSVs in `results/nasa_burnin_calibration/`: burnin_thresholds.csv, burnin_clean_scores.csv, burnin_seed_stability.csv, burnin_review.csv, eligible_configurations.csv, eligible_anomaly_metrics.csv. Empty eligible metrics contain headers, not fabricated zero scores. Figure: `figures/nasa/burnin_calibration/post_calibration_fpr.png`. Shift analysis is in `results/nasa_cross_cell_shift.md`.
