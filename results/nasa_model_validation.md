> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/nasa_model_validation.md`  
> **Archival SHA-256:** `68674f651f56f7bf921156f1243db39cc7ba5a13e9529d7d26cb6d405d0a6654`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# NASA Isolation Forest development validation

DEVELOPMENT ONLY. No model, feature set or threshold is finalized. B0018 was never opened by the Phase 4 loader or used in calculations. Only individual B0005/B0006/B0007 CSVs were read. Frozen anomaly protocol and feature sets were not changed.

## Training and preprocessing

| feature_set | initial_nominal_rows | effective_rows | B0005 | B0006 | clean_validation_scored |
| --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 92 | 46 | 46 | 164 |
| measurement_oriented | 100 | 100 | 50 | 50 | 168 |

Nominal selection is cycles 1–50 of each training cell (floor(0.30*168)); then required-feature NaNs are dropped, never imputed. Rows stay in cell/cycle order. StandardScaler fit and IsolationForest fit receive only these same feature matrices, no labels. Per-model scaler means, variances, sample counts, exact training row IDs and hashes are in training_provenance.json and the DEVELOPMENT joblib bundles. B0007 is transform/score only.

## Scores, thresholds and review rule

Anomaly score = -IsolationForest.score_samples(scaled X). Higher means more anomalous; an alarm uses strict score > threshold. predict() and the contamination=auto offset are not decision rules. See [scikit-learn IsolationForest API](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).

Every threshold is the linear-interpolated 95th, 97.5th or 99th percentile of the SAME model’s CLEAN NOMINAL TRAINING scores, after feature filtering. These are in-sample scores, not a held-out calibration set; false-alarm control on another battery is not guaranteed. No B0007 or synthetic score is used to calculate percentile values.

Predeclared tolerance: clean B0007 FPR <=5% for EVERY seed. Per configuration the lowest percentile satisfying this condition is only a review suggestion, never final. Synthetic F1/precision/recall/AP never enter this rule. Clean B0007 is an unmodified aging trajectory, not certified fault-free data: reported FPR is a baseline alarm fraction, not a verified natural-fault false-positive rate.

| feature_set | n_estimators | max_features | percentile | threshold_mean | threshold_std | clean_fpr_mean | clean_fpr_std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | 95.0000 | 0.5772 | 0.0048 | 0.6016 | 0.0176 |
| degradation_aware | 100 | 0.7500 | 97.5000 | 0.5954 | 0.0086 | 0.5650 | 0.0336 |
| degradation_aware | 100 | 0.7500 | 99.0000 | 0.6067 | 0.0094 | 0.5467 | 0.0186 |
| degradation_aware | 100 | 1.0000 | 95.0000 | 0.5808 | 0.0056 | 0.5854 | 0.0279 |
| degradation_aware | 100 | 1.0000 | 97.5000 | 0.5956 | 0.0054 | 0.5549 | 0.0122 |
| degradation_aware | 100 | 1.0000 | 99.0000 | 0.6068 | 0.0098 | 0.5366 | 0.0061 |
| degradation_aware | 200 | 0.7500 | 95.0000 | 0.5788 | 0.0013 | 0.5955 | 0.0070 |
| degradation_aware | 200 | 0.7500 | 97.5000 | 0.5900 | 0.0036 | 0.5671 | 0.0220 |
| degradation_aware | 200 | 0.7500 | 99.0000 | 0.6070 | 0.0080 | 0.5386 | 0.0070 |
| degradation_aware | 200 | 1.0000 | 95.0000 | 0.5847 | 0.0050 | 0.5793 | 0.0161 |
| degradation_aware | 200 | 1.0000 | 97.5000 | 0.5924 | 0.0015 | 0.5549 | 0.0000 |
| degradation_aware | 200 | 1.0000 | 99.0000 | 0.6084 | 0.0079 | 0.5264 | 0.0070 |
| measurement_oriented | 100 | 0.7500 | 95.0000 | 0.5718 | 0.0034 | 0.6845 | 0.0536 |
| measurement_oriented | 100 | 0.7500 | 97.5000 | 0.6000 | 0.0065 | 0.6012 | 0.0238 |
| measurement_oriented | 100 | 0.7500 | 99.0000 | 0.6573 | 0.0105 | 0.4028 | 0.1635 |
| measurement_oriented | 100 | 1.0000 | 95.0000 | 0.5647 | 0.0044 | 0.6786 | 0.0309 |
| measurement_oriented | 100 | 1.0000 | 97.5000 | 0.5999 | 0.0080 | 0.5933 | 0.0241 |
| measurement_oriented | 100 | 1.0000 | 99.0000 | 0.6424 | 0.0113 | 0.5000 | 0.0259 |
| measurement_oriented | 200 | 0.7500 | 95.0000 | 0.5677 | 0.0028 | 0.7123 | 0.0034 |
| measurement_oriented | 200 | 0.7500 | 97.5000 | 0.5972 | 0.0059 | 0.6032 | 0.0137 |
| measurement_oriented | 200 | 0.7500 | 99.0000 | 0.6488 | 0.0082 | 0.4861 | 0.0305 |
| measurement_oriented | 200 | 1.0000 | 95.0000 | 0.5714 | 0.0023 | 0.6687 | 0.0248 |
| measurement_oriented | 200 | 1.0000 | 97.5000 | 0.6009 | 0.0032 | 0.6012 | 0.0119 |
| measurement_oriented | 200 | 1.0000 | 99.0000 | 0.6463 | 0.0127 | 0.4901 | 0.0364 |

### Threshold review decisions

| feature_set | n_estimators | max_features | recommended_percentile_for_review | final_threshold | status |
| --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | None | None | no_candidate_meets_clean_fpr_tolerance |
| degradation_aware | 100 | 1.0000 | None | None | no_candidate_meets_clean_fpr_tolerance |
| degradation_aware | 200 | 0.7500 | None | None | no_candidate_meets_clean_fpr_tolerance |
| degradation_aware | 200 | 1.0000 | None | None | no_candidate_meets_clean_fpr_tolerance |
| measurement_oriented | 100 | 0.7500 | None | None | no_candidate_meets_clean_fpr_tolerance |
| measurement_oriented | 100 | 1.0000 | None | None | no_candidate_meets_clean_fpr_tolerance |
| measurement_oriented | 200 | 0.7500 | None | None | no_candidate_meets_clean_fpr_tolerance |
| measurement_oriented | 200 | 1.0000 | None | None | no_candidate_meets_clean_fpr_tolerance |

## Evaluation design and dependence

All frozen eligible contiguous windows are evaluated as separate counterfactual copies. Zero-offset A1/A4 onset rows are saved with false synthetic labels and excluded from positive-class metrics; clean full trajectory supplies the negative class once per comparison. Only required-feature-complete observations are scored. A1 is NOT applicable to measurement_oriented and is not treated as a detection failure.

Primary precision, F1 and PR-AUC use equal total class weights (50% synthetic evaluation prevalence); PR-AUC is non-interpolated average precision, baseline 0.5. This avoids artificial precision inflation from thousands of overlapping positive copies versus 164/168 clean observations. Raw instance precision/F1/AP and class counts are also in metrics.csv. ROC-AUC and within-class recall/FPR do not depend on this class balancing. These are descriptive counterfactual-instance metrics, not real-world precision estimates; overlapping windows and repeated source cycles are dependent. Seed SD measures model randomness only, not sampling uncertainty. A4 pooled metrics combine four scenarios; channel/sign results are separately retained. Paired score differences compare each copy to its original cycle.

### Window acceptance

| anomaly_family | severity | channel | drift_sign | accepted_windows | rejected_windows | rejection_reasons |
| --- | --- | --- | --- | --- | --- | --- |
| A1_ACCELERATED_DEGRADATION | mild | joint | 0 | 74 | 4 | {"Missing required anomaly feature": 4} |
| A1_ACCELERATED_DEGRADATION | moderate | joint | 0 | 74 | 4 | {"Missing required anomaly feature": 4} |
| A1_ACCELERATED_DEGRADATION | strong | joint | 0 | 74 | 4 | {"Missing required anomaly feature": 4} |
| A2_EARLY_VOLTAGE_COLLAPSE | mild | joint | 0 | 164 | 0 | {} |
| A2_EARLY_VOLTAGE_COLLAPSE | moderate | joint | 0 | 164 | 0 | {} |
| A2_EARLY_VOLTAGE_COLLAPSE | strong | joint | 0 | 164 | 0 | {} |
| A3_THERMAL_ABNORMALITY | mild | joint | 0 | 164 | 0 | {} |
| A3_THERMAL_ABNORMALITY | moderate | joint | 0 | 164 | 0 | {} |
| A3_THERMAL_ABNORMALITY | strong | joint | 0 | 164 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_voltage_v | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_voltage_v | 1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_temp_c | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | mild | mean_temp_c | 1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_voltage_v | 1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_temp_c | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | moderate | mean_temp_c | 1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_voltage_v | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_voltage_v | 1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_temp_c | -1 | 159 | 0 | {} |
| A4_SENSOR_DRIFT | strong | mean_temp_c | 1 | 159 | 0 | {} |

## Model grid (macro average over applicable families/severities at P97.5)

Grid: 100/200 trees x max_features 0.75/1.0 x seeds 42/123/2026; max_samples=auto, contamination=auto. Effective max_samples is 92 or 100 because these training sets have fewer than 256 rows. No search expansion. Macro scores have different family coverage across feature sets (A1 only in A); use shared-family tables for direct comparison.

| feature_set | n_estimators | max_features | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std | recall_mean | recall_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | 0.5821 | 0.0060 | 0.5808 | 0.0016 | 0.7212 | 0.0542 |
| degradation_aware | 100 | 1.0000 | 0.5855 | 0.0093 | 0.5814 | 0.0068 | 0.7012 | 0.0229 |
| degradation_aware | 200 | 0.7500 | 0.5842 | 0.0072 | 0.5813 | 0.0032 | 0.7418 | 0.0193 |
| degradation_aware | 200 | 1.0000 | 0.5743 | 0.0056 | 0.5772 | 0.0057 | 0.7197 | 0.0094 |
| measurement_oriented | 100 | 0.7500 | 0.5935 | 0.0201 | 0.6003 | 0.0117 | 0.7923 | 0.0155 |
| measurement_oriented | 100 | 1.0000 | 0.6005 | 0.0032 | 0.6034 | 0.0026 | 0.7786 | 0.0122 |
| measurement_oriented | 200 | 0.7500 | 0.5958 | 0.0107 | 0.5980 | 0.0086 | 0.7982 | 0.0343 |
| measurement_oriented | 200 | 1.0000 | 0.6040 | 0.0019 | 0.6028 | 0.0026 | 0.7815 | 0.0046 |

## Predeclared display reference: 100 trees, max_features=1.0

This configuration was specified before fitting for reporting/plots, not chosen for favorable metrics. P97.5 below is a display threshold, NOT a selected threshold. Means and sample SD are across the three fixed seeds.

| feature_set | anomaly_family | severity | precision_mean | precision_std | recall_mean | recall_std | f1_mean | f1_std | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | A1_ACCELERATED_DEGRADATION | mild | 0.5440 | 0.0132 | 0.6630 | 0.0461 | 0.5974 | 0.0267 | 0.5204 | 0.0127 | 0.5433 | 0.0094 |
| degradation_aware | A1_ACCELERATED_DEGRADATION | moderate | 0.5558 | 0.0165 | 0.6958 | 0.0569 | 0.6177 | 0.0328 | 0.5491 | 0.0202 | 0.5661 | 0.0094 |
| degradation_aware | A1_ACCELERATED_DEGRADATION | strong | 0.5678 | 0.0112 | 0.7298 | 0.0427 | 0.6385 | 0.0233 | 0.5970 | 0.0264 | 0.6006 | 0.0051 |
| degradation_aware | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.6011 | 0.0268 | 0.8395 | 0.0849 | 0.7002 | 0.0479 | 0.5694 | 0.0095 | 0.6255 | 0.0127 |
| degradation_aware | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.6295 | 0.0243 | 0.9465 | 0.0927 | 0.7556 | 0.0473 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.6295 | 0.0243 | 0.9465 | 0.0927 | 0.7556 | 0.0473 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | A3_THERMAL_ABNORMALITY | mild | 0.5129 | 0.0083 | 0.5844 | 0.0143 | 0.5463 | 0.0102 | 0.6288 | 0.0121 | 0.5661 | 0.0137 |
| degradation_aware | A3_THERMAL_ABNORMALITY | moderate | 0.5290 | 0.0117 | 0.6235 | 0.0269 | 0.5723 | 0.0177 | 0.7139 | 0.0090 | 0.6244 | 0.0105 |
| degradation_aware | A3_THERMAL_ABNORMALITY | strong | 0.5540 | 0.0073 | 0.6893 | 0.0094 | 0.6143 | 0.0076 | 0.7587 | 0.0133 | 0.6770 | 0.0153 |
| degradation_aware | A4_SENSOR_DRIFT | mild | 0.5002 | 0.0007 | 0.5554 | 0.0135 | 0.5264 | 0.0064 | 0.4962 | 0.0030 | 0.4947 | 0.0029 |
| degradation_aware | A4_SENSOR_DRIFT | moderate | 0.5046 | 0.0017 | 0.5653 | 0.0151 | 0.5332 | 0.0075 | 0.5123 | 0.0030 | 0.5001 | 0.0012 |
| degradation_aware | A4_SENSOR_DRIFT | strong | 0.5093 | 0.0028 | 0.5759 | 0.0178 | 0.5405 | 0.0092 | 0.5328 | 0.0035 | 0.5090 | 0.0029 |
| measurement_oriented | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.6219 | 0.0128 | 0.9756 | 0.0279 | 0.7595 | 0.0165 | 0.5656 | 0.0078 | 0.6308 | 0.0089 |
| measurement_oriented | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.6277 | 0.0096 | 1.0000 | 0.0000 | 0.7713 | 0.0072 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.6277 | 0.0096 | 1.0000 | 0.0000 | 0.7713 | 0.0072 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | A3_THERMAL_ABNORMALITY | mild | 0.5284 | 0.0135 | 0.6646 | 0.0161 | 0.5887 | 0.0136 | 0.6303 | 0.0043 | 0.5994 | 0.0069 |
| measurement_oriented | A3_THERMAL_ABNORMALITY | moderate | 0.5461 | 0.0084 | 0.7134 | 0.0061 | 0.6186 | 0.0038 | 0.7169 | 0.0094 | 0.6668 | 0.0092 |
| measurement_oriented | A3_THERMAL_ABNORMALITY | strong | 0.5729 | 0.0084 | 0.7967 | 0.0576 | 0.6661 | 0.0261 | 0.7663 | 0.0188 | 0.7095 | 0.0150 |
| measurement_oriented | A4_SENSOR_DRIFT | mild | 0.5018 | 0.0053 | 0.5974 | 0.0196 | 0.5453 | 0.0084 | 0.5021 | 0.0038 | 0.5027 | 0.0016 |
| measurement_oriented | A4_SENSOR_DRIFT | moderate | 0.5106 | 0.0081 | 0.6190 | 0.0259 | 0.5595 | 0.0133 | 0.5225 | 0.0022 | 0.5101 | 0.0019 |
| measurement_oriented | A4_SENSOR_DRIFT | strong | 0.5190 | 0.0085 | 0.6402 | 0.0292 | 0.5731 | 0.0149 | 0.5454 | 0.0021 | 0.5232 | 0.0029 |

### Comparison and observed failures

Neither feature set meets the predefined clean-FPR tolerance at any threshold/configuration. There is no acceptable model/threshold recommendation under this policy. The reference degradation-aware model has lower clean alarm rates at P95/P97.5, while measurement-oriented has lower clean alarm rate at P99 and stronger thermal separation. These trade-offs do not establish a winner.

A1 mild separation is weak (reference balanced AP about 0.52, ROC-AUC about 0.54). A4 pooled separation is near chance for both feature sets; negative temperature drift and positive voltage drift often LOWER the score relative to the same clean source cycle. A2 moderate and strong give identical reference scores/metrics despite strictly larger physical perturbations: model score saturation, not an injection error. High A2 recall coexists with high clean alarm rates and only modest ROC-AUC.

A3 improves with severity and measurement-oriented shows stronger thermal ROC-AUC than degradation-aware in the reference configuration, but this does not resolve the baseline alarm-rate problem. A1 is excluded from measurement-oriented rather than scored as an unobservable anomaly.

### A4 channel/sign reference results

| feature_set | variant | severity | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std | paired_score_change_mean_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | mean_temp_c_-1 | mild | 0.4502 | 0.0030 | 0.4604 | 0.0053 | -0.0024 |
| degradation_aware | mean_temp_c_1 | mild | 0.5746 | 0.0118 | 0.5342 | 0.0122 | 0.0044 |
| degradation_aware | mean_voltage_v_-1 | mild | 0.5362 | 0.0054 | 0.5428 | 0.0062 | 0.0131 |
| degradation_aware | mean_voltage_v_1 | mild | 0.4271 | 0.0027 | 0.4412 | 0.0075 | -0.0025 |
| degradation_aware | mean_temp_c_-1 | moderate | 0.4321 | 0.0058 | 0.4439 | 0.0091 | -0.0033 |
| degradation_aware | mean_temp_c_1 | moderate | 0.6412 | 0.0114 | 0.5705 | 0.0115 | 0.0103 |
| degradation_aware | mean_voltage_v_-1 | moderate | 0.5451 | 0.0059 | 0.5655 | 0.0076 | 0.0217 |
| degradation_aware | mean_voltage_v_1 | moderate | 0.4162 | 0.0032 | 0.4206 | 0.0092 | -0.0054 |
| degradation_aware | mean_temp_c_-1 | strong | 0.4252 | 0.0080 | 0.4371 | 0.0135 | -0.0025 |
| degradation_aware | mean_temp_c_1 | strong | 0.6934 | 0.0094 | 0.6085 | 0.0113 | 0.0194 |
| degradation_aware | mean_voltage_v_-1 | strong | 0.5488 | 0.0062 | 0.5754 | 0.0088 | 0.0255 |
| degradation_aware | mean_voltage_v_1 | strong | 0.4151 | 0.0038 | 0.4150 | 0.0112 | -0.0058 |
| measurement_oriented | mean_temp_c_-1 | mild | 0.4472 | 0.0114 | 0.4579 | 0.0145 | -0.0038 |
| measurement_oriented | mean_temp_c_1 | mild | 0.5918 | 0.0056 | 0.5471 | 0.0019 | 0.0067 |
| measurement_oriented | mean_voltage_v_-1 | mild | 0.5225 | 0.0032 | 0.5386 | 0.0094 | 0.0112 |
| measurement_oriented | mean_voltage_v_1 | mild | 0.4429 | 0.0093 | 0.4671 | 0.0174 | -0.0006 |
| measurement_oriented | mean_temp_c_-1 | moderate | 0.4296 | 0.0117 | 0.4402 | 0.0197 | -0.0054 |
| measurement_oriented | mean_temp_c_1 | moderate | 0.6689 | 0.0034 | 0.5965 | 0.0006 | 0.0161 |
| measurement_oriented | mean_voltage_v_-1 | moderate | 0.5319 | 0.0053 | 0.5632 | 0.0140 | 0.0192 |
| measurement_oriented | mean_voltage_v_1 | moderate | 0.4242 | 0.0081 | 0.4406 | 0.0200 | -0.0026 |
| measurement_oriented | mean_temp_c_-1 | strong | 0.4214 | 0.0106 | 0.4297 | 0.0207 | -0.0064 |
| measurement_oriented | mean_temp_c_1 | strong | 0.7287 | 0.0045 | 0.6523 | 0.0052 | 0.0299 |
| measurement_oriented | mean_voltage_v_-1 | strong | 0.5361 | 0.0063 | 0.5742 | 0.0161 | 0.0228 |
| measurement_oriented | mean_voltage_v_1 | strong | 0.4229 | 0.0100 | 0.4366 | 0.0245 | -0.0019 |

### Reference seed variability ranges across applicable families/severities

| feature_set | recall_std_min | recall_std_max | f1_std_min | f1_std_max | pr_auc_std_min | pr_auc_std_max | roc_auc_std_min | roc_auc_std_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 0.0094 | 0.0927 | 0.0064 | 0.0479 | 0.0030 | 0.0264 | 0.0012 | 0.0153 |
| measurement_oriented | 0.0000 | 0.0576 | 0.0038 | 0.0261 | 0.0021 | 0.0188 | 0.0016 | 0.0150 |

At the reference configuration, AP seed SD stays below 0.027, but thresholded recall SD reaches about 0.093. Across the wider predefined grid, measurement-oriented with 100 trees/max_features=0.75 at P99 has clean-FPR seed SD about 0.163: do not select its unusually favorable individual seed. Seed variability is reported separately from configuration differences.

## All configurations: family/severity/threshold seed mean and SD

metrics.csv contains every seed/configuration/threshold/family/severity plus separate A4 channel/sign metrics. metric_seed_stability.csv contains all seed aggregates. The following table includes all pooled-family aggregates; PR/ROC-AUC are threshold-independent and therefore repeat across thresholds.

| feature_set | n_estimators | max_features | anomaly_family | severity | percentile | precision_mean | precision_std | recall_mean | recall_std | f1_mean | f1_std | clean_fpr_mean | clean_fpr_std | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 95.0000 | 0.5481 | 0.0038 | 0.7294 | 0.0128 | 0.6258 | 0.0039 | 0.6016 | 0.0176 | 0.5243 | 0.0150 | 0.5408 | 0.0060 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 97.5000 | 0.5428 | 0.0150 | 0.6728 | 0.0733 | 0.6001 | 0.0386 | 0.5650 | 0.0336 | 0.5243 | 0.0150 | 0.5408 | 0.0060 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 99.0000 | 0.5428 | 0.0219 | 0.6518 | 0.0729 | 0.5918 | 0.0433 | 0.5467 | 0.0186 | 0.5243 | 0.0150 | 0.5408 | 0.0060 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 95.0000 | 0.5630 | 0.0071 | 0.7751 | 0.0202 | 0.6522 | 0.0103 | 0.6016 | 0.0176 | 0.5408 | 0.0152 | 0.5634 | 0.0040 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 97.5000 | 0.5578 | 0.0149 | 0.7147 | 0.0749 | 0.6259 | 0.0382 | 0.5650 | 0.0336 | 0.5408 | 0.0152 | 0.5634 | 0.0040 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 99.0000 | 0.5543 | 0.0237 | 0.6831 | 0.0798 | 0.6114 | 0.0468 | 0.5467 | 0.0186 | 0.5408 | 0.0152 | 0.5634 | 0.0040 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 95.0000 | 0.5776 | 0.0055 | 0.8225 | 0.0084 | 0.6786 | 0.0034 | 0.6016 | 0.0176 | 0.6049 | 0.0443 | 0.6060 | 0.0115 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 97.5000 | 0.5768 | 0.0062 | 0.7705 | 0.0533 | 0.6593 | 0.0225 | 0.5650 | 0.0336 | 0.6049 | 0.0443 | 0.6060 | 0.0115 |
| degradation_aware | 100 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 99.0000 | 0.5687 | 0.0135 | 0.7223 | 0.0543 | 0.6361 | 0.0293 | 0.5467 | 0.0186 | 0.6049 | 0.0443 | 0.6060 | 0.0115 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.6215 | 0.0067 | 0.9877 | 0.0163 | 0.7629 | 0.0078 | 0.6016 | 0.0176 | 0.5756 | 0.0135 | 0.6322 | 0.0104 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6160 | 0.0212 | 0.9115 | 0.1212 | 0.7339 | 0.0552 | 0.5650 | 0.0336 | 0.5756 | 0.0135 | 0.6322 | 0.0104 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.6006 | 0.0179 | 0.8251 | 0.0867 | 0.6945 | 0.0428 | 0.5467 | 0.0186 | 0.5756 | 0.0135 | 0.6322 | 0.0104 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.6244 | 0.0068 | 1.0000 | 0.0000 | 0.7688 | 0.0052 | 0.6016 | 0.0176 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6348 | 0.0077 | 0.9815 | 0.0321 | 0.7708 | 0.0080 | 0.5650 | 0.0336 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.6336 | 0.0173 | 0.9486 | 0.0891 | 0.7592 | 0.0412 | 0.5467 | 0.0186 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.6244 | 0.0068 | 1.0000 | 0.0000 | 0.7688 | 0.0052 | 0.6016 | 0.0176 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6348 | 0.0077 | 0.9815 | 0.0321 | 0.7708 | 0.0080 | 0.5650 | 0.0336 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.6336 | 0.0173 | 0.9486 | 0.0891 | 0.7592 | 0.0412 | 0.5467 | 0.0186 | 0.5805 | 0.0143 | 0.6428 | 0.0124 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5210 | 0.0063 | 0.6543 | 0.0107 | 0.5801 | 0.0060 | 0.6016 | 0.0176 | 0.6046 | 0.0305 | 0.5534 | 0.0185 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5065 | 0.0030 | 0.5802 | 0.0405 | 0.5405 | 0.0193 | 0.5650 | 0.0336 | 0.6046 | 0.0305 | 0.5534 | 0.0185 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5037 | 0.0087 | 0.5556 | 0.0375 | 0.5281 | 0.0215 | 0.5467 | 0.0186 | 0.6046 | 0.0305 | 0.5534 | 0.0185 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5318 | 0.0096 | 0.6831 | 0.0128 | 0.5980 | 0.0101 | 0.6016 | 0.0176 | 0.6968 | 0.0283 | 0.6124 | 0.0151 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5241 | 0.0121 | 0.6235 | 0.0589 | 0.5689 | 0.0315 | 0.5650 | 0.0336 | 0.6968 | 0.0283 | 0.6124 | 0.0151 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5128 | 0.0091 | 0.5761 | 0.0402 | 0.5424 | 0.0228 | 0.5467 | 0.0186 | 0.6968 | 0.0283 | 0.6124 | 0.0151 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5435 | 0.0055 | 0.7160 | 0.0062 | 0.6179 | 0.0024 | 0.6016 | 0.0176 | 0.7428 | 0.0216 | 0.6598 | 0.0155 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5426 | 0.0098 | 0.6708 | 0.0518 | 0.5994 | 0.0256 | 0.5650 | 0.0336 | 0.7428 | 0.0216 | 0.6598 | 0.0155 |
| degradation_aware | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5361 | 0.0190 | 0.6337 | 0.0631 | 0.5804 | 0.0377 | 0.5467 | 0.0186 | 0.7428 | 0.0216 | 0.6598 | 0.0155 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5038 | 0.0031 | 0.6109 | 0.0144 | 0.5522 | 0.0057 | 0.6016 | 0.0176 | 0.4955 | 0.0033 | 0.4983 | 0.0027 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5016 | 0.0012 | 0.5688 | 0.0352 | 0.5328 | 0.0160 | 0.5650 | 0.0336 | 0.4955 | 0.0033 | 0.4983 | 0.0027 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4990 | 0.0062 | 0.5449 | 0.0305 | 0.5207 | 0.0172 | 0.5467 | 0.0186 | 0.4955 | 0.0033 | 0.4983 | 0.0027 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5158 | 0.0066 | 0.6408 | 0.0086 | 0.5715 | 0.0054 | 0.6016 | 0.0176 | 0.5102 | 0.0083 | 0.5046 | 0.0025 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5075 | 0.0045 | 0.5825 | 0.0402 | 0.5420 | 0.0194 | 0.5650 | 0.0336 | 0.5102 | 0.0083 | 0.5046 | 0.0025 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.5005 | 0.0122 | 0.5487 | 0.0425 | 0.5232 | 0.0259 | 0.5467 | 0.0186 | 0.5102 | 0.0083 | 0.5046 | 0.0025 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5230 | 0.0071 | 0.6594 | 0.0076 | 0.5833 | 0.0058 | 0.6016 | 0.0176 | 0.5284 | 0.0110 | 0.5132 | 0.0019 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5132 | 0.0066 | 0.5961 | 0.0433 | 0.5512 | 0.0216 | 0.5650 | 0.0336 | 0.5284 | 0.0110 | 0.5132 | 0.0019 |
| degradation_aware | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.5053 | 0.0127 | 0.5594 | 0.0442 | 0.5307 | 0.0268 | 0.5467 | 0.0186 | 0.5284 | 0.0110 | 0.5132 | 0.0019 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 95.0000 | 0.5481 | 0.0090 | 0.7096 | 0.0085 | 0.6184 | 0.0030 | 0.5854 | 0.0279 | 0.5204 | 0.0127 | 0.5433 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 97.5000 | 0.5440 | 0.0132 | 0.6630 | 0.0461 | 0.5974 | 0.0267 | 0.5549 | 0.0122 | 0.5204 | 0.0127 | 0.5433 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 99.0000 | 0.5401 | 0.0230 | 0.6324 | 0.0624 | 0.5823 | 0.0401 | 0.5366 | 0.0061 | 0.5204 | 0.0127 | 0.5433 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 95.0000 | 0.5593 | 0.0118 | 0.7425 | 0.0088 | 0.6380 | 0.0088 | 0.5854 | 0.0279 | 0.5491 | 0.0202 | 0.5661 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 97.5000 | 0.5558 | 0.0165 | 0.6958 | 0.0569 | 0.6177 | 0.0328 | 0.5549 | 0.0122 | 0.5491 | 0.0202 | 0.5661 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 99.0000 | 0.5474 | 0.0289 | 0.6525 | 0.0792 | 0.5948 | 0.0505 | 0.5366 | 0.0061 | 0.5491 | 0.0202 | 0.5661 | 0.0094 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 95.0000 | 0.5711 | 0.0126 | 0.7790 | 0.0201 | 0.6589 | 0.0130 | 0.5854 | 0.0279 | 0.5970 | 0.0264 | 0.6006 | 0.0051 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 97.5000 | 0.5678 | 0.0112 | 0.7298 | 0.0427 | 0.6385 | 0.0233 | 0.5549 | 0.0122 | 0.5970 | 0.0264 | 0.6006 | 0.0051 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 99.0000 | 0.5598 | 0.0321 | 0.6870 | 0.0917 | 0.6163 | 0.0570 | 0.5366 | 0.0061 | 0.5970 | 0.0264 | 0.6006 | 0.0051 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.6142 | 0.0282 | 0.9362 | 0.1052 | 0.7411 | 0.0532 | 0.5854 | 0.0279 | 0.5694 | 0.0095 | 0.6255 | 0.0127 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6011 | 0.0268 | 0.8395 | 0.0849 | 0.7002 | 0.0479 | 0.5549 | 0.0122 | 0.5694 | 0.0095 | 0.6255 | 0.0127 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5886 | 0.0184 | 0.7695 | 0.0574 | 0.6668 | 0.0335 | 0.5366 | 0.0061 | 0.5694 | 0.0095 | 0.6255 | 0.0127 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.6280 | 0.0113 | 0.9877 | 0.0214 | 0.7677 | 0.0120 | 0.5854 | 0.0279 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6295 | 0.0243 | 0.9465 | 0.0927 | 0.7556 | 0.0473 | 0.5549 | 0.0122 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.6205 | 0.0273 | 0.8827 | 0.1092 | 0.7280 | 0.0557 | 0.5366 | 0.0061 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.6280 | 0.0113 | 0.9877 | 0.0214 | 0.7677 | 0.0120 | 0.5854 | 0.0279 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6295 | 0.0243 | 0.9465 | 0.0927 | 0.7556 | 0.0473 | 0.5549 | 0.0122 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.6205 | 0.0273 | 0.8827 | 0.1092 | 0.7280 | 0.0557 | 0.5366 | 0.0061 | 0.5738 | 0.0097 | 0.6350 | 0.0125 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5196 | 0.0192 | 0.6337 | 0.0411 | 0.5709 | 0.0270 | 0.5854 | 0.0279 | 0.6288 | 0.0121 | 0.5661 | 0.0137 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5129 | 0.0083 | 0.5844 | 0.0143 | 0.5463 | 0.0102 | 0.5549 | 0.0122 | 0.6288 | 0.0121 | 0.5661 | 0.0137 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5049 | 0.0032 | 0.5473 | 0.0128 | 0.5252 | 0.0076 | 0.5366 | 0.0061 | 0.6288 | 0.0121 | 0.5661 | 0.0137 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5339 | 0.0179 | 0.6708 | 0.0362 | 0.5944 | 0.0238 | 0.5854 | 0.0279 | 0.7139 | 0.0090 | 0.6244 | 0.0105 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5290 | 0.0117 | 0.6235 | 0.0269 | 0.5723 | 0.0177 | 0.5549 | 0.0122 | 0.7139 | 0.0090 | 0.6244 | 0.0105 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5220 | 0.0092 | 0.5864 | 0.0283 | 0.5523 | 0.0176 | 0.5366 | 0.0061 | 0.7139 | 0.0090 | 0.6244 | 0.0105 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5518 | 0.0119 | 0.7202 | 0.0143 | 0.6247 | 0.0103 | 0.5854 | 0.0279 | 0.7587 | 0.0133 | 0.6770 | 0.0153 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5540 | 0.0073 | 0.6893 | 0.0094 | 0.6143 | 0.0076 | 0.5549 | 0.0122 | 0.7587 | 0.0133 | 0.6770 | 0.0153 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5502 | 0.0027 | 0.6564 | 0.0094 | 0.5986 | 0.0051 | 0.5366 | 0.0061 | 0.7587 | 0.0133 | 0.6770 | 0.0153 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5011 | 0.0067 | 0.5876 | 0.0171 | 0.5408 | 0.0064 | 0.5854 | 0.0279 | 0.4962 | 0.0030 | 0.4947 | 0.0029 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5002 | 0.0007 | 0.5554 | 0.0135 | 0.5264 | 0.0064 | 0.5549 | 0.0122 | 0.4962 | 0.0030 | 0.4947 | 0.0029 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4997 | 0.0062 | 0.5361 | 0.0190 | 0.5172 | 0.0122 | 0.5366 | 0.0061 | 0.4962 | 0.0030 | 0.4947 | 0.0029 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5067 | 0.0075 | 0.6012 | 0.0213 | 0.5498 | 0.0096 | 0.5854 | 0.0279 | 0.5123 | 0.0030 | 0.5001 | 0.0012 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5046 | 0.0017 | 0.5653 | 0.0151 | 0.5332 | 0.0075 | 0.5549 | 0.0122 | 0.5123 | 0.0030 | 0.5001 | 0.0012 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.5019 | 0.0090 | 0.5410 | 0.0253 | 0.5206 | 0.0165 | 0.5366 | 0.0061 | 0.5123 | 0.0030 | 0.5001 | 0.0012 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5120 | 0.0068 | 0.6140 | 0.0247 | 0.5582 | 0.0110 | 0.5854 | 0.0279 | 0.5328 | 0.0035 | 0.5090 | 0.0029 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5093 | 0.0028 | 0.5759 | 0.0178 | 0.5405 | 0.0092 | 0.5549 | 0.0122 | 0.5328 | 0.0035 | 0.5090 | 0.0029 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.5063 | 0.0100 | 0.5506 | 0.0282 | 0.5274 | 0.0184 | 0.5366 | 0.0061 | 0.5328 | 0.0035 | 0.5090 | 0.0029 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 95.0000 | 0.5486 | 0.0026 | 0.7237 | 0.0055 | 0.6241 | 0.0028 | 0.5955 | 0.0070 | 0.5231 | 0.0095 | 0.5398 | 0.0037 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 97.5000 | 0.5510 | 0.0020 | 0.6959 | 0.0242 | 0.6149 | 0.0092 | 0.5671 | 0.0220 | 0.5231 | 0.0095 | 0.5398 | 0.0037 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | mild | 99.0000 | 0.5406 | 0.0185 | 0.6354 | 0.0544 | 0.5839 | 0.0338 | 0.5386 | 0.0070 | 0.5231 | 0.0095 | 0.5398 | 0.0037 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 95.0000 | 0.5623 | 0.0054 | 0.7652 | 0.0162 | 0.6482 | 0.0091 | 0.5955 | 0.0070 | 0.5381 | 0.0204 | 0.5614 | 0.0111 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 97.5000 | 0.5657 | 0.0034 | 0.7385 | 0.0248 | 0.6405 | 0.0093 | 0.5671 | 0.0220 | 0.5381 | 0.0204 | 0.5614 | 0.0111 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | moderate | 99.0000 | 0.5499 | 0.0213 | 0.6603 | 0.0641 | 0.5997 | 0.0390 | 0.5386 | 0.0070 | 0.5381 | 0.0204 | 0.5614 | 0.0111 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 95.0000 | 0.5761 | 0.0047 | 0.8095 | 0.0153 | 0.6731 | 0.0081 | 0.5955 | 0.0070 | 0.5943 | 0.0554 | 0.6011 | 0.0256 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 97.5000 | 0.5801 | 0.0032 | 0.7837 | 0.0348 | 0.6665 | 0.0141 | 0.5671 | 0.0220 | 0.5943 | 0.0554 | 0.6011 | 0.0256 |
| degradation_aware | 200 | 0.7500 | A1_ACCELERATED_DEGRADATION | strong | 99.0000 | 0.5669 | 0.0122 | 0.7058 | 0.0405 | 0.6286 | 0.0234 | 0.5386 | 0.0070 | 0.5943 | 0.0554 | 0.6011 | 0.0256 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.6233 | 0.0052 | 0.9856 | 0.0249 | 0.7636 | 0.0111 | 0.5955 | 0.0070 | 0.5750 | 0.0105 | 0.6310 | 0.0117 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6259 | 0.0108 | 0.9506 | 0.0751 | 0.7544 | 0.0318 | 0.5671 | 0.0220 | 0.5750 | 0.0105 | 0.6310 | 0.0117 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.6101 | 0.0097 | 0.8436 | 0.0434 | 0.7080 | 0.0218 | 0.5386 | 0.0070 | 0.5750 | 0.0105 | 0.6310 | 0.0117 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.6268 | 0.0028 | 1.0000 | 0.0000 | 0.7706 | 0.0021 | 0.5955 | 0.0070 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6382 | 0.0090 | 1.0000 | 0.0000 | 0.7791 | 0.0067 | 0.5671 | 0.0220 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.6490 | 0.0027 | 0.9959 | 0.0036 | 0.7859 | 0.0020 | 0.5386 | 0.0070 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.6268 | 0.0028 | 1.0000 | 0.0000 | 0.7706 | 0.0021 | 0.5955 | 0.0070 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6382 | 0.0090 | 1.0000 | 0.0000 | 0.7791 | 0.0067 | 0.5671 | 0.0220 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.6490 | 0.0027 | 0.9959 | 0.0036 | 0.7859 | 0.0020 | 0.5386 | 0.0070 | 0.5801 | 0.0129 | 0.6418 | 0.0168 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5243 | 0.0013 | 0.6564 | 0.0094 | 0.5829 | 0.0042 | 0.5955 | 0.0070 | 0.6182 | 0.0135 | 0.5607 | 0.0082 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5145 | 0.0069 | 0.6008 | 0.0143 | 0.5543 | 0.0067 | 0.5671 | 0.0220 | 0.6182 | 0.0135 | 0.5607 | 0.0082 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5085 | 0.0083 | 0.5576 | 0.0249 | 0.5319 | 0.0159 | 0.5386 | 0.0070 | 0.6182 | 0.0135 | 0.5607 | 0.0082 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5350 | 0.0059 | 0.6852 | 0.0107 | 0.6008 | 0.0076 | 0.5955 | 0.0070 | 0.7075 | 0.0081 | 0.6176 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5358 | 0.0059 | 0.6543 | 0.0107 | 0.5891 | 0.0020 | 0.5671 | 0.0220 | 0.7075 | 0.0081 | 0.6176 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5185 | 0.0054 | 0.5802 | 0.0185 | 0.5476 | 0.0112 | 0.5386 | 0.0070 | 0.7075 | 0.0081 | 0.6176 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5495 | 0.0005 | 0.7263 | 0.0071 | 0.6256 | 0.0023 | 0.5955 | 0.0070 | 0.7520 | 0.0063 | 0.6668 | 0.0081 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5509 | 0.0064 | 0.6955 | 0.0155 | 0.6147 | 0.0062 | 0.5671 | 0.0220 | 0.7520 | 0.0063 | 0.6668 | 0.0081 |
| degradation_aware | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5485 | 0.0047 | 0.6543 | 0.0163 | 0.5967 | 0.0093 | 0.5386 | 0.0070 | 0.7520 | 0.0063 | 0.6668 | 0.0081 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5046 | 0.0019 | 0.6066 | 0.0025 | 0.5509 | 0.0001 | 0.5955 | 0.0070 | 0.4969 | 0.0020 | 0.4973 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5039 | 0.0047 | 0.5758 | 0.0139 | 0.5374 | 0.0049 | 0.5671 | 0.0220 | 0.4969 | 0.0020 | 0.4973 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.5021 | 0.0016 | 0.5432 | 0.0099 | 0.5218 | 0.0054 | 0.5386 | 0.0070 | 0.4969 | 0.0020 | 0.4973 | 0.0010 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5153 | 0.0038 | 0.6331 | 0.0022 | 0.5682 | 0.0032 | 0.5955 | 0.0070 | 0.5127 | 0.0033 | 0.5035 | 0.0014 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5124 | 0.0066 | 0.5956 | 0.0144 | 0.5508 | 0.0067 | 0.5671 | 0.0220 | 0.5127 | 0.0033 | 0.5035 | 0.0014 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.5061 | 0.0010 | 0.5520 | 0.0093 | 0.5281 | 0.0048 | 0.5386 | 0.0070 | 0.5127 | 0.0033 | 0.5035 | 0.0014 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5219 | 0.0039 | 0.6500 | 0.0024 | 0.5789 | 0.0033 | 0.5955 | 0.0070 | 0.5324 | 0.0017 | 0.5122 | 0.0018 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5184 | 0.0071 | 0.6104 | 0.0156 | 0.5606 | 0.0077 | 0.5671 | 0.0220 | 0.5324 | 0.0017 | 0.5122 | 0.0018 |
| degradation_aware | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.5105 | 0.0007 | 0.5616 | 0.0075 | 0.5348 | 0.0035 | 0.5386 | 0.0070 | 0.5324 | 0.0017 | 0.5122 | 0.0018 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 95.0000 | 0.5467 | 0.0026 | 0.6986 | 0.0168 | 0.6134 | 0.0065 | 0.5793 | 0.0161 | 0.5071 | 0.0061 | 0.5334 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 97.5000 | 0.5497 | 0.0056 | 0.6774 | 0.0155 | 0.6069 | 0.0096 | 0.5549 | 0.0000 | 0.5071 | 0.0061 | 0.5334 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | 99.0000 | 0.5402 | 0.0158 | 0.6193 | 0.0364 | 0.5770 | 0.0247 | 0.5264 | 0.0070 | 0.5071 | 0.0061 | 0.5334 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 95.0000 | 0.5568 | 0.0036 | 0.7278 | 0.0257 | 0.6308 | 0.0114 | 0.5793 | 0.0161 | 0.5127 | 0.0110 | 0.5486 | 0.0109 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 97.5000 | 0.5585 | 0.0084 | 0.7024 | 0.0241 | 0.6222 | 0.0146 | 0.5549 | 0.0000 | 0.5127 | 0.0110 | 0.5486 | 0.0109 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | 99.0000 | 0.5448 | 0.0190 | 0.6313 | 0.0456 | 0.5847 | 0.0304 | 0.5264 | 0.0070 | 0.5127 | 0.0110 | 0.5486 | 0.0109 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 95.0000 | 0.5666 | 0.0053 | 0.7574 | 0.0183 | 0.6482 | 0.0083 | 0.5793 | 0.0161 | 0.5323 | 0.0233 | 0.5725 | 0.0161 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 97.5000 | 0.5692 | 0.0071 | 0.7332 | 0.0213 | 0.6408 | 0.0126 | 0.5549 | 0.0000 | 0.5323 | 0.0233 | 0.5725 | 0.0161 |
| degradation_aware | 200 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | 99.0000 | 0.5536 | 0.0157 | 0.6536 | 0.0406 | 0.5993 | 0.0261 | 0.5264 | 0.0070 | 0.5323 | 0.0233 | 0.5725 | 0.0161 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.6238 | 0.0083 | 0.9609 | 0.0351 | 0.7564 | 0.0156 | 0.5793 | 0.0161 | 0.5640 | 0.0046 | 0.6249 | 0.0034 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6131 | 0.0144 | 0.8807 | 0.0525 | 0.7228 | 0.0278 | 0.5549 | 0.0000 | 0.5640 | 0.0046 | 0.6249 | 0.0034 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5949 | 0.0207 | 0.7757 | 0.0747 | 0.6729 | 0.0417 | 0.5264 | 0.0070 | 0.5640 | 0.0046 | 0.6249 | 0.0034 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.6332 | 0.0065 | 1.0000 | 0.0000 | 0.7754 | 0.0049 | 0.5793 | 0.0161 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6431 | 0.0000 | 1.0000 | 0.0000 | 0.7828 | 0.0000 | 0.5549 | 0.0000 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.6290 | 0.0295 | 0.8992 | 0.1207 | 0.7392 | 0.0620 | 0.5264 | 0.0070 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.6332 | 0.0065 | 1.0000 | 0.0000 | 0.7754 | 0.0049 | 0.5793 | 0.0161 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6431 | 0.0000 | 1.0000 | 0.0000 | 0.7828 | 0.0000 | 0.5549 | 0.0000 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.6290 | 0.0295 | 0.8992 | 0.1207 | 0.7392 | 0.0620 | 0.5264 | 0.0070 | 0.5680 | 0.0046 | 0.6337 | 0.0027 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5138 | 0.0140 | 0.6132 | 0.0479 | 0.5588 | 0.0279 | 0.5793 | 0.0161 | 0.6258 | 0.0046 | 0.5661 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5162 | 0.0136 | 0.5926 | 0.0327 | 0.5517 | 0.0219 | 0.5549 | 0.0000 | 0.6258 | 0.0046 | 0.5661 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5115 | 0.0048 | 0.5514 | 0.0178 | 0.5307 | 0.0109 | 0.5264 | 0.0070 | 0.6258 | 0.0046 | 0.5661 | 0.0078 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5317 | 0.0104 | 0.6584 | 0.0397 | 0.5882 | 0.0217 | 0.5793 | 0.0161 | 0.7138 | 0.0077 | 0.6259 | 0.0094 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5314 | 0.0105 | 0.6296 | 0.0269 | 0.5763 | 0.0174 | 0.5549 | 0.0000 | 0.7138 | 0.0077 | 0.6259 | 0.0094 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5258 | 0.0105 | 0.5844 | 0.0317 | 0.5534 | 0.0201 | 0.5264 | 0.0070 | 0.7138 | 0.0077 | 0.6259 | 0.0094 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5499 | 0.0019 | 0.7078 | 0.0217 | 0.6189 | 0.0089 | 0.5793 | 0.0161 | 0.7610 | 0.0053 | 0.6789 | 0.0066 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5554 | 0.0070 | 0.6934 | 0.0198 | 0.6168 | 0.0122 | 0.5549 | 0.0000 | 0.7610 | 0.0053 | 0.6789 | 0.0066 |
| degradation_aware | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5491 | 0.0135 | 0.6420 | 0.0428 | 0.5917 | 0.0262 | 0.5264 | 0.0070 | 0.7610 | 0.0053 | 0.6789 | 0.0066 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.4998 | 0.0009 | 0.5788 | 0.0146 | 0.5364 | 0.0060 | 0.5793 | 0.0161 | 0.4955 | 0.0012 | 0.4965 | 0.0015 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5031 | 0.0032 | 0.5618 | 0.0071 | 0.5308 | 0.0049 | 0.5549 | 0.0000 | 0.4955 | 0.0012 | 0.4965 | 0.0015 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.5025 | 0.0016 | 0.5318 | 0.0074 | 0.5167 | 0.0038 | 0.5264 | 0.0070 | 0.4955 | 0.0012 | 0.4965 | 0.0015 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5056 | 0.0023 | 0.5925 | 0.0182 | 0.5456 | 0.0084 | 0.5793 | 0.0161 | 0.5108 | 0.0011 | 0.5015 | 0.0031 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5093 | 0.0047 | 0.5760 | 0.0108 | 0.5406 | 0.0074 | 0.5549 | 0.0000 | 0.5108 | 0.0011 | 0.5015 | 0.0031 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.5058 | 0.0019 | 0.5388 | 0.0085 | 0.5217 | 0.0046 | 0.5264 | 0.0070 | 0.5108 | 0.0011 | 0.5015 | 0.0031 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5112 | 0.0023 | 0.6060 | 0.0192 | 0.5545 | 0.0089 | 0.5793 | 0.0161 | 0.5321 | 0.0032 | 0.5102 | 0.0049 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5149 | 0.0046 | 0.5889 | 0.0107 | 0.5494 | 0.0073 | 0.5549 | 0.0000 | 0.5321 | 0.0032 | 0.5102 | 0.0049 |
| degradation_aware | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.5103 | 0.0026 | 0.5487 | 0.0120 | 0.5288 | 0.0069 | 0.5264 | 0.0070 | 0.5321 | 0.0032 | 0.5102 | 0.0049 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.5940 | 0.0189 | 1.0000 | 0.0000 | 0.7452 | 0.0149 | 0.6845 | 0.0536 | 0.5676 | 0.0036 | 0.6332 | 0.0100 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6208 | 0.0099 | 0.9837 | 0.0141 | 0.7612 | 0.0097 | 0.6012 | 0.0238 | 0.5676 | 0.0036 | 0.6332 | 0.0100 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5488 | 0.0492 | 0.5159 | 0.2758 | 0.5102 | 0.1845 | 0.4028 | 0.1635 | 0.5676 | 0.0036 | 0.6332 | 0.0100 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.5940 | 0.0189 | 1.0000 | 0.0000 | 0.7452 | 0.0149 | 0.6845 | 0.0536 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6246 | 0.0093 | 1.0000 | 0.0000 | 0.7689 | 0.0070 | 0.6012 | 0.0238 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.5573 | 0.0487 | 0.5346 | 0.2855 | 0.5233 | 0.1885 | 0.4028 | 0.1635 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.5940 | 0.0189 | 1.0000 | 0.0000 | 0.7452 | 0.0149 | 0.6845 | 0.0536 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6246 | 0.0093 | 1.0000 | 0.0000 | 0.7689 | 0.0070 | 0.6012 | 0.0238 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.5573 | 0.0487 | 0.5346 | 0.2855 | 0.5233 | 0.1885 | 0.4028 | 0.1635 | 0.5756 | 0.0079 | 0.6440 | 0.0144 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5317 | 0.0118 | 0.7764 | 0.0406 | 0.6308 | 0.0135 | 0.6845 | 0.0536 | 0.6193 | 0.0566 | 0.5967 | 0.0357 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5281 | 0.0073 | 0.6728 | 0.0288 | 0.5915 | 0.0140 | 0.6012 | 0.0238 | 0.6193 | 0.0566 | 0.5967 | 0.0357 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5712 | 0.0975 | 0.5061 | 0.0381 | 0.5315 | 0.0187 | 0.4028 | 0.1635 | 0.6193 | 0.0566 | 0.5967 | 0.0357 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5601 | 0.0204 | 0.8740 | 0.1060 | 0.6817 | 0.0440 | 0.6845 | 0.0536 | 0.6932 | 0.0624 | 0.6545 | 0.0437 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5497 | 0.0170 | 0.7337 | 0.0214 | 0.6285 | 0.0190 | 0.6012 | 0.0238 | 0.6932 | 0.0624 | 0.6545 | 0.0437 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5841 | 0.1051 | 0.5350 | 0.0220 | 0.5543 | 0.0351 | 0.4028 | 0.1635 | 0.6932 | 0.0624 | 0.6545 | 0.0437 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5863 | 0.0220 | 0.9695 | 0.0476 | 0.7305 | 0.0268 | 0.6845 | 0.0536 | 0.7443 | 0.0551 | 0.7034 | 0.0504 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5877 | 0.0231 | 0.8598 | 0.0860 | 0.6976 | 0.0438 | 0.6012 | 0.0238 | 0.7443 | 0.0551 | 0.7034 | 0.0504 |
| measurement_oriented | 100 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5937 | 0.1084 | 0.5581 | 0.0301 | 0.5716 | 0.0462 | 0.4028 | 0.1635 | 0.7443 | 0.0551 | 0.7034 | 0.0504 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5049 | 0.0012 | 0.6981 | 0.0516 | 0.5855 | 0.0175 | 0.6845 | 0.0536 | 0.5024 | 0.0039 | 0.5002 | 0.0016 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5019 | 0.0016 | 0.6058 | 0.0273 | 0.5488 | 0.0121 | 0.6012 | 0.0238 | 0.5024 | 0.0039 | 0.5002 | 0.0016 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4883 | 0.0082 | 0.3879 | 0.1657 | 0.4184 | 0.1208 | 0.4028 | 0.1635 | 0.5024 | 0.0039 | 0.5002 | 0.0016 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5142 | 0.0043 | 0.7246 | 0.0576 | 0.6009 | 0.0202 | 0.6845 | 0.0536 | 0.5191 | 0.0120 | 0.5063 | 0.0031 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5102 | 0.0036 | 0.6264 | 0.0329 | 0.5622 | 0.0152 | 0.6012 | 0.0238 | 0.5191 | 0.0120 | 0.5063 | 0.0031 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.4775 | 0.0133 | 0.3719 | 0.1613 | 0.4046 | 0.1193 | 0.4028 | 0.1635 | 0.5191 | 0.0120 | 0.5063 | 0.0031 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5225 | 0.0045 | 0.7491 | 0.0592 | 0.6150 | 0.0203 | 0.6845 | 0.0536 | 0.5444 | 0.0130 | 0.5205 | 0.0069 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5189 | 0.0043 | 0.6486 | 0.0344 | 0.5763 | 0.0158 | 0.6012 | 0.0238 | 0.5444 | 0.0130 | 0.5205 | 0.0069 |
| measurement_oriented | 100 | 0.7500 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.4775 | 0.0224 | 0.3690 | 0.1566 | 0.4032 | 0.1131 | 0.4028 | 0.1635 | 0.5444 | 0.0130 | 0.5205 | 0.0069 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.5959 | 0.0111 | 1.0000 | 0.0000 | 0.7467 | 0.0087 | 0.6786 | 0.0309 | 0.5656 | 0.0078 | 0.6308 | 0.0089 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6219 | 0.0128 | 0.9756 | 0.0279 | 0.7595 | 0.0165 | 0.5933 | 0.0241 | 0.5656 | 0.0078 | 0.6308 | 0.0089 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5855 | 0.0138 | 0.7073 | 0.0588 | 0.6402 | 0.0307 | 0.5000 | 0.0259 | 0.5656 | 0.0078 | 0.6308 | 0.0089 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.5959 | 0.0111 | 1.0000 | 0.0000 | 0.7467 | 0.0087 | 0.6786 | 0.0309 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6277 | 0.0096 | 1.0000 | 0.0000 | 0.7713 | 0.0072 | 0.5933 | 0.0241 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.5986 | 0.0195 | 0.7480 | 0.0812 | 0.6643 | 0.0425 | 0.5000 | 0.0259 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.5959 | 0.0111 | 1.0000 | 0.0000 | 0.7467 | 0.0087 | 0.6786 | 0.0309 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6277 | 0.0096 | 1.0000 | 0.0000 | 0.7713 | 0.0072 | 0.5933 | 0.0241 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.5986 | 0.0195 | 0.7480 | 0.0812 | 0.6643 | 0.0425 | 0.5000 | 0.0259 | 0.5778 | 0.0092 | 0.6439 | 0.0116 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5337 | 0.0194 | 0.7764 | 0.0254 | 0.6326 | 0.0220 | 0.6786 | 0.0309 | 0.6303 | 0.0043 | 0.5994 | 0.0069 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5284 | 0.0135 | 0.6646 | 0.0161 | 0.5887 | 0.0136 | 0.5933 | 0.0241 | 0.6303 | 0.0043 | 0.5994 | 0.0069 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5165 | 0.0071 | 0.5337 | 0.0134 | 0.5248 | 0.0035 | 0.5000 | 0.0259 | 0.6303 | 0.0043 | 0.5994 | 0.0069 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5604 | 0.0248 | 0.8659 | 0.0542 | 0.6803 | 0.0346 | 0.6786 | 0.0309 | 0.7169 | 0.0094 | 0.6668 | 0.0092 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5461 | 0.0084 | 0.7134 | 0.0061 | 0.6186 | 0.0038 | 0.5933 | 0.0241 | 0.7169 | 0.0094 | 0.6668 | 0.0092 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5278 | 0.0076 | 0.5585 | 0.0172 | 0.5426 | 0.0071 | 0.5000 | 0.0259 | 0.7169 | 0.0094 | 0.6668 | 0.0092 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5949 | 0.0120 | 0.9959 | 0.0070 | 0.7448 | 0.0107 | 0.6786 | 0.0309 | 0.7663 | 0.0188 | 0.7095 | 0.0150 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5729 | 0.0084 | 0.7967 | 0.0576 | 0.6661 | 0.0261 | 0.5933 | 0.0241 | 0.7663 | 0.0188 | 0.7095 | 0.0150 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5528 | 0.0195 | 0.6183 | 0.0361 | 0.5835 | 0.0251 | 0.5000 | 0.0259 | 0.7663 | 0.0188 | 0.7095 | 0.0150 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5049 | 0.0061 | 0.6916 | 0.0158 | 0.5836 | 0.0027 | 0.6786 | 0.0309 | 0.5021 | 0.0038 | 0.5027 | 0.0016 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5018 | 0.0053 | 0.5974 | 0.0196 | 0.5453 | 0.0084 | 0.5933 | 0.0241 | 0.5021 | 0.0038 | 0.5027 | 0.0016 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4984 | 0.0030 | 0.4969 | 0.0303 | 0.4974 | 0.0167 | 0.5000 | 0.0259 | 0.5021 | 0.0038 | 0.5027 | 0.0016 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5181 | 0.0080 | 0.7292 | 0.0160 | 0.6057 | 0.0057 | 0.6786 | 0.0309 | 0.5225 | 0.0022 | 0.5101 | 0.0019 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5106 | 0.0081 | 0.6190 | 0.0259 | 0.5595 | 0.0133 | 0.5933 | 0.0241 | 0.5225 | 0.0022 | 0.5101 | 0.0019 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.4935 | 0.0126 | 0.4884 | 0.0488 | 0.4904 | 0.0313 | 0.5000 | 0.0259 | 0.5225 | 0.0022 | 0.5101 | 0.0019 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5279 | 0.0089 | 0.7584 | 0.0177 | 0.6224 | 0.0077 | 0.6786 | 0.0309 | 0.5454 | 0.0021 | 0.5232 | 0.0029 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5190 | 0.0085 | 0.6402 | 0.0292 | 0.5731 | 0.0149 | 0.5933 | 0.0241 | 0.5454 | 0.0021 | 0.5232 | 0.0029 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.4951 | 0.0150 | 0.4918 | 0.0535 | 0.4929 | 0.0347 | 0.5000 | 0.0259 | 0.5454 | 0.0021 | 0.5232 | 0.0029 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.5840 | 0.0012 | 1.0000 | 0.0000 | 0.7374 | 0.0009 | 0.7123 | 0.0034 | 0.5645 | 0.0087 | 0.6273 | 0.0173 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6219 | 0.0047 | 0.9919 | 0.0141 | 0.7644 | 0.0059 | 0.6032 | 0.0137 | 0.5645 | 0.0087 | 0.6273 | 0.0173 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5585 | 0.0393 | 0.6244 | 0.1378 | 0.5875 | 0.0821 | 0.4861 | 0.0305 | 0.5645 | 0.0087 | 0.6273 | 0.0173 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.5840 | 0.0012 | 1.0000 | 0.0000 | 0.7374 | 0.0009 | 0.7123 | 0.0034 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6238 | 0.0053 | 1.0000 | 0.0000 | 0.7683 | 0.0040 | 0.6032 | 0.0137 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.5720 | 0.0489 | 0.6646 | 0.1764 | 0.6117 | 0.1019 | 0.4861 | 0.0305 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.5840 | 0.0012 | 1.0000 | 0.0000 | 0.7374 | 0.0009 | 0.7123 | 0.0034 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6238 | 0.0053 | 1.0000 | 0.0000 | 0.7683 | 0.0040 | 0.6032 | 0.0137 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.5720 | 0.0489 | 0.6646 | 0.1764 | 0.6117 | 0.1019 | 0.4861 | 0.0305 | 0.5722 | 0.0102 | 0.6384 | 0.0186 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5234 | 0.0080 | 0.7825 | 0.0231 | 0.6272 | 0.0131 | 0.7123 | 0.0034 | 0.6289 | 0.0272 | 0.5973 | 0.0218 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5328 | 0.0149 | 0.6890 | 0.0521 | 0.6007 | 0.0291 | 0.6032 | 0.0137 | 0.6289 | 0.0272 | 0.5973 | 0.0218 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5175 | 0.0123 | 0.5207 | 0.0088 | 0.5190 | 0.0036 | 0.4861 | 0.0305 | 0.6289 | 0.0272 | 0.5973 | 0.0218 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5582 | 0.0218 | 0.9024 | 0.0749 | 0.6896 | 0.0387 | 0.7123 | 0.0034 | 0.7092 | 0.0334 | 0.6545 | 0.0294 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5477 | 0.0238 | 0.7337 | 0.0872 | 0.6266 | 0.0471 | 0.6032 | 0.0137 | 0.7092 | 0.0334 | 0.6545 | 0.0294 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5248 | 0.0179 | 0.5362 | 0.0051 | 0.5304 | 0.0114 | 0.4861 | 0.0305 | 0.7092 | 0.0334 | 0.6545 | 0.0294 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5835 | 0.0018 | 0.9980 | 0.0035 | 0.7364 | 0.0023 | 0.7123 | 0.0034 | 0.7501 | 0.0361 | 0.6969 | 0.0385 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5811 | 0.0304 | 0.8435 | 0.1280 | 0.6871 | 0.0633 | 0.6032 | 0.0137 | 0.7501 | 0.0361 | 0.6969 | 0.0385 |
| measurement_oriented | 200 | 0.7500 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5377 | 0.0249 | 0.5650 | 0.0210 | 0.5510 | 0.0230 | 0.4861 | 0.0305 | 0.7501 | 0.0361 | 0.6969 | 0.0385 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5041 | 0.0051 | 0.7242 | 0.0114 | 0.5944 | 0.0074 | 0.7123 | 0.0034 | 0.5007 | 0.0026 | 0.4993 | 0.0045 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5057 | 0.0012 | 0.6171 | 0.0160 | 0.5558 | 0.0070 | 0.6032 | 0.0137 | 0.5007 | 0.0026 | 0.4993 | 0.0045 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4902 | 0.0019 | 0.4675 | 0.0313 | 0.4782 | 0.0172 | 0.4861 | 0.0305 | 0.5007 | 0.0026 | 0.4993 | 0.0045 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5160 | 0.0074 | 0.7596 | 0.0192 | 0.6145 | 0.0115 | 0.7123 | 0.0034 | 0.5193 | 0.0072 | 0.5074 | 0.0065 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5158 | 0.0018 | 0.6425 | 0.0182 | 0.5721 | 0.0081 | 0.6032 | 0.0137 | 0.5193 | 0.0072 | 0.5074 | 0.0065 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.4812 | 0.0078 | 0.4516 | 0.0417 | 0.4655 | 0.0259 | 0.4861 | 0.0305 | 0.5193 | 0.0072 | 0.5074 | 0.0065 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5262 | 0.0080 | 0.7912 | 0.0220 | 0.6320 | 0.0128 | 0.7123 | 0.0034 | 0.5446 | 0.0072 | 0.5223 | 0.0095 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5248 | 0.0021 | 0.6663 | 0.0185 | 0.5871 | 0.0081 | 0.6032 | 0.0137 | 0.5446 | 0.0072 | 0.5223 | 0.0095 |
| measurement_oriented | 200 | 0.7500 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.4860 | 0.0110 | 0.4605 | 0.0453 | 0.4724 | 0.0285 | 0.4861 | 0.0305 | 0.5446 | 0.0072 | 0.5223 | 0.0095 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 95.0000 | 0.5994 | 0.0088 | 1.0000 | 0.0000 | 0.7495 | 0.0069 | 0.6687 | 0.0248 | 0.5649 | 0.0076 | 0.6302 | 0.0111 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 97.5000 | 0.6197 | 0.0085 | 0.9797 | 0.0254 | 0.7591 | 0.0135 | 0.6012 | 0.0119 | 0.5649 | 0.0076 | 0.6302 | 0.0111 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 99.0000 | 0.5790 | 0.0413 | 0.6809 | 0.1177 | 0.6244 | 0.0730 | 0.4901 | 0.0364 | 0.5649 | 0.0076 | 0.6302 | 0.0111 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95.0000 | 0.5994 | 0.0088 | 1.0000 | 0.0000 | 0.7495 | 0.0069 | 0.6687 | 0.0248 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 97.5000 | 0.6246 | 0.0046 | 1.0000 | 0.0000 | 0.7689 | 0.0035 | 0.6012 | 0.0119 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 99.0000 | 0.5967 | 0.0513 | 0.7378 | 0.1582 | 0.6576 | 0.0946 | 0.4901 | 0.0364 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 95.0000 | 0.5994 | 0.0088 | 1.0000 | 0.0000 | 0.7495 | 0.0069 | 0.6687 | 0.0248 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 97.5000 | 0.6246 | 0.0046 | 1.0000 | 0.0000 | 0.7689 | 0.0035 | 0.6012 | 0.0119 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 99.0000 | 0.5967 | 0.0513 | 0.7378 | 0.1582 | 0.6576 | 0.0946 | 0.4901 | 0.0364 | 0.5787 | 0.0127 | 0.6463 | 0.0154 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 95.0000 | 0.5341 | 0.0098 | 0.7663 | 0.0093 | 0.6294 | 0.0085 | 0.6687 | 0.0248 | 0.6551 | 0.0084 | 0.6090 | 0.0030 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 97.5000 | 0.5264 | 0.0079 | 0.6687 | 0.0301 | 0.5890 | 0.0165 | 0.6012 | 0.0119 | 0.6551 | 0.0084 | 0.6090 | 0.0030 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | 99.0000 | 0.5242 | 0.0034 | 0.5398 | 0.0378 | 0.5315 | 0.0177 | 0.4901 | 0.0364 | 0.6551 | 0.0084 | 0.6090 | 0.0030 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 95.0000 | 0.5649 | 0.0149 | 0.8679 | 0.0214 | 0.6843 | 0.0175 | 0.6687 | 0.0248 | 0.7268 | 0.0104 | 0.6652 | 0.0131 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 97.5000 | 0.5420 | 0.0018 | 0.7114 | 0.0093 | 0.6152 | 0.0025 | 0.6012 | 0.0119 | 0.7268 | 0.0104 | 0.6652 | 0.0131 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | 99.0000 | 0.5330 | 0.0058 | 0.5593 | 0.0416 | 0.5454 | 0.0200 | 0.4901 | 0.0364 | 0.7268 | 0.0104 | 0.6652 | 0.0131 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 95.0000 | 0.5989 | 0.0087 | 0.9980 | 0.0035 | 0.7485 | 0.0067 | 0.6687 | 0.0248 | 0.7612 | 0.0267 | 0.7043 | 0.0230 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 97.5000 | 0.5706 | 0.0096 | 0.7988 | 0.0161 | 0.6656 | 0.0121 | 0.6012 | 0.0119 | 0.7612 | 0.0267 | 0.7043 | 0.0230 |
| measurement_oriented | 200 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | 99.0000 | 0.5531 | 0.0154 | 0.6073 | 0.0583 | 0.5783 | 0.0320 | 0.4901 | 0.0364 | 0.7612 | 0.0267 | 0.7043 | 0.0230 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 95.0000 | 0.5063 | 0.0038 | 0.6856 | 0.0184 | 0.5824 | 0.0057 | 0.6687 | 0.0248 | 0.5028 | 0.0046 | 0.4993 | 0.0024 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 97.5000 | 0.5018 | 0.0018 | 0.6055 | 0.0087 | 0.5488 | 0.0030 | 0.6012 | 0.0119 | 0.5028 | 0.0046 | 0.4993 | 0.0024 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | mild | 99.0000 | 0.4983 | 0.0083 | 0.4871 | 0.0429 | 0.4921 | 0.0240 | 0.4901 | 0.0364 | 0.5028 | 0.0046 | 0.4993 | 0.0024 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 95.0000 | 0.5210 | 0.0041 | 0.7271 | 0.0157 | 0.6070 | 0.0033 | 0.6687 | 0.0248 | 0.5239 | 0.0053 | 0.5066 | 0.0033 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 97.5000 | 0.5095 | 0.0016 | 0.6244 | 0.0107 | 0.5611 | 0.0042 | 0.6012 | 0.0119 | 0.5239 | 0.0053 | 0.5066 | 0.0033 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | moderate | 99.0000 | 0.4895 | 0.0181 | 0.4719 | 0.0654 | 0.4797 | 0.0414 | 0.4901 | 0.0364 | 0.5239 | 0.0053 | 0.5066 | 0.0033 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 95.0000 | 0.5311 | 0.0043 | 0.7570 | 0.0153 | 0.6242 | 0.0025 | 0.6687 | 0.0248 | 0.5437 | 0.0024 | 0.5184 | 0.0038 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 97.5000 | 0.5177 | 0.0012 | 0.6454 | 0.0105 | 0.5745 | 0.0038 | 0.6012 | 0.0119 | 0.5437 | 0.0024 | 0.5184 | 0.0038 |
| measurement_oriented | 200 | 1.0000 | A4_SENSOR_DRIFT | strong | 99.0000 | 0.4895 | 0.0210 | 0.4723 | 0.0703 | 0.4798 | 0.0452 | 0.4901 | 0.0364 | 0.5437 | 0.0024 | 0.5184 | 0.0038 |

## Score distributions and seed stability

score_distributions.csv: count, mean, SD, minimum, P5, median, P95, maximum for each seed/configuration and clean or family/severity/variant. score_seed_stability.csv: cross-seed mean and SD of those summaries. scores.csv.gz preserves every scored copy with scenario/source provenance and paired clean score. Clean unscorable initial cycles are retained as NaN in clean_scores.csv.

| feature_set | n_estimators | max_features | anomaly_family | severity | variant | score_mean_mean | score_mean_std | score_std_mean | score_std_std | score_median_mean | score_median_std | score_p05_mean | score_p05_std | score_p95_mean | score_p95_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | pooled | 0.6115 | 0.0012 | 0.0712 | 0.0052 | 0.6437 | 0.0049 | 0.4707 | 0.0181 | 0.6802 | 0.0005 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | pooled | 0.6166 | 0.0001 | 0.0672 | 0.0038 | 0.6444 | 0.0031 | 0.4757 | 0.0199 | 0.6808 | 0.0003 |
| degradation_aware | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | pooled | 0.6236 | 0.0015 | 0.0624 | 0.0023 | 0.6463 | 0.0011 | 0.4891 | 0.0164 | 0.6828 | 0.0022 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 0.6408 | 0.0040 | 0.0346 | 0.0061 | 0.6520 | 0.0039 | 0.5811 | 0.0153 | 0.6817 | 0.0007 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 0.6461 | 0.0033 | 0.0276 | 0.0051 | 0.6525 | 0.0030 | 0.6033 | 0.0138 | 0.6817 | 0.0007 |
| degradation_aware | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 0.6461 | 0.0033 | 0.0276 | 0.0051 | 0.6525 | 0.0030 | 0.6033 | 0.0138 | 0.6817 | 0.0007 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 0.6013 | 0.0061 | 0.0852 | 0.0071 | 0.6409 | 0.0086 | 0.4572 | 0.0171 | 0.6876 | 0.0032 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 0.6133 | 0.0048 | 0.0822 | 0.0072 | 0.6504 | 0.0069 | 0.4651 | 0.0154 | 0.6986 | 0.0071 |
| degradation_aware | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 0.6308 | 0.0040 | 0.0741 | 0.0071 | 0.6635 | 0.0101 | 0.4940 | 0.0182 | 0.7021 | 0.0077 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 0.5951 | 0.0043 | 0.0780 | 0.0077 | 0.6259 | 0.0042 | 0.4660 | 0.0180 | 0.6801 | 0.0012 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 0.5978 | 0.0035 | 0.0741 | 0.0078 | 0.6241 | 0.0060 | 0.4737 | 0.0180 | 0.6825 | 0.0010 |
| degradation_aware | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 0.6011 | 0.0027 | 0.0712 | 0.0080 | 0.6260 | 0.0056 | 0.4797 | 0.0176 | 0.6887 | 0.0028 |
| degradation_aware | 100 | 1.0000 | CLEAN | clean | pooled | 0.5934 | 0.0047 | 0.0835 | 0.0078 | 0.6312 | 0.0049 | 0.4573 | 0.0149 | 0.6793 | 0.0014 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 0.6544 | 0.0072 | 0.0269 | 0.0017 | 0.6633 | 0.0075 | 0.6068 | 0.0113 | 0.6875 | 0.0077 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 0.6596 | 0.0062 | 0.0203 | 0.0028 | 0.6639 | 0.0077 | 0.6272 | 0.0065 | 0.6879 | 0.0073 |
| measurement_oriented | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 0.6596 | 0.0062 | 0.0203 | 0.0028 | 0.6639 | 0.0077 | 0.6272 | 0.0065 | 0.6879 | 0.0073 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 0.6281 | 0.0058 | 0.0626 | 0.0036 | 0.6580 | 0.0120 | 0.5201 | 0.0014 | 0.6935 | 0.0079 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 0.6422 | 0.0049 | 0.0544 | 0.0015 | 0.6671 | 0.0097 | 0.5504 | 0.0048 | 0.7013 | 0.0015 |
| measurement_oriented | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 0.6550 | 0.0008 | 0.0474 | 0.0002 | 0.6761 | 0.0044 | 0.5791 | 0.0031 | 0.7041 | 0.0030 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 0.6137 | 0.0042 | 0.0661 | 0.0046 | 0.6409 | 0.0098 | 0.5048 | 0.0008 | 0.6866 | 0.0080 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 0.6172 | 0.0036 | 0.0625 | 0.0044 | 0.6399 | 0.0084 | 0.5099 | 0.0019 | 0.6911 | 0.0078 |
| measurement_oriented | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 0.6215 | 0.0034 | 0.0602 | 0.0042 | 0.6412 | 0.0051 | 0.5185 | 0.0016 | 0.6994 | 0.0081 |
| measurement_oriented | 100 | 1.0000 | CLEAN | clean | pooled | 0.6114 | 0.0048 | 0.0704 | 0.0047 | 0.6455 | 0.0085 | 0.5008 | 0.0007 | 0.6856 | 0.0080 |

## Limitations and suspicious behaviour

Across the grid, clean B0007 FPR ranges from 21.43% to 73.81%. High baseline alarm fractions indicate transfer/aging mismatch with early training cycles; high injected recall alone does not establish useful separation.

Isolation Forest scores need not increase monotonically with perturbation magnitude. Outside training support, scores can saturate; weak sensor drift or thermal shifts can move a point toward learned nominal regions. Compare channel/sign results and paired score changes, not only pooled recall. Feature-summary injections are not natural fault labels or full physical simulations. No threshold/model is automatically frozen or deployed.

## Reproducibility and artifacts

Run `.venv/Scripts/python.exe scripts/train_nasa_isolation_forest.py`. Artifacts: `models/development/` (24 DEVELOPMENT bundles), `results/nasa_model_validation/` (copies, metrics, distributions, scores, provenance, dependency versions and hashes), `figures/nasa/model_validation/` (seven requested plots).

```json
{
  "python": "3.14.6",
  "numpy": "2.5.3",
  "pandas": "3.0.6",
  "scipy": "1.18.1",
  "scikit_learn": "1.9.1",
  "joblib": "1.6.0",
  "matplotlib": "3.11.2",
  "sha256": {
    "config\\nasa_feature_manifest.json": "ae29e5ea2168b9613d826188406cc69666a8ec7d421879145c3d75805e8edb4e",
    "config\\anomaly_injection_protocol.json": "e00a3804aee6fb67f2280f7e2818a618e2d0c48be2a7b2daf6c9d6fefbfff017",
    "config\\nasa_experiment_protocol.json": "2b06398c1f777904f95340c7c2d3023bb89b76cc7fbb117647adf1c69d8cd264",
    "config\\nasa_model_development.json": "aa948dadb5e4a69a1628782079b30a74c5ce2bd57f95d5fb19fe58c163751329",
    "data\\processed\\nasa\\B0005_discharge_features.csv": "c63d08a467c8205c30b166cff64b97ffb065439b07eae67cbb0744a28395baa9",
    "data\\processed\\nasa\\B0006_discharge_features.csv": "dae3332c2c415d2bd84f123fe3a4e1f24db193cd6ce773b86cd164d4cddf5ca6",
    "data\\processed\\nasa\\B0007_discharge_features.csv": "937c9fd8ec19fe9dc223557034e07f1f57216511a962ecb5233a16b8461152ae",
    "scripts\\train_nasa_isolation_forest.py": "7a79bf3288fac979f28aaa1d766cc4417536aa5e77b32d50e08a50eda7d491e6",
    "scripts\\nasa_development.py": "aacce3d70d3b3204c6ed0e0272201fe77043f19ba2183a373560c91d3ea43535",
    "scripts\\inject_nasa_anomalies.py": "eb0c1416316b68907ddb9432d597c751f4455db48034484a55f783e7d4a14662"
  },
  "report_generation_note": "Report-only interpretation added after fitting; original training source hashes retained.",
  "report_generator_sha256": "de4f4382b0f0ba44ed3e23c518df445d66512b7f2d4f0912e37849ab7c936fb4"
}
```
