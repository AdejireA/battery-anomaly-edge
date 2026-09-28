# Public Artifact Manifest

## Overview and Publication Model

This repository follows a **source + compact evidence** publication model. The public tree contains:
1. complete research implementation scripts and test modules;
2. immutable scientific configuration files;
3. compact aggregate evidence files (evaluation metrics, threshold summaries, seed stability tables, denominator diagnostics, and distribution summaries);
4. historical model freeze receipts and hash sidecars;
5. sanitized derivatives of internal historical research reports;
6. physical Raspberry Pi 3B+ replay benchmark results, playback validation, execution environment record, and deployment implementation.

The repository deliberately omits raw datasets, detailed per-cycle observation tables, per-observation score files, and serialized model binaries (`.joblib`).

### Historical Receipts and Absent Dependencies

Historical freeze and integrity receipts (such as `models/final_nasa/freeze_receipt.json`, `models/final_calce/freeze_receipt.json`, `results/nasa_final_test/integrity_receipt.json`, and `deployment/pi/results/research_hashes_before.json`) are preserved as immutable historical scientific evidence.

These receipts were generated during experimental execution and record cryptographic hashes of the research environment as it existed at execution time. Some dependencies recorded in these receipts—such as raw dataset files, processed per-cycle observation tables (`data/processed/`), development-model exploration grids, and serialized `.joblib` binaries—remain exclusively in the private research archive.

The receipts have **NOT** been rewritten or truncated to make them artificially describe the smaller public subset. The absence of those omitted dependencies from this Git repository reflects an intentional publication boundary and does not indicate that the historical receipts were incomplete when created. The public repository does not claim to independently satisfy every historical archive-wide hash verification without external datasets.

### Public Reconstruction Documentation

Public documentation files created during repository reconstruction (including root `README.md`, `docs/research-process.md`, `docs/data-acquisition.md`, `docs/reproducibility.md`, `docs/model-card.md`, `docs/workflow.md`, `deployment/pi/README.md`, `requirements.txt`, `.gitignore`, and `pytest.ini`) provide narrative, technical, and reproducibility context for the public repository. These files are outside the frozen historical evidence hash inventory documented below.

---

## 1. Source Code

All source files are copied byte-identically from the research archive.

