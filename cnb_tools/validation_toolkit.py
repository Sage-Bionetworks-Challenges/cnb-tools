from pandas import Series


def check_missing_keys(
    gold_col: Series, pred_col: Series, verbose: bool = False
) -> str:
    """Check for missing keys.

    Tip: Example Use Case
      There is at least one prediction for every patient / sample / etc.

    Args:
      gold_col: Dataframe column containing the true keys
      pred_col: Dataframe column containing the keys to validate
      verbose: Include list of affected keys in error message

    Returns:
       An error message, if any (default is an empty string)

    """
    error = ""
    missing_ids = gold_col[~gold_col.isin(pred_col)]
    if missing_ids.any():
        error = f"Found {missing_ids.shape[0]} missing ID(s)"

        if verbose:
            error += f": {missing_ids.to_list()}"
    return error


def check_unknown_keys(
    gold_col: Series, pred_col: Series, verbose: bool = False
) -> str:
    """Check for unknown keys.

    Tip: Example Use Case
      There are no predictions without a corresponding groundtruth value.

    Args:
      gold_col: Dataframe column containing the true keys
      pred_col: Dataframe column containing the keys to validate
      verbose: Include list of affected keys in error message

    Returns:
       An error message, if any (default is an empty string)

    """
    error = ""
    unknown_ids = pred_col[~pred_col.isin(gold_col)]
    if unknown_ids.any():
        error = f"Found {unknown_ids.shape[0]} unknown ID(s)"

        if verbose:
            error += f": {unknown_ids.to_list()}"
    return error


def check_duplicate_keys(pred_col: Series, verbose: bool = False) -> str:
    """Check for duplicate keys.

    Tip: Example Use Case
      There is exactly one prediction for a patient / sample / etc.

    Args:
      pred_col: Dataframe column containing the keys to validate
      verbose: Include list of affected keys in error message

    Returns:
       An error message, if any (default is an empty string)

    """
    error = ""
    duplicates = pred_col.duplicated()
    if duplicates.any():
        error = f"Found {duplicates.sum()} duplicate ID(s)"

        if verbose:
            error += f": {pred_col[duplicates].to_list()}"
    return error


def check_nan_values(pred_col: Series) -> str:
    """Check for NAN values.

    Tip: Example Use Case
      Predictions must not be null / None.

    Args:
      pred_col: Dataframe column containing the values to validate

    Returns:
       An error message, if any (default is an empty string)

    """
    nan_count = pred_col.isna().sum()
    if nan_count:
        return f"'{pred_col.name}' column contains {nan_count} NaN value(s)."
    return ""


def check_binary_values(
    pred_col: Series, label1: int = 0, label2: int = 1
) -> str:
    """Check that values are binary (default: 0 or 1).

    Tip: Example Use Case
      Predictions can only be 0 (no disease present) or 1 (disease present).

    Args:
        pred_col: Dataframe column containing the values to validate.
        label1: First acceptable binary value.
        label2: Second acceptable binary value.

    Returns:
        An error message, if any (default is an empty string)

    """
    if not pred_col.isin([label1, label2]).all():
        return f"'{pred_col.name}' values should only be {label1} or {label2}."
    return ""


# pylint: disable=unsupported-binary-operation
def check_values_range(
    pred_col: Series, min_val: int | float = 0, max_val: int | float = 1
) -> str:
    """Check that values are between min and max values, inclusive.

    Tip: Example Use Case
      Predictions must be a probability from 0 (disease not likely) to 1
      (disease likely).

    Args:
      pred_col: Dataframe column containing the values to validate
      min_val: Lower limit of range
      max_val: Upper limit of range

    Returns:
       An error message, if any (default is an empty string)

    """
    if (pred_col < min_val).any() or (pred_col > max_val).any():
        return f"'{pred_col.name}' values should be between [{min_val}, {max_val}]."
    return ""
