# Synthetic mechanics demo

From the repository root, after installing `requirements-lock.txt`:

```bash
python -B demo/run_demo.py
python -B demo/run_demo.py --output-dir output/demo
```

The second command optionally saves `synthetic_input.csv` and `predictions.csv` in an ignored output directory. Re-running replaces those two demo outputs.

All observations are generated from explicit invented centers, scales and seeded noise. Nothing is extracted or adapted from NASA/CALCE measurements. A separate synthetic training cell supplies 210 rows (200 scorable); a separate demonstration cell supplies 30 rows, including a manually specified perturbation at cycles 21–23. The seven input measurements and their order match `deployment/pi/features.py`: duration and time to 3.4 V in seconds, mean voltage in volts, mean current in amperes, and mean/max/delta temperature in degrees Celsius, plus `cell_id` and consecutive `cycle`.

The first ten observations establish history and return `INSUFFICIENT_HISTORY`. Subsequent rows use prior-only median/MAD residuals, a synthetic-data-fitted StandardScaler and Isolation Forest, negative `score_samples`, and a training P95 threshold with strict `score > threshold` alerts. Both generators and the estimator have fixed seeds. Future observations cannot alter earlier features.

This is an executable illustration of software mechanics, not a physically validated battery simulator or an estimate of fault sensitivity/FPR. It does not use the released research model or attempt to reproduce the research percentages. Frozen models are checked separately by `python -B scripts/verify_artifacts.py --load-models`; see [reproduction](../docs/reproduction.md).
