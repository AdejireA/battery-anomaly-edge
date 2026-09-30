# v0.2 validation and handoff

This record covers the selected-artifact reproducibility upgrade. Starting HEAD was `0b357012d73a9a2a66feebb4639c846c5e0bff58`. The initial working tree had one user edit: `.gitignore` excluded the internal v0.2 audit. That edit is preserved. No Git state was mutated; all changes are ordinary unstaged working-tree files. The original research directory was used only as read-only evidence, including read-only use of its Python environment with bytecode disabled and plotting caches redirected into this public repository.

## Tests and execution

Commands run from the public root with Python 3.14.6 and the scientific versions in [requirements-lock.txt](../requirements-lock.txt):

```bash
python -B -m unittest tests.test_calce_cs2_35_extraction tests.test_nasa_causal_features tests.test_v02_reproducibility -v
python -B demo/run_demo.py --output-dir output/demo
python -B scripts/verify_artifacts.py --load-models
python -B -m unittest discover -s tests -v
python -B scripts/prepare_reproduction.py
```

The public-safe subset has **19 tests**: seven existing synthetic CALCE extraction tests, three existing NASA causal-feature tests, and nine new v0.2 tests. It checks deterministic demo behavior, prefix invariance, strict threshold comparison, historical rate arithmetic, all released hashes and model loads, standalone/bundle score equivalence, frozen Pi runtime scoring without fitting, tamper rejection before deserialization and reproduction-directory safety. See the final execution results below.

The baseline complete suite ran **45 tests, with 2 failures and 22 errors**. Many classes fail setup because processed datasets are intentionally absent. Two failures compare the public inventory against archive-wide historical inventories. Other errors involve omitted development models/sample data and process-wide research audit hooks. Existing tests and scientific guards were not changed. Three new artifact tests run in child processes when historical audit hooks are installed, so they do not disable or inherit those research restrictions.

Windows sandbox permissions initially blocked temporary test-directory access. The final test runs used approved execution outside that sandbox; writes remained inside the public repository. The exact final results are recorded at the end of this document.

Artifact verification reports **114 released artifacts verified; models loaded**: eight binary files, six figures and 100 compact evidence/configuration records. PNG metadata contains only Matplotlib software identification and DPI. Model inspection found fitted trees, feature scaling statistics and aggregate provenance/identifiers, with no embedded raw training matrix, credential or private absolute path. Source and release model/figure hashes match.

The demo returns ten history warmup rows and twenty finite scores. In the tested environment, alerts occur at cycles **16, 21, 22 and 23**; only 21–23 have the programmed perturbation. Cycle 16 illustrates an alert on unperturbed synthetic noise. The synthetic threshold is approximately **0.4971476411827305**. These are mechanics-demo outputs, not measured battery fault sensitivity or research FPR estimates. No demo runtime benchmark is claimed.

The reproduction helper successfully created `output/reproduction/` containing source, non-final configurations and empty data/result directories. It omitted historical results, final configurations, models and external data. Rejection of an existing destination and of the release root is tested. Full raw-data execution was not performed.

## Frozen models and provenance

Model bytes total **2,538,319**, including the two Pi copies. NASA hashes match `config/final_nasa_model.json`; CALCE hashes match its frozen configuration/receipt. Existing `models/final_*/final_*_model.sha256` sidecars hash the configuration files, not the adjacent binaries.

| File | Bytes | SHA-256 |
|---|---:|---|
| `models/final_nasa/model.joblib` | 491,357 | `18ecd3c66d71e89c321570e683c8abdece4aab6d421e4121d4b46003a0f5dd63` |
| `models/final_nasa/scaler.joblib` | 1,295 | `ea80b93bc0d1fec25b5c760763f9c95ef859fcae6a67964fe24e4cabf1429f78` |
| `models/final_nasa/model_bundle.joblib` | 113,688 | `8801466200c725e5869ab6483a4b2ba2e93418013026c04b366aaa0f20045aee` |
| `deployment/pi/artifacts/model.joblib` | 491,357 | `18ecd3c66d71e89c321570e683c8abdece4aab6d421e4121d4b46003a0f5dd63` |
| `deployment/pi/artifacts/scaler.joblib` | 1,295 | `ea80b93bc0d1fec25b5c760763f9c95ef859fcae6a67964fe24e4cabf1429f78` |
| `models/final_calce/model.joblib` | 713,629 | `e9184bd468e00835f3624587f09c5bf23a2ca2f612fba1bdd27fae270e97d31e` |
| `models/final_calce/scaler.joblib` | 1,127 | `fcf02ec5b7f826799b134a2c4d187ba4090960394a97065e6fd180c4c8ddf9c7` |
| `models/final_calce/model_bundle.joblib` | 724,571 | `491ab2d22826574dcbf7cf378596ec908bfc28f253617066de45ae32b61f586e` |