| Public Path | Archive Source Path | Type | SHA-256 | Role |
|---|---|---|---|---|
| `scripts/analyze_anomaly_ranges.py` | `scripts/analyze_anomaly_ranges.py` | Byte-identical | `6813732348bd5d870853181976f0aa0f83b4a63d01d5ef3ec50fa8959270d609` | Anomaly injection parameter and dynamic range analysis |
| `scripts/analyze_cross_cell_shift.py` | `scripts/analyze_cross_cell_shift.py` | Byte-identical | `407a7f80a319a2acd954b40caaaa7bbaf81f0af87fd608435ba80b6771bf2291` | Cross-cell feature distribution shift diagnostics |
| `scripts/audit_calce_cells.py` | `scripts/audit_calce_cells.py` | Byte-identical | `6358e0df8daf2d13811a3ceed6e5b2fe8240abe12690b296f9b7285334d32af4` | CALCE raw cell structure and cycle boundary audit |
| `scripts/audit_nasa_features.py` | `scripts/audit_nasa_features.py` | Byte-identical | `89571aa48c7baa291032b4cf09cc0698dbdb00ce833a66f6a53e5e5a0a1e54ce` | NASA feature extraction integrity audit |
| `scripts/build_calce_relative_features.py` | `scripts/build_calce_relative_features.py` | Byte-identical | `887464e6767aef2784cd86dcfdc603684fbc13b78c9d46673e980b7fda7a14bb` | CALCE causal trajectory-relative feature transformer |
| `scripts/build_nasa_relative_features.py` | `scripts/build_nasa_relative_features.py` | Byte-identical | `2793b14adf49aaea146bef1b4277fb0304a9fc8587a17d03b4a00998245a8b4a` | NASA causal trajectory-relative feature transformer |
| `scripts/build_nasa_splits.py` | `scripts/build_nasa_splits.py` | Byte-identical | `d55ac5570fcf10fe17b0bfdebb30049737314f89b5d3b88eeee2dad84ffc5d65` | NASA cell splitting and nominal prefix partitioner |
| `scripts/calce_replication.py` | `scripts/calce_replication.py` | Byte-identical | `8e67b1544cbf66f9c98fb008b85eb8a877265f67c78ec6cfb10293f57165d87d` | CALCE methodological replication pipeline |
| `scripts/diagnose_nasa_failures.py` | `scripts/diagnose_nasa_failures.py` | Byte-identical | `33f8725cff7213977caa52b8b994b4b16e5ef02afd722fb84c3c04ac61aeee23` | NASA failure analysis diagnostics for drift and adaptation |
| `scripts/evaluate_final_calce.py` | `scripts/evaluate_final_calce.py` | Byte-identical | `0a30d1d2c21b4593555f6c68773f70f0864f8f39536d0bca974bd21eca36018d` | CALCE final evaluation execution on held-out CS2-38 |
| `scripts/evaluate_nasa_burnin.py` | `scripts/evaluate_nasa_burnin.py` | Byte-identical | `f4e2688b6d58344f48fb85525533a28fd1ae197cfa90f5074dfa2dcd5e835ab4` | NASA burn-in calibration failure evaluation |
| `scripts/extract_calce.py` | `scripts/extract_calce.py` | Byte-identical | `e0c4ca5d73a86a634d9d0223ed1d36f9ddc05d4952da684d8f37dc0c8a6e9aac` | CALCE raw XML workbook cycle extractor |
| `scripts/extract_calce_cs2_35.py` | `scripts/extract_calce_cs2_35.py` | Byte-identical | `782684371c84f3f25b1c991a3b92c8ea5b03531c11afdca93ef6419c38ca3578` | CALCE CS2-35 specific extraction implementation |
| `scripts/extract_nasa.py` | `scripts/extract_nasa.py` | Byte-identical | `c8b5601bbeb2c985a37beb5688cc32025dc44147b18c5f77ea69b4fc44ad483d` | NASA MATLAB cycle discharge extractor |
| `scripts/finalize_nasa.py` | `scripts/finalize_nasa.py` | Byte-identical | `d928203c2b7763f61e63ef2714025691f34c602a063cd0af5f30e68b7aca0157` | NASA final held-out evaluation runner on B0018 |
| `scripts/inject_nasa_anomalies.py` | `scripts/inject_nasa_anomalies.py` | Byte-identical | `aa0b64d92eda34315c6b52e2cf4d7426a31472c38918af97a983462f6b63c657` | NASA controlled synthetic anomaly injection engine |
| `scripts/inspect_calce_workbooks.py` | `scripts/inspect_calce_workbooks.py` | Byte-identical | `5c48114844a36b57e8305c263774a1fd9ac1ad73f9c9073a9592ee65f880c79d` | Low-level CALCE XLSX ZIP/XML structure inspector |
| `scripts/inspect_nasa.py` | `scripts/inspect_nasa.py` | Byte-identical | `6af03fc47b92e346d1698ea0e74d5628f248dc68fa496878a0122a7d52944b93` | Low-level NASA .mat file structure inspector |
| `scripts/inspect_voltage_cutoff.py` | `scripts/inspect_voltage_cutoff.py` | Byte-identical | `ca096d1adadda9335eafbe2dc35c09efb6b087582fd5e400302cd9b36cb7a508` | Discharge cutoff voltage consistency auditor |
| `scripts/nasa_burnin.py` | `scripts/nasa_burnin.py` | Byte-identical | `b2f52c01f321adfc4ebfc426a6030f4ecdaeb53002a801bb1e12152683a7ebc1` | NASA per-cell threshold calibration runner |
| `scripts/nasa_development.py` | `scripts/nasa_development.py` | Byte-identical | `aacce3d70d3b3204c6ed0e0272201fe77043f19ba2183a373560c91d3ea43535` | NASA model development grid runner |
| `scripts/plot_nasa_degradation.py` | `scripts/plot_nasa_degradation.py` | Byte-identical | `db2264e35dd9cfbd1f93b552a4d660a0fcc73d4a5583c562ef1edf6d91e90bb8` | NASA capacity degradation trajectory visualizer |
| `scripts/train_nasa_isolation_forest.py` | `scripts/train_nasa_isolation_forest.py` | Byte-identical | `de4f4382b0f0ba44ed3e23c518df445d66512b7f2d4f0912e37849ab7c936fb4` | NASA Isolation Forest training and threshold selector |
| `scripts/validate_nasa_relative_features.py` | `scripts/validate_nasa_relative_features.py` | Byte-identical | `d5126072128582bad2a44290d64e7df5b1286a5c931711bc418c5fdf7412b5b8` | NASA relative feature validation experiment runner |
| `tests/test_anomaly_protocol.py` | `tests/test_anomaly_protocol.py` | Byte-identical | `e9c0d2f28f12eb324fcd13ab3c958d49a90aed21c8fbbe32a558aa05a8aa2f98` | Tests for synthetic anomaly injection protocol |
| `tests/test_calce_cells.py` | `tests/test_calce_cells.py` | Byte-identical | `8078315fc97c695b08e82056ee3635dfa7cde9766520cee538cfdf57fe89eef7` | Tests for CALCE cell boundaries and features |
| `tests/test_calce_cs2_35_extraction.py` | `tests/test_calce_cs2_35_extraction.py` | Byte-identical | `a2175701644cbb7b38a377b349995bea65e5c343333c29f2d9c469f99c09df72` | Tests for CALCE CS2-35 extraction logic |
| `tests/test_calce_replication.py` | `tests/test_calce_replication.py` | Byte-identical | `1ea93fba4b7fcd0884962c10cea8909d34fac18e56082ef158fec6fb1c776981` | Tests for CALCE replication pipeline and thresholds |
| `tests/test_final_calce.py` | `tests/test_final_calce.py` | Byte-identical | `dafab026837cf41f61aedaccc0261bec87d0479cef1adb052c531b13b1af466b` | Tests for CALCE freeze, gate, and evaluation |
| `tests/test_nasa_burnin.py` | `tests/test_nasa_burnin.py` | Byte-identical | `4f4064ed35336ed210979d5cffc3146a9d1e8758313b156f85804a40ff489e46` | Tests for NASA burn-in calibration |
| `tests/test_nasa_causal_features.py` | `tests/test_nasa_causal_features.py` | Byte-identical | `3826276cb3141f2b6b0b685c98d93e02d011850e58702391f7022f9f8828d277` | Unit tests for causal rolling-window arithmetic |
| `tests/test_nasa_failure_analysis.py` | `tests/test_nasa_failure_analysis.py` | Byte-identical | `4dd68cd32b5031abefa85361ff43fc8a3df688c0d685e35dbd2c70212033629c` | Tests for failure analysis diagnostic outputs |
| `tests/test_nasa_final_evaluation.py` | `tests/test_nasa_final_evaluation.py` | Byte-identical | `a6ca68449e29616c5a7aa1d17d0b15be54119f1f334a4ef37df973674a84a753` | Tests for NASA final freeze gate and held-out evaluation |
| `tests/test_nasa_model_development.py` | `tests/test_nasa_model_development.py` | Byte-identical | `8400eb43c06891ad1b09b425c9155b20e2f9a8c2d99c5d17c79fdd75fcc3de57` | Tests for NASA absolute-feature model development |
| `tests/test_nasa_relative_features.py` | `tests/test_nasa_relative_features.py` | Byte-identical | `11465f85a4fe4f14a33fc96e92a01798c37caaaf80c64db86016e0a539afc6b5` | Tests for NASA relative feature pipeline and eligibility |
| `tests/test_nasa_splits.py` | `tests/test_nasa_splits.py` | Byte-identical | `2ec44bcfad2b04a2585650e96badaa499d769f3c5cd7ba935065c0fb8ca3ba74` | Tests for NASA data splits and retrospective prefix logic |
| `tests/test_pi_deployment.py` | `tests/test_pi_deployment.py` | Byte-identical | `2a001a80339f721172c7acbb5a21c236d40ffe3eefd41c1b002a72ff9b70f7b5` | Tests for Raspberry Pi deployment and replay scoring |

