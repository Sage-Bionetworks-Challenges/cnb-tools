# How-To: Write a Validation Script

This guide walks through writing a validation script for a Synapse challenge
using the `cnb_tools.validation_toolkit` module (imported here as `vtk`).

Validation scripts are designed to catch malformed or incomplete prediction
files **before** they reach the scoring step, returning a machine-readable
result that the evaluation workflow can act on.

---

## Overview

A typical validation script does four things:

1. Reads the prediction file submitted by a participant
2. Reads the groundtruth file to determine what a valid prediction looks like
3. Runs a series of checks and collects any error messages
4. Writes a JSON result file containing a `submission_status` and `submission_errors`

The last step is optional, but is standard practice in the evaluation workflows
developed at Sage.

The `validation_toolkit` module provides ready-made check functions for the
most common validation patterns, so you don't have to write them from scratch.

---

## Available Check Functions

| Function | What it checks |
|---|---|
| `check_missing_keys(gold_col, pred_col)` | Every groundtruth ID has a matching prediction |
| `check_unknown_keys(gold_col, pred_col)` | No prediction IDs are absent from the groundtruth |
| `check_duplicate_keys(pred_col)` | No ID appears more than once in the prediction file |
| `check_nan_values(pred_col, include_inf)` | No `NaN` or `None` values; set `include_inf=True` to also flag `inf`/`-inf` |
| `check_binary_values(pred_col)` | All values are 0 or 1 (configurable via `label1`/`label2`); NaN values are ignored |
| `check_values_range(pred_col, min_val, max_val)` | All values fall within `[min_val, max_val]`; NaN values are ignored |
| `check_valid_values(pred_col, valid_values)` | All values belong to an allowed set (e.g. category labels); NaN values are ignored |
| `check_not_constant(pred_col)` | Column has more than one unique non-null value |

All functions return an **empty string** when the check passes, or a
**descriptive error message** when it fails. This makes it easy to collect
errors in a list and filter out the empty strings at the end.

---

## Worked Example

Below is a minimal example of a `validate()` function for a challenge where
participants submit a CSV with one row per sample and a single numeric
prediction column with values in the range [0, 1].

```python
import pandas as pd
from cnb_tools import validation_toolkit as vtk

# Groundtruth: only the ID column is needed for key checks.
ID_COL = "id"
GROUNDTRUTH_COLS = {ID_COL: str}

# Required columns in the prediction file and their expected dtypes.
PREDICTION_COLS = {ID_COL: str, "score": float}


def validate(gt_file: str, pred_file: str) -> list[str]:
    errors = []
    truth = pd.read_csv(gt_file, usecols=GROUNDTRUTH_COLS, dtype=GROUNDTRUTH_COLS)

    try:
        pred = pd.read_csv(
            pred_file,
            usecols=list(PREDICTION_COLS),
            dtype=PREDICTION_COLS,
            float_precision="round_trip",
        )
        assert set(PREDICTION_COLS).issubset(pred.columns)
    except (ValueError, AssertionError):
        return [f"Missing required columns. Expecting: {list(PREDICTION_COLS)}."]

    errors.append(vtk.check_duplicate_keys(pred[ID_COL]))
    errors.append(vtk.check_missing_keys(truth[ID_COL], pred[ID_COL]))
    errors.append(vtk.check_unknown_keys(truth[ID_COL], pred[ID_COL]))
    errors.append(vtk.check_nan_values(pred["score"]))
    errors.append(vtk.check_values_range(pred["score"], min_val=0, max_val=1))

    return [e for e in errors if e]
```

!!! tip "Useful options"
    - Pass `verbose=True` to `check_missing_keys`, `check_unknown_keys`, and
      `check_duplicate_keys` to include the actual offending IDs in the error
      message — useful during development.
    - Pass `include_inf=True` to `check_nan_values` if infinite values should
      also be treated as invalid.

!!! note "Integrating with a Synapse workflow"
    The `validate()` function returns a plain list of error strings and has no
    Synapse-specific dependencies — you can call it from any orchestration
    layer. If you are building a Synapse-based evaluation pipeline, refer to
    our starter templates:

    - [orca-evaluation-templates](https://github.com/Sage-Bionetworks-Challenges/orca-evaluation-templates)
    - [data-to-model-challenge-workflow](https://github.com/Sage-Bionetworks-Challenges/data-to-model-challenge-workflow)
    - [model-to-data-challenge-workflow](https://github.com/Sage-Bionetworks-Challenges/model-to-data-challenge-workflow)

### Multi-task challenges

For challenges with more than one task, write a `validate_task2()` (etc.) and
route by evaluation queue ID:

```python
def validate(task_number: int, gt_file: str, pred_file: str) -> list[str]:
    validation_func = {
        12345678: validate_task1,
        12345679: validate_task2,
    }.get(task_number)

    if validation_func:
        return validation_func(gt_file=gt_file, pred_file=pred_file)
    return [f"Invalid task number: `{task_number}`"]
```

---

## Adding Custom Checks

The built-in functions cover the most common cases, but you can write your own
in the same style — return `""` on pass, or a descriptive message string on
failure:

```python
def check_no_future_dates(col: pd.Series, cutoff: str) -> str:
    """Check that no dates are after the cutoff."""
    invalid = col[pd.to_datetime(col) > pd.Timestamp(cutoff)]
    if not invalid.empty:
        return f"'{col.name}' contains {len(invalid)} date(s) after {cutoff}."
    return ""
```

Then use it like any built-in check:

```python
errors.append(check_no_future_dates(pred["date"], cutoff="2025-01-01"))
```

---
