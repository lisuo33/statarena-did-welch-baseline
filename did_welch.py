"""Two-period difference-in-differences with a Welch t interval."""

import argparse
import csv
from pathlib import Path
import sys

import numpy as np
from scipy.stats import t


def _vector(values, name):
    array = np.asarray(values)
    if array.ndim == 2 and array.shape[1] == 1:
        array = array[:, 0]
    if array.ndim != 1 or array.dtype.kind not in "biuf":
        raise ValueError(f"{name} must be a numeric vector or a single column")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains a missing or nonfinite value")
    return array


def estimate(study):
    """Return the contrast in mean changes and its nominal 95% interval."""
    treatment = _vector(study["D"], "D")
    change = _vector(study["delta_y"], "delta_y").astype(float, copy=False)
    if treatment.size != change.size or not np.isin(treatment, [0, 1]).all():
        raise ValueError("D must contain one binary treatment indicator per outcome change")

    treated = change[treatment == 1]
    control = change[treatment == 0]
    if min(treated.size, control.size) < 2:
        raise ValueError("Welch inference requires at least two units in each group")

    point = float(treated.mean() - control.mean())
    treated_var = treated.var(ddof=1) / treated.size
    control_var = control.var(ddof=1) / control.size
    variance = treated_var + control_var
    if variance == 0:
        return point, point, point

    treated_share = treated_var / variance
    control_share = control_var / variance
    df = 1 / (treated_share**2 / (treated.size - 1) + control_share**2 / (control.size - 1))
    margin = float(t.ppf(0.975, df) * np.sqrt(variance))
    return point, point - margin, point + margin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="One study in NumPy .npz format")
    args = parser.parse_args()
    with np.load(args.table, allow_pickle=False) as study:
        result = estimate(study)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["table_id", "estimate", "ci_lower", "ci_upper"])
    writer.writerow([args.table.stem, *result])


if __name__ == "__main__":
    main()