## 2. Scientific Configuration

All configuration files are copied byte-identically from the research archive.

| Public Path | Archive Source Path | Type | SHA-256 | Role |
|---|---|---|---|---|
| `config/anomaly_injection_protocol.json` | `config/anomaly_injection_protocol.json` | Byte-identical | `e00a3804aee6fb67f2280f7e2818a618e2d0c48be2a7b2daf6c9d6fefbfff017` | Synthetic anomaly injection protocol for NASA |
| `config/calce_anomaly_injection_protocol.json` | `config/calce_anomaly_injection_protocol.json` | Byte-identical | `bea0792fb8e3ec2065458d2873366a4401e8a73d79fd70fb012e678b80068f37` | Synthetic anomaly injection protocol for CALCE |
| `config/calce_experiment_protocol.json` | `config/calce_experiment_protocol.json` | Byte-identical | `ab7ef8ccea50b584f10dfdaf48923a7de15792961bd1c67e22fc5185694637ca` | Experimental protocol for CALCE replication |
| `config/final_calce_model.json` | `config/final_calce_model.json` | Byte-identical | `571fb85db6aba717bee1c7a1353a9ca20ac1fe9eab578d8f34740a2160bb00fe` | Frozen configuration for CALCE model |
| `config/final_nasa_model.json` | `config/final_nasa_model.json` | Byte-identical | `fd4747b45ef8edfae3674fd284209b8df7b2aa4520906ca7ba9799eda46cde21` | Frozen configuration for NASA model |
| `config/nasa_experiment_protocol.json` | `config/nasa_experiment_protocol.json` | Byte-identical | `2b06398c1f777904f95340c7c2d3023bb89b76cc7fbb117647adf1c69d8cd264` | Experimental protocol for NASA primary study |
| `config/nasa_feature_manifest.json` | `config/nasa_feature_manifest.json` | Byte-identical | `ae29e5ea2168b9613d826188406cc69666a8ec7d421879145c3d75805e8edb4e` | Feature definitions for absolute NASA features |
| `config/nasa_model_development.json` | `config/nasa_model_development.json` | Byte-identical | `aa948dadb5e4a69a1628782079b30a74c5ce2bd57f95d5fb19fe58c163751329` | Hyperparameter grid for initial development |
| `config/nasa_relative_feature_manifest.json` | `config/nasa_relative_feature_manifest.json` | Byte-identical | `9c9c5d9d0b76ccbc6962d3e103607bebc4907a5cbac36b92343497de64309d76` | Feature definitions for causal trajectory-relative features |

## 3. Compact Result Evidence

These files contain aggregate evaluation summaries, threshold tables, seed stability metrics, denominator diagnostics, and verification receipts. Detailed per-cycle observation scores and synthetic evaluation copies remain in the research archive.

