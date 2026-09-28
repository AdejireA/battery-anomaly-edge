> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/nasa_failure_analysis.md`  
> **Archival SHA-256:** `b24d24623d02c3e11cbb476cc9cda2bf635da9d6f8891c2fb5c5e03239172545`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# Phase 4C read-only failure analysis



Only existing saved Phase 4C models, embedded scalers, thresholds, B0007 relative data and synthetic copies were used. No injection, feature recomputation, fitting, calibration, selection or protocol modification occurred. Higher score means more anomalous. All tables refer to development diagnostics.


## Diagnosis

| Family | Ranking quality | Thresholded detection | Main failure mechanism | Implication |
|---|---|---|---|---|
| A1 | Near chance (AP approximately 0.46–0.49 at the reference) | Almost absent | Baseline adaptation / representation failure | A sustained change in degradation rate becomes the new local reference |
| A4 | Weak to moderate; voltage better than temperature | Very low | Baseline adaptation plus detector/representation limitations and conservative operating point | Preserving physical drift does not guarantee separation in this multivariate detector |
| A2 | Excellent clean/anomaly separation; high cross-seed rank correlation | Strongly seed-sensitive | Operating-point calibration instability with score-scale changes | Stable ranking does not imply stable decisions at clean-derived thresholds |
| A3 | Severity dependent, strong substantially better than mild | Low relative to strong-anomaly ranking quality | Mainly operating point for strong anomalies, with genuine score overlap | This is not the near-total signal loss seen for A1 |

A1: all matched saved ramps span 91 cycles. The median final retention effect remaining is 3.33%, 6.11%, and 11.67% for histories 5, 10, and 20 (absorption 96.67%, 93.89%, 88.33%). The added slope effect is completely absorbed at the endpoint for all histories. For a locally linear ramp, the median-baseline lag is approximately (k+1)/2 cycles, so retained ramp effect scales as (k+1)/(2×90). Longer histories retain more physical residual and slow adaptation, but do not preserve the cumulative loss as a lasting anomaly. The strong-retention MAD grows by median factors 2.70, 3.16, and 4.11, further normalizing away the altered trend. Very large peak Δz for k=5 can reflect a large clean residual becoming smaller, not stronger injected abnormality; it is not interchangeable with injected |z|.

A4: the first drift sample has zero injected offset, so its incremental residual is exactly zero although its existing clean residual need not be zero. At the final strong-drift sample, k=5 retains 33.3% of raw drift; k=10 retains approximately 61%; k=20 retains 95.6–99.2% for voltage and 89.4–90.7% for temperature. This is a material window-length effect over the finite 10-cycle sequence, not evidence of long-term resistance to drift. At k=10, strong voltage drift inflates final MAD roughly 15–17 fold, versus approximately 2 fold at k=20. Nevertheless k=20 voltage recall at the fixed reference P97.5 is only 0.24–1.44%, despite AP 0.68–0.76 / ROC-AUC 0.79–0.85. Temperature ranks less well. Thus short-window adaptation is important, but does not by itself explain the remaining weak detection; the multivariate representation/detector and unchanged high operating point also limit sensitivity. These diagnostics cannot causally separate detector architecture from feature representation without a new experiment, which was not performed.

A2: for RELATIVE_B/k=10/100 trees/full features, strong recall at the existing P97.5 is 47.92%, 95.32%, and 66.36% for seeds 42, 123, and 2026; moderate recall is 46.49%, 92.86%, and 64.16%. Strong-anomaly medians are 0.5871, 0.6209, and 0.5945, while thresholds are 0.5898, 0.6004, and 0.5885. The thresholds lie at the 52.08th, 4.68th, and 33.64th percentiles of strong A2 scores, even though each is near the 98th–99th percentile of clean B0007 scores. Between 19.5% and 47.5% of strong scores are within 0.01 of the corresponding threshold. Strong-anomaly Spearman correlations are 0.898–0.923, clean correlations 0.967–0.983, and pooled correlations 0.935–0.953. Ranking is comparatively stable but operating-point calibration is unstable. Rank differences are not zero; the dominant evidence is seed-dependent anomaly score placement relative to the clean tail, rather than collapse of clean/anomaly ranking. It is not just a common affine rescaling, since that alone would preserve threshold decisions.

A3 quick check: at the same k=10 reference, strong AP/ROC-AUC average 0.917/0.938, but recall averages 19.83%. About 27–31% of strong scores lie within the clean P5–P95 interval, and the thresholds are at the 75th–89th percentiles of strong scores. This supports a restrictive operating point plus real overlap, rather than wholesale representation failure. Mild anomalies rank substantially worse (AP about 0.662 / ROC-AUC 0.697), so the strong-anomaly conclusion should not be extended to every severity.


## Definitions and comparison controls

For a matched source cycle, d = injected raw value − clean raw value; Δr = injected unstandardized residual − clean residual; Δb = injected prior median − clean prior median. Thus d = Δr + Δb. The signed retained fraction is Δr/d and absorption is 100(1−Δr/d). Zero-effect onset is undefined, not zero absorption. Values are not clipped: negative/>100% values can arise from nonlinear medians and pre-existing trajectory variation. Actual Δz is reported separately; it also includes changes in the MAD denominator and is not a physical-unit absorption percentage.

Adaptation comparisons use only scenario IDs present at all three history lengths, avoiding different source-onset mixtures. Each saved sequence retains its own evolving injected history; no clean copy is contaminated. No observations beyond the saved sequence are fabricated. Near-clean is the descriptive clean-B0007 z P5–P95 band (not a detector threshold). Return time is the number of cycles after the first excursion until three consecutive samples are inside that band. Never-excursing sequences and right-censored nonreturns have no return time; medians of observed returns alone cannot establish recovery.

Figures use the fixed source onset cycle 50, strong severity, 100 trees / max_features=1 / seed 42. This illustrative reference is not a winning-model selection. A4 figures show positive drift; tables cover both signs and both channels. A1 tables cover all severities and both retention and slope. A2/A3 score diagnostics cover every eligible RELATIVE_B history-10 grid/percentile combination and all three seeds.


## A1 and A4 matched-window adaptation

| anomaly_family | history_window | severity | base_feature | drift_sign | scenarios | raw_peak_median | residual_peak_median | z_peak_median | remaining_final_median | absorbed_final_percent_median | mad_ratio_final_median | ever_outside_fraction | return_observed_fraction | return_cycles_median |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1_ACCELERATED_DEGRADATION | 5 | mild | capacity_retention | 0 | 54 | 0.11619 | 0.0064551 | 188.36 | 0.033333 | 96.667 | 1.5343 | 1 | 1 | 1 |
| A1_ACCELERATED_DEGRADATION | 5 | mild | capacity_slope_5 | 0 | 54 | 0.0024414 | 0.0019531 | 2.7184 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 5 | moderate | capacity_retention | 0 | 54 | 0.23238 | 0.01291 | 198.59 | 0.033333 | 96.667 | 2.024 | 0.37037 | 0.31481 | 1 |
| A1_ACCELERATED_DEGRADATION | 5 | moderate | capacity_slope_5 | 0 | 54 | 0.0048828 | 0.0039062 | 4.7426 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 5 | strong | capacity_retention | 0 | 54 | 0.38731 | 0.020049 | 203.15 | 0.033333 | 96.667 | 2.6969 | 0.11111 | 0.11111 | 1.5 |
| A1_ACCELERATED_DEGRADATION | 5 | strong | capacity_slope_5 | 0 | 54 | 0.008138 | 0.0065104 | 5.2689 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 10 | mild | capacity_retention | 0 | 54 | 0.11619 | 0.011053 | 2.6448 | 0.061111 | 93.889 | 1.6514 | 1 | 1 | 1 |
| A1_ACCELERATED_DEGRADATION | 10 | mild | capacity_slope_5 | 0 | 54 | 0.0024414 | 0.002361 | 2.2868 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 10 | moderate | capacity_retention | 0 | 54 | 0.23238 | 0.020626 | 3.8751 | 0.061111 | 93.889 | 2.2594 | 1 | 1 | 1 |
| A1_ACCELERATED_DEGRADATION | 10 | moderate | capacity_slope_5 | 0 | 54 | 0.0048828 | 0.0045973 | 3.5975 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 10 | strong | capacity_retention | 0 | 54 | 0.38731 | 0.032264 | 4.7406 | 0.061111 | 93.889 | 3.1628 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 10 | strong | capacity_slope_5 | 0 | 54 | 0.008138 | 0.007709 | 5.2502 | -0 | 100 | 1 | 1 | 1 | 3 |
| A1_ACCELERATED_DEGRADATION | 20 | mild | capacity_retention | 0 | 54 | 0.11619 | 0.017508 | 1.1095 | 0.11667 | 88.333 | 1.8413 | 1 | 1 | 1 |
| A1_ACCELERATED_DEGRADATION | 20 | mild | capacity_slope_5 | 0 | 54 | 0.0024414 | 0.0024414 | 1.3932 | -0 | 100 | 1 | 1 | 1 | 2 |
| A1_ACCELERATED_DEGRADATION | 20 | moderate | capacity_retention | 0 | 54 | 0.23238 | 0.033536 | 1.651 | 0.11667 | 88.333 | 2.7383 | 1 | 1 | 7 |
| A1_ACCELERATED_DEGRADATION | 20 | moderate | capacity_slope_5 | 0 | 54 | 0.0048828 | 0.0047772 | 2.3986 | -0 | 100 | 1 | 1 | 1 | 3 |
| A1_ACCELERATED_DEGRADATION | 20 | strong | capacity_retention | 0 | 54 | 0.38731 | 0.053781 | 2.0516 | 0.11667 | 88.333 | 4.113 | 1 | 1 | 9 |
| A1_ACCELERATED_DEGRADATION | 20 | strong | capacity_slope_5 | 0 | 54 | 0.008138 | 0.0078092 | 3.6535 | -0 | 100 | 1 | 1 | 1 | 5 |
| A4_SENSOR_DRIFT | 5 | mild | mean_temp_c | -1 | 139 | 0.46653 | 0.21305 | 4.9225 | 0.33333 | 66.667 | 1.3456 | 0.72662 | 0.48201 | 1 |
| A4_SENSOR_DRIFT | 5 | mild | mean_temp_c | 1 | 139 | 0.46653 | 0.20734 | 3.1317 | 0.33333 | 66.667 | 1.1694 | 0.23741 | 0.21583 | 1 |
| A4_SENSOR_DRIFT | 5 | mild | mean_voltage_v | -1 | 139 | 0.048472 | 0.018523 | 6.3123 | 0.33333 | 66.667 | 4.6275 | 0.65468 | 0.64748 | 2 |
| A4_SENSOR_DRIFT | 5 | mild | mean_voltage_v | 1 | 139 | 0.048472 | 0.018144 | 7.0892 | 0.33333 | 66.667 | 3.3996 | 0.53957 | 0.48201 | 2 |
| A4_SENSOR_DRIFT | 5 | moderate | mean_temp_c | -1 | 139 | 0.93305 | 0.41169 | 4.3566 | 0.33333 | 66.667 | 1.6475 | 0.84892 | 0.67626 | 1 |
| A4_SENSOR_DRIFT | 5 | moderate | mean_temp_c | 1 | 139 | 0.93305 | 0.40168 | 7.4913 | 0.33333 | 66.667 | 1.3403 | 0.16547 | 0.16547 | 2 |
| A4_SENSOR_DRIFT | 5 | moderate | mean_voltage_v | -1 | 139 | 0.096944 | 0.034499 | 8.8501 | 0.33333 | 66.667 | 8.3948 | 0.82014 | 0.82014 | 3 |
| A4_SENSOR_DRIFT | 5 | moderate | mean_voltage_v | 1 | 139 | 0.096944 | 0.034545 | 10.384 | 0.33333 | 66.667 | 7.2544 | 0.73381 | 0.73381 | 2 |
| A4_SENSOR_DRIFT | 5 | strong | mean_temp_c | -1 | 139 | 1.5551 | 0.62871 | 5.524 | 0.33333 | 66.667 | 2.3483 | 0.84892 | 0.67626 | 2 |
| A4_SENSOR_DRIFT | 5 | strong | mean_temp_c | 1 | 139 | 1.5551 | 0.6572 | 13.246 | 0.33333 | 66.667 | 1.8245 | 0.31655 | 0.20863 | 2 |
| A4_SENSOR_DRIFT | 5 | strong | mean_voltage_v | -1 | 139 | 0.16157 | 0.056223 | 12.275 | 0.33333 | 66.667 | 13.015 | 0.93525 | 0.93525 | 3 |
| A4_SENSOR_DRIFT | 5 | strong | mean_voltage_v | 1 | 139 | 0.16157 | 0.056088 | 13.917 | 0.33333 | 66.667 | 12.088 | 0.90647 | 0.90647 | 3 |
| A4_SENSOR_DRIFT | 10 | mild | mean_temp_c | -1 | 139 | 0.46653 | 0.29648 | 1.8949 | 0.60306 | 39.694 | 1.2139 | 0.4964 | 0.28058 | 2 |
| A4_SENSOR_DRIFT | 10 | mild | mean_temp_c | 1 | 139 | 0.46653 | 0.29522 | 1.7402 | 0.59002 | 40.998 | 1.2353 | 0.48921 | 0.30216 | 2 |
| A4_SENSOR_DRIFT | 10 | mild | mean_voltage_v | -1 | 139 | 0.048472 | 0.030534 | 3.8736 | 0.61111 | 38.889 | 5.338 | 0.96403 | 0.76978 | 5 |
| A4_SENSOR_DRIFT | 10 | mild | mean_voltage_v | 1 | 139 | 0.048472 | 0.030152 | 5.3363 | 0.61111 | 38.889 | 3.8355 | 0.99281 | 0.14388 | 5 |
| A4_SENSOR_DRIFT | 10 | moderate | mean_temp_c | -1 | 139 | 0.93305 | 0.59532 | 2.8431 | 0.61371 | 38.629 | 1.8881 | 0.64029 | 0.38849 | 1 |
| A4_SENSOR_DRIFT | 10 | moderate | mean_temp_c | 1 | 139 | 0.93305 | 0.58907 | 2.7872 | 0.60375 | 39.625 | 1.828 | 0.48921 | 0.32374 | 2 |
| A4_SENSOR_DRIFT | 10 | moderate | mean_voltage_v | -1 | 139 | 0.096944 | 0.060155 | 7.3015 | 0.61111 | 38.889 | 10.166 | 1 | 0.83453 | 6 |
| A4_SENSOR_DRIFT | 10 | moderate | mean_voltage_v | 1 | 139 | 0.096944 | 0.060112 | 7.7907 | 0.61111 | 38.889 | 9.2114 | 1 | 0.10072 | 6 |
| A4_SENSOR_DRIFT | 10 | strong | mean_temp_c | -1 | 139 | 1.5551 | 0.98242 | 3.3949 | 0.61111 | 38.889 | 2.9854 | 0.79856 | 0.54676 | 2 |
| A4_SENSOR_DRIFT | 10 | strong | mean_temp_c | 1 | 139 | 1.5551 | 0.98522 | 3.6127 | 0.60669 | 39.331 | 3.0037 | 0.68345 | 0.4964 | 2 |
| A4_SENSOR_DRIFT | 10 | strong | mean_voltage_v | -1 | 139 | 0.16157 | 0.099651 | 11.412 | 0.61111 | 38.889 | 16.938 | 1 | 0.85612 | 6 |
| A4_SENSOR_DRIFT | 10 | strong | mean_voltage_v | 1 | 139 | 0.16157 | 0.099607 | 11.436 | 0.61111 | 38.889 | 15.402 | 1 | 0.064748 | 6 |
| A4_SENSOR_DRIFT | 20 | mild | mean_temp_c | -1 | 139 | 0.46653 | 0.38629 | 1.4081 | 0.8119 | 18.81 | 1.0545 | 0.6259 | 0.32374 | 2 |
| A4_SENSOR_DRIFT | 20 | mild | mean_temp_c | 1 | 139 | 0.46653 | 0.40649 | 1.3067 | 0.87082 | 12.918 | 1.2111 | 0.36691 | 0.20144 | 1 |
| A4_SENSOR_DRIFT | 20 | mild | mean_voltage_v | -1 | 139 | 0.048472 | 0.047341 | 4.5466 | 0.97668 | 2.3319 | 1.8401 | 0.99281 | 0.057554 | 1 |
| A4_SENSOR_DRIFT | 20 | mild | mean_voltage_v | 1 | 139 | 0.048472 | 0.042747 | 5.7523 | 0.88189 | 11.811 | 1.3426 | 1 | 0.028777 | 1 |
| A4_SENSOR_DRIFT | 20 | moderate | mean_temp_c | -1 | 139 | 0.93305 | 0.81556 | 2.5995 | 0.87292 | 12.708 | 1.3249 | 0.82734 | 0.26619 | 2 |
| A4_SENSOR_DRIFT | 20 | moderate | mean_temp_c | 1 | 139 | 0.93305 | 0.80787 | 2.5122 | 0.86584 | 13.416 | 1.4836 | 0.5036 | 0.17266 | 1 |
| A4_SENSOR_DRIFT | 20 | moderate | mean_voltage_v | -1 | 139 | 0.096944 | 0.095786 | 8.378 | 0.98806 | 1.1937 | 2.015 | 1 | 0.014388 | 1 |
| A4_SENSOR_DRIFT | 20 | moderate | mean_voltage_v | 1 | 139 | 0.096944 | 0.090235 | 9.6588 | 0.9308 | 6.92 | 1.7402 | 1 | 0 | nan |
| A4_SENSOR_DRIFT | 20 | strong | mean_temp_c | -1 | 139 | 1.5551 | 1.4101 | 3.9068 | 0.90679 | 9.3209 | 1.6448 | 0.95683 | 0.14388 | 1 |
| A4_SENSOR_DRIFT | 20 | strong | mean_temp_c | 1 | 139 | 1.5551 | 1.3909 | 3.8821 | 0.89443 | 10.557 | 1.8471 | 0.74101 | 0.15827 | 2 |
| A4_SENSOR_DRIFT | 20 | strong | mean_voltage_v | -1 | 139 | 0.16157 | 0.16036 | 13.901 | 0.99248 | 0.75225 | 2.1637 | 1 | 0 | nan |
| A4_SENSOR_DRIFT | 20 | strong | mean_voltage_v | 1 | 139 | 0.16157 | 0.15438 | 14.587 | 0.95551 | 4.4494 | 2.0297 | 1 | 0 | nan |


## A1 return-time qualification

| history_window | severity | base_feature | stable_return_fraction | stable_return_cycles_median | onset_already_outside_fraction |
|---|---|---|---|---|---|
| 5 | mild | capacity_retention | 1 | 1 | 0.018519 |
| 5 | mild | capacity_slope_5 | 0.83333 | 74 | 0.11111 |
| 5 | moderate | capacity_retention | 0.31481 | 1 | 0.018519 |
| 5 | moderate | capacity_slope_5 | 0.83333 | 75 | 0.11111 |
| 5 | strong | capacity_retention | 0.11111 | 1.5 | 0.018519 |
| 5 | strong | capacity_slope_5 | 0.83333 | 76 | 0.11111 |
| 10 | mild | capacity_retention | 0.88889 | 62 | 0.055556 |
| 10 | mild | capacity_slope_5 | 0.7963 | 74 | 0.074074 |
| 10 | moderate | capacity_retention | 0.7963 | 66 | 0.055556 |
| 10 | moderate | capacity_slope_5 | 0.7963 | 78 | 0.074074 |
| 10 | strong | capacity_retention | 0.85185 | 71 | 0.055556 |
| 10 | strong | capacity_slope_5 | 0.7963 | 78 | 0.074074 |
| 20 | mild | capacity_retention | 0.92593 | 59.5 | 0.14815 |
| 20 | mild | capacity_slope_5 | 0.72222 | 73 | 0.074074 |
| 20 | moderate | capacity_retention | 1 | 37 | 0.14815 |
| 20 | moderate | capacity_slope_5 | 0.72222 | 74 | 0.074074 |
| 20 | strong | capacity_retention | 1 | 10 | 0.14815 |
| 20 | strong | capacity_slope_5 | 0.72222 | 74 | 0.074074 |

The first-three-inside return times in the adaptation table can be temporary. This additional table requires all remaining saved samples to stay inside the clean range, with at least three remaining samples. Onset-already-outside flags reveal clean outliers present before any injected offset; return times are descriptive trajectory timings, not proof that injection caused every excursion. Sequences without an observed sustained return remain censored. No post-ramp recovery is inferred.


## A2 moderate/strong seed diagnostics: fixed 100-tree/full-feature reference

| severity | seed | threshold | clean_median | clean_p95 | synthetic_median | synthetic_p05 | synthetic_p95 | recall | threshold_clean_percentile | threshold_synthetic_percentile | threshold_clean_z | synthetic_within_001_threshold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moderate | 42 | 0.58979 | 0.37064 | 0.52504 | 0.5863 | 0.56087 | 0.64624 | 0.46494 | 98.101 | 53.506 | 3.499 | 0.25844 |
| moderate | 123 | 0.60043 | 0.38286 | 0.52503 | 0.62077 | 0.59976 | 0.66679 | 0.92857 | 98.101 | 7.1429 | 3.6751 | 0.2026 |
| moderate | 2026 | 0.58846 | 0.38057 | 0.50884 | 0.59373 | 0.57541 | 0.66032 | 0.64156 | 98.734 | 35.844 | 3.5774 | 0.45974 |
| strong | 42 | 0.58979 | 0.37064 | 0.52504 | 0.58711 | 0.56293 | 0.64624 | 0.47922 | 98.101 | 52.078 | 3.499 | 0.26364 |
| strong | 123 | 0.60043 | 0.38286 | 0.52503 | 0.62089 | 0.60091 | 0.66679 | 0.95325 | 98.101 | 4.6753 | 3.6751 | 0.19481 |
| strong | 2026 | 0.58846 | 0.38057 | 0.50884 | 0.59455 | 0.57814 | 0.66032 | 0.66364 | 98.734 | 33.636 | 3.5774 | 0.47532 |

Threshold-to-distribution positions are empirical percentages at or below the unchanged threshold. Synthetic score multiplicity reflects the original overlapping windows; these are not independent biological replicates. The ±0.01 score band is descriptive only, in model-specific score units.


## Rank stability on identical observations

| n_estimators | max_features | anomaly_family | severity | seed_a | seed_b | region | spearman |
|---|---|---|---|---|---|---|---|
| 100 | 0.75 | A2 | moderate | 42 | 123 | clean | 0.94333 |
| 100 | 0.75 | A2 | moderate | 42 | 123 | synthetic | 0.94262 |
| 100 | 0.75 | A2 | moderate | 42 | 123 | pooled | 0.96618 |
| 100 | 0.75 | A2 | moderate | 42 | 2026 | clean | 0.95287 |
| 100 | 0.75 | A2 | moderate | 42 | 2026 | synthetic | 0.92611 |
| 100 | 0.75 | A2 | moderate | 42 | 2026 | pooled | 0.95627 |
| 100 | 0.75 | A2 | moderate | 123 | 2026 | clean | 0.97397 |
| 100 | 0.75 | A2 | moderate | 123 | 2026 | synthetic | 0.95156 |
| 100 | 0.75 | A2 | moderate | 123 | 2026 | pooled | 0.9717 |
| 100 | 0.75 | A2 | strong | 42 | 123 | clean | 0.94333 |
| 100 | 0.75 | A2 | strong | 42 | 123 | synthetic | 0.94917 |
| 100 | 0.75 | A2 | strong | 42 | 123 | pooled | 0.96998 |
| 100 | 0.75 | A2 | strong | 42 | 2026 | clean | 0.95287 |
| 100 | 0.75 | A2 | strong | 42 | 2026 | synthetic | 0.92846 |
| 100 | 0.75 | A2 | strong | 42 | 2026 | pooled | 0.95756 |
| 100 | 0.75 | A2 | strong | 123 | 2026 | clean | 0.97397 |
| 100 | 0.75 | A2 | strong | 123 | 2026 | synthetic | 0.95089 |
| 100 | 0.75 | A2 | strong | 123 | 2026 | pooled | 0.9713 |
| 100 | 1 | A2 | moderate | 42 | 123 | clean | 0.98349 |
| 100 | 1 | A2 | moderate | 42 | 123 | synthetic | 0.90237 |
| 100 | 1 | A2 | moderate | 42 | 123 | pooled | 0.93806 |
| 100 | 1 | A2 | moderate | 42 | 2026 | clean | 0.97163 |
| 100 | 1 | A2 | moderate | 42 | 2026 | synthetic | 0.92468 |
| 100 | 1 | A2 | moderate | 42 | 2026 | pooled | 0.95404 |
| 100 | 1 | A2 | moderate | 123 | 2026 | clean | 0.96651 |
| 100 | 1 | A2 | moderate | 123 | 2026 | synthetic | 0.9217 |
| 100 | 1 | A2 | moderate | 123 | 2026 | pooled | 0.95262 |
| 100 | 1 | A2 | strong | 42 | 123 | clean | 0.98349 |
| 100 | 1 | A2 | strong | 42 | 123 | synthetic | 0.89836 |
| 100 | 1 | A2 | strong | 42 | 123 | pooled | 0.93545 |
| 100 | 1 | A2 | strong | 42 | 2026 | clean | 0.97163 |
| 100 | 1 | A2 | strong | 42 | 2026 | synthetic | 0.92288 |
| 100 | 1 | A2 | strong | 42 | 2026 | pooled | 0.95289 |
| 100 | 1 | A2 | strong | 123 | 2026 | clean | 0.96651 |
| 100 | 1 | A2 | strong | 123 | 2026 | synthetic | 0.91132 |
| 100 | 1 | A2 | strong | 123 | 2026 | pooled | 0.94653 |
| 200 | 0.75 | A2 | moderate | 42 | 123 | clean | 0.97724 |
| 200 | 0.75 | A2 | moderate | 42 | 123 | synthetic | 0.9478 |
| 200 | 0.75 | A2 | moderate | 42 | 123 | pooled | 0.96917 |
| 200 | 0.75 | A2 | moderate | 42 | 2026 | clean | 0.98543 |
| 200 | 0.75 | A2 | moderate | 42 | 2026 | synthetic | 0.97509 |
| 200 | 0.75 | A2 | moderate | 42 | 2026 | pooled | 0.98481 |
| 200 | 0.75 | A2 | moderate | 123 | 2026 | clean | 0.9848 |
| 200 | 0.75 | A2 | moderate | 123 | 2026 | synthetic | 0.96072 |
| 200 | 0.75 | A2 | moderate | 123 | 2026 | pooled | 0.97733 |
| 200 | 0.75 | A2 | strong | 42 | 123 | clean | 0.97724 |
| 200 | 0.75 | A2 | strong | 42 | 123 | synthetic | 0.95242 |
| 200 | 0.75 | A2 | strong | 42 | 123 | pooled | 0.97182 |
| 200 | 0.75 | A2 | strong | 42 | 2026 | clean | 0.98543 |
| 200 | 0.75 | A2 | strong | 42 | 2026 | synthetic | 0.97313 |
| 200 | 0.75 | A2 | strong | 42 | 2026 | pooled | 0.98368 |
| 200 | 0.75 | A2 | strong | 123 | 2026 | clean | 0.9848 |
| 200 | 0.75 | A2 | strong | 123 | 2026 | synthetic | 0.96545 |
| 200 | 0.75 | A2 | strong | 123 | 2026 | pooled | 0.98008 |
| 200 | 1 | A2 | moderate | 42 | 123 | clean | 0.98008 |
| 200 | 1 | A2 | moderate | 42 | 123 | synthetic | 0.93294 |
| 200 | 1 | A2 | moderate | 42 | 123 | pooled | 0.95852 |
| 200 | 1 | A2 | moderate | 42 | 2026 | clean | 0.98261 |
| 200 | 1 | A2 | moderate | 42 | 2026 | synthetic | 0.96204 |
| 200 | 1 | A2 | moderate | 42 | 2026 | pooled | 0.97794 |
| 200 | 1 | A2 | moderate | 123 | 2026 | clean | 0.97888 |
| 200 | 1 | A2 | moderate | 123 | 2026 | synthetic | 0.92995 |
| 200 | 1 | A2 | moderate | 123 | 2026 | pooled | 0.95792 |
| 200 | 1 | A2 | strong | 42 | 123 | clean | 0.98008 |
| 200 | 1 | A2 | strong | 42 | 123 | synthetic | 0.93892 |
| 200 | 1 | A2 | strong | 42 | 123 | pooled | 0.96175 |
| 200 | 1 | A2 | strong | 42 | 2026 | clean | 0.98261 |
| 200 | 1 | A2 | strong | 42 | 2026 | synthetic | 0.96058 |
| 200 | 1 | A2 | strong | 42 | 2026 | pooled | 0.97712 |
| 200 | 1 | A2 | strong | 123 | 2026 | clean | 0.97888 |
| 200 | 1 | A2 | strong | 123 | 2026 | synthetic | 0.93681 |
| 200 | 1 | A2 | strong | 123 | 2026 | pooled | 0.96168 |

Synthetic rows are aligned by scenario ID and source cycle; clean rows are aligned by cycle. Pooled rank correlation is also supplied because within-anomaly rankings and clean-versus-anomaly separation answer different questions. Ties are handled by Spearman average ranks.


## Existing eligible reference metrics

| feature_set | history_window | anomaly_family | severity | recall_mean | recall_std | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std |
|---|---|---|---|---|---|---|---|---|---|
| RELATIVE_A | 5 | A1_ACCELERATED_DEGRADATION | mild | 0.0050456 | 9.2971e-05 | 0.46109 | 0.0011279 | 0.44981 | 0.0022152 |
| RELATIVE_A | 5 | A1_ACCELERATED_DEGRADATION | moderate | 0.0049919 | 0.00016103 | 0.46018 | 0.00099015 | 0.44787 | 0.0026637 |
| RELATIVE_A | 5 | A1_ACCELERATED_DEGRADATION | strong | 0.0048309 | 0.00016103 | 0.46081 | 0.00073297 | 0.4501 | 0.0030773 |
| RELATIVE_A | 5 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.025806 | 0.003871 | 0.66047 | 0.0012849 | 0.69514 | 0.0018975 |
| RELATIVE_A | 5 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.051183 | 0.012264 | 0.71525 | 0.0066014 | 0.7234 | 0.0021697 |
| RELATIVE_A | 5 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.071398 | 0.018713 | 0.74263 | 0.009989 | 0.73787 | 0.0028761 |
| RELATIVE_A | 5 | A3_THERMAL_ABNORMALITY | mild | 0.020645 | 0.0034139 | 0.54005 | 0.0026534 | 0.5761 | 0.0041082 |
| RELATIVE_A | 5 | A3_THERMAL_ABNORMALITY | moderate | 0.026237 | 0.0041478 | 0.57832 | 0.0048702 | 0.61952 | 0.005687 |
| RELATIVE_A | 5 | A3_THERMAL_ABNORMALITY | strong | 0.030108 | 0.0014899 | 0.60941 | 0.0066745 | 0.65119 | 0.0060379 |
| RELATIVE_A | 5 | A4_SENSOR_DRIFT | mild | 0.018889 | 0.0033995 | 0.49807 | 0.0010188 | 0.50694 | 0.0031255 |
| RELATIVE_A | 5 | A4_SENSOR_DRIFT | moderate | 0.019691 | 0.0025279 | 0.50328 | 0.0022259 | 0.51847 | 0.0038256 |
| RELATIVE_A | 5 | A4_SENSOR_DRIFT | strong | 0.020864 | 0.0021463 | 0.51552 | 0.0025276 | 0.53791 | 0.0040428 |
| RELATIVE_A | 10 | A1_ACCELERATED_DEGRADATION | mild | 0 | 0 | 0.48297 | 0.0028422 | 0.48057 | 0.0064699 |
| RELATIVE_A | 10 | A1_ACCELERATED_DEGRADATION | moderate | 0 | 0 | 0.4884 | 0.0046529 | 0.49163 | 0.0093952 |
| RELATIVE_A | 10 | A1_ACCELERATED_DEGRADATION | strong | 0 | 0 | 0.4922 | 0.0053965 | 0.49917 | 0.01033 |
| RELATIVE_A | 10 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.24133 | 0.075625 | 0.97545 | 0.0063317 | 0.98106 | 0.0034118 |
| RELATIVE_A | 10 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.308 | 0.099662 | 0.9869 | 0.0056036 | 0.99146 | 0.0028664 |
| RELATIVE_A | 10 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.31644 | 0.10654 | 0.98829 | 0.0056386 | 0.99265 | 0.0028553 |
| RELATIVE_A | 10 | A3_THERMAL_ABNORMALITY | mild | 0.0093333 | 0.0023094 | 0.63989 | 0.024289 | 0.6868 | 0.019204 |
| RELATIVE_A | 10 | A3_THERMAL_ABNORMALITY | moderate | 0.014667 | 0.0053333 | 0.78756 | 0.036034 | 0.8399 | 0.022076 |
| RELATIVE_A | 10 | A3_THERMAL_ABNORMALITY | strong | 0.031111 | 0.010096 | 0.86898 | 0.036263 | 0.91352 | 0.018002 |
| RELATIVE_A | 10 | A4_SENSOR_DRIFT | mild | 0.0024266 | 0.002608 | 0.5583 | 0.0027602 | 0.59197 | 0.0010002 |
| RELATIVE_A | 10 | A4_SENSOR_DRIFT | moderate | 0.0029374 | 0.0026429 | 0.59732 | 0.0043346 | 0.6409 | 0.0021045 |
| RELATIVE_A | 10 | A4_SENSOR_DRIFT | strong | 0.0035121 | 0.0031903 | 0.62494 | 0.0053963 | 0.67534 | 0.0033944 |
| RELATIVE_A | 20 | A1_ACCELERATED_DEGRADATION | mild | 0.021742 | 0.0051659 | 0.47255 | 0.0026335 | 0.45353 | 0.0059703 |
| RELATIVE_A | 20 | A1_ACCELERATED_DEGRADATION | moderate | 0.021399 | 0.0051564 | 0.47545 | 0.0044158 | 0.45804 | 0.0085447 |
| RELATIVE_A | 20 | A1_ACCELERATED_DEGRADATION | strong | 0.02085 | 0.004944 | 0.48299 | 0.0033595 | 0.46713 | 0.007134 |
| RELATIVE_A | 20 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.26 | 0.087563 | 0.90204 | 0.018131 | 0.96061 | 0.008987 |
| RELATIVE_A | 20 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.26476 | 0.090185 | 0.90274 | 0.017997 | 0.96081 | 0.0089526 |
| RELATIVE_A | 20 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.26476 | 0.090185 | 0.90274 | 0.017997 | 0.96081 | 0.0089526 |
| RELATIVE_A | 20 | A3_THERMAL_ABNORMALITY | mild | 0.020476 | 0.0043644 | 0.5894 | 0.011996 | 0.63648 | 0.0059861 |
| RELATIVE_A | 20 | A3_THERMAL_ABNORMALITY | moderate | 0.03619 | 0.010135 | 0.73088 | 0.01853 | 0.81372 | 0.012109 |
| RELATIVE_A | 20 | A3_THERMAL_ABNORMALITY | strong | 0.06 | 0.012206 | 0.80884 | 0.01725 | 0.88881 | 0.0092514 |
| RELATIVE_A | 20 | A4_SENSOR_DRIFT | mild | 0.028258 | 0.0059683 | 0.58007 | 0.0051035 | 0.61348 | 0.00703 |
| RELATIVE_A | 20 | A4_SENSOR_DRIFT | moderate | 0.030453 | 0.0048649 | 0.61124 | 0.0076595 | 0.65647 | 0.0093017 |
| RELATIVE_A | 20 | A4_SENSOR_DRIFT | strong | 0.031962 | 0.0053432 | 0.63659 | 0.0091712 | 0.69428 | 0.012524 |
| RELATIVE_B | 10 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.53247 | 0.19905 | 0.97183 | 0.013987 | 0.97926 | 0.0056827 |
| RELATIVE_B | 10 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.67835 | 0.234 | 0.9829 | 0.014134 | 0.99022 | 0.0063214 |
| RELATIVE_B | 10 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.6987 | 0.23895 | 0.98409 | 0.014005 | 0.99117 | 0.0063899 |
| RELATIVE_B | 10 | A3_THERMAL_ABNORMALITY | mild | 0.022944 | 0.0052486 | 0.66203 | 0.018931 | 0.69722 | 0.016333 |
| RELATIVE_B | 10 | A3_THERMAL_ABNORMALITY | moderate | 0.079654 | 0.028611 | 0.82938 | 0.016573 | 0.85975 | 0.011404 |
| RELATIVE_B | 10 | A3_THERMAL_ABNORMALITY | strong | 0.19827 | 0.07986 | 0.91666 | 0.012543 | 0.93791 | 0.0052333 |
| RELATIVE_B | 10 | A4_SENSOR_DRIFT | mild | 0.010751 | 0.0020535 | 0.5524 | 0.0050822 | 0.58144 | 0.0034984 |
| RELATIVE_B | 10 | A4_SENSOR_DRIFT | moderate | 0.01218 | 0.0010268 | 0.59152 | 0.008037 | 0.63361 | 0.0048242 |
| RELATIVE_B | 10 | A4_SENSOR_DRIFT | strong | 0.013796 | 0.0016252 | 0.62087 | 0.0099646 | 0.67164 | 0.0058491 |
| RELATIVE_B | 20 | A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.068981 | 0.0080188 | 0.93044 | 0.021786 | 0.96232 | 0.0088843 |
| RELATIVE_B | 20 | A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.068981 | 0.0080188 | 0.93213 | 0.022165 | 0.96359 | 0.0089895 |
| RELATIVE_B | 20 | A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.068981 | 0.0080188 | 0.93214 | 0.022164 | 0.96359 | 0.0089895 |
| RELATIVE_B | 20 | A3_THERMAL_ABNORMALITY | mild | 0.014352 | 0.0057824 | 0.66162 | 0.042132 | 0.68868 | 0.032402 |
| RELATIVE_B | 20 | A3_THERMAL_ABNORMALITY | moderate | 0.060648 | 0.029343 | 0.84943 | 0.04062 | 0.88016 | 0.025014 |
| RELATIVE_B | 20 | A3_THERMAL_ABNORMALITY | strong | 0.17778 | 0.082086 | 0.93745 | 0.023554 | 0.95039 | 0.013608 |
| RELATIVE_B | 20 | A4_SENSOR_DRIFT | mild | 0.0057288 | 0.0014999 | 0.59053 | 0.015875 | 0.62563 | 0.010893 |
| RELATIVE_B | 20 | A4_SENSOR_DRIFT | moderate | 0.0059286 | 0.001221 | 0.62892 | 0.021014 | 0.67791 | 0.015154 |
| RELATIVE_B | 20 | A4_SENSOR_DRIFT | strong | 0.0062617 | 0.00075658 | 0.66672 | 0.024826 | 0.72898 | 0.019007 |

PR-AUC is the saved class-balanced average precision (50/50 class weight), not raw prevalence-weighted AP. ROC-AUC uses the saved evaluation. The full score/threshold CSV includes A3 overlap: fraction of injected scores in clean P5–P95. No supervised metrics were used to choose a configuration or threshold.


## Integrity verification

All 127 protected files have identical before/after SHA-256 digests. This includes 96 development model/scaler bundles, the frozen configuration files, existing relative-result artifacts (including thresholds and synthetic copies), and explicitly named B0005/B0006/B0007 processed files. B0018 and the combined source CSV were never opened, including for hashing. A runtime audit guard blocked forbidden data paths and writes outside the new diagnostic outputs. Scaler fit/partial_fit and Isolation Forest fit were blocked during scoring. Full evidence: `results/nasa_failure_analysis/integrity_checks.json`.


## Outputs

New diagnostic source: `scripts/diagnose_nasa_failures.py`. Report: `results/nasa_failure_analysis.md`. Diagnostic tables and integrity evidence: `results/nasa_failure_analysis/`. Figures: `figures/nasa/failure_analysis/a1_baseline_absorption.png`, `a4_drift_absorption.png`, `a2_seed_score_distributions.png`, `a2_threshold_overlap.png`. No experimental artifact was modified.

## Additional residual detail

Retention is a dimensionless fraction; capacity slope is Ah/cycle; voltage is V; temperature is degrees Celsius; robust residual z is dimensionless. Effect columns compare the injected value with its identical clean source cycle. Injected-residual columns give the actual residual rather than its change. Medians below are across matched scenarios, separately by sign.

| history_window | severity | base_feature | drift_sign | residual_effect_first | residual_effect_peak | residual_effect_final | injected_residual_first | injected_residual_peak_abs | injected_residual_final | remaining_fraction_final |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | mild | mean_temp_c | -1 | 0 | 0.21305 | -0.15551 | -0.01648 | 0.50616 | -0.13813 | 0.33333 |
| 5 | mild | mean_temp_c | 1 | 0 | 0.20734 | 0.15551 | -0.01648 | 0.54078 | 0.17168 | 0.33333 |
| 5 | mild | mean_voltage_v | -1 | 0 | 0.018523 | -0.016157 | -0.0032019 | 0.023571 | -0.019057 | 0.33333 |
| 5 | mild | mean_voltage_v | 1 | 0 | 0.018144 | 0.016157 | -0.0032019 | 0.018777 | 0.013152 | 0.33333 |
| 5 | moderate | mean_temp_c | -1 | 0 | 0.41169 | -0.31102 | -0.01648 | 0.60295 | -0.30804 | 0.33333 |
| 5 | moderate | mean_temp_c | 1 | 0 | 0.40168 | 0.31102 | -0.01648 | 0.69651 | 0.32719 | 0.33333 |
| 5 | moderate | mean_voltage_v | -1 | 0 | 0.034499 | -0.032315 | -0.0032019 | 0.04025 | -0.035238 | 0.33333 |
| 5 | moderate | mean_voltage_v | 1 | 0 | 0.034545 | 0.032315 | -0.0032019 | 0.034959 | 0.029386 | 0.33333 |
| 5 | strong | mean_temp_c | -1 | 0 | 0.62871 | -0.51836 | -0.01648 | 0.83975 | -0.49645 | 0.33333 |
| 5 | strong | mean_temp_c | 1 | 0 | 0.6572 | 0.51836 | -0.01648 | 0.93742 | 0.53454 | 0.33333 |
| 5 | strong | mean_voltage_v | -1 | 0 | 0.056223 | -0.053858 | -0.0032019 | 0.061997 | -0.056786 | 0.33333 |
| 5 | strong | mean_voltage_v | 1 | 0 | 0.056088 | 0.053858 | -0.0032019 | 0.056502 | 0.050929 | 0.33333 |
| 10 | mild | mean_temp_c | -1 | 0 | 0.29648 | -0.28134 | 0.019598 | 0.51882 | -0.21809 | 0.60306 |
| 10 | mild | mean_temp_c | 1 | 0 | 0.29522 | 0.27526 | 0.019598 | 0.58434 | 0.31325 | 0.59002 |
| 10 | mild | mean_voltage_v | -1 | 0 | 0.030534 | -0.029622 | -0.0041675 | 0.037298 | -0.035142 | 0.61111 |
| 10 | mild | mean_voltage_v | 1 | 0 | 0.030152 | 0.029622 | -0.0041675 | 0.026818 | 0.023985 | 0.61111 |
| 10 | moderate | mean_temp_c | -1 | 0 | 0.59532 | -0.57262 | 0.019598 | 0.74143 | -0.50542 | 0.61371 |
| 10 | moderate | mean_temp_c | 1 | 0 | 0.58907 | 0.56333 | 0.019598 | 0.78992 | 0.60935 | 0.60375 |
| 10 | moderate | mean_voltage_v | -1 | 0 | 0.060155 | -0.059243 | -0.0041675 | 0.067066 | -0.064763 | 0.61111 |
| 10 | moderate | mean_voltage_v | 1 | 0 | 0.060112 | 0.059243 | -0.0041675 | 0.056439 | 0.053696 | 0.61111 |
| 10 | strong | mean_temp_c | -1 | 0 | 0.98242 | -0.95033 | 0.019598 | 1.0996 | -0.87927 | 0.61111 |
| 10 | strong | mean_temp_c | 1 | 0 | 0.98522 | 0.94346 | 0.019598 | 1.1344 | 1.0112 | 0.60669 |
| 10 | strong | mean_voltage_v | -1 | 0 | 0.099651 | -0.098739 | -0.0041675 | 0.10656 | -0.10429 | 0.61111 |
| 10 | strong | mean_voltage_v | 1 | 0 | 0.099607 | 0.098739 | -0.0041675 | 0.095935 | 0.093192 | 0.61111 |
| 20 | mild | mean_temp_c | -1 | 0 | 0.38629 | -0.37877 | 0.070104 | 0.62879 | -0.26266 | 0.8119 |
| 20 | mild | mean_temp_c | 1 | 0 | 0.40649 | 0.40626 | 0.070104 | 0.70354 | 0.46247 | 0.87082 |
| 20 | mild | mean_voltage_v | -1 | 0 | 0.047341 | -0.047341 | -0.0073899 | 0.054603 | -0.054392 | 0.97668 |
| 20 | mild | mean_voltage_v | 1 | 0 | 0.042747 | 0.042747 | -0.0073899 | 0.036198 | 0.035961 | 0.88189 |
| 20 | moderate | mean_temp_c | -1 | 0 | 0.81556 | -0.81448 | 0.070104 | 0.9449 | -0.64969 | 0.87292 |
| 20 | moderate | mean_temp_c | 1 | 0 | 0.80787 | 0.80787 | 0.070104 | 1.0031 | 0.89307 | 0.86584 |
| 20 | moderate | mean_voltage_v | -1 | 0 | 0.095786 | -0.095786 | -0.0073899 | 0.10286 | -0.10286 | 0.98806 |
| 20 | moderate | mean_voltage_v | 1 | 0 | 0.090235 | 0.090235 | -0.0073899 | 0.083436 | 0.083436 | 0.9308 |
| 20 | strong | mean_temp_c | -1 | 0 | 1.4101 | -1.4101 | 0.070104 | 1.4386 | -1.2424 | 0.90679 |
| 20 | strong | mean_temp_c | 1 | 0 | 1.3909 | 1.3909 | 0.070104 | 1.5363 | 1.4636 | 0.89443 |
| 20 | strong | mean_voltage_v | -1 | 0 | 0.16036 | -0.16036 | -0.0073899 | 0.16749 | -0.16749 | 0.99248 |
| 20 | strong | mean_voltage_v | 1 | 0 | 0.15438 | 0.15438 | -0.0073899 | 0.14741 | 0.14741 | 0.95551 |

### A4 channel-specific existing metrics

Seed means at the fixed reference P97.5, for already eligible configurations only.

| history_window | variant | recall | pr_auc | roc_auc |
|---|---|---|---|---|
| 10 | mean_temp_c_-1 | 0.0054686 | 0.52792 | 0.55685 |
| 10 | mean_temp_c_1 | 0.015411 | 0.5766 | 0.62923 |
| 10 | mean_voltage_v_-1 | 0.01566 | 0.67145 | 0.72363 |
| 10 | mean_voltage_v_1 | 0.018643 | 0.69954 | 0.77686 |
| 10 | pooled | 0.013796 | 0.62087 | 0.67164 |
| 20 | mean_temp_c_-1 | 0.00053291 | 0.56073 | 0.59233 |
| 20 | mean_temp_c_1 | 0.0077272 | 0.65091 | 0.69224 |
| 20 | mean_voltage_v_-1 | 0.014388 | 0.75902 | 0.84598 |
| 20 | mean_voltage_v_1 | 0.0023981 | 0.68312 | 0.78539 |
| 20 | pooled | 0.0062617 | 0.66672 | 0.72898 |

Additional diagnostic safety tests: `tests/test_nasa_failure_analysis.py`. No protocol changes are recommended or selected in this diagnostic report.


## Completed verification

Five diagnostic safety tests passed. All six PNG figures passed image-integrity checks. All 127 protected artifact hashes remained unchanged after final rendering. Verification evidence: results/nasa_failure_analysis/verification_results.json.
