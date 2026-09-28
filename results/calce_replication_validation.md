> **Historical Research Report — Public Derivative**  
> **Archival Source:** `results/calce_replication_validation.md`  
> **Archival SHA-256:** `f96eb8d01c0dbfdaa27eaf48f1fc4924b9619af50dbaba245f6c61b622635ef4`  
> **Context & Scope:** This document is a sanitized public derivative of an executed historical research report. All reported experimental metrics, thresholds, splits, parameters, and scientific findings are preserved exactly as originally generated. Certain referenced artifacts (such as serialized `.joblib` model/scaler binaries, raw/processed per-cycle observation tables under `data/processed/`, detailed per-cycle score files, and visualization figures) are retained exclusively in the archival research workspace and are omitted from this compact public reconstruction.

# Independent CALCE replication validation

Train: CS2-35/36; validation: CS2-37; CS2-38 remains locked. Effective training rows: {'CS2-35': 254, 'CS2-36': 281} (535 total). Nominal boundaries are cycles 264 and 291; cycles 1–10 are dropped after applying those boundaries. Usable validation: 1026 (cycles 11–1036). The separate relative table contains only the three development cells, not the held-out cell.

Fresh StandardScaler and Isolation Forest fits use only four prior-10 robust residuals on nominal training rows. No NASA fitted artifact, threshold or anomaly magnitude is reused. Capacity and metadata never enter fitting. Scores are minus score_samples; decisions use score > threshold. No imputation or burn-in recalibration occurs.

## Clean-only thresholds

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

## Seed stability

| percentile | mean | std | min | max |
|---|---|---|---|---|
| 95 | 0.031514 | 0.005368 | 0.0253411 | 0.0350877 |
| 97.5 | 0.014295 | 0.00112544 | 0.0136452 | 0.0155945 |
| 99 | 0.00454841 | 0.00056272 | 0.00389864 | 0.00487329 |

First all-seed eligible percentile: 95. Eligible for development review only. No final configuration or test access is authorized automatically.

## Training versus validation scores

| seed | region | count | mean | std | p05 | median | p95 | minimum | maximum |
|---|---|---|---|---|---|---|---|---|---|
| 42 | nominal_training | 535 | 0.377566 | 0.0889278 | 0.323047 | 0.338614 | 0.595563 | 0.320888 | 0.749668 |
| 42 | CS2-37 | 1026 | 0.367499 | 0.0710945 | 0.323087 | 0.33968 | 0.52346 | 0.320392 | 0.750683 |
| 123 | nominal_training | 535 | 0.37976 | 0.0885806 | 0.325743 | 0.341035 | 0.594081 | 0.323065 | 0.755369 |
| 123 | CS2-37 | 1026 | 0.371607 | 0.0729201 | 0.326209 | 0.342711 | 0.531046 | 0.322625 | 0.751115 |
| 2026 | nominal_training | 535 | 0.376991 | 0.0873311 | 0.322147 | 0.340767 | 0.580072 | 0.319761 | 0.750607 |
| 2026 | CS2-37 | 1026 | 0.36903 | 0.0727921 | 0.322159 | 0.34118 | 0.53203 | 0.31924 | 0.756802 |

## Early-to-late validation score drift

| seed | early_mean | late_mean | late_minus_early | early_median | late_median |
|---|---|---|---|---|---|
| 42 | 0.370795 | 0.364335 | -0.0064602 | 0.337148 | 0.344418 |
| 123 | 0.375033 | 0.367602 | -0.00743084 | 0.340417 | 0.346778 |
| 2026 | 0.37167 | 0.366705 | -0.00496574 | 0.337554 | 0.348729 |

First/last thirds use usable chronological rows. Small or negative drift is not proof of stationarity; transient clean spikes remain visible.

## Remaining robust feature shift

| feature | training_median | validation_median | training_MAD | validation_MAD | shift_in_training_MAD |
|---|---|---|---|---|---|
| duration_s_prior10_robust_residual | -0.673126 | -0.680897 | 1.06924 | 1.15756 | -0.00726733 |
| time_to_3_4v_s_prior10_robust_residual | -0.411713 | -0.451342 | 1.168 | 1.17211 | -0.0339295 |
| mean_voltage_v_prior10_robust_residual | 0.140926 | -0.00245292 | 0.981576 | 1.00782 | -0.14607 |
| mean_current_a_prior10_robust_residual | -0.199056 | 0.0914871 | 1.07376 | 0.926333 | 0.270585 |