### NASA Absolute-Feature Model Validation (`results/nasa_model_validation/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/nasa_model_validation/injection_window_counts.csv` | Byte-identical | `a3eca97162e68c4e0e06be801895e6694d868c3fed28d8e58f2b9a3fa7af693a` | Synthetic injection window count summary |
| `results/nasa_model_validation/metric_seed_stability.csv` | Byte-identical | `c78e8fbd4b2fc10c013b1516c2d3e55372650cb4bdb5c54c2de3554921d80a37` | Aggregate metric stability across 3 random seeds |
| `results/nasa_model_validation/metrics.csv` | Byte-identical | `5afcbbc4cc7254881c2ef32b89ab3ffa7ff7fcdebdca72bc38ba785d3bccf62c` | Full grid validation metrics for absolute features |
| `results/nasa_model_validation/run_provenance.json` | Byte-identical | `9c2d2b9b16fe1b0c24994db73221da0c9abeea926ecfc19b313df653c20735eb` | Runtime environment and source code hashes |
| `results/nasa_model_validation/score_distributions.csv` | Byte-identical | `103abeb94d2db3c6ab998fd005116ffbaf835656146ba00d2dea8ecea0ee970b` | Anomaly score distribution summary statistics |
| `results/nasa_model_validation/score_seed_stability.csv` | Byte-identical | `0312d335d92d0e289699ebd6534740dff656c01d47f32e8e6a882f179a152f0b` | Score distribution stability across seeds |
| `results/nasa_model_validation/threshold_review.json` | Byte-identical | `8a98983c8f081aecc64bb09a53532ed500b296b1814416a35c3cb44c7d8462ab` | Evaluation of threshold eligibility (all fail clean FPR target) |
| `results/nasa_model_validation/threshold_seed_stability.csv` | Byte-identical | `58a6f9282db8872f4bf82d32536ffd3196b5881dae732d1b045096bbf4342959` | Threshold and clean FPR stability across seeds (~56-60% FPR) |
| `results/nasa_model_validation/thresholds.csv` | Byte-identical | `60f689205764213ad23d36855b56267b65dfae32972ee8e09bc6f6c977b7d48b` | Threshold values and high clean validation FPRs |
| `results/nasa_model_validation/validation_checks.json` | Byte-identical | `f2b957fc6a22ea49e17313a68c1f666075b928fd861589a73f14c56a0fe23138` | Pre-freeze validation integrity assertions |

### NASA Burn-in Failure Evidence (`results/nasa_burnin_calibration/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/nasa_burnin_calibration/burnin_integrity.json` | Byte-identical | `8f34a1bc358dd6b0c03d8bc642ad859c46955e27d1e418257b5f19da4bed7752` | Burn-in calibration run integrity assertions |
| `results/nasa_burnin_calibration/burnin_review.csv` | Byte-identical | `01e9ada69f5c639365dc9c7403b5a369ab064e65685dd666a58623243fe322e0` | Review showing 0 of 72 configurations eligible (clean FPR ~77%) |
| `results/nasa_burnin_calibration/burnin_seed_stability.csv` | Byte-identical | `63e259c0b00ae258e39b4c0adf11d09e1b353b9a3300ba0a05306e2d9af7c044` | Threshold and post-calibration clean FPR stability |
| `results/nasa_burnin_calibration/burnin_thresholds.csv` | Byte-identical | `64380d2c10a7bb3b8e23ce467c7f89a3d9f88a434766480fa72c952289c5c53f` | Calibration threshold values and individual run FPRs |
| `results/nasa_burnin_calibration/eligible_anomaly_metrics.csv` | Byte-identical | `82163a066721a5777386b6d44862e96e7106cedd828bc1affeda4771b7d339f3` | Empty table confirming 0 configurations met eligibility criteria |
| `results/nasa_burnin_calibration/eligible_configurations.csv` | Byte-identical | `308b4380098cfa9604f598d9dca050aa062ba0c4476522d1bbce68648bb7430f` | Empty table confirming threshold-only burn-in failed |
| `results/nasa_burnin_calibration/feature_shifts.csv` | Byte-identical | `48d744bf58917d04099288c6580b92b3f083ff5af70ca0bf2db16dbdc2097921` | Feature distribution shift statistics between cells |
| `results/nasa_burnin_calibration/shift_integrity.json` | Byte-identical | `354c78a7ea528f6710ff094787cc8614a6a35aab01f386e860c084838bcd2bb9` | Shift evaluation integrity assertions |
| `results/nasa_burnin_calibration/shift_score_distributions.csv` | Byte-identical | `bcec85ddbfc2eaa4829d131e56d8b6fffb02a69810af0d324c6a4fa3fc11320e` | Score distributions under shift experiment |
| `results/nasa_burnin_calibration/shift_score_seed_stability.csv` | Byte-identical | `70abdbe039af7f50fbb0489533a8b2fb1871c0919f49ef3f8ec75818dba5c6b3` | Shift score stability across random seeds |
| `results/nasa_burnin_calibration/validation_checks.json` | Byte-identical | `42a1654c090eea00d04c472368335c2d1120c8950be96434bf9e60fc996e5461` | Assertion confirming 0 eligible configurations found |

