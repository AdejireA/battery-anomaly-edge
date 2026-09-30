# Released scientific artifacts

[manifest.json](manifest.json) is the machine-readable inventory of eight binary files (six final components plus two identical Pi runtime copies), six unmodified figures and the existing compact evidence. Each entry records bytes and SHA-256. Model entries identify cells, feature order, history, threshold, seed, serialization and provenance. Figure entries identify cell, split, clean/synthetic scope, generator and supporting evidence.

Final binaries remain under [NASA](../models/final_nasa/) and [CALCE](../models/final_calce/) so preserved evaluation scripts and historical paths still agree. Only the two small-runtime interfaces needed by the unchanged Pi loader are duplicated under [Pi artifacts](../deployment/pi/artifacts/). No development collection is released.

The frozen NASA configuration and CALCE freeze receipt independently name the released model hashes. All six source digests matched before copying; copies are byte-identical. Inspection found sklearn tree structures and scaling statistics, feature names and (in bundles) training cell/cycle identifiers and aggregate provenance. It found no raw training matrix, source measurement table, credential or absolute local path. Training identifiers are laboratory cell IDs, not personal identifiers.

Bundle metadata deliberately remains unchanged: NASA `final_threshold` is `None` and lists candidate percentiles; CALCE retains `CALCE_DEVELOPMENT_ONLY`. These are the exact selected bundles copied during finalization. Use [NASA frozen configuration](../config/final_nasa_model.json) and [CALCE frozen configuration](../config/final_calce_model.json) as the authoritative final thresholds. Standalone and bundled estimators/scalers produce identical scores on a synthetic feature fixture.

The six selected figures are final-test results or the final saved validation summaries that explain the representation change. They show clean B0007 score drift and history sensitivity, clean final B0018 and CS2-38 scores, B0018 synthetic score distributions, and weak A4 drift sensitivity. They are research plots; their use in a formal publication is unknown. Absolute/relative models have different score scales and differ in one thermal input, so the comparison is not a controlled representation-only ablation. History 10 is a reporting reference, not a proven global optimum. See the manifest for individual captions and provenance.

Verify without deserializing:

```bash
python -B scripts/verify_artifacts.py
```

Add `--load-models` only for trusted artifacts in the pinned environment. Joblib/pickle loading can execute code; hashes verify correspondence to this inventory, not trustworthiness of an arbitrary source. Historical receipts still reference omitted raw data, processed tables and development artifacts. This inventory verifies the public subset, not the entire archival hash chain. The `.sha256` files in `models/final_*` hash the configuration files, not the adjacent binaries.