The NASA bundle is the exact selected RELATIVE_B/history-10/100-tree/full-feature/seed-42 development bundle copied during freeze. Its `final_threshold` remains `None`; use frozen NASA P95 **0.5548682376720724**. The CALCE bundle is the separately fitted selected seed-42 artifact and retains a development-status string; use frozen CALCE P95 **0.595563163424274**. Both standalone estimators/scalers agree with their bundles on a synthetic feature fixture. No retraining or reserialization was performed.

NASA training is B0005/B0006, validation B0007, final test B0018; CALCE training is CS2-35/36, validation CS2-37, final test CS2-38. The manifest records features, history length 10, thresholds, seed, exact sizes, hashes and provenance. The exact original CALCE Python version and original joblib serialization version are not independently established; they are marked unknown, separately from tested loading versions.

## Selected figures

Six unchanged figures total **1,184,556 bytes**. They are surviving final-test plots and final saved validation summaries; use in a formal publication is unknown. No figure was regenerated.

| File | Bytes | Scope and reason |
|---|---:|---|
| `artifacts/figures/nasa/relative_features/absolute_vs_relative_score_drift.png` | 381,848 | B0007; validation; clean. Seed-mean within-model score drift, absolute versus relative. Scores have model-specific scales. |
| `artifacts/figures/nasa/relative_features/clean_fpr_by_history_window.png` | 273,781 | B0007; validation; clean. Compares clean validation FPR across the evaluated history windows (k=5, 10, 20) and feature sets. k=10 with RELATIVE_B was used as the final reporting reference. |
| `artifacts/figures/nasa/final_test/b0018_clean_score_vs_cycle.png` | 99,740 | B0018; final test; clean. Frozen P95: 5 of 122 scorable cycles flagged (4.10%). |
| `artifacts/figures/calce/final_test/cs2_38_clean_score_vs_cycle.png` | 173,168 | CS2-38; final test; clean. Separately fitted CALCE model: 32 of 1015 flagged (3.15%). |
| `artifacts/figures/nasa/final_test/b0018_anomaly_score_distributions.png` | 204,517 | B0018; final test; clean and synthetic. A2/A3/A4 score CDFs at three severities; synthetic labels are not observed faults. |
| `artifacts/figures/nasa/final_test/b0018_A4_severity.png` | 51,502 | B0018; final test; synthetic. Weak gradual-drift recall 4.50/4.55/4.67%; precision/F1/AP use 50% evaluation prevalence. The pr_auc label denotes average precision. |

The larger exploratory A4 absorption diagnostic was deliberately excluded in favor of final B0018 severity results. The absolute/relative comparison uses model-specific score scales and differs in one thermal input; it does not prove a representation-only causal effect. History 10 is a reporting reference, not a proven global optimum.

## Environment and full reproduction

Python **3.14.6**, NumPy **2.5.3**, pandas **3.0.6**, SciPy **1.18.1**, scikit-learn **1.9.1**, joblib **1.6.0** and Matplotlib **3.11.2** are both present in the surviving workstation environment and recorded in `results/nasa_model_validation/run_provenance.json`. NASA's final freeze also records Python, NumPy, pandas and sklearn. Pi records corroborate Python **3.13.5** and its pinned numerical dependencies; PNG metadata corroborates Matplotlib. The lockfile pins the tested scientific dependency closure, including recovered transitive versions, without freezing unrelated development packages. A fresh network installation was not tested. The optional Pi benchmark requires psutil. The recovered conversational history reports psutil 7.2.2 on the physical Pi. The checked saved environment and benchmark records do not independently preserve its exact version; requirements-pi.txt specifies a version range. psutil was absent from the workstation environment used for v0.2 validation.

[Reproduction instructions](reproduction.md) describe three levels: no-data synthetic demo; model/figure/hash inspection; and full independent NASA/CALCE reproduction. The full workflow prepares a new ignored run directory, acquires all eight cells independently, extracts/audits cycle summaries, constructs causal relative features, performs clean validation and synthetic evaluation, freezes before guarded final evaluation, and reconstructs Pi replay inputs locally. Expected output paths and historical counts are documented. No download URL was invented. Historical timestamps and archive-wide hashes need not match a new run.

## Scientific-integrity and publication-safety audit

The headline rates remain distinct: NASA B0007 **3/158 = 1.90%**, B0018 **5/122 = 4.10%**; CALCE CS2-37 seed-42 P95 **26/1026 = 2.53%**, its three-seed P95 mean **3.15%**, and CS2-38 final **32/1015 = 3.15%**. Tests validate these against preserved result tables/configurations. The CALCE model is separately fitted. Early-life nominal proxies are not certified fault-free; synthetic labels are evaluation labels, not observed real faults. Gradual drift remains difficult.

The physical Pi reference remains recorded cycle-level replay: 122 scorable predictions, zero mismatches, warm median 63.77 ms, P95 64.94 ms and throughput 15.64 observations/s, excluding data input/context preparation. The inconsistent saved peak/current RSS counters are preserved without an invented explanation. No live sensing, field deployment, BMS integration or control is claimed.

Historical “never opened” wording in the Phase 4 loader, failure-analysis and CALCE replication reports describes those guarded phases. It is not a lifetime claim: B0018/CS2-38 appeared in earlier extraction/descriptive audits. Original reports and hash receipts remain unchanged; the current guide makes this scope explicit.