### NASA Relative-Feature Evidence (`results/nasa_relative_features/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/nasa_relative_features/denominator_diagnostics.csv` | Byte-identical | `4ef6b1fc992cb43b7b43c67de94f4bc5731d2c23bb392861279c15b55b498ff3` | Denominator zero-MAD guard diagnostics |
| `results/nasa_relative_features/eligibility_review.csv` | Byte-identical | `684536b1f5a3fe5b8c6753a728dfcc8f59d04ddfaa88307441e0eeda495e1024` | Candidate review for clean FPR <= 5% criterion |
| `results/nasa_relative_features/eligible_anomaly_metrics.csv` | Byte-identical | `fabfe6b425f761197041426767fd139b6a812cda6e91a981217e3c6f042aeb64` | Evaluation metrics for all eligible relative configurations |
| `results/nasa_relative_features/eligible_anomaly_seed_stability.csv` | Byte-identical | `fe72108fa326da4a980b5f7a9bc125308d67adbed60f8aba08d7c8062a18535b` | Seed stability of anomaly metrics for eligible models |
| `results/nasa_relative_features/eligible_configurations.csv` | Byte-identical | `a116785385748cdb7d2beca8ba8efb1679864404db86762c61d1383aa0fb8928` | Full list of 58 eligible configuration combinations |
| `results/nasa_relative_features/injection_window_counts.csv` | Byte-identical | `cbaac359a011e0f6daca28db273201f725caf74b6109366286c3c8cd4ad37322` | Injection window counts across relative feature sets |
| `results/nasa_relative_features/relative_feature_shifts.csv` | Byte-identical | `091472a661ca6cfd700d1baa43e14698138133491c31f875732f78bdb87ebc19` | Standardized feature shift after relative transformation |
| `results/nasa_relative_features/run_integrity.json` | Byte-identical | `16d0079008fb9a7c941049368b2c795ff7a22d14aefb7b2e1a2c886a1e8c7bc1` | Run integrity and dependency environment record |
| `results/nasa_relative_features/sample_counts.csv` | Byte-identical | `f471acb4523107026e4c0bdd170f66a4444e3fba1bb9be9a7f3c3e677095df51` | Sample counts by history window (k=5, 10, 20) |
| `results/nasa_relative_features/score_distributions.csv` | Byte-identical | `e4140c7703e92be1af3483cedf6c06f210654ee63107885efb00f846138f5843` | Relative model score distribution statistics |
| `results/nasa_relative_features/score_drift.csv` | Byte-identical | `469ed1aeaf7f640c57011fc343f9001d5bfe590a50a3e3f183dafc590435c207` | Score drift analysis from early to late life |
| `results/nasa_relative_features/score_drift_seed_stability.csv` | Byte-identical | `ffc06786570fdea041ea7206b21cc3ae7e43c47b4e1e429e779fe11255ee1719` | Score drift stability across random seeds |
| `results/nasa_relative_features/threshold_seed_stability.csv` | Byte-identical | `2bb03edf7d435005ff4c30fd938665b270cac40dd4582d5ac795ad818565189e` | Stability of relative thresholds across random seeds |
| `results/nasa_relative_features/thresholds.csv` | Byte-identical | `13c1b8fa5458c712565a956c9cdd162c07e10c84b20c34f3c2f8a7e81d29ee82` | Relative threshold values and validation clean FPRs |
| `results/nasa_relative_features/validation_checks.json` | Byte-identical | `7c1b0868d9331225de23a3417a74538c4c2475e29a087d413f54915c87117ebf` | Relative feature phase verification assertions |

### NASA Final Held-Out Evaluation (`results/nasa_final_test/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/nasa_final_test/anomaly_metrics.csv` | Byte-identical | `9f3db575f545c0c223b2af0123654bfad95c903df317f8ea6156986b3ab8d2bb` | Final evaluation metrics on held-out B0018 |
| `results/nasa_final_test/clean_temporal_statistics.csv` | Byte-identical | `e659059cad85ae79d0327e49808a2ad09592d6565fca9792f20c5a063c979ba4` | Early/mid/late statistics: 122 cycles, 5 flagged, FPR 4.10% |
| `results/nasa_final_test/development_comparison_metrics.csv` | Byte-identical | `f6d09220d424e0d41bdf2048264f775fa1fb1b6fa9b6f10cda92e578cd9a0560` | Comparison of metrics on B0007 (dev) vs B0018 (test) |
| `results/nasa_final_test/development_temporal_scores.csv` | Byte-identical | `b3d2d31999cb4699cb96f9f2a434df723c82a0f2eb1a67e5c7365ef988712ab4` | Reference B0007 temporal score progression |
| `results/nasa_final_test/evaluation_started.json` | Byte-identical | `7b9fbeba69c05c5f7bf935798c2f576f8562fae2336f2eea6bf7f94db993f7d9` | Execution lock and freeze confirmation timestamp |
| `results/nasa_final_test/injection_window_counts.csv` | Byte-identical | `a98ca50cd30573ed38dc3d7cc2a34a0070eed48cab314563584c988d78d1553e` | Synthetic injection window counts on B0018 |
| `results/nasa_final_test/integrity_receipt.json` | Byte-identical | `ff522c57bb27abea830acea26f15b679a9c51c4a0d01a71553715cd8066e6c60` | Freeze-before-access integrity receipt and audit log |
| `results/nasa_final_test/score_distributions.csv` | Byte-identical | `967af5ee9c3871f92a5b58bd4f6610bff33f8035fb1ae7c74c4ac3f4aa1a07b3` | Score distribution statistics on B0018 |
| `results/nasa_final_test/verification_results.json` | Byte-identical | `44a4ef28b23a040b7f1b41dc175c870bec513f81ff05989defbf27dc797e1a79` | Post-test verification checks (all safety tests passed) |

