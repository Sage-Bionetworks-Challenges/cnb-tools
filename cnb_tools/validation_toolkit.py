import pandas as pd


def check_missing_keys(
    gold_col: pd.Series, pred_col: pd.Series, verbose: bool = False
) -> str:
    """Check for missing keys.

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
    gold_col: pd.Series, pred_col: pd.Series, verbose: bool = False
) -> str:
    """Check for unknown keys.

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


def check_duplicate_keys(pred_col: pd.Series, verbose: bool = False) -> str:
    """Check for duplicate keys.

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


def check_nan_values(pred_col: pd.Series) -> str:
    """Check for NAN predictions.

    Args:
      pred_col: Dataframe column containing the values to validate

    Returns:
       An error message, if any (default is an empty string)

    """
    nan_count = pred_col.isna().sum()
    if nan_count:
        return f"'{pred_col.name}' column contains {nan_count} NaN value(s)."
    return ""


# pylint: disable=unsupported-binary-operation
def check_values_range(
    pred_col: pd.Series, min_val: int | float = 0, max_val: int | float = 1
) -> str:
    """Check that predictions are between min and max values, inclusive.

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