Shift is (validation median − training median)/training MAD, calculated per relative feature. Near-zero local MAD can create large residual tails; no clipping is performed.

## CALCE-only controlled-anomaly design

{
  "version": "1.0",
  "status": "CALCE_VALIDATION_DERIVED_NO_TEST_ACCESS",
  "calibration_cell": "CS2-37",
  "calibration_rows": 1036,
  "source_sha256": "22e8cb819fa61b6172962515fb21f66c84c53cf1b6acb45a83245ee25df08831",
  "statistics": {
    "duration_s": {
      "median": 3074.818626004475,
      "MAD": 287.265981048542,
      "p05": 1034.532459575712,
      "p95": 3482.9143108322896,
      "minimum": 595.7555930122326,
      "maximum": 3714.914296016226
    },
    "time_to_3_4v_s": {
      "median": 2870.34530232509,
      "MAD": 338.5124807471291,
      "p05": 390.03782281669925,
      "p95": 3322.0246074619977,
      "minimum": 209.7737435422732,
      "maximum": 3526.122675248805
    },
    "mean_voltage_v": {
      "median": 3.61999121758719,
      "MAD": 0.029179482218267383,
      "p05": 3.337686336558798,
      "p95": 3.659322768186046,
      "minimum": 3.306350751356645,
      "maximum": 3.672856949577647
    },
    "mean_current_a": {
      "median": -1.099691321020541,
      "MAD": 3.353640529690782e-05,
      "p05": -1.099777600687483,
      "p95": -1.099615670128084,
      "minimum": -1.099903308826944,
      "maximum": -1.0995860473782408
    }
  },
  "severity": {
    "mild": {
      "multiplier": 1.5,
      "timing_factor": 0.849688696830087,
      "duration_reduction_at_median_s": 462.17999468585407,
      "crossing_reduction_at_median_s": 431.44534294012226,
      "voltage_offset_v": 0.043769223327401074
    },
    "moderate": {
      "multiplier": 3.0,
      "timing_factor": 0.738659782346396,
      "duration_reduction_at_median_s": 803.5737689653652,
      "crossing_reduction_at_median_s": 750.136666050639,
      "voltage_offset_v": 0.08753844665480215
    },
    "strong": {
      "multiplier": 5.0,
      "timing_factor": 0.6290605655934088,
      "duration_reduction_at_median_s": 1140.5714820329517,
      "crossing_reduction_at_median_s": 1064.7242629960847,
      "voltage_offset_v": 0.14589741109133691
    }
  },
  "families": {
    "CALCE_A2_EARLY_VOLTAGE_COLLAPSE": {
      "window_cycles": 5,
      "affected_features": [
        "duration_s",
        "time_to_3_4v_s",
        "mean_voltage_v"
      ],
      "directions": "timing multiplied by shared factor; mean voltage reduced by offset"
    },
    "CALCE_A4_VOLTAGE_SENSOR_DRIFT": {
      "window_cycles": 10,
      "affected_features": [
        "mean_voltage_v"
      ],
      "directions": "separate positive and negative linear ramps from zero to total offset"
    }
  },
  "timing_redesign": "Use factor=1/(1+m*max(MAD/median of both timing features)) instead of subtracting m*MAD: guarantees positive times and preserves crossing<=duration. No fitted/test-derived magnitudes.",
  "physical_guard": "Reject whole scenario if mean voltage leaves original observed min/max voltage envelope, duration/crossing becomes nonpositive or crossing exceeds duration. No clipping.",
  "baseline_rule": "Fresh scenario context; prior injected samples influence later baselines only within that scenario. Current/future excluded.",
  "protected": "All columns except explicitly affected raw features remain unchanged; no capacity or metadata changes"
}

Magnitudes use only CS2-37 raw feature MADs, with 1.5/3/5 multipliers. Shared positive timing contraction preserves crossing<=duration; its nonlinear formulation avoids impossible negative times at large spreads. Voltage offsets use literal m×MAD. Raw-value envelope guards reject whole scenarios, never clip or change magnitudes. Timing reductions at the observed median and observed ranges are recorded above. A4 is a signed monotonic ten-cycle drift, not independent noise. No capacity or metadata modifications are allowed.

## Eligible synthetic evaluation