### NASA Failure Analysis Evidence (`results/nasa_failure_analysis/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/nasa_failure_analysis/a1_sustained_return_diagnostics.csv` | Byte-identical | `12ccd2895da754ca3a5ca62dd929e56926c74acd3a3edbdabca46025cb01b56f` | Diagnostic of A1 degradation absorption into rolling baseline |
| `results/nasa_failure_analysis/a4_residual_summary.csv` | Byte-identical | `7d9a1826b1b6e854ae6e5d22b1d90aa7fb4621eb6fcba509667cf588eada2e77` | Residual effect of gradual sensor drift (A4) |
| `results/nasa_failure_analysis/adaptation_summary.csv` | Byte-identical | `488c54bbf62d5022edb00ecd9a1d84f1fe5b0ad833fe7dbf509998131fa0b1ff` | Adaptation summary across injection scenarios |
| `results/nasa_failure_analysis/integrity_checks.json` | Byte-identical | `1cd7da403dc7c404504f665bb349d91d7e46d6a74c25f1ff4196eb1b8e12efc5` | Diagnostic experiment integrity assertions |
| `results/nasa_failure_analysis/reference_existing_metrics.csv` | Byte-identical | `2ecd21dab005f7d244ec2e4839033606a79bb183b81aff915c3f3da25a6da44a` | Reference development metrics used during analysis |
| `results/nasa_failure_analysis/seed_rank_correlations.csv` | Byte-identical | `d2cfc498c32747167e420deefae6bba253176e596c0fe34105aaf39765a50e82` | Rank correlations between models trained with different seeds |
| `results/nasa_failure_analysis/seed_score_and_threshold_diagnostics.csv` | Byte-identical | `8fec61021150ec32e771545c7b83a9ef4268be673ebfe00b4d4232f90b8d3c59` | Seed score diagnostics and threshold sensitivity |
| `results/nasa_failure_analysis/verification_results.json` | Byte-identical | `62565294741267352f22b4a6e5ac8df9153e259c647090c01c6d015cdc635394` | Verification results for failure analysis pipeline |

### CALCE Replication Evidence (`results/calce_replication/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/calce_replication/anomaly_metrics.csv` | Byte-identical | `ce3ed52eb05a8099835db2f70ab49444b367adc5480dd87ed687cb0bf60e4ccf` | Anomaly metrics for separately fitted CALCE model on CS2-37 |
| `results/calce_replication/anomaly_seed_stability.csv` | Byte-identical | `44859dc9707ababd6da938154d380383cfe5eb8ca5a0d44e5ec48174bb3a64f1` | Metric stability across random seeds on CALCE |
| `results/calce_replication/integrity_checks.json` | Byte-identical | `b3923ee1001c58cf27be130e7de9c5f357f07d6a539f782e044f1ebd9961e8cf` | CALCE replication pipeline integrity and NASA immutability |
| `results/calce_replication/relative_feature_shifts.csv` | Byte-identical | `6286a655540a90aa7efb93f289e27852a3c68cd4f8178233fb313c4d84ec1824` | Standardized feature shifts on CALCE cells |
| `results/calce_replication/score_distributions.csv` | Byte-identical | `f737e0d9075e0ac5e25e925e2b60c7dcc0aedce31376caaa2c4b1d99a940bf0b` | Score distributions for nominal training vs CS2-37 validation |
| `results/calce_replication/score_drift.csv` | Byte-identical | `b76afe732ddee630dd6f680fb4e5e66262e770516dfd7e3a71a6cbd6b3bde638` | Validation score drift from early to late life |
| `results/calce_replication/synthetic_window_counts.csv` | Byte-identical | `71733271822cc4825847e9bddff243066b4b38d8c21af4749bc9e9c30385a39b` | Accepted synthetic injection windows on CALCE |
| `results/calce_replication/threshold_seed_stability.csv` | Byte-identical | `1ec5a837ea32a3b6dd75a7cdf373f08b86b5c29312eb0121fc5725122866a7c8` | CS2-37 P95 validation mean across seeds 42/123/2026: 3.15%; seed 42: 2.53%, distinct from CS2-38 final 3.15% |
| `results/calce_replication/thresholds.csv` | Byte-identical | `67d74bf2410bd29e7d6d4a8f4f73c12187535775a792356342028f758d065c44` | Threshold values and validation clean FPRs on CS2-37 |
| `results/calce_replication/verification_results.json` | Byte-identical | `798f8824d5c16b1d43baad36a55467b519c29b266f82a2fc7422de2c8c24c9f3` | Verification assertions for CALCE replication |

### CALCE Final Held-Out Evaluation (`results/calce_final_test/`)

| Public Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|
| `results/calce_final_test/anomaly_metrics.csv` | Byte-identical | `cb51ec4b976324f362161e47ec19c36aebceb6f232bef331072505d8aef3ebf4` | Final evaluation metrics on held-out CS2-38 |
| `results/calce_final_test/clean_periods.csv` | Byte-identical | `cb879cfb70dee23a45cadb1653a48fa15964f92487230542c2efb5e9429381b1` | Temporal period statistics on CS2-38 |
| `results/calce_final_test/development_comparison.csv` | Byte-identical | `a96cc4dcad45f1467175c07a8bcb676b133a35fdd4448921b9af5fe03ff6a5a2` | Comparison of metrics between CS2-37 and CS2-38 |
| `results/calce_final_test/integrity_checks.json` | Byte-identical | `8fd84e887e6e0ac2284f3bc9fcdcd87ff75c00151110f4ddb85caff993e51542` | Final CALCE freeze integrity check and NASA hash verification |
| `results/calce_final_test/summary.json` | Byte-identical | `e7fa7f763ee41b81d55b83771bfca520c1c5809e9f59deb1db2ab318b2f94fa0` | CS2-38 summary: 1,015 cycles, 32 flagged, FPR 3.15% |
| `results/calce_final_test/synthetic_window_counts.csv` | Byte-identical | `b6684e911336fe696ceaae9c1248baae88acc33813955753c12502a2eb35ebfe` | Synthetic injection window counts on CS2-38 |
| `results/calce_final_test/verification_results.json` | Byte-identical | `546f52fcb4515ed1dd88db2d27b085537d8ad6e5918b704fb73dc841939cd0f4` | Post-test verification results on CALCE |

