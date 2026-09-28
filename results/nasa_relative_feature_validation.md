> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/nasa_relative_feature_validation.md`  
> **Archival SHA-256:** `a696d7966eca2e9f9a6096312c2b3075c3577546cead93b2a3c6c826e5af21dc`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# Phase 4C causal trajectory-relative feature validation

DEVELOPMENT ONLY. Only individual B0005/B0006/B0007 processed files are loaded. Original data, frozen absolute feature sets, injection protocol and previous models are preserved. No per-cell burn-in is used.

## Findings for review

58 of 72 configuration/window/threshold combinations meet <=5% clean B0007 FPR for every seed. This demonstrates improved clean transfer on this validation cell, not a final fault detector or test-cell generalization result.

In the reporting reference (100 trees, max_features=1.0), matched-cycle late-minus-early score drift changes from approximately +0.126 to +0.153 for absolute models to -0.039 to -0.014 for relative models. Drift magnitude is reduced but not eliminated; the small negative drift is also a change in score distribution.

Sensitivity trade-off: A1 is mostly absorbed by the adaptive trajectory baseline, with near-chance ranking and very low recall. A4 remains weak at eligible thresholds even where its ranking improves. A2 is much better ranked at 10/20-cycle histories, and A3 ranking improves with severity, but high PR-AUC does not imply high recall at the clean-only threshold. No configuration is chosen using these metrics.

After normalization the largest absolute robust standardized feature-median shift is below 1 (about 0.946 for duration, RELATIVE_B/prior20). This uses the full usable B0007 distribution, so it is not directly comparable with the earlier early-life-only shift audit. There are no zero-MAD windows in the clean model-eligible samples, but the prior5 current residual reaches about 1,140 from a very small nonzero local MAD; it is retained without clipping.

## Feature definition and causality

For each base feature x and k=5/10/20, baseline median and raw MAD use exactly cycles t-k through t-1 from the same cell. The current cycle is excluded. Residual=x_t-median; robust residual=residual/(1.4826*MAD+1e-9). Epsilon is 1e-9 in the base feature units, solely a zero-denominator guard; no clipping or imputation. Every prior window entry must be available. Current capacity_slope_5 itself is causal and includes the current discharge; its historical baseline excludes it. Its unstandardized residual is saved as capacity_slope_change_prior{k}_ah_per_cycle; RELATIVE_A uses the robust slope residual. No absolute values enter model features.

Relative sets are in `config/nasa_relative_feature_manifest.json`. Separate processed output is `data/processed/nasa_relative/` (504 development observations retaining all original columns).

## Training/evaluation counts

| feature_set | history_window | training_rows | per_training_cell | validation_rows |
| --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 82 | 41 | 159 |
| RELATIVE_B | 5 | 90 | 45 | 163 |
| RELATIVE_A | 10 | 72 | 36 | 154 |
| RELATIVE_B | 10 | 80 | 40 | 158 |
| RELATIVE_A | 20 | 52 | 26 | 144 |
| RELATIVE_B | 20 | 60 | 30 | 148 |

First 50 cycles per training cell define the nominal region before dropping initial history NaNs. RELATIVE_A starts at cycle k+5 because capacity_slope_5 has four initial NaNs; RELATIVE_B starts at k+1. StandardScaler and IsolationForest fit only complete nominal training features, without labels. Grid remains 100/200 trees x 0.75/1.0 max_features x seeds 42/123/2026, max_samples=auto, contamination=auto (72 models across six representations).

## Clean-only thresholds and eligibility

Higher score=-score_samples. P95/P97.5/P99 are linear percentiles of clean nominal TRAINING scores only; strict score>threshold is anomalous. These are in-sample calibration distributions, not calibrated transfer guarantees. A configuration/percentile is eligible only if clean B0007 FPR <=5% for every seed. No synthetic metric is used to choose history, feature set, model or threshold. No automatic final model/threshold.

Eligible configuration/window/percentile combinations: 58.

| feature_set | history_window | n_estimators | max_features | percentile | clean_fpr_mean | clean_fpr_std | clean_fpr_max | eligible | recommended_percentile_for_review | final_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 0.7500 | 97.5000 | 0.0189 | 0.0109 | 0.0314 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 100 | 0.7500 | 99.0000 | 0.0105 | 0.0036 | 0.0126 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 100 | 1.0000 | 97.5000 | 0.0231 | 0.0036 | 0.0252 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 100 | 1.0000 | 99.0000 | 0.0147 | 0.0036 | 0.0189 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 200 | 0.7500 | 97.5000 | 0.0210 | 0.0036 | 0.0252 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 200 | 0.7500 | 99.0000 | 0.0084 | 0.0036 | 0.0126 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 200 | 1.0000 | 97.5000 | 0.0231 | 0.0096 | 0.0314 | True | 97.5000 | nan |
| RELATIVE_A | 5 | 200 | 1.0000 | 99.0000 | 0.0126 | 0.0000 | 0.0126 | True | 97.5000 | nan |
| RELATIVE_A | 10 | 100 | 0.7500 | 95.0000 | 0.0173 | 0.0150 | 0.0260 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 100 | 0.7500 | 97.5000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 100 | 0.7500 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 100 | 1.0000 | 95.0000 | 0.0173 | 0.0037 | 0.0195 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 100 | 1.0000 | 97.5000 | 0.0022 | 0.0037 | 0.0065 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 100 | 1.0000 | 99.0000 | 0.0022 | 0.0037 | 0.0065 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 0.7500 | 95.0000 | 0.0216 | 0.0037 | 0.0260 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 0.7500 | 97.5000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 0.7500 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 1.0000 | 95.0000 | 0.0173 | 0.0075 | 0.0260 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 1.0000 | 97.5000 | 0.0022 | 0.0037 | 0.0065 | True | 95.0000 | nan |
| RELATIVE_A | 10 | 200 | 1.0000 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 0.7500 | 95.0000 | 0.0370 | 0.0040 | 0.0417 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 0.7500 | 97.5000 | 0.0347 | 0.0000 | 0.0347 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 0.7500 | 99.0000 | 0.0231 | 0.0040 | 0.0278 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 1.0000 | 95.0000 | 0.0347 | 0.0000 | 0.0347 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 1.0000 | 97.5000 | 0.0301 | 0.0040 | 0.0347 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 100 | 1.0000 | 99.0000 | 0.0162 | 0.0080 | 0.0208 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 0.7500 | 95.0000 | 0.0370 | 0.0040 | 0.0417 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 0.7500 | 97.5000 | 0.0347 | 0.0000 | 0.0347 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 0.7500 | 99.0000 | 0.0208 | 0.0000 | 0.0208 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 1.0000 | 95.0000 | 0.0324 | 0.0040 | 0.0347 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 1.0000 | 97.5000 | 0.0278 | 0.0000 | 0.0278 | True | 95.0000 | nan |
| RELATIVE_A | 20 | 200 | 1.0000 | 99.0000 | 0.0185 | 0.0040 | 0.0208 | True | 95.0000 | nan |
| RELATIVE_B | 5 | 100 | 1.0000 | 99.0000 | 0.0409 | 0.0071 | 0.0491 | True | 99.0000 | nan |
| RELATIVE_B | 5 | 200 | 0.7500 | 99.0000 | 0.0266 | 0.0154 | 0.0429 | True | 99.0000 | nan |
| RELATIVE_B | 5 | 200 | 1.0000 | 99.0000 | 0.0266 | 0.0094 | 0.0368 | True | 99.0000 | nan |
| RELATIVE_B | 10 | 100 | 0.7500 | 97.5000 | 0.0105 | 0.0037 | 0.0127 | True | 97.5000 | nan |
| RELATIVE_B | 10 | 100 | 0.7500 | 99.0000 | 0.0063 | 0.0063 | 0.0127 | True | 97.5000 | nan |
| RELATIVE_B | 10 | 100 | 1.0000 | 95.0000 | 0.0253 | 0.0110 | 0.0380 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 100 | 1.0000 | 97.5000 | 0.0169 | 0.0037 | 0.0190 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 100 | 1.0000 | 99.0000 | 0.0042 | 0.0037 | 0.0063 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 0.7500 | 95.0000 | 0.0295 | 0.0037 | 0.0316 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 0.7500 | 97.5000 | 0.0127 | 0.0000 | 0.0127 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 0.7500 | 99.0000 | 0.0042 | 0.0037 | 0.0063 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 1.0000 | 95.0000 | 0.0253 | 0.0000 | 0.0253 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 1.0000 | 97.5000 | 0.0127 | 0.0063 | 0.0190 | True | 95.0000 | nan |
| RELATIVE_B | 10 | 200 | 1.0000 | 99.0000 | 0.0042 | 0.0037 | 0.0063 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 0.7500 | 95.0000 | 0.0158 | 0.0078 | 0.0203 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 0.7500 | 97.5000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 0.7500 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 1.0000 | 95.0000 | 0.0113 | 0.0078 | 0.0203 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 1.0000 | 97.5000 | 0.0023 | 0.0039 | 0.0068 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 100 | 1.0000 | 99.0000 | 0.0023 | 0.0039 | 0.0068 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 0.7500 | 95.0000 | 0.0203 | 0.0068 | 0.0270 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 0.7500 | 97.5000 | 0.0068 | 0.0068 | 0.0135 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 0.7500 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 1.0000 | 95.0000 | 0.0180 | 0.0039 | 0.0203 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 1.0000 | 97.5000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |
| RELATIVE_B | 20 | 200 | 1.0000 | 99.0000 | 0.0000 | 0.0000 | 0.0000 | True | 95.0000 | nan |

### Predeclared display reference: 100 trees, max_features=1.0

| feature_set | history_window | n_estimators | max_features | percentile | threshold_mean | threshold_std | clean_fpr_mean | clean_fpr_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 1.0000 | 95.0000 | 0.5623 | 0.0140 | 0.0629 | 0.0218 |
| RELATIVE_A | 5 | 100 | 1.0000 | 97.5000 | 0.6226 | 0.0098 | 0.0231 | 0.0036 |
| RELATIVE_A | 5 | 100 | 1.0000 | 99.0000 | 0.6421 | 0.0088 | 0.0147 | 0.0036 |
| RELATIVE_A | 10 | 100 | 1.0000 | 95.0000 | 0.5832 | 0.0171 | 0.0173 | 0.0037 |
| RELATIVE_A | 10 | 100 | 1.0000 | 97.5000 | 0.6176 | 0.0012 | 0.0022 | 0.0037 |
| RELATIVE_A | 10 | 100 | 1.0000 | 99.0000 | 0.6272 | 0.0062 | 0.0022 | 0.0037 |
| RELATIVE_A | 20 | 100 | 1.0000 | 95.0000 | 0.5606 | 0.0073 | 0.0347 | 0.0000 |
| RELATIVE_A | 20 | 100 | 1.0000 | 97.5000 | 0.5727 | 0.0045 | 0.0301 | 0.0040 |
| RELATIVE_A | 20 | 100 | 1.0000 | 99.0000 | 0.6181 | 0.0028 | 0.0162 | 0.0080 |
| RELATIVE_B | 5 | 100 | 1.0000 | 95.0000 | 0.5476 | 0.0032 | 0.0695 | 0.0154 |
| RELATIVE_B | 5 | 100 | 1.0000 | 97.5000 | 0.5689 | 0.0009 | 0.0470 | 0.0071 |
| RELATIVE_B | 5 | 100 | 1.0000 | 99.0000 | 0.5888 | 0.0080 | 0.0409 | 0.0071 |
| RELATIVE_B | 10 | 100 | 1.0000 | 95.0000 | 0.5479 | 0.0095 | 0.0253 | 0.0110 |
| RELATIVE_B | 10 | 100 | 1.0000 | 97.5000 | 0.5929 | 0.0066 | 0.0169 | 0.0037 |
| RELATIVE_B | 10 | 100 | 1.0000 | 99.0000 | 0.6218 | 0.0101 | 0.0042 | 0.0037 |
| RELATIVE_B | 20 | 100 | 1.0000 | 95.0000 | 0.5582 | 0.0057 | 0.0113 | 0.0078 |
| RELATIVE_B | 20 | 100 | 1.0000 | 97.5000 | 0.5749 | 0.0052 | 0.0023 | 0.0039 |
| RELATIVE_B | 20 | 100 | 1.0000 | 99.0000 | 0.5858 | 0.0080 | 0.0023 | 0.0039 |

### Full-grid seed means and sample SD

| feature_set | history_window | n_estimators | max_features | percentile | threshold_mean | threshold_std | clean_fpr_mean | clean_fpr_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 0.7500 | 95.0000 | 0.5544 | 0.0156 | 0.0671 | 0.0096 |
| RELATIVE_A | 5 | 100 | 0.7500 | 97.5000 | 0.6136 | 0.0242 | 0.0189 | 0.0109 |
| RELATIVE_A | 5 | 100 | 0.7500 | 99.0000 | 0.6365 | 0.0090 | 0.0105 | 0.0036 |
| RELATIVE_A | 5 | 100 | 1.0000 | 95.0000 | 0.5623 | 0.0140 | 0.0629 | 0.0218 |
| RELATIVE_A | 5 | 100 | 1.0000 | 97.5000 | 0.6226 | 0.0098 | 0.0231 | 0.0036 |
| RELATIVE_A | 5 | 100 | 1.0000 | 99.0000 | 0.6421 | 0.0088 | 0.0147 | 0.0036 |
| RELATIVE_A | 5 | 200 | 0.7500 | 95.0000 | 0.5521 | 0.0132 | 0.0692 | 0.0126 |
| RELATIVE_A | 5 | 200 | 0.7500 | 97.5000 | 0.6174 | 0.0183 | 0.0210 | 0.0036 |
| RELATIVE_A | 5 | 200 | 0.7500 | 99.0000 | 0.6380 | 0.0040 | 0.0084 | 0.0036 |
| RELATIVE_A | 5 | 200 | 1.0000 | 95.0000 | 0.5621 | 0.0060 | 0.0566 | 0.0000 |
| RELATIVE_A | 5 | 200 | 1.0000 | 97.5000 | 0.6222 | 0.0084 | 0.0231 | 0.0096 |
| RELATIVE_A | 5 | 200 | 1.0000 | 99.0000 | 0.6400 | 0.0031 | 0.0126 | 0.0000 |
| RELATIVE_A | 10 | 100 | 0.7500 | 95.0000 | 0.5766 | 0.0245 | 0.0173 | 0.0150 |
| RELATIVE_A | 10 | 100 | 0.7500 | 97.5000 | 0.6182 | 0.0064 | 0.0000 | 0.0000 |
| RELATIVE_A | 10 | 100 | 0.7500 | 99.0000 | 0.6346 | 0.0083 | 0.0000 | 0.0000 |
| RELATIVE_A | 10 | 100 | 1.0000 | 95.0000 | 0.5832 | 0.0171 | 0.0173 | 0.0037 |
| RELATIVE_A | 10 | 100 | 1.0000 | 97.5000 | 0.6176 | 0.0012 | 0.0022 | 0.0037 |
| RELATIVE_A | 10 | 100 | 1.0000 | 99.0000 | 0.6272 | 0.0062 | 0.0022 | 0.0037 |
| RELATIVE_A | 10 | 200 | 0.7500 | 95.0000 | 0.5677 | 0.0090 | 0.0216 | 0.0037 |
| RELATIVE_A | 10 | 200 | 0.7500 | 97.5000 | 0.6201 | 0.0053 | 0.0000 | 0.0000 |
| RELATIVE_A | 10 | 200 | 0.7500 | 99.0000 | 0.6240 | 0.0038 | 0.0000 | 0.0000 |
| RELATIVE_A | 10 | 200 | 1.0000 | 95.0000 | 0.5782 | 0.0112 | 0.0173 | 0.0075 |
| RELATIVE_A | 10 | 200 | 1.0000 | 97.5000 | 0.6150 | 0.0030 | 0.0022 | 0.0037 |
| RELATIVE_A | 10 | 200 | 1.0000 | 99.0000 | 0.6225 | 0.0057 | 0.0000 | 0.0000 |
| RELATIVE_A | 20 | 100 | 0.7500 | 95.0000 | 0.5602 | 0.0072 | 0.0370 | 0.0040 |
| RELATIVE_A | 20 | 100 | 0.7500 | 97.5000 | 0.5665 | 0.0067 | 0.0347 | 0.0000 |
| RELATIVE_A | 20 | 100 | 0.7500 | 99.0000 | 0.6066 | 0.0010 | 0.0231 | 0.0040 |
| RELATIVE_A | 20 | 100 | 1.0000 | 95.0000 | 0.5606 | 0.0073 | 0.0347 | 0.0000 |
| RELATIVE_A | 20 | 100 | 1.0000 | 97.5000 | 0.5727 | 0.0045 | 0.0301 | 0.0040 |
| RELATIVE_A | 20 | 100 | 1.0000 | 99.0000 | 0.6181 | 0.0028 | 0.0162 | 0.0080 |
| RELATIVE_A | 20 | 200 | 0.7500 | 95.0000 | 0.5599 | 0.0058 | 0.0370 | 0.0040 |
| RELATIVE_A | 20 | 200 | 0.7500 | 97.5000 | 0.5670 | 0.0051 | 0.0347 | 0.0000 |
| RELATIVE_A | 20 | 200 | 0.7500 | 99.0000 | 0.6086 | 0.0022 | 0.0208 | 0.0000 |
| RELATIVE_A | 20 | 200 | 1.0000 | 95.0000 | 0.5614 | 0.0123 | 0.0324 | 0.0040 |
| RELATIVE_A | 20 | 200 | 1.0000 | 97.5000 | 0.5712 | 0.0142 | 0.0278 | 0.0000 |
| RELATIVE_A | 20 | 200 | 1.0000 | 99.0000 | 0.6172 | 0.0065 | 0.0185 | 0.0040 |
| RELATIVE_B | 5 | 100 | 0.7500 | 95.0000 | 0.5412 | 0.0032 | 0.0818 | 0.0094 |
| RELATIVE_B | 5 | 100 | 0.7500 | 97.5000 | 0.5595 | 0.0051 | 0.0532 | 0.0142 |
| RELATIVE_B | 5 | 100 | 0.7500 | 99.0000 | 0.5769 | 0.0181 | 0.0409 | 0.0154 |
| RELATIVE_B | 5 | 100 | 1.0000 | 95.0000 | 0.5476 | 0.0032 | 0.0695 | 0.0154 |
| RELATIVE_B | 5 | 100 | 1.0000 | 97.5000 | 0.5689 | 0.0009 | 0.0470 | 0.0071 |
| RELATIVE_B | 5 | 100 | 1.0000 | 99.0000 | 0.5888 | 0.0080 | 0.0409 | 0.0071 |
| RELATIVE_B | 5 | 200 | 0.7500 | 95.0000 | 0.5372 | 0.0024 | 0.0818 | 0.0035 |
| RELATIVE_B | 5 | 200 | 0.7500 | 97.5000 | 0.5584 | 0.0095 | 0.0552 | 0.0106 |
| RELATIVE_B | 5 | 200 | 0.7500 | 99.0000 | 0.5904 | 0.0168 | 0.0266 | 0.0154 |
| RELATIVE_B | 5 | 200 | 1.0000 | 95.0000 | 0.5461 | 0.0069 | 0.0838 | 0.0154 |
| RELATIVE_B | 5 | 200 | 1.0000 | 97.5000 | 0.5646 | 0.0060 | 0.0532 | 0.0128 |
| RELATIVE_B | 5 | 200 | 1.0000 | 99.0000 | 0.5977 | 0.0051 | 0.0266 | 0.0094 |
| RELATIVE_B | 10 | 100 | 0.7500 | 95.0000 | 0.5405 | 0.0042 | 0.0295 | 0.0183 |
| RELATIVE_B | 10 | 100 | 0.7500 | 97.5000 | 0.5802 | 0.0132 | 0.0105 | 0.0037 |
| RELATIVE_B | 10 | 100 | 0.7500 | 99.0000 | 0.6080 | 0.0069 | 0.0063 | 0.0063 |
| RELATIVE_B | 10 | 100 | 1.0000 | 95.0000 | 0.5479 | 0.0095 | 0.0253 | 0.0110 |
| RELATIVE_B | 10 | 100 | 1.0000 | 97.5000 | 0.5929 | 0.0066 | 0.0169 | 0.0037 |
| RELATIVE_B | 10 | 100 | 1.0000 | 99.0000 | 0.6218 | 0.0101 | 0.0042 | 0.0037 |
| RELATIVE_B | 10 | 200 | 0.7500 | 95.0000 | 0.5385 | 0.0045 | 0.0295 | 0.0037 |
| RELATIVE_B | 10 | 200 | 0.7500 | 97.5000 | 0.5863 | 0.0074 | 0.0127 | 0.0000 |
| RELATIVE_B | 10 | 200 | 0.7500 | 99.0000 | 0.6149 | 0.0022 | 0.0042 | 0.0037 |
| RELATIVE_B | 10 | 200 | 1.0000 | 95.0000 | 0.5506 | 0.0054 | 0.0253 | 0.0000 |
| RELATIVE_B | 10 | 200 | 1.0000 | 97.5000 | 0.5999 | 0.0118 | 0.0127 | 0.0063 |
| RELATIVE_B | 10 | 200 | 1.0000 | 99.0000 | 0.6241 | 0.0064 | 0.0042 | 0.0037 |
| RELATIVE_B | 20 | 100 | 0.7500 | 95.0000 | 0.5532 | 0.0041 | 0.0158 | 0.0078 |
| RELATIVE_B | 20 | 100 | 0.7500 | 97.5000 | 0.5768 | 0.0075 | 0.0000 | 0.0000 |
| RELATIVE_B | 20 | 100 | 0.7500 | 99.0000 | 0.5928 | 0.0098 | 0.0000 | 0.0000 |
| RELATIVE_B | 20 | 100 | 1.0000 | 95.0000 | 0.5582 | 0.0057 | 0.0113 | 0.0078 |
| RELATIVE_B | 20 | 100 | 1.0000 | 97.5000 | 0.5749 | 0.0052 | 0.0023 | 0.0039 |
| RELATIVE_B | 20 | 100 | 1.0000 | 99.0000 | 0.5858 | 0.0080 | 0.0023 | 0.0039 |
| RELATIVE_B | 20 | 200 | 0.7500 | 95.0000 | 0.5536 | 0.0066 | 0.0203 | 0.0068 |
| RELATIVE_B | 20 | 200 | 0.7500 | 97.5000 | 0.5722 | 0.0063 | 0.0068 | 0.0068 |
| RELATIVE_B | 20 | 200 | 0.7500 | 99.0000 | 0.5904 | 0.0040 | 0.0000 | 0.0000 |
| RELATIVE_B | 20 | 200 | 1.0000 | 95.0000 | 0.5516 | 0.0030 | 0.0180 | 0.0039 |
| RELATIVE_B | 20 | 200 | 1.0000 | 97.5000 | 0.5800 | 0.0022 | 0.0000 | 0.0000 |
| RELATIVE_B | 20 | 200 | 1.0000 | 99.0000 | 0.5869 | 0.0091 | 0.0000 | 0.0000 |

## Early-to-late clean score drift

Early=usable cycles <=50; late=cycles >50. Absolute counterparts are compared on exactly the same usable cycles per history window and seed/configuration. For RELATIVE_B the absolute measurement-oriented set includes start_temp while relative B does not (as requested), so this is not a perfectly controlled change-of-representation ablation. Score scales differ across models; compare within-model late-minus-early changes, not raw score levels as calibrated probabilities. Shorter trajectories and different nominal sample sizes can also affect models.

| feature_set | history_window | n_estimators | max_features | representation | early_mean_mean | early_mean_std | late_mean_mean | late_mean_std | late_minus_early_mean | late_minus_early_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 1.0000 | absolute_matched_cycles | 0.4816 | 0.0160 | 0.6347 | 0.0007 | 0.1531 | 0.0155 |
| RELATIVE_A | 5 | 100 | 1.0000 | relative | 0.3976 | 0.0037 | 0.3625 | 0.0041 | -0.0351 | 0.0038 |
| RELATIVE_A | 10 | 100 | 1.0000 | absolute_matched_cycles | 0.4833 | 0.0173 | 0.6347 | 0.0007 | 0.1514 | 0.0168 |
| RELATIVE_A | 10 | 100 | 1.0000 | relative | 0.4171 | 0.0039 | 0.3842 | 0.0011 | -0.0329 | 0.0042 |
| RELATIVE_A | 20 | 100 | 1.0000 | absolute_matched_cycles | 0.4830 | 0.0184 | 0.6347 | 0.0007 | 0.1517 | 0.0179 |
| RELATIVE_A | 20 | 100 | 1.0000 | relative | 0.4668 | 0.0009 | 0.4398 | 0.0021 | -0.0270 | 0.0023 |
| RELATIVE_B | 5 | 100 | 1.0000 | absolute_matched_cycles | 0.5208 | 0.0034 | 0.6466 | 0.0064 | 0.1258 | 0.0067 |
| RELATIVE_B | 5 | 100 | 1.0000 | relative | 0.4044 | 0.0014 | 0.3653 | 0.0021 | -0.0391 | 0.0030 |
| RELATIVE_B | 10 | 100 | 1.0000 | absolute_matched_cycles | 0.5181 | 0.0023 | 0.6466 | 0.0064 | 0.1285 | 0.0063 |
| RELATIVE_B | 10 | 100 | 1.0000 | relative | 0.4153 | 0.0042 | 0.3923 | 0.0050 | -0.0230 | 0.0016 |
| RELATIVE_B | 20 | 100 | 1.0000 | absolute_matched_cycles | 0.5207 | 0.0038 | 0.6466 | 0.0064 | 0.1258 | 0.0052 |
| RELATIVE_B | 20 | 100 | 1.0000 | relative | 0.4400 | 0.0046 | 0.4264 | 0.0014 | -0.0137 | 0.0057 |

Full matched-cycle drift comparisons: score_drift.csv and score_drift_seed_stability.csv.

## Cross-cell shift after normalization

Training nominal distribution versus ALL usable clean B0007, not only early B0007. Raw training MAD defines standardized median shift; zero MAD produces NaN. Complete-case eligibility is feature-set-specific.

| feature_set | history_window | feature | training_median | validation_median | training_MAD | validation_MAD | median_shift | standardized_shift | absolute_standardized_shift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | mean_temp_c_prior5_robust_residual | -0.5063 | -0.1315 | 0.9170 | 1.1268 | 0.3748 | 0.4087 | 0.4087 |
| RELATIVE_A | 5 | mean_voltage_v_prior5_robust_residual | -0.4029 | -0.9110 | 1.3980 | 1.1650 | -0.5080 | -0.3634 | 0.3634 |
| RELATIVE_A | 5 | time_to_3_4v_s_prior5_robust_residual | -1.2354 | -1.3187 | 0.8330 | 0.7465 | -0.0834 | -0.1001 | 0.1001 |
| RELATIVE_A | 5 | capacity_retention_prior5_robust_residual | -1.2845 | -1.3736 | 0.9690 | 0.6975 | -0.0891 | -0.0920 | 0.0920 |
| RELATIVE_A | 5 | duration_s_prior5_robust_residual | -1.3068 | -1.3789 | 0.8732 | 0.6991 | -0.0721 | -0.0825 | 0.0825 |
| RELATIVE_A | 5 | capacity_slope_5_prior5_robust_residual | 0.1918 | 0.3075 | 1.7154 | 1.1234 | 0.1156 | 0.0674 | 0.0674 |
| RELATIVE_A | 5 | delta_temp_c_prior5_robust_residual | 0.5069 | 0.4674 | 1.2343 | 1.0981 | -0.0396 | -0.0321 | 0.0321 |
| RELATIVE_A | 10 | duration_s_prior10_robust_residual | -0.9535 | -1.3047 | 0.6586 | 0.4169 | -0.3512 | -0.5334 | 0.5334 |
| RELATIVE_A | 10 | capacity_retention_prior10_robust_residual | -0.9138 | -1.2884 | 0.7245 | 0.2938 | -0.3747 | -0.5172 | 0.5172 |
| RELATIVE_A | 10 | mean_temp_c_prior10_robust_residual | -0.4643 | 0.1593 | 1.2612 | 1.0344 | 0.6237 | 0.4945 | 0.4945 |
| RELATIVE_A | 10 | mean_voltage_v_prior10_robust_residual | -0.6325 | -0.9793 | 1.1384 | 0.6929 | -0.3468 | -0.3046 | 0.3046 |
| RELATIVE_A | 10 | delta_temp_c_prior10_robust_residual | 0.6457 | 0.3658 | 1.0367 | 0.8846 | -0.2799 | -0.2700 | 0.2700 |
| RELATIVE_A | 10 | time_to_3_4v_s_prior10_robust_residual | -1.1517 | -1.2620 | 0.8115 | 0.3807 | -0.1102 | -0.1359 | 0.1359 |
| RELATIVE_A | 10 | capacity_slope_5_prior10_robust_residual | 0.3052 | 0.2228 | 1.4063 | 0.8770 | -0.0824 | -0.0586 | 0.0586 |
| RELATIVE_A | 20 | mean_temp_c_prior20_robust_residual | -0.4938 | 0.2790 | 1.0936 | 0.9565 | 0.7728 | 0.7066 | 0.7066 |
| RELATIVE_A | 20 | duration_s_prior20_robust_residual | -1.2060 | -1.4050 | 0.3396 | 0.2869 | -0.1989 | -0.5859 | 0.5859 |
| RELATIVE_A | 20 | delta_temp_c_prior20_robust_residual | 0.9839 | 0.5355 | 1.2041 | 0.7842 | -0.4485 | -0.3724 | 0.3724 |
| RELATIVE_A | 20 | capacity_slope_5_prior20_robust_residual | -0.0788 | 0.0694 | 0.8417 | 0.6821 | 0.1482 | 0.1761 | 0.1761 |
| RELATIVE_A | 20 | mean_voltage_v_prior20_robust_residual | -1.0310 | -1.2022 | 1.0671 | 0.5183 | -0.1712 | -0.1604 | 0.1604 |
| RELATIVE_A | 20 | capacity_retention_prior20_robust_residual | -1.3361 | -1.3863 | 0.5501 | 0.3414 | -0.0502 | -0.0913 | 0.0913 |
| RELATIVE_A | 20 | time_to_3_4v_s_prior20_robust_residual | -1.3698 | -1.3866 | 0.5975 | 0.3462 | -0.0168 | -0.0281 | 0.0281 |
| RELATIVE_B | 5 | mean_temp_c_prior5_robust_residual | -0.5445 | -0.1633 | 0.7889 | 1.1056 | 0.3812 | 0.4832 | 0.4832 |
| RELATIVE_B | 5 | mean_voltage_v_prior5_robust_residual | -0.2736 | -0.8511 | 1.3099 | 1.2053 | -0.5776 | -0.4409 | 0.4409 |
| RELATIVE_B | 5 | max_temp_c_prior5_robust_residual | -0.1707 | 0.1472 | 1.0728 | 1.1605 | 0.3179 | 0.2963 | 0.2963 |
| RELATIVE_B | 5 | mean_current_a_prior5_robust_residual | 0.3694 | 0.8400 | 1.8802 | 2.0442 | 0.4706 | 0.2503 | 0.2503 |
| RELATIVE_B | 5 | time_to_3_4v_s_prior5_robust_residual | -1.1769 | -1.3128 | 1.0533 | 0.7804 | -0.1358 | -0.1290 | 0.1290 |
| RELATIVE_B | 5 | delta_temp_c_prior5_robust_residual | 0.5069 | 0.4046 | 1.2239 | 1.1326 | -0.1024 | -0.0836 | 0.0836 |
| RELATIVE_B | 5 | duration_s_prior5_robust_residual | -1.3068 | -1.3789 | 0.9675 | 0.7093 | -0.0721 | -0.0745 | 0.0745 |
| RELATIVE_B | 10 | mean_temp_c_prior10_robust_residual | -0.4786 | 0.1114 | 1.2154 | 1.0290 | 0.5900 | 0.4854 | 0.4854 |
| RELATIVE_B | 10 | duration_s_prior10_robust_residual | -1.0033 | -1.3196 | 0.6679 | 0.4308 | -0.3163 | -0.4736 | 0.4736 |
| RELATIVE_B | 10 | mean_voltage_v_prior10_robust_residual | -0.4795 | -0.9580 | 1.1938 | 0.7267 | -0.4785 | -0.4008 | 0.4008 |
| RELATIVE_B | 10 | max_temp_c_prior10_robust_residual | -0.2480 | 0.1509 | 1.0723 | 0.9242 | 0.3989 | 0.3720 | 0.3720 |
| RELATIVE_B | 10 | mean_current_a_prior10_robust_residual | 0.5198 | 0.7717 | 1.0552 | 0.7575 | 0.2520 | 0.2388 | 0.2388 |
| RELATIVE_B | 10 | delta_temp_c_prior10_robust_residual | 0.5519 | 0.3658 | 1.1399 | 0.8781 | -0.1861 | -0.1633 | 0.1633 |
| RELATIVE_B | 10 | time_to_3_4v_s_prior10_robust_residual | -1.1517 | -1.2706 | 0.8278 | 0.3932 | -0.1189 | -0.1436 | 0.1436 |
| RELATIVE_B | 20 | duration_s_prior20_robust_residual | -0.9322 | -1.3989 | 0.4932 | 0.3042 | -0.4667 | -0.9462 | 0.9462 |
| RELATIVE_B | 20 | mean_temp_c_prior20_robust_residual | -0.7466 | 0.2496 | 1.1398 | 0.9661 | 0.9963 | 0.8741 | 0.8741 |
| RELATIVE_B | 20 | mean_current_a_prior20_robust_residual | 0.1079 | 0.8908 | 1.1339 | 0.6608 | 0.7828 | 0.6904 | 0.6904 |
| RELATIVE_B | 20 | mean_voltage_v_prior20_robust_residual | -0.7671 | -1.1939 | 1.0489 | 0.5504 | -0.4267 | -0.4068 | 0.4068 |
| RELATIVE_B | 20 | max_temp_c_prior20_robust_residual | -0.2503 | 0.3973 | 2.1879 | 1.1230 | 0.6476 | 0.2960 | 0.2960 |
| RELATIVE_B | 20 | delta_temp_c_prior20_robust_residual | 0.7937 | 0.5094 | 1.2152 | 0.8007 | -0.2843 | -0.2340 | 0.2340 |
| RELATIVE_B | 20 | time_to_3_4v_s_prior20_robust_residual | -1.2516 | -1.3662 | 0.7546 | 0.3637 | -0.1146 | -0.1519 | 0.1519 |

## Numerical diagnostics

Zero local MAD can create extreme robust residuals because epsilon is not a statistically meaningful scale floor. These values are not clipped; denominator_diagnostics.csv reports affected counts and maxima. This limitation can distort StandardScaler and is not silently corrected using validation labels.

| feature_set | history_window | feature | region | zero_history_mad | max_absolute_robust_residual |
| --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | capacity_retention_prior5_robust_residual | training | 0 | 166.8293 |
| RELATIVE_A | 5 | capacity_retention_prior5_robust_residual | B0007 | 0 | 208.5249 |
| RELATIVE_A | 5 | capacity_slope_5_prior5_robust_residual | training | 0 | 247.5327 |
| RELATIVE_A | 5 | capacity_slope_5_prior5_robust_residual | B0007 | 0 | 300.9221 |
| RELATIVE_A | 5 | duration_s_prior5_robust_residual | training | 0 | 23.9564 |
| RELATIVE_A | 5 | duration_s_prior5_robust_residual | B0007 | 0 | 296.1123 |
| RELATIVE_A | 5 | time_to_3_4v_s_prior5_robust_residual | training | 0 | 47.3265 |
| RELATIVE_A | 5 | time_to_3_4v_s_prior5_robust_residual | B0007 | 0 | 269.7329 |
| RELATIVE_A | 5 | mean_voltage_v_prior5_robust_residual | training | 0 | 45.6290 |
| RELATIVE_A | 5 | mean_voltage_v_prior5_robust_residual | B0007 | 0 | 25.4588 |
| RELATIVE_A | 5 | mean_temp_c_prior5_robust_residual | training | 0 | 48.4919 |
| RELATIVE_A | 5 | mean_temp_c_prior5_robust_residual | B0007 | 0 | 38.4956 |
| RELATIVE_A | 5 | delta_temp_c_prior5_robust_residual | training | 0 | 20.0266 |
| RELATIVE_A | 5 | delta_temp_c_prior5_robust_residual | B0007 | 0 | 20.7795 |
| RELATIVE_B | 5 | duration_s_prior5_robust_residual | training | 0 | 36.3821 |
| RELATIVE_B | 5 | duration_s_prior5_robust_residual | B0007 | 0 | 296.1123 |
| RELATIVE_B | 5 | time_to_3_4v_s_prior5_robust_residual | training | 0 | 47.3265 |
| RELATIVE_B | 5 | time_to_3_4v_s_prior5_robust_residual | B0007 | 0 | 269.7329 |
| RELATIVE_B | 5 | mean_voltage_v_prior5_robust_residual | training | 0 | 45.6290 |
| RELATIVE_B | 5 | mean_voltage_v_prior5_robust_residual | B0007 | 0 | 25.4588 |
| RELATIVE_B | 5 | mean_current_a_prior5_robust_residual | training | 0 | 63.8575 |
| RELATIVE_B | 5 | mean_current_a_prior5_robust_residual | B0007 | 0 | 1139.9277 |
| RELATIVE_B | 5 | mean_temp_c_prior5_robust_residual | training | 0 | 48.4919 |
| RELATIVE_B | 5 | mean_temp_c_prior5_robust_residual | B0007 | 0 | 38.4956 |
| RELATIVE_B | 5 | max_temp_c_prior5_robust_residual | training | 0 | 31.6102 |
| RELATIVE_B | 5 | max_temp_c_prior5_robust_residual | B0007 | 0 | 36.3111 |
| RELATIVE_B | 5 | delta_temp_c_prior5_robust_residual | training | 0 | 20.0266 |
| RELATIVE_B | 5 | delta_temp_c_prior5_robust_residual | B0007 | 0 | 20.7795 |
| RELATIVE_A | 10 | capacity_retention_prior10_robust_residual | training | 0 | 4.6623 |
| RELATIVE_A | 10 | capacity_retention_prior10_robust_residual | B0007 | 0 | 5.5974 |
| RELATIVE_A | 10 | capacity_slope_5_prior10_robust_residual | training | 0 | 241.3453 |
| RELATIVE_A | 10 | capacity_slope_5_prior10_robust_residual | B0007 | 0 | 42.9305 |
| RELATIVE_A | 10 | duration_s_prior10_robust_residual | training | 0 | 3.9213 |
| RELATIVE_A | 10 | duration_s_prior10_robust_residual | B0007 | 0 | 7.5079 |
| RELATIVE_A | 10 | time_to_3_4v_s_prior10_robust_residual | training | 0 | 9.1135 |
| RELATIVE_A | 10 | time_to_3_4v_s_prior10_robust_residual | B0007 | 0 | 6.1799 |
| RELATIVE_A | 10 | mean_voltage_v_prior10_robust_residual | training | 0 | 5.6068 |
| RELATIVE_A | 10 | mean_voltage_v_prior10_robust_residual | B0007 | 0 | 6.1144 |
| RELATIVE_A | 10 | mean_temp_c_prior10_robust_residual | training | 0 | 9.4599 |
| RELATIVE_A | 10 | mean_temp_c_prior10_robust_residual | B0007 | 0 | 11.0682 |
| RELATIVE_A | 10 | delta_temp_c_prior10_robust_residual | training | 0 | 9.7157 |
| RELATIVE_A | 10 | delta_temp_c_prior10_robust_residual | B0007 | 0 | 11.6999 |
| RELATIVE_B | 10 | duration_s_prior10_robust_residual | training | 0 | 3.9213 |
| RELATIVE_B | 10 | duration_s_prior10_robust_residual | B0007 | 0 | 7.5079 |
| RELATIVE_B | 10 | time_to_3_4v_s_prior10_robust_residual | training | 0 | 9.1135 |
| RELATIVE_B | 10 | time_to_3_4v_s_prior10_robust_residual | B0007 | 0 | 6.1799 |
| RELATIVE_B | 10 | mean_voltage_v_prior10_robust_residual | training | 0 | 5.6068 |
| RELATIVE_B | 10 | mean_voltage_v_prior10_robust_residual | B0007 | 0 | 6.1144 |
| RELATIVE_B | 10 | mean_current_a_prior10_robust_residual | training | 0 | 45.2604 |
| RELATIVE_B | 10 | mean_current_a_prior10_robust_residual | B0007 | 0 | 141.4048 |
| RELATIVE_B | 10 | mean_temp_c_prior10_robust_residual | training | 0 | 9.4599 |
| RELATIVE_B | 10 | mean_temp_c_prior10_robust_residual | B0007 | 0 | 11.0682 |
| RELATIVE_B | 10 | max_temp_c_prior10_robust_residual | training | 0 | 18.2202 |
| RELATIVE_B | 10 | max_temp_c_prior10_robust_residual | B0007 | 0 | 15.9485 |
| RELATIVE_B | 10 | delta_temp_c_prior10_robust_residual | training | 0 | 9.7157 |
| RELATIVE_B | 10 | delta_temp_c_prior10_robust_residual | B0007 | 0 | 11.6999 |
| RELATIVE_A | 20 | capacity_retention_prior20_robust_residual | training | 0 | 2.6636 |
| RELATIVE_A | 20 | capacity_retention_prior20_robust_residual | B0007 | 0 | 3.0091 |
| RELATIVE_A | 20 | capacity_slope_5_prior20_robust_residual | training | 0 | 7.0717 |
| RELATIVE_A | 20 | capacity_slope_5_prior20_robust_residual | B0007 | 0 | 15.0282 |
| RELATIVE_A | 20 | duration_s_prior20_robust_residual | training | 0 | 2.0752 |
| RELATIVE_A | 20 | duration_s_prior20_robust_residual | B0007 | 0 | 2.5803 |
| RELATIVE_A | 20 | time_to_3_4v_s_prior20_robust_residual | training | 0 | 2.7360 |
| RELATIVE_A | 20 | time_to_3_4v_s_prior20_robust_residual | B0007 | 0 | 2.5755 |
| RELATIVE_A | 20 | mean_voltage_v_prior20_robust_residual | training | 0 | 4.0296 |
| RELATIVE_A | 20 | mean_voltage_v_prior20_robust_residual | B0007 | 0 | 3.9199 |
| RELATIVE_A | 20 | mean_temp_c_prior20_robust_residual | training | 0 | 10.0071 |
| RELATIVE_A | 20 | mean_temp_c_prior20_robust_residual | B0007 | 0 | 7.4176 |
| RELATIVE_A | 20 | delta_temp_c_prior20_robust_residual | training | 0 | 3.7998 |
| RELATIVE_A | 20 | delta_temp_c_prior20_robust_residual | B0007 | 0 | 4.9209 |
| RELATIVE_B | 20 | duration_s_prior20_robust_residual | training | 0 | 2.0752 |
| RELATIVE_B | 20 | duration_s_prior20_robust_residual | B0007 | 0 | 2.5803 |
| RELATIVE_B | 20 | time_to_3_4v_s_prior20_robust_residual | training | 0 | 2.7360 |
| RELATIVE_B | 20 | time_to_3_4v_s_prior20_robust_residual | B0007 | 0 | 2.5755 |
| RELATIVE_B | 20 | mean_voltage_v_prior20_robust_residual | training | 0 | 4.0296 |
| RELATIVE_B | 20 | mean_voltage_v_prior20_robust_residual | B0007 | 0 | 3.9199 |
| RELATIVE_B | 20 | mean_current_a_prior20_robust_residual | training | 0 | 84.8589 |
| RELATIVE_B | 20 | mean_current_a_prior20_robust_residual | B0007 | 0 | 93.6945 |
| RELATIVE_B | 20 | mean_temp_c_prior20_robust_residual | training | 0 | 10.0071 |
| RELATIVE_B | 20 | mean_temp_c_prior20_robust_residual | B0007 | 0 | 7.4176 |
| RELATIVE_B | 20 | max_temp_c_prior20_robust_residual | training | 0 | 12.8529 |
| RELATIVE_B | 20 | max_temp_c_prior20_robust_residual | B0007 | 0 | 6.3352 |
| RELATIVE_B | 20 | delta_temp_c_prior20_robust_residual | training | 0 | 6.9210 |
| RELATIVE_B | 20 | delta_temp_c_prior20_robust_residual | B0007 | 0 | 4.9209 |

## Training and clean validation score distributions

| feature_set | history_window | n_estimators | max_features | seed | region | count | score_mean | score_std | score_min | score_p05 | score_median | score_p95 | score_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 0.7500 | 42 | training | 82 | 0.3756 | 0.0809 | 0.3041 | 0.3084 | 0.3460 | 0.5679 | 0.6520 |
| RELATIVE_A | 5 | 100 | 0.7500 | 42 | B0007 | 159 | 0.3774 | 0.0867 | 0.3041 | 0.3072 | 0.3293 | 0.5761 | 0.6945 |
| RELATIVE_A | 5 | 100 | 0.7500 | 123 | training | 82 | 0.3672 | 0.0784 | 0.2991 | 0.3015 | 0.3349 | 0.5373 | 0.6352 |
| RELATIVE_A | 5 | 100 | 0.7500 | 123 | B0007 | 159 | 0.3680 | 0.0847 | 0.2984 | 0.3003 | 0.3265 | 0.5616 | 0.6400 |
| RELATIVE_A | 5 | 100 | 0.7500 | 2026 | training | 82 | 0.3757 | 0.0828 | 0.3065 | 0.3089 | 0.3444 | 0.5579 | 0.6560 |
| RELATIVE_A | 5 | 100 | 0.7500 | 2026 | B0007 | 159 | 0.3737 | 0.0857 | 0.3056 | 0.3076 | 0.3333 | 0.5901 | 0.6811 |
| RELATIVE_A | 5 | 100 | 1.0000 | 42 | training | 82 | 0.3692 | 0.0844 | 0.3009 | 0.3036 | 0.3365 | 0.5780 | 0.6586 |
| RELATIVE_A | 5 | 100 | 1.0000 | 42 | B0007 | 159 | 0.3674 | 0.0852 | 0.3017 | 0.3025 | 0.3239 | 0.5572 | 0.6843 |
| RELATIVE_A | 5 | 100 | 1.0000 | 123 | training | 82 | 0.3724 | 0.0817 | 0.3057 | 0.3094 | 0.3372 | 0.5577 | 0.6547 |
| RELATIVE_A | 5 | 100 | 1.0000 | 123 | B0007 | 159 | 0.3736 | 0.0879 | 0.3046 | 0.3066 | 0.3309 | 0.5819 | 0.6876 |
| RELATIVE_A | 5 | 100 | 1.0000 | 2026 | training | 82 | 0.3716 | 0.0835 | 0.3017 | 0.3036 | 0.3364 | 0.5511 | 0.6675 |
| RELATIVE_A | 5 | 100 | 1.0000 | 2026 | B0007 | 159 | 0.3737 | 0.0895 | 0.3005 | 0.3033 | 0.3284 | 0.5813 | 0.6802 |
| RELATIVE_A | 5 | 200 | 0.7500 | 42 | training | 82 | 0.3768 | 0.0806 | 0.3058 | 0.3091 | 0.3452 | 0.5616 | 0.6436 |
| RELATIVE_A | 5 | 200 | 0.7500 | 42 | B0007 | 159 | 0.3775 | 0.0871 | 0.3048 | 0.3075 | 0.3316 | 0.5889 | 0.6803 |
| RELATIVE_A | 5 | 200 | 0.7500 | 123 | training | 82 | 0.3705 | 0.0794 | 0.3025 | 0.3052 | 0.3394 | 0.5370 | 0.6395 |
| RELATIVE_A | 5 | 200 | 0.7500 | 123 | B0007 | 159 | 0.3720 | 0.0864 | 0.3007 | 0.3042 | 0.3285 | 0.5747 | 0.6536 |
| RELATIVE_A | 5 | 200 | 0.7500 | 2026 | training | 82 | 0.3760 | 0.0824 | 0.3057 | 0.3088 | 0.3423 | 0.5577 | 0.6623 |
| RELATIVE_A | 5 | 200 | 0.7500 | 2026 | B0007 | 159 | 0.3745 | 0.0872 | 0.3045 | 0.3073 | 0.3313 | 0.5967 | 0.6808 |
| RELATIVE_A | 5 | 200 | 1.0000 | 42 | training | 82 | 0.3701 | 0.0830 | 0.3015 | 0.3035 | 0.3399 | 0.5583 | 0.6619 |
| RELATIVE_A | 5 | 200 | 1.0000 | 42 | B0007 | 159 | 0.3693 | 0.0866 | 0.3015 | 0.3031 | 0.3255 | 0.5813 | 0.6824 |
| RELATIVE_A | 5 | 200 | 1.0000 | 123 | training | 82 | 0.3739 | 0.0823 | 0.3053 | 0.3083 | 0.3366 | 0.5690 | 0.6568 |
| RELATIVE_A | 5 | 200 | 1.0000 | 123 | B0007 | 159 | 0.3731 | 0.0855 | 0.3035 | 0.3061 | 0.3316 | 0.5829 | 0.6771 |
| RELATIVE_A | 5 | 200 | 1.0000 | 2026 | training | 82 | 0.3688 | 0.0834 | 0.3004 | 0.3040 | 0.3325 | 0.5591 | 0.6527 |
| RELATIVE_A | 5 | 200 | 1.0000 | 2026 | B0007 | 159 | 0.3687 | 0.0873 | 0.3000 | 0.3030 | 0.3242 | 0.5785 | 0.6811 |
| RELATIVE_B | 5 | 100 | 0.7500 | 42 | training | 90 | 0.3728 | 0.0721 | 0.3075 | 0.3096 | 0.3471 | 0.5388 | 0.5823 |
| RELATIVE_B | 5 | 100 | 0.7500 | 42 | B0007 | 163 | 0.3821 | 0.0836 | 0.3061 | 0.3084 | 0.3485 | 0.5594 | 0.6535 |
| RELATIVE_B | 5 | 100 | 0.7500 | 123 | training | 90 | 0.3730 | 0.0768 | 0.3037 | 0.3066 | 0.3459 | 0.5398 | 0.6216 |
| RELATIVE_B | 5 | 100 | 0.7500 | 123 | B0007 | 163 | 0.3803 | 0.0826 | 0.3031 | 0.3059 | 0.3469 | 0.5472 | 0.6548 |
| RELATIVE_B | 5 | 100 | 0.7500 | 2026 | training | 90 | 0.3734 | 0.0753 | 0.3059 | 0.3091 | 0.3397 | 0.5448 | 0.6153 |
| RELATIVE_B | 5 | 100 | 0.7500 | 2026 | B0007 | 163 | 0.3790 | 0.0809 | 0.3057 | 0.3080 | 0.3489 | 0.5660 | 0.6422 |
| RELATIVE_B | 5 | 100 | 1.0000 | 42 | training | 90 | 0.3707 | 0.0785 | 0.3042 | 0.3071 | 0.3392 | 0.5447 | 0.6234 |
| RELATIVE_B | 5 | 100 | 1.0000 | 42 | B0007 | 163 | 0.3769 | 0.0855 | 0.3036 | 0.3052 | 0.3410 | 0.5635 | 0.6322 |
| RELATIVE_B | 5 | 100 | 1.0000 | 123 | training | 90 | 0.3712 | 0.0798 | 0.3018 | 0.3049 | 0.3340 | 0.5471 | 0.6206 |
| RELATIVE_B | 5 | 100 | 1.0000 | 123 | B0007 | 163 | 0.3770 | 0.0843 | 0.3022 | 0.3039 | 0.3424 | 0.5633 | 0.6479 |
| RELATIVE_B | 5 | 100 | 1.0000 | 2026 | training | 90 | 0.3695 | 0.0796 | 0.3021 | 0.3045 | 0.3340 | 0.5509 | 0.5859 |
| RELATIVE_B | 5 | 100 | 1.0000 | 2026 | B0007 | 163 | 0.3745 | 0.0867 | 0.3022 | 0.3030 | 0.3350 | 0.5680 | 0.6677 |
| RELATIVE_B | 5 | 200 | 0.7500 | 42 | training | 90 | 0.3763 | 0.0749 | 0.3071 | 0.3115 | 0.3497 | 0.5374 | 0.5895 |
| RELATIVE_B | 5 | 200 | 0.7500 | 42 | B0007 | 163 | 0.3847 | 0.0820 | 0.3064 | 0.3083 | 0.3514 | 0.5552 | 0.6473 |
| RELATIVE_B | 5 | 200 | 0.7500 | 123 | training | 90 | 0.3725 | 0.0758 | 0.3028 | 0.3064 | 0.3432 | 0.5348 | 0.6124 |
| RELATIVE_B | 5 | 200 | 0.7500 | 123 | B0007 | 163 | 0.3775 | 0.0808 | 0.3028 | 0.3056 | 0.3451 | 0.5474 | 0.6405 |
| RELATIVE_B | 5 | 200 | 0.7500 | 2026 | training | 90 | 0.3735 | 0.0755 | 0.3048 | 0.3079 | 0.3424 | 0.5395 | 0.5970 |
| RELATIVE_B | 5 | 200 | 0.7500 | 2026 | B0007 | 163 | 0.3801 | 0.0816 | 0.3046 | 0.3067 | 0.3479 | 0.5557 | 0.6400 |
| RELATIVE_B | 5 | 200 | 1.0000 | 42 | training | 90 | 0.3713 | 0.0782 | 0.3034 | 0.3063 | 0.3391 | 0.5400 | 0.6142 |
| RELATIVE_B | 5 | 200 | 1.0000 | 42 | B0007 | 163 | 0.3786 | 0.0845 | 0.3033 | 0.3051 | 0.3448 | 0.5633 | 0.6315 |
| RELATIVE_B | 5 | 200 | 1.0000 | 123 | training | 90 | 0.3718 | 0.0789 | 0.3035 | 0.3065 | 0.3361 | 0.5449 | 0.6080 |
| RELATIVE_B | 5 | 200 | 1.0000 | 123 | B0007 | 163 | 0.3783 | 0.0845 | 0.3032 | 0.3047 | 0.3430 | 0.5675 | 0.6481 |
| RELATIVE_B | 5 | 200 | 1.0000 | 2026 | training | 90 | 0.3700 | 0.0802 | 0.3018 | 0.3046 | 0.3338 | 0.5536 | 0.5986 |
| RELATIVE_B | 5 | 200 | 1.0000 | 2026 | B0007 | 163 | 0.3780 | 0.0878 | 0.3018 | 0.3027 | 0.3397 | 0.5759 | 0.6690 |
| RELATIVE_A | 10 | 100 | 0.7500 | 42 | training | 72 | 0.4206 | 0.0803 | 0.3387 | 0.3413 | 0.3932 | 0.6048 | 0.6582 |
| RELATIVE_A | 10 | 100 | 0.7500 | 42 | B0007 | 154 | 0.3925 | 0.0568 | 0.3324 | 0.3447 | 0.3735 | 0.5271 | 0.5975 |
| RELATIVE_A | 10 | 100 | 0.7500 | 123 | training | 72 | 0.4225 | 0.0745 | 0.3412 | 0.3511 | 0.3962 | 0.5620 | 0.6350 |
| RELATIVE_A | 10 | 100 | 0.7500 | 123 | B0007 | 154 | 0.3971 | 0.0567 | 0.3414 | 0.3494 | 0.3756 | 0.5163 | 0.6235 |
| RELATIVE_A | 10 | 100 | 0.7500 | 2026 | training | 72 | 0.4265 | 0.0721 | 0.3450 | 0.3579 | 0.4031 | 0.5631 | 0.6470 |
| RELATIVE_A | 10 | 100 | 0.7500 | 2026 | B0007 | 154 | 0.3996 | 0.0540 | 0.3456 | 0.3499 | 0.3832 | 0.5179 | 0.6084 |
| RELATIVE_A | 10 | 100 | 1.0000 | 42 | training | 72 | 0.4178 | 0.0768 | 0.3310 | 0.3416 | 0.3911 | 0.5676 | 0.6392 |
| RELATIVE_A | 10 | 100 | 1.0000 | 42 | B0007 | 154 | 0.3916 | 0.0568 | 0.3286 | 0.3361 | 0.3758 | 0.5182 | 0.6031 |
| RELATIVE_A | 10 | 100 | 1.0000 | 123 | training | 72 | 0.4172 | 0.0783 | 0.3330 | 0.3418 | 0.3901 | 0.5806 | 0.6300 |
| RELATIVE_A | 10 | 100 | 1.0000 | 123 | B0007 | 154 | 0.3909 | 0.0571 | 0.3273 | 0.3357 | 0.3737 | 0.5180 | 0.6107 |
| RELATIVE_A | 10 | 100 | 1.0000 | 2026 | training | 72 | 0.4217 | 0.0781 | 0.3356 | 0.3448 | 0.3937 | 0.6015 | 0.6227 |
| RELATIVE_A | 10 | 100 | 1.0000 | 2026 | B0007 | 154 | 0.3932 | 0.0612 | 0.3338 | 0.3393 | 0.3722 | 0.5299 | 0.6427 |
| RELATIVE_A | 10 | 200 | 0.7500 | 42 | training | 72 | 0.4233 | 0.0762 | 0.3406 | 0.3470 | 0.3987 | 0.5763 | 0.6317 |
| RELATIVE_A | 10 | 200 | 0.7500 | 42 | B0007 | 154 | 0.3962 | 0.0566 | 0.3351 | 0.3466 | 0.3798 | 0.5327 | 0.6116 |
| RELATIVE_A | 10 | 200 | 0.7500 | 123 | training | 72 | 0.4215 | 0.0740 | 0.3432 | 0.3512 | 0.3932 | 0.5584 | 0.6269 |
| RELATIVE_A | 10 | 200 | 0.7500 | 123 | B0007 | 154 | 0.3976 | 0.0551 | 0.3420 | 0.3484 | 0.3777 | 0.5192 | 0.6164 |
| RELATIVE_A | 10 | 200 | 0.7500 | 2026 | training | 72 | 0.4292 | 0.0730 | 0.3454 | 0.3588 | 0.4051 | 0.5683 | 0.6262 |
| RELATIVE_A | 10 | 200 | 0.7500 | 2026 | B0007 | 154 | 0.4022 | 0.0553 | 0.3470 | 0.3508 | 0.3855 | 0.5210 | 0.6077 |
| RELATIVE_A | 10 | 200 | 1.0000 | 42 | training | 72 | 0.4221 | 0.0740 | 0.3378 | 0.3491 | 0.3964 | 0.5707 | 0.6288 |
| RELATIVE_A | 10 | 200 | 1.0000 | 42 | B0007 | 154 | 0.3948 | 0.0550 | 0.3368 | 0.3439 | 0.3782 | 0.5161 | 0.6015 |
| RELATIVE_A | 10 | 200 | 1.0000 | 123 | training | 72 | 0.4179 | 0.0758 | 0.3360 | 0.3460 | 0.3894 | 0.5729 | 0.6223 |
| RELATIVE_A | 10 | 200 | 1.0000 | 123 | B0007 | 154 | 0.3915 | 0.0562 | 0.3315 | 0.3398 | 0.3744 | 0.5114 | 0.6040 |
| RELATIVE_A | 10 | 200 | 1.0000 | 2026 | training | 72 | 0.4230 | 0.0773 | 0.3368 | 0.3476 | 0.3969 | 0.5911 | 0.6245 |
| RELATIVE_A | 10 | 200 | 1.0000 | 2026 | B0007 | 154 | 0.3961 | 0.0583 | 0.3364 | 0.3425 | 0.3777 | 0.5228 | 0.6224 |
| RELATIVE_B | 10 | 100 | 0.7500 | 42 | training | 80 | 0.4188 | 0.0669 | 0.3372 | 0.3504 | 0.3962 | 0.5451 | 0.6280 |
| RELATIVE_B | 10 | 100 | 0.7500 | 42 | B0007 | 158 | 0.3980 | 0.0543 | 0.3394 | 0.3423 | 0.3827 | 0.5153 | 0.6167 |
| RELATIVE_B | 10 | 100 | 0.7500 | 123 | training | 80 | 0.4191 | 0.0659 | 0.3412 | 0.3491 | 0.3953 | 0.5368 | 0.6538 |
| RELATIVE_B | 10 | 100 | 0.7500 | 123 | B0007 | 158 | 0.4034 | 0.0563 | 0.3372 | 0.3464 | 0.3836 | 0.5298 | 0.6078 |
| RELATIVE_B | 10 | 100 | 0.7500 | 2026 | training | 80 | 0.4150 | 0.0654 | 0.3351 | 0.3476 | 0.3886 | 0.5398 | 0.6328 |
| RELATIVE_B | 10 | 100 | 0.7500 | 2026 | B0007 | 158 | 0.3984 | 0.0543 | 0.3382 | 0.3425 | 0.3830 | 0.5023 | 0.6119 |
| RELATIVE_B | 10 | 100 | 1.0000 | 42 | training | 80 | 0.4098 | 0.0711 | 0.3300 | 0.3365 | 0.3864 | 0.5549 | 0.6542 |
| RELATIVE_B | 10 | 100 | 1.0000 | 42 | B0007 | 158 | 0.3936 | 0.0626 | 0.3278 | 0.3351 | 0.3706 | 0.5250 | 0.6353 |
| RELATIVE_B | 10 | 100 | 1.0000 | 123 | training | 80 | 0.4195 | 0.0645 | 0.3386 | 0.3499 | 0.3976 | 0.5371 | 0.6254 |
| RELATIVE_B | 10 | 100 | 1.0000 | 123 | B0007 | 158 | 0.4031 | 0.0592 | 0.3390 | 0.3461 | 0.3829 | 0.5250 | 0.6105 |
| RELATIVE_B | 10 | 100 | 1.0000 | 2026 | training | 80 | 0.4150 | 0.0704 | 0.3370 | 0.3450 | 0.3887 | 0.5518 | 0.6406 |
| RELATIVE_B | 10 | 100 | 1.0000 | 2026 | B0007 | 158 | 0.3977 | 0.0581 | 0.3372 | 0.3430 | 0.3806 | 0.5088 | 0.6255 |
| RELATIVE_B | 10 | 200 | 0.7500 | 42 | training | 80 | 0.4158 | 0.0678 | 0.3369 | 0.3478 | 0.3903 | 0.5409 | 0.6378 |
| RELATIVE_B | 10 | 200 | 0.7500 | 42 | B0007 | 158 | 0.3980 | 0.0568 | 0.3373 | 0.3425 | 0.3797 | 0.5101 | 0.6239 |
| RELATIVE_B | 10 | 200 | 0.7500 | 123 | training | 80 | 0.4218 | 0.0661 | 0.3469 | 0.3518 | 0.3956 | 0.5414 | 0.6571 |
| RELATIVE_B | 10 | 200 | 0.7500 | 123 | B0007 | 158 | 0.4050 | 0.0569 | 0.3406 | 0.3468 | 0.3863 | 0.5319 | 0.6212 |
| RELATIVE_B | 10 | 200 | 0.7500 | 2026 | training | 80 | 0.4160 | 0.0653 | 0.3378 | 0.3506 | 0.3941 | 0.5333 | 0.6333 |
| RELATIVE_B | 10 | 200 | 0.7500 | 2026 | B0007 | 158 | 0.3993 | 0.0555 | 0.3365 | 0.3416 | 0.3827 | 0.5110 | 0.6012 |
| RELATIVE_B | 10 | 200 | 1.0000 | 42 | training | 80 | 0.4155 | 0.0694 | 0.3344 | 0.3447 | 0.3890 | 0.5523 | 0.6539 |
| RELATIVE_B | 10 | 200 | 1.0000 | 42 | B0007 | 158 | 0.4000 | 0.0610 | 0.3369 | 0.3426 | 0.3793 | 0.5239 | 0.6242 |
| RELATIVE_B | 10 | 200 | 1.0000 | 123 | training | 80 | 0.4152 | 0.0683 | 0.3345 | 0.3482 | 0.3921 | 0.5446 | 0.6285 |
| RELATIVE_B | 10 | 200 | 1.0000 | 123 | B0007 | 158 | 0.3965 | 0.0605 | 0.3350 | 0.3401 | 0.3733 | 0.5161 | 0.6194 |
| RELATIVE_B | 10 | 200 | 1.0000 | 2026 | training | 80 | 0.4170 | 0.0705 | 0.3373 | 0.3463 | 0.3907 | 0.5550 | 0.6528 |
| RELATIVE_B | 10 | 200 | 1.0000 | 2026 | B0007 | 158 | 0.3999 | 0.0601 | 0.3382 | 0.3435 | 0.3803 | 0.5087 | 0.6292 |
| RELATIVE_A | 20 | 100 | 0.7500 | 42 | training | 52 | 0.4609 | 0.0543 | 0.3854 | 0.3983 | 0.4491 | 0.5521 | 0.6522 |
| RELATIVE_A | 20 | 100 | 0.7500 | 42 | B0007 | 144 | 0.4447 | 0.0504 | 0.3821 | 0.3899 | 0.4331 | 0.5414 | 0.6458 |
| RELATIVE_A | 20 | 100 | 0.7500 | 123 | training | 52 | 0.4597 | 0.0561 | 0.3862 | 0.3961 | 0.4453 | 0.5624 | 0.6398 |
| RELATIVE_A | 20 | 100 | 0.7500 | 123 | B0007 | 144 | 0.4438 | 0.0509 | 0.3805 | 0.3879 | 0.4353 | 0.5455 | 0.6396 |
| RELATIVE_A | 20 | 100 | 0.7500 | 2026 | training | 52 | 0.4617 | 0.0537 | 0.3902 | 0.4020 | 0.4494 | 0.5660 | 0.6495 |
| RELATIVE_A | 20 | 100 | 0.7500 | 2026 | B0007 | 144 | 0.4491 | 0.0479 | 0.3848 | 0.3975 | 0.4378 | 0.5415 | 0.6466 |
| RELATIVE_A | 20 | 100 | 1.0000 | 42 | training | 52 | 0.4630 | 0.0541 | 0.3844 | 0.4018 | 0.4514 | 0.5567 | 0.6632 |
| RELATIVE_A | 20 | 100 | 1.0000 | 42 | B0007 | 144 | 0.4452 | 0.0486 | 0.3864 | 0.3913 | 0.4370 | 0.5439 | 0.6461 |
| RELATIVE_A | 20 | 100 | 1.0000 | 123 | training | 52 | 0.4608 | 0.0555 | 0.3801 | 0.3933 | 0.4519 | 0.5559 | 0.6603 |
| RELATIVE_A | 20 | 100 | 1.0000 | 123 | B0007 | 144 | 0.4462 | 0.0468 | 0.3809 | 0.3890 | 0.4393 | 0.5235 | 0.6538 |
| RELATIVE_A | 20 | 100 | 1.0000 | 2026 | training | 52 | 0.4584 | 0.0586 | 0.3783 | 0.3982 | 0.4430 | 0.5690 | 0.6662 |
| RELATIVE_A | 20 | 100 | 1.0000 | 2026 | B0007 | 144 | 0.4428 | 0.0498 | 0.3750 | 0.3867 | 0.4339 | 0.5388 | 0.6549 |
| RELATIVE_A | 20 | 200 | 0.7500 | 42 | training | 52 | 0.4637 | 0.0536 | 0.3933 | 0.4010 | 0.4527 | 0.5559 | 0.6550 |
| RELATIVE_A | 20 | 200 | 0.7500 | 42 | B0007 | 144 | 0.4489 | 0.0486 | 0.3907 | 0.3953 | 0.4389 | 0.5376 | 0.6457 |
| RELATIVE_A | 20 | 200 | 0.7500 | 123 | training | 52 | 0.4613 | 0.0544 | 0.3888 | 0.3991 | 0.4434 | 0.5572 | 0.6431 |
| RELATIVE_A | 20 | 200 | 0.7500 | 123 | B0007 | 144 | 0.4455 | 0.0480 | 0.3858 | 0.3916 | 0.4376 | 0.5387 | 0.6294 |
| RELATIVE_A | 20 | 200 | 0.7500 | 2026 | training | 52 | 0.4657 | 0.0538 | 0.3934 | 0.4081 | 0.4586 | 0.5666 | 0.6522 |
| RELATIVE_A | 20 | 200 | 0.7500 | 2026 | B0007 | 144 | 0.4526 | 0.0473 | 0.3898 | 0.4012 | 0.4428 | 0.5380 | 0.6443 |
| RELATIVE_A | 20 | 200 | 1.0000 | 42 | training | 52 | 0.4657 | 0.0541 | 0.3902 | 0.4053 | 0.4516 | 0.5597 | 0.6670 |
| RELATIVE_A | 20 | 200 | 1.0000 | 42 | B0007 | 144 | 0.4479 | 0.0464 | 0.3919 | 0.3987 | 0.4380 | 0.5452 | 0.6365 |
| RELATIVE_A | 20 | 200 | 1.0000 | 123 | training | 52 | 0.4615 | 0.0533 | 0.3826 | 0.3980 | 0.4507 | 0.5500 | 0.6609 |
| RELATIVE_A | 20 | 200 | 1.0000 | 123 | B0007 | 144 | 0.4451 | 0.0457 | 0.3841 | 0.3906 | 0.4366 | 0.5229 | 0.6335 |
| RELATIVE_A | 20 | 200 | 1.0000 | 2026 | training | 52 | 0.4620 | 0.0578 | 0.3855 | 0.3989 | 0.4487 | 0.5744 | 0.6604 |
| RELATIVE_A | 20 | 200 | 1.0000 | 2026 | B0007 | 144 | 0.4454 | 0.0487 | 0.3836 | 0.3939 | 0.4350 | 0.5420 | 0.6399 |
| RELATIVE_B | 20 | 100 | 0.7500 | 42 | training | 60 | 0.4549 | 0.0556 | 0.3862 | 0.3921 | 0.4385 | 0.5489 | 0.6266 |
| RELATIVE_B | 20 | 100 | 0.7500 | 42 | B0007 | 148 | 0.4315 | 0.0415 | 0.3809 | 0.3854 | 0.4192 | 0.5259 | 0.5612 |
| RELATIVE_B | 20 | 100 | 0.7500 | 123 | training | 60 | 0.4492 | 0.0595 | 0.3784 | 0.3841 | 0.4245 | 0.5570 | 0.6041 |
| RELATIVE_B | 20 | 100 | 0.7500 | 123 | B0007 | 148 | 0.4240 | 0.0376 | 0.3793 | 0.3843 | 0.4118 | 0.4980 | 0.5697 |
| RELATIVE_B | 20 | 100 | 0.7500 | 2026 | training | 60 | 0.4515 | 0.0550 | 0.3834 | 0.3930 | 0.4300 | 0.5538 | 0.5842 |
| RELATIVE_B | 20 | 100 | 0.7500 | 2026 | B0007 | 148 | 0.4287 | 0.0387 | 0.3789 | 0.3891 | 0.4175 | 0.5018 | 0.5689 |
| RELATIVE_B | 20 | 100 | 1.0000 | 42 | training | 60 | 0.4542 | 0.0585 | 0.3864 | 0.3898 | 0.4333 | 0.5646 | 0.5884 |
| RELATIVE_B | 20 | 100 | 1.0000 | 42 | B0007 | 148 | 0.4299 | 0.0421 | 0.3754 | 0.3829 | 0.4224 | 0.5213 | 0.5820 |
| RELATIVE_B | 20 | 100 | 1.0000 | 123 | training | 60 | 0.4557 | 0.0566 | 0.3902 | 0.3921 | 0.4374 | 0.5562 | 0.5886 |
| RELATIVE_B | 20 | 100 | 1.0000 | 123 | B0007 | 148 | 0.4283 | 0.0388 | 0.3810 | 0.3855 | 0.4199 | 0.5157 | 0.5572 |
| RELATIVE_B | 20 | 100 | 1.0000 | 2026 | training | 60 | 0.4525 | 0.0550 | 0.3845 | 0.3970 | 0.4316 | 0.5538 | 0.6026 |
| RELATIVE_B | 20 | 100 | 1.0000 | 2026 | B0007 | 148 | 0.4292 | 0.0398 | 0.3858 | 0.3919 | 0.4167 | 0.5078 | 0.5721 |
| RELATIVE_B | 20 | 200 | 0.7500 | 42 | training | 60 | 0.4546 | 0.0560 | 0.3855 | 0.3894 | 0.4356 | 0.5606 | 0.6290 |
| RELATIVE_B | 20 | 200 | 0.7500 | 42 | B0007 | 148 | 0.4297 | 0.0411 | 0.3824 | 0.3864 | 0.4186 | 0.5100 | 0.5727 |
| RELATIVE_B | 20 | 200 | 0.7500 | 123 | training | 60 | 0.4522 | 0.0561 | 0.3837 | 0.3874 | 0.4316 | 0.5474 | 0.5916 |
| RELATIVE_B | 20 | 200 | 0.7500 | 123 | B0007 | 148 | 0.4286 | 0.0391 | 0.3804 | 0.3859 | 0.4171 | 0.5121 | 0.5646 |
| RELATIVE_B | 20 | 200 | 0.7500 | 2026 | training | 60 | 0.4538 | 0.0534 | 0.3869 | 0.3927 | 0.4349 | 0.5529 | 0.5955 |
| RELATIVE_B | 20 | 200 | 0.7500 | 2026 | B0007 | 148 | 0.4309 | 0.0398 | 0.3857 | 0.3902 | 0.4198 | 0.5088 | 0.5737 |
| RELATIVE_B | 20 | 200 | 1.0000 | 42 | training | 60 | 0.4538 | 0.0564 | 0.3870 | 0.3942 | 0.4332 | 0.5540 | 0.5817 |
| RELATIVE_B | 20 | 200 | 1.0000 | 42 | B0007 | 148 | 0.4304 | 0.0407 | 0.3791 | 0.3873 | 0.4201 | 0.5153 | 0.5623 |
| RELATIVE_B | 20 | 200 | 1.0000 | 123 | training | 60 | 0.4559 | 0.0566 | 0.3906 | 0.3940 | 0.4330 | 0.5483 | 0.5834 |
| RELATIVE_B | 20 | 200 | 1.0000 | 123 | B0007 | 148 | 0.4285 | 0.0397 | 0.3805 | 0.3852 | 0.4164 | 0.5122 | 0.5655 |
| RELATIVE_B | 20 | 200 | 1.0000 | 2026 | training | 60 | 0.4506 | 0.0575 | 0.3845 | 0.3912 | 0.4284 | 0.5524 | 0.6011 |
| RELATIVE_B | 20 | 200 | 1.0000 | 2026 | B0007 | 148 | 0.4261 | 0.0422 | 0.3791 | 0.3854 | 0.4131 | 0.5143 | 0.5709 |

## Controlled deviations: eligible configurations only

Each frozen window is injected into a fresh isolated copy. Its preceding clean k-cycle context is included only for baseline calculation. Within an A1/A4 sequence, earlier altered observations enter subsequent prior baselines, so sustained deviations can be adapted away; the current observation never enters its own baseline. The baseline is NOT frozen at pre-event values. No synthetic baseline is shared across unrelated copies. A1 derives altered slopes from its own capacity history; only the ramp is evaluated and no recovery tail is added. A2/A3 prior injected samples also enter later window baselines. Scenario onset must have sufficient model history; whole unusable windows are excluded. Zero-offset onset rows remain negative and are not counted as synthetic positives.

A1 is applicable only to RELATIVE_A. Severity magnitudes/durations are frozen and unchanged. Metrics use the established equal-class-weight 50% evaluation prevalence; PR-AUC means average precision. ROC-AUC is reported where both classes exist. Repeated overlapping windows are dependent, not independent trials. No synthetic F1 optimization.

### Eligible reference results, P97.5 (display convention only; not a selected threshold)

| feature_set | history_window | n_estimators | max_features | anomaly_family | severity | variant | percentile | precision_mean | precision_std | recall_mean | recall_std | f1_mean | f1_std | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RELATIVE_A | 5 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | pooled | 97.5000 | 0.1819 | 0.0283 | 0.0050 | 0.0001 | 0.0098 | 0.0002 | 0.4611 | 0.0011 | 0.4498 | 0.0022 |
| RELATIVE_A | 5 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | pooled | 97.5000 | 0.1804 | 0.0296 | 0.0050 | 0.0002 | 0.0097 | 0.0003 | 0.4602 | 0.0010 | 0.4479 | 0.0027 |
| RELATIVE_A | 5 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | pooled | 97.5000 | 0.1756 | 0.0292 | 0.0048 | 0.0002 | 0.0094 | 0.0003 | 0.4608 | 0.0007 | 0.4501 | 0.0031 |
| RELATIVE_A | 5 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 97.5000 | 0.5282 | 0.0571 | 0.0258 | 0.0039 | 0.0492 | 0.0072 | 0.6605 | 0.0013 | 0.6951 | 0.0019 |
| RELATIVE_A | 5 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 97.5000 | 0.6846 | 0.0685 | 0.0512 | 0.0123 | 0.0951 | 0.0217 | 0.7153 | 0.0066 | 0.7234 | 0.0022 |
| RELATIVE_A | 5 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 97.5000 | 0.7499 | 0.0627 | 0.0714 | 0.0187 | 0.1301 | 0.0319 | 0.7426 | 0.0100 | 0.7379 | 0.0029 |
| RELATIVE_A | 5 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 97.5000 | 0.4725 | 0.0327 | 0.0206 | 0.0034 | 0.0395 | 0.0063 | 0.5401 | 0.0027 | 0.5761 | 0.0041 |
| RELATIVE_A | 5 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 97.5000 | 0.5324 | 0.0336 | 0.0262 | 0.0041 | 0.0500 | 0.0076 | 0.5783 | 0.0049 | 0.6195 | 0.0057 |
| RELATIVE_A | 5 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 97.5000 | 0.5678 | 0.0477 | 0.0301 | 0.0015 | 0.0572 | 0.0029 | 0.6094 | 0.0067 | 0.6512 | 0.0060 |
| RELATIVE_A | 5 | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 97.5000 | 0.4501 | 0.0359 | 0.0189 | 0.0034 | 0.0362 | 0.0063 | 0.4981 | 0.0010 | 0.5069 | 0.0031 |
| RELATIVE_A | 5 | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 97.5000 | 0.4617 | 0.0406 | 0.0197 | 0.0025 | 0.0378 | 0.0047 | 0.5033 | 0.0022 | 0.5185 | 0.0038 |
| RELATIVE_A | 5 | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 97.5000 | 0.4765 | 0.0384 | 0.0209 | 0.0021 | 0.0400 | 0.0040 | 0.5155 | 0.0025 | 0.5379 | 0.0040 |
| RELATIVE_A | 10 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | pooled | 97.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4830 | 0.0028 | 0.4806 | 0.0065 |
| RELATIVE_A | 10 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | pooled | 97.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4884 | 0.0047 | 0.4916 | 0.0094 |
| RELATIVE_A | 10 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | pooled | 97.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4922 | 0.0054 | 0.4992 | 0.0103 |
| RELATIVE_A | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 97.5000 | 0.9930 | 0.0121 | 0.2413 | 0.0756 | 0.3840 | 0.1000 | 0.9754 | 0.0063 | 0.9811 | 0.0034 |
| RELATIVE_A | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 97.5000 | 0.9946 | 0.0094 | 0.3080 | 0.0997 | 0.4639 | 0.1197 | 0.9869 | 0.0056 | 0.9915 | 0.0029 |
| RELATIVE_A | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 97.5000 | 0.9947 | 0.0092 | 0.3164 | 0.1065 | 0.4730 | 0.1270 | 0.9883 | 0.0056 | 0.9927 | 0.0029 |
| RELATIVE_A | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 97.5000 | 0.8739 | 0.2185 | 0.0093 | 0.0023 | 0.0184 | 0.0045 | 0.6399 | 0.0243 | 0.6868 | 0.0192 |
| RELATIVE_A | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 97.5000 | 0.8977 | 0.1772 | 0.0147 | 0.0053 | 0.0288 | 0.0104 | 0.7876 | 0.0360 | 0.8399 | 0.0221 |
| RELATIVE_A | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 97.5000 | 0.9347 | 0.1131 | 0.0311 | 0.0101 | 0.0601 | 0.0190 | 0.8690 | 0.0363 | 0.9135 | 0.0180 |
| RELATIVE_A | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 97.5000 | 0.8175 | 0.3162 | 0.0024 | 0.0026 | 0.0048 | 0.0051 | 0.5583 | 0.0028 | 0.5920 | 0.0010 |
| RELATIVE_A | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 97.5000 | 0.8259 | 0.3016 | 0.0029 | 0.0026 | 0.0058 | 0.0052 | 0.5973 | 0.0043 | 0.6409 | 0.0021 |
| RELATIVE_A | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 97.5000 | 0.8406 | 0.2760 | 0.0035 | 0.0032 | 0.0070 | 0.0063 | 0.6249 | 0.0054 | 0.6753 | 0.0034 |
| RELATIVE_A | 20 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | mild | pooled | 97.5000 | 0.4165 | 0.0336 | 0.0217 | 0.0052 | 0.0413 | 0.0095 | 0.4725 | 0.0026 | 0.4535 | 0.0060 |
| RELATIVE_A | 20 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | moderate | pooled | 97.5000 | 0.4125 | 0.0351 | 0.0214 | 0.0052 | 0.0407 | 0.0095 | 0.4754 | 0.0044 | 0.4580 | 0.0085 |
| RELATIVE_A | 20 | 100 | 1.0000 | A1_ACCELERATED_DEGRADATION | strong | pooled | 97.5000 | 0.4064 | 0.0348 | 0.0209 | 0.0049 | 0.0396 | 0.0091 | 0.4830 | 0.0034 | 0.4671 | 0.0071 |
| RELATIVE_A | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 97.5000 | 0.8895 | 0.0344 | 0.2600 | 0.0876 | 0.3980 | 0.1116 | 0.9020 | 0.0181 | 0.9606 | 0.0090 |
| RELATIVE_A | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 97.5000 | 0.8910 | 0.0347 | 0.2648 | 0.0902 | 0.4035 | 0.1148 | 0.9027 | 0.0180 | 0.9608 | 0.0090 |
| RELATIVE_A | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 97.5000 | 0.8910 | 0.0347 | 0.2648 | 0.0902 | 0.4035 | 0.1148 | 0.9027 | 0.0180 | 0.9608 | 0.0090 |
| RELATIVE_A | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 97.5000 | 0.4045 | 0.0820 | 0.0205 | 0.0044 | 0.0390 | 0.0083 | 0.5894 | 0.0120 | 0.6365 | 0.0060 |
| RELATIVE_A | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 97.5000 | 0.5401 | 0.0772 | 0.0362 | 0.0101 | 0.0678 | 0.0184 | 0.7309 | 0.0185 | 0.8137 | 0.0121 |
| RELATIVE_A | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 97.5000 | 0.6627 | 0.0499 | 0.0600 | 0.0122 | 0.1099 | 0.0212 | 0.8088 | 0.0173 | 0.8888 | 0.0093 |
| RELATIVE_A | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 97.5000 | 0.4819 | 0.0328 | 0.0283 | 0.0060 | 0.0533 | 0.0108 | 0.5801 | 0.0051 | 0.6135 | 0.0070 |
| RELATIVE_A | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 97.5000 | 0.5022 | 0.0256 | 0.0305 | 0.0049 | 0.0574 | 0.0087 | 0.6112 | 0.0077 | 0.6565 | 0.0093 |
| RELATIVE_A | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 97.5000 | 0.5140 | 0.0296 | 0.0320 | 0.0053 | 0.0601 | 0.0096 | 0.6366 | 0.0092 | 0.6943 | 0.0125 |
| RELATIVE_B | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 97.5000 | 0.9667 | 0.0142 | 0.5325 | 0.1990 | 0.6733 | 0.1635 | 0.9718 | 0.0140 | 0.9793 | 0.0057 |
| RELATIVE_B | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 97.5000 | 0.9738 | 0.0113 | 0.6784 | 0.2340 | 0.7853 | 0.1637 | 0.9829 | 0.0141 | 0.9902 | 0.0063 |
| RELATIVE_B | 10 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 97.5000 | 0.9745 | 0.0110 | 0.6987 | 0.2390 | 0.7994 | 0.1636 | 0.9841 | 0.0140 | 0.9912 | 0.0064 |
| RELATIVE_B | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 97.5000 | 0.5760 | 0.0337 | 0.0229 | 0.0052 | 0.0441 | 0.0097 | 0.6620 | 0.0189 | 0.6972 | 0.0163 |
| RELATIVE_B | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 97.5000 | 0.8189 | 0.0280 | 0.0797 | 0.0286 | 0.1443 | 0.0487 | 0.8294 | 0.0166 | 0.8597 | 0.0114 |
| RELATIVE_B | 10 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 97.5000 | 0.9164 | 0.0198 | 0.1983 | 0.0799 | 0.3211 | 0.1137 | 0.9167 | 0.0125 | 0.9379 | 0.0052 |
| RELATIVE_B | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 97.5000 | 0.3906 | 0.0276 | 0.0108 | 0.0021 | 0.0209 | 0.0039 | 0.5524 | 0.0051 | 0.5814 | 0.0035 |
| RELATIVE_B | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 97.5000 | 0.4231 | 0.0363 | 0.0122 | 0.0010 | 0.0237 | 0.0019 | 0.5915 | 0.0080 | 0.6336 | 0.0048 |
| RELATIVE_B | 10 | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 97.5000 | 0.4529 | 0.0281 | 0.0138 | 0.0016 | 0.0268 | 0.0030 | 0.6209 | 0.0100 | 0.6716 | 0.0058 |
| RELATIVE_B | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | mild | pooled | 97.5000 | 0.9720 | 0.0485 | 0.0690 | 0.0080 | 0.1287 | 0.0139 | 0.9304 | 0.0218 | 0.9623 | 0.0089 |
| RELATIVE_B | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | pooled | 97.5000 | 0.9720 | 0.0485 | 0.0690 | 0.0080 | 0.1287 | 0.0139 | 0.9321 | 0.0222 | 0.9636 | 0.0090 |
| RELATIVE_B | 20 | 100 | 1.0000 | A2_EARLY_VOLTAGE_COLLAPSE | strong | pooled | 97.5000 | 0.9720 | 0.0485 | 0.0690 | 0.0080 | 0.1287 | 0.0139 | 0.9321 | 0.0222 | 0.9636 | 0.0090 |
| RELATIVE_B | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | mild | pooled | 97.5000 | 0.8633 | 0.2367 | 0.0144 | 0.0058 | 0.0282 | 0.0113 | 0.6616 | 0.0421 | 0.6887 | 0.0324 |
| RELATIVE_B | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | moderate | pooled | 97.5000 | 0.9535 | 0.0806 | 0.0606 | 0.0293 | 0.1132 | 0.0516 | 0.8494 | 0.0406 | 0.8802 | 0.0250 |
| RELATIVE_B | 20 | 100 | 1.0000 | A3_THERMAL_ABNORMALITY | strong | pooled | 97.5000 | 0.9827 | 0.0299 | 0.1778 | 0.0821 | 0.2961 | 0.1147 | 0.9375 | 0.0236 | 0.9504 | 0.0136 |
| RELATIVE_B | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | mild | pooled | 97.5000 | 0.8313 | 0.2922 | 0.0057 | 0.0015 | 0.0114 | 0.0029 | 0.5905 | 0.0159 | 0.6256 | 0.0109 |
| RELATIVE_B | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | moderate | pooled | 97.5000 | 0.8261 | 0.3012 | 0.0059 | 0.0012 | 0.0118 | 0.0024 | 0.6289 | 0.0210 | 0.6779 | 0.0152 |
| RELATIVE_B | 20 | 100 | 1.0000 | A4_SENSOR_DRIFT | strong | pooled | 97.5000 | 0.8313 | 0.2922 | 0.0063 | 0.0008 | 0.0124 | 0.0015 | 0.6667 | 0.0248 | 0.7290 | 0.0190 |

The display uses all eligible history windows for the predeclared 100-tree/max_features=1.0 reference. RELATIVE_B/prior5/P97.5 is not shown because it fails the all-seed clean-FPR gate despite its mean being below 5%. Full results for every eligible configuration, seed, family, severity, threshold and A4 channel/sign are in `results/nasa_relative_features/eligible_anomaly_metrics.csv`; cross-seed means and sample SD are in `eligible_anomaly_seed_stability.csv`. Precision/F1/AP use 50% evaluation prevalence, not a real deployment prevalence.

## Artifacts

Detailed results: `results/nasa_relative_features/`. DEVELOPMENT models: `models/development/relative_features/`. Figures: `figures/nasa/relative_features/`. Reproduce with `scripts/validate_nasa_relative_features.py`; standalone builder: `scripts/build_nasa_relative_features.py`. No final-test evaluation or deployment.
