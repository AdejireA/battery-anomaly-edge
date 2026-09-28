# Raspberry Pi edge deployment package

This directory contains the standalone edge deployment runtime designed to execute causal history-relative anomaly scoring on physical Raspberry Pi hardware.

## Deployment purpose and architecture

The deployment package provides a minimal, self-contained inference runtime:
- `features.py`: Computes causal history-relative residual features for each completed discharge cycle using a rolling buffer of prior observations. Only prior cycles within the sliding window ($k=10$) are included.
- `infer.py`: Standalone CLI tool that accepts cycle observation data, loads the serialized model and scaler, scales features, calculates the anomaly score ($- \text{score\_samples}(z)$), and compares it against the frozen decision threshold ($0.554868$).
- `validate_playback.py`: Replay harness that processes recorded cycle sequences and verifies that edge scores match workstation research scores within numerical precision ($10^{-12}$).
- `benchmark.py`: Timing and resource profiling harness that benchmarks feature extraction, model scoring, memory usage, and throughput across 1,000 repeated observations.

## Physical hardware benchmark environment

The physical hardware benchmark was conducted on actual single-board edge hardware with the following recorded specifications:

- **Device:** Raspberry Pi 3B+
- **Processor:** ARM Cortex-A53 (ARMv8 64-bit), 4 cores @ 1.2 GHz
- **Operating system:** Debian GNU/Linux 13 (trixie), kernel 6.18.50+rpt-rpi-v8 (aarch64)
- **Python version:** Python 3.13.5
- **System memory:** 905 MiB RAM, 904 MiB swap
- **Hardware environment log:** Preserved in [results/pi_environment.txt](results/pi_environment.txt)

## Executed benchmark results

The benchmark executed 1,000 timed inference calls with 100 untimed warmup calls using 122 distinct B0018 historical contexts:

| Metric | Median | 95th Percentile | Minimum | Maximum |
|---|---|---|---|---|
| Feature computation | 0.76 ms | 0.85 ms | 0.74 ms | 1.04 ms |
| Model inference | 63.00 ms | 64.17 ms | 62.16 ms | 87.87 ms |
| **Combined cycle latency** | **63.77 ms** | **64.94 ms** | **62.92 ms** | **88.63 ms** |

- **Inference throughput:** 15.64 observations/second
- **Memory consumption (RSS):** Approximately 130 MB
- **Power consumption:** Not measured

### Historical memory accounting note
In `results/pi_benchmark.json`, `psutil` reported:
- `rss_bytes`: 129,765,376 (~123.76 MiB)
- `peak_rss_bytes`: 129,392,640 (~123.40 MiB)

These are before-run counters. After-run RSS/peak are 130,093,056/129,785,856 bytes. Both pairs report peak below current RSS; the cause is not established by the records. Preserve the discrepancy and do not use peak RSS as a reliable upper bound.

## Prediction equivalence validation

Playback validation on test cell B0018 verified complete numerical equivalence between workstation research outputs and edge execution:
- Total scorable cycles: 122
- Prediction mismatches: 0
- Maximum score difference: 0.0
- Flagged cycles: 5 (cycles 46, 47, 106, 107, 108; clean FPR = 4.10%)
- Receipt: Preserved in [results/playback_validation.json](results/playback_validation.json)

## Understanding verification receipts

The receipt in `results/integrity_verification.json` includes:
```json
"pi_hardware_tested": false
```
This flag belongs to the pre-transfer packaging verification stage, which was executed on the x86_64 development workstation before transfer to verify that all deployment dependencies and files were bundled. It does not contradict the subsequent physical Raspberry Pi benchmark records ([results/pi_benchmark.json](results/pi_benchmark.json) and [results/pi_environment.txt](results/pi_environment.txt)), which document execution on the physical device.

## Omitted binaries and reproduction instructions

This release omits `artifacts/model.joblib`, `artifacts/scaler.joblib` and `sample_data/`. The runtime cannot execute from the compact public tree alone.

`infer.py` requires the exact trusted historical model/scaler hashes and pinned dependencies. Training a new absolute-feature model with `train_nasa_isolation_forest.py` cannot supply these artifacts, and independently fitting a relative model does not guarantee their bytes. Historical replay requires the omitted approved archival artifacts and inputs; no download is promised here. Do not disable hash checks or alter frozen constants to force a new model to load.

The recorded Pi environment used Python 3.13.5 with dependencies listed in `requirements-pi.txt`. Inspect the implementation and [benchmark evidence](results/pi_benchmark.json) directly without running inference. Warm timing excludes CSV I/O and context preparation; fresh-process loading does not flush OS caches.

## Operational scope and limitations

- **Cycle-level inference:** Inference runs once at the end of each completed discharge cycle. It is not designed for continuous high-frequency intra-cycle waveform monitoring.
- **Playback inference:** Hardware results demonstrate compute feasibility and latency under sequential replay; they do not represent real-time integration with physical battery cell ADC sensors or CAN-bus telemetry.
- **Advisory monitoring:** The detector produces an anomaly score and alarm flag for diagnostic monitoring. It does not replace certified Battery Management System (BMS) hardware protection circuitry (over-voltage, under-voltage, over-temperature, and short-circuit cutoffs).