## 4. Freeze and Integrity Evidence

These files record the cryptographic state and receipts of the frozen models. The model binaries (`.joblib`) themselves remain archive-only.

| Public Path | Archive Source Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|---|
| `models/final_nasa/final_nasa_model.sha256` | `models/final_nasa/final_nasa_model.sha256` | Byte-identical | `a78faa4521c4daec4aaa6d556107d5c9b7bed9553b2628bef8cebbccd0b27883` | SHA-256 sidecar checksum for `config/final_nasa_model.json` |
| `models/final_nasa/freeze_receipt.json` | `models/final_nasa/freeze_receipt.json` | Byte-identical | `ba7fe753bee393eb0219947a0a5d9ff555a97cb6871b44b8c5b85bba1b8798e7` | Pre-test model freeze receipt for NASA final model |
| `models/final_calce/final_calce_model.sha256` | `models/final_calce/final_calce_model.sha256` | Byte-identical | `494e6fbdcd45023553cfca3d38320c6b1454e5ff28f5f26ae92948a175eb342a` | SHA-256 sidecar checksum for `config/final_calce_model.json` |
| `models/final_calce/freeze_receipt.json` | `models/final_calce/freeze_receipt.json` | Byte-identical | `208f33469d8127758643c3a6b660eccbeaa4f3c4422e58572267e2fac8c56913` | Pre-test model freeze receipt for CALCE replication model |

## 5. Sanitized Historical Reports

These documents are sanitized public derivatives of internal historical research reports. All scientific values, thresholds, metrics, splits, parameters, and conclusions are preserved without change. Each derivative contains an explanatory header disclosing its origin, archival SHA-256, and noting omitted archive-only dependencies (such as binaries, observation tables, and figures).

