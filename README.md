# Unadjusted DiD with a Welch interval

A CPU baseline for the StatArena **Difference-in-Differences** domain. For each two-period panel, it subtracts the control group's mean outcome change from the treated group's mean outcome change. It estimates the average treatment effect on the treated (ATT) under no anticipation and unconditional parallel trends. If parallel trends holds only after adjustment for covariates, this baseline can be biased.

## Run one study

From this repository, with Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python did_welch.py study.npz > predictions.csv
```

Supply an NPZ with two arrays, `D` (0 for control, 1 for treated) and `delta_y` (post minus pre). Each row represents one unit; each array may be one-dimensional or a single column. The filename stem becomes the table ID. The script writes a header and one row with columns `table_id,estimate,ci_lower,ci_upper`. Covariates are optional and unused.

## Run with StatArena Lite

With the same Python environment, install Lite from an accessible copy of the Arena repository. Run these commands from the baseline directory, replacing the Arena path with your local checkout:

```sh
python -m pip install -e /path/to/Statistical-Intelligence-Arena/lite
statarena-lite run --domain did --split dev --method ./did_welch.py --output ./did-dev-predictions.csv
```

Lite calls `estimate(study)` once per study, writes the predictions CSV and prints its development metrics. The estimator uses only the current study's observed group indicators and changes. It has no fitted checkpoint, training split, tuning parameters or calibration stage.

## Interval and assumptions

The standard error is the square root of the sum of the two sample variances of the outcome change, each divided by its group size. The nominal two-sided 95% interval uses the Welch–Satterthwaite degrees of freedom. This calculation treats units as independent and permits unequal group variances. Common cluster shocks can invalidate its coverage. With zero sample variance in both groups, the calculated interval has zero width. The implementation requires finite observations and at least two units per group. [Welch formula (NIST)](https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm)
