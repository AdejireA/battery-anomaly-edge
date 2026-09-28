# Data acquisition

This repository does not redistribute the raw NASA Ames or CALCE battery ageing datasets. Researchers wishing to reproduce feature extraction or model training from raw laboratory measurements must obtain the original data files directly from the providers and review each provider's current terms before reuse or redistribution.

## NASA Ames Li-ion Battery Aging Dataset

### Overview and source
The primary development dataset is the Li-ion Battery Aging Dataset published by the Prognostics Center of Excellence (PCoE) at NASA Ames Research Center. The dataset comprises commercially available 18650-size cylindrical cells with a nominal capacity of 2.0 Ah, run through repeated charge, discharge, and impedance cycles at room temperature.

### Required cells and partition roles
The research pipeline uses four specific cells from this collection:
- `B0005`: Training cell (nominal early-life proxy, cycles 1-50, with final fitted rows 11-50)
- `B0006`: Training cell (nominal early-life proxy, cycles 1-50, with final fitted rows 11-50)
- `B0007`: Validation cell (unseen cell evaluation, cycles 11 to 168)
- `B0018`: Guarded final evaluation cell (cycles 11 to 132)

### Expected format and placement
The raw files are distributed as MATLAB binary format (`.mat`) files. To reproduce extraction, download the archives corresponding to these cells and place the files under:
```
data/raw/nasa/
├── B0005.mat
├── B0006.mat
├── B0007.mat
└── B0018.mat
```

### Extraction script
Run the extraction script to process discharge cycles and compute physical cycle statistics:
```bash
python scripts/extract_nasa.py --raw-dir data/raw/nasa --output-dir data/processed/nasa
```
The script extracts cycle duration, cutoff voltage metrics, current, capacity, and temperature summaries into `data/processed/nasa/`.

## CALCE Battery Research Group Dataset

### Overview and source
The replication dataset comes from the Center for Advanced Life Cycle Engineering (CALCE) Battery Research Group at the University of Maryland. The study uses the prismatic CS2 cell series (lithium cobalt oxide chemistry, nominal capacity 1.1 Ah), subjected to continuous cycle-life testing under constant current charge and discharge regimes.

### Required cells and partition roles
The replication pipeline uses four CS2 cells:
- `CS2-35`: Training cell (nominal early-life proxy earliest 30% of accepted discharges; final fitted rows 11-264 for CS2-35 and 11-291 for CS2-36)
- `CS2-36`: Training cell (nominal early-life proxy earliest 30% of accepted discharges; final fitted rows 11-264 for CS2-35 and 11-291 for CS2-36)
- `CS2-37`: Validation cell (1,026 clean scorable cycles)
- `CS2-38`: Guarded final evaluation cell (1,015 clean scorable cycles)

### Expected format and placement
CALCE test records are provided as multi-sheet Microsoft Excel workbooks (`.xlsx`), where each workbook corresponds to a continuous testing interval. The extraction scripts expect each cell's workbooks in its own subdirectory:
```
data/raw/calce/
├── CS2_35/
│   ├── CS2_35_*.xlsx
├── CS2_36/
│   ├── CS2_36_*.xlsx
├── CS2_37/
│   ├── CS2_37_*.xlsx
└── CS2_38/
    ├── CS2_38_*.xlsx
```

### Extraction scripts
Due to the multi-workbook structure, extraction proceeds in two stages:
1. Validate workbook structure and reconstruct baseline discharge cycles:
```bash
python scripts/inspect_calce_workbooks.py
python scripts/extract_calce_cs2_35.py
```
2. Extract all four cells across testing periods:
```bash
python scripts/extract_calce.py
```
This produces structured per-cycle summaries in `data/processed/calce/`. Note that CALCE files do not include recorded temperature channels.

## Processing relative features

Once raw datasets are extracted, the causal history-relative residual features are computed:
```bash
# NASA relative features
python scripts/build_nasa_relative_features.py

# CALCE relative features
python scripts/build_calce_relative_features.py
```
These scripts compute rolling prior-cycle medians and median absolute deviations (MAD) with NASA histories 5/10/20 and CALCE history 10, writing tables to `data/processed/nasa_relative/` and `data/processed/calce/calce_cs2_relative_features.csv`.

## License and attribution note

This project does not assert any intellectual property rights or licensing over external datasets. Researchers are responsible for adhering to the respective data usage, attribution, and citation guidelines established by NASA PCoE and the CALCE Battery Research Group.

Run extraction only in an independent experimental checkout with an explicit output plan. Several scripts derive their root from their own location and may write reports or figures as well as processed data; changing the shell working directory alone is insufficient. These instructions describe external-data preparation, not actions performed for this release. Original repository material uses MIT; external data and third-party terms remain separate.