| Public Path | Archive Source Path | Derivative Type | Archival SHA-256 | Public SHA-256 | Exact Redaction / Edit Performed |
|---|---|---|---|---|---|
| `results/nasa_model_validation.md` | `results/nasa_model_validation.md` | Sanitized Derivative | `68674f651f56f7bf921156f1243db39cc7ba5a13e9529d7d26cb6d405d0a6654` | `122ec43f323cac386c02463cb9cc9a50297104b5d4a2a81491f958b52c01a264` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/nasa_burnin_calibration.md` | `results/nasa_burnin_calibration.md` | Sanitized Derivative | `329815a6db56fd21ab7ceadd881a3f1f6c491cbdb6e1170ed49fb99cd816a019` | `777866c1172c5ddae287a4227d5ecf5b677b9c51af023e242463dbf4e14ade86` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/nasa_relative_feature_validation.md` | `results/nasa_relative_feature_validation.md` | Sanitized Derivative | `a696d7966eca2e9f9a6096312c2b3075c3577546cead93b2a3c6c826e5af21dc` | `458c8098dd24881c72cbfbe467f22b87b3962877400872c59462e3bb79849d50` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/nasa_failure_analysis.md` | `results/nasa_failure_analysis.md` | Sanitized Derivative | `b24d24623d02c3e11cbb476cc9cda2bf635da9d6f8891c2fb5c5e03239172545` | `00ca79b4351c55904171a3f5087796e27cb4461b4d4a9a181968b6c937858d07` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/nasa_final_test.md` | `results/nasa_final_test.md` | Sanitized Derivative | `dbfa5353e8f879964f0f2788ea5973d8f72a9f2085fbe29ccdd6296f23c75834` | `0a24569e9ffee50a8bda4193bd80337945ff4b52d6a595333e2c993ed13129a5` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/calce_replication_validation.md` | `results/calce_replication_validation.md` | Sanitized Derivative | `f96eb8d01c0dbfdaa27eaf48f1fc4924b9619af50dbaba245f6c61b622635ef4` | `62e0d830a154f62a32ea9cc23442787c7e93364ed23c11172412acf528534061` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |
| `results/calce_final_test.md` | `results/calce_final_test.md` | Sanitized Derivative | `7cb1cc7ef999aee1403dc414fde13aeea8e838021802650fdb34815acbc6fabc` | `8ba9e0cf2656409c427aaf5fd43b57cba1d7252ef1400452a5e38318a1135d9c` | Added public historical disclosure header noting archival origin, original hash, and omitted archive-only dependencies (binaries, observation tables, figures). All original scientific text and tables preserved unchanged. |

## 6. Raspberry Pi Implementation and Evidence

The physical Raspberry Pi 3B+ evidence supports replay inference using pre-recorded cycle-level data. It does not establish live sensor streaming or field deployment.

| Public Path | Archive Source Path | Type | SHA-256 | Role / Interpretation Notes |
|---|---|---|---|---|
| `deployment/pi/features.py` | `deployment/pi/features.py` | Byte-identical | `5989cd735033ece7363d7fd442dbab4a3a35cd176622475887711353f4991663` | Lightweight feature transformation for edge inference |
| `deployment/pi/infer.py` | `deployment/pi/infer.py` | Byte-identical | `2c07ed12d793dd6dc98fb58f303ab34c7ddfa145818dd0c60ed71d664ce41641` | Streaming inference and anomaly scoring engine |
| `deployment/pi/validate_playback.py` | `deployment/pi/validate_playback.py` | Byte-identical | `3452ce967a07e18d8c6f4a9f5c36d204933e6afde9f8dc7aae36a47b369f46b2` | Verification script for recorded cycle replay |
| `deployment/pi/benchmark.py` | `deployment/pi/benchmark.py` | Byte-identical | `83fe17efd97782bcca38df1ba81045e0c1857eb4b8ba868d1d4b7992cbcb82ac` | Benchmark harness for latency, throughput, and memory |
| `deployment/pi/requirements-pi.txt` | `deployment/pi/requirements-pi.txt` | Byte-identical | `e51ce3b6e900f798b9e2f609d1326f2856e49720107bff1a50701b60054d9677` | Pinned dependency specifications for Raspberry Pi |
| `deployment/pi/results/pi_benchmark.json` | `deployment/pi/results/pi_benchmark.json` | Byte-identical | `274ffbd8a7cd2f9aa9e1de1eee8846d4b6a8a1805a1257329e4ef0c4d811afd2` | Physical Raspberry Pi 3B+ benchmark results (63.9 ms combined latency; preserves historical memory counter discrepancy) |
| `deployment/pi/results/pi_benchmark.txt` | `deployment/pi/results/pi_benchmark.txt` | Byte-identical | `8b004683ff849f3ec60741e7406ce4184e848fe1c51cf0ce9224884fb06b2a2b` | Plain text benchmark output summary from physical device |
| `deployment/pi/results/playback_validation.json` | `deployment/pi/results/playback_validation.json` | Byte-identical | `26f4636593353529608dcce3c6d3c446a9c3ebd2d90fc83ef1231d3fd139c877` | Playback validation result (122 usable cycles, exactly 5 flagged cycles: 46, 47, 106, 107, 108) |
| `deployment/pi/results/integrity_verification.json` | `deployment/pi/results/integrity_verification.json` | Byte-identical | `541183b894f3faa1a7a8973fc2a7c0cf1ea71de2c478c518963e86d928b4dd88` | Packaging integrity record (preserves historical `pi_hardware_tested=false` packaging flag) |
| `deployment/pi/results/research_hashes_before.json` | `deployment/pi/results/research_hashes_before.json` | Byte-identical | `d7fc015adc83f77b666e041679ec0362c522088acd410a35538e6cdd6e086c89` | Pre-deployment cryptographic hash inventory (384 entries) |
| `deployment/pi/artifacts/artifact_hashes.json` | `deployment/pi/artifacts/artifact_hashes.json` | Byte-identical | `ca72482e2e832c1b3aa079f065468423f29b1db0979dd611cacc1af900a00b45` | Checksum manifest of packaged deployment artifacts |
| `deployment/pi/artifacts/final_nasa_model.json` | `deployment/pi/artifacts/final_nasa_model.json` | Byte-identical | `fd4747b45ef8edfae3674fd284209b8df7b2aa4520906ca7ba9799eda46cde21` | Packaged model configuration for edge deployment |
| `deployment/pi/artifacts/final_nasa_model.sha256` | `deployment/pi/artifacts/final_nasa_model.sha256` | Byte-identical | `a78faa4521c4daec4aaa6d556107d5c9b7bed9553b2628bef8cebbccd0b27883` | Checksum sidecar for packaged configuration |
| `deployment/pi/artifacts/nasa_relative_feature_manifest.json` | `deployment/pi/artifacts/nasa_relative_feature_manifest.json` | Byte-identical | `9c9c5d9d0b76ccbc6962d3e103607bebc4907a5cbac36b92343497de64309d76` | Feature definition manifest packaged for edge inference |
| `deployment/pi/results/pi_environment.txt` | `deployment/pi/results/pi_environment.txt` | Sanitized Derivative | Archival: `8a9536b879ba12c65127c57fd7151b99b1c70039c9009eddfd12e4458b55e5df`<br>Public: `5d6b6a9219d3659d0d069ded8177793b120a9fc819023b301fe21d8689615e7f` | Redacted private device hostname (replaced with `[redacted-hostname]` in Linux kernel banner line). Retained exact CPU, architecture, memory, Debian 13, and Python 3.13.5 environment facts. |

## 7. Deferred and Archive-Only Assets

The following categories remain exclusively in the research archive and are not distributed in this repository:
- **Raw laboratory datasets**: NASA .mat files and CALCE .xlsx files.
- **Source-derived observation tables**: All tables under `data/processed/` and `models/final_nasa/development_source_table.csv`.
- **Detailed per-cycle score files**: Per-cycle score traces across all validation and test runs (`clean_scores.csv`, `scores.csv.gz`).
- **Synthetic evaluation copies**: Multi-megabyte synthetic perturbation evaluation traces.
- **Serialized model binaries**: All `.joblib` estimators, scalers, and model bundles.
- **Visualization figures**: All `.png` figures under `figures/nasa/` and `figures/calce/` are excluded from v0.1.0.
- **Deployment sample data**: Real B0018 cycle inputs under `deployment/pi/sample_data/`.