| seed | family | severity | percentile | synthetic_rows | precision | recall | f1 | pr_auc | roc_auc | clean_fpr | score_count | score_mean | score_std | score_p05 | score_median | score_p95 | score_minimum | score_maximum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 42 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 95 | 5110 | 0.876965 | 0.180626 | 0.299554 | 0.846042 | 0.877926 | 0.0253411 | 5110 | 0.496464 | 0.113317 | 0.349147 | 0.463972 | 0.747779 | 0.320427 | 0.812991 |
| 42 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95 | 5110 | 0.922667 | 0.302348 | 0.45545 | 0.90543 | 0.92734 | 0.0253411 | 5110 | 0.54837 | 0.115187 | 0.382544 | 0.533154 | 0.792355 | 0.32345 | 0.812991 |
| 42 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 95 | 5110 | 0.948296 | 0.464775 | 0.62381 | 0.937956 | 0.953251 | 0.0253411 | 5110 | 0.58918 | 0.112052 | 0.413956 | 0.586834 | 0.794798 | 0.328402 | 0.812991 |
| 42 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 95 | 18306 | 0.45224 | 0.0209221 | 0.039994 | 0.558212 | 0.607189 | 0.0253411 | 18306 | 0.377665 | 0.0679479 | 0.324362 | 0.354251 | 0.528147 | 0.319979 | 0.761256 |
| 42 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 95 | 18306 | 0.492398 | 0.0245821 | 0.0468265 | 0.597018 | 0.668727 | 0.0253411 | 18306 | 0.386013 | 0.0690723 | 0.326716 | 0.36308 | 0.541279 | 0.320392 | 0.770507 |
| 42 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 95 | 18306 | 0.526587 | 0.0281875 | 0.0535106 | 0.631858 | 0.714355 | 0.0253411 | 18306 | 0.395343 | 0.0706532 | 0.329679 | 0.373217 | 0.551762 | 0.320392 | 0.770507 |
| 123 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 95 | 5110 | 0.856448 | 0.203523 | 0.328889 | 0.85044 | 0.879845 | 0.0341131 | 5110 | 0.507394 | 0.115172 | 0.351917 | 0.488787 | 0.752362 | 0.323633 | 0.827419 |
| 123 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95 | 5110 | 0.90749 | 0.334638 | 0.488968 | 0.910193 | 0.931516 | 0.0341131 | 5110 | 0.563171 | 0.111191 | 0.392359 | 0.553668 | 0.788078 | 0.325643 | 0.827979 |
| 123 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 95 | 5110 | 0.934818 | 0.489237 | 0.642317 | 0.940246 | 0.956871 | 0.0341131 | 5110 | 0.601048 | 0.103649 | 0.429037 | 0.591327 | 0.791284 | 0.332363 | 0.827979 |
| 123 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 95 | 18306 | 0.454357 | 0.028406 | 0.0534691 | 0.561677 | 0.613785 | 0.0341131 | 18306 | 0.382722 | 0.0698673 | 0.328294 | 0.358767 | 0.539492 | 0.322617 | 0.751115 |
| 123 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 95 | 18306 | 0.470997 | 0.0303726 | 0.0570652 | 0.600645 | 0.674257 | 0.0341131 | 18306 | 0.391578 | 0.0707466 | 0.330931 | 0.368727 | 0.550669 | 0.322959 | 0.751115 |
| 123 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 95 | 18306 | 0.493317 | 0.0332132 | 0.0622362 | 0.637213 | 0.720011 | 0.0341131 | 18306 | 0.402104 | 0.0724032 | 0.333354 | 0.380566 | 0.562929 | 0.323369 | 0.755375 |
| 2026 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 95 | 5110 | 0.852708 | 0.203131 | 0.328102 | 0.852379 | 0.885131 | 0.0350877 | 5110 | 0.505338 | 0.109817 | 0.356263 | 0.487165 | 0.75051 | 0.319505 | 0.810794 |
| 2026 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 95 | 5110 | 0.906776 | 0.341292 | 0.495927 | 0.909815 | 0.933596 | 0.0350877 | 5110 | 0.556377 | 0.108749 | 0.401531 | 0.539855 | 0.78648 | 0.321271 | 0.810794 |
| 2026 | CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 95 | 5110 | 0.935995 | 0.513112 | 0.662849 | 0.939643 | 0.95673 | 0.0350877 | 5110 | 0.593384 | 0.104453 | 0.4295 | 0.583451 | 0.789145 | 0.33711 | 0.811891 |
| 2026 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 95 | 18306 | 0.475796 | 0.0318475 | 0.059699 | 0.571367 | 0.626749 | 0.0350877 | 18306 | 0.382878 | 0.0702353 | 0.324135 | 0.362321 | 0.539276 | 0.319641 | 0.760833 |
| 2026 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 95 | 18306 | 0.512406 | 0.0368732 | 0.0687957 | 0.614406 | 0.693371 | 0.0350877 | 18306 | 0.39289 | 0.0708992 | 0.327199 | 0.371915 | 0.551541 | 0.3199 | 0.764963 |
| 2026 | CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 95 | 18306 | 0.547128 | 0.0423905 | 0.0786846 | 0.650149 | 0.737908 | 0.0350877 | 18306 | 0.40351 | 0.0725247 | 0.330552 | 0.382536 | 0.567383 | 0.320501 | 0.764963 |