The scan scope is tracked files plus nonignored new files, excluding `.git` and local ignored material. It checks forbidden dataset/development/cache paths, measurement-table headers, private absolute paths, common credential/token/private-key patterns, Markdown links and scientific wording. No forbidden data files, source-derived measurement tables, development collections, credential patterns or private absolute paths were found in that intended publication set. Public author attribution is intentional. This is a scoped scan, not a proof against every possible secret format. Model state and PNG metadata were also inspected. Existing internal reconstruction reports remain ignored and were not packaged.

## Working-tree handoff

Created public files (24):

- `artifacts/README.md`
- `artifacts/figures/calce/final_test/cs2_38_clean_score_vs_cycle.png`
- `artifacts/figures/nasa/final_test/b0018_A4_severity.png`
- `artifacts/figures/nasa/final_test/b0018_anomaly_score_distributions.png`
- `artifacts/figures/nasa/final_test/b0018_clean_score_vs_cycle.png`
- `artifacts/figures/nasa/relative_features/absolute_vs_relative_score_drift.png`
- `artifacts/figures/nasa/relative_features/clean_fpr_by_history_window.png`
- `artifacts/manifest.json`
- `demo/README.md`
- `demo/run_demo.py`
- `deployment/pi/artifacts/model.joblib`
- `deployment/pi/artifacts/scaler.joblib`
- `docs/reproduction.md`
- `docs/v02-validation.md`
- `models/final_calce/model.joblib`
- `models/final_calce/model_bundle.joblib`
- `models/final_calce/scaler.joblib`
- `models/final_nasa/model.joblib`
- `models/final_nasa/model_bundle.joblib`
- `models/final_nasa/scaler.joblib`
- `requirements-lock.txt`
- `scripts/prepare_reproduction.py`
- `scripts/verify_artifacts.py`
- `tests/test_v02_reproducibility.py`

Modified tracked files (7):

- `.gitignore`
- `README.md`
- `deployment/pi/README.md`
- `docs/artifact-manifest.md`
- `docs/model-card.md`
- `docs/reproducibility.md`
- `requirements.txt`

Raw NASA/CALCE files, source-derived processed/sample tables, development grids, other figures, virtual environments, caches, internal reports and unrelated experiments were deliberately excluded. Ignored `tmp/` validation logs/scripts and `output/` synthetic/preparation outputs remain local only. Citation metadata still identifies the published v0.1.0; v0.2 has not been released.

Remaining limits: full external-data reproduction and a new physical Pi run were not executed; fresh environment installation was not tested; archive-wide tests require omitted artifacts; original CALCE Python/joblib serialization versions and formal figure-publication placement are incompletely documented. These do not block the scoped Tier-B package, but the repository must not be described as a fully tested one-command reproduction of every historical experiment.

## Final execution and repository checks

- Public-safe tests: **19 run in 7.211 seconds; OK**, no skips, failures or errors.
- Complete discovery: **54 run in 38.758 seconds; 2 failures and 20 errors**. Both failures and all remaining errors were present in the baseline. Two existing CALCE tests now pass because the final binaries are available: clean-only selection/training provenance and scoring without fitting. All nine new tests pass in both execution modes.
- Demo: exited successfully; 30 output rows, 10 warmup and 20 scored, with the four alerts documented above.
- Artifact verifier: **114 verified; all eight binary files loaded**. All 14 copied model/figure files, including duplicate runtime copies, still match their source hashes.
- Markdown link scan: **zero broken local links** in the intended public set.
- Publication-safety scan: **zero forbidden-path, credential-pattern or private-absolute-path findings** in the intended public set; no measurement-table headers found among its CSV files.
- `git diff --check`: **exit 0**, no whitespace errors. Git prints existing LF-to-CRLF conversion notices for `.gitignore` and `requirements.txt`; these are not diff-check failures.
- Final read-only `git status`, `git diff --stat` and `git diff` reviewed. **7 modified tracked files, 24 untracked public files, no staged changes**, and HEAD unchanged. The tracked diff is 65 insertions and 113 deletions across seven files; untracked additions are not counted by `git diff --stat`.
- Intended-public size (tracked plus nonignored new files, excluding Git metadata, ignored reports, caches and local outputs): **3,813,938 bytes before; 7619437 bytes after**. The initial physical working tree excluding `.git` and scratch `tmp/` was 4,074,712 bytes because it also held ignored internal reports. Publication size is the comparable before/after measure; this upgrade does not package those reports.

## Manual review checklist

- [ ] Scientific claims, cell roles, percentages and guarded-access wording.
- [ ] Frozen model provenance, hashes and authoritative configuration thresholds.
- [ ] Six figures, their captions and clean/synthetic validation/test scope.
- [ ] Three-level reproduction workflow and external-data prerequisites.
- [ ] Historical versus tested environment versions and optional Pi dependencies.
- [ ] Public-data/privacy boundaries, ignored internal files and scan scope.
- [ ] README quick start, limitations and unreleased v0.2 status.