| family | severity | sign | accepted_windows | rejected_windows |
|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 0 | 1022 | 0 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0 | 1022 | 0 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 0 | 1022 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | -1 | 1017 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 1 | 1017 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | -1 | 1017 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 1 | 1017 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | -1 | 1017 | 0 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 1 | 1017 | 0 |

Precision/F1 and average precision (PR-AUC) use 50% evaluation prevalence. ROC-AUC and recall are unweighted within class. A4 variants are pooled across both drift signs. Zero-offset onset rows are not labeled anomalous. Each scenario has isolated causal history; prior injected values can adapt its baseline. Overlapping windows are dependent copies, not independent battery failures. Synthetic deviations are not claimed to be naturally observed faults. None of these metrics enters fitting or threshold choice.

## Integrity

All 260 NASA hashes and all three permitted CALCE source hashes match before/after. A runtime audit blocks CS2-38 and the combined raw feature table, and blocks writes to protected artifacts. Only development models are saved under models/development/calce_replication/. Test-cell access did not occur.

## Development outcome

P95 is the first eligible threshold: clean validation FPR is 2.5341%, 3.4113%, and 3.5088%. P97.5 and P99 also meet the clean requirement but are not preferred under the fixed order. No final model or test evaluation was performed.

Late-minus-early mean scores are -0.00646, -0.00743, and -0.00497; medians increase slightly (about 0.006-0.011). There is no sustained upward mean-score drift in this validation run, but this is not proof of stationarity or a causal comparison with an absolute-feature CALCE model. The largest relative-feature location shift is mean current at +0.271 training MAD; mean voltage is -0.146 MAD. No major median shift remains by these diagnostics.

A2 ranking and recall improve with severity, but strong recall is still only 48.9%. A4 ranking improves modestly while strong recall is 3.46%, close to the mean clean FPR (3.15%); drift detection remains weak. Strong A2 recall has seed SD 2.42 percentage points; strong A4 recall SD is 0.72 points. All planned synthetic windows passed the stated physical guards. These evaluation metrics did not affect threshold selection.

## Synthetic metric seed means and standard deviations

| family | severity | precision_mean | precision_std | recall_mean | recall_std | f1_mean | f1_std | pr_auc_mean | pr_auc_std | roc_auc_mean | roc_auc_std |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | mild | 0.86204 | 0.0130599 | 0.19576 | 0.0131077 | 0.318848 | 0.0167141 | 0.849621 | 0.00324737 | 0.880968 | 0.00373125 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | moderate | 0.912311 | 0.00897584 | 0.326093 | 0.0208305 | 0.480115 | 0.0216418 | 0.908479 | 0.0026479 | 0.930817 | 0.00318598 |
| CALCE_A2_EARLY_VOLTAGE_COLLAPSE | strong | 0.939703 | 0.00746494 | 0.489041 | 0.0241689 | 0.642992 | 0.0195283 | 0.939282 | 0.00118698 | 0.955617 | 0.00205077 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | mild | 0.460798 | 0.0130316 | 0.0270585 | 0.00558594 | 0.051054 | 0.0100721 | 0.563752 | 0.00681856 | 0.615908 | 0.00995139 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | moderate | 0.491934 | 0.020708 | 0.0306093 | 0.00614894 | 0.0575625 | 0.0109931 | 0.604023 | 0.00917323 | 0.678785 | 0.0129309 |
| CALCE_A4_VOLTAGE_SENSOR_DRIFT | strong | 0.522344 | 0.0271553 | 0.034597 | 0.00720192 | 0.0648105 | 0.0127829 | 0.63974 | 0.00940386 | 0.724091 | 0.0122956 |

## Verification completion

All eight CALCE replication tests passed. All five figures passed image validation. NASA hashes and permitted CALCE source hashes remain unchanged. CS2-38 and the combined extraction CSV were never opened. The relative table contains only development cells (2,886 rows); ten initial history rows per cell remain NaN.
