"""Unit tests for cnb_tools.validation_toolkit"""

import pandas as pd
from cnb_tools import validation_toolkit


class TestCheckMissingKeys:
    """Tests for check_missing_keys function"""

    def test_no_missing_keys(self, truth_ids, pred_ids_valid):
        """Test when all keys are present"""
        result = validation_toolkit.check_missing_keys(truth_ids, pred_ids_valid)
        assert result == ""

    def test_missing_keys(self, truth_ids, pred_ids_invalid):
        """Test when keys are missing"""
        result = validation_toolkit.check_missing_keys(truth_ids, pred_ids_invalid)
        assert "Found 2 missing ID(s)" in result

    def test_missing_keys_verbose(self, truth_ids, pred_ids_invalid):
        """Test missing keys with verbose output"""
        result = validation_toolkit.check_missing_keys(
            truth_ids, pred_ids_invalid, verbose=True
        )
        assert "Found 2 missing ID(s)" in result
        assert "id2" in result
        assert "id3" in result


class TestCheckUnknownKeys:
    """Tests for check_unknown_keys function"""

    def test_no_unknown_keys(self, truth_ids, pred_ids_valid):
        """Test when no unknown keys are present"""
        result = validation_toolkit.check_unknown_keys(truth_ids, pred_ids_valid)
        assert result == ""

    def test_unknown_keys(self, truth_ids, pred_ids_invalid):
        """Test when unknown keys are present"""
        result = validation_toolkit.check_unknown_keys(truth_ids, pred_ids_invalid)
        assert "Found 1 unknown ID(s)" in result

    def test_unknown_keys_verbose(self, truth_ids, pred_ids_invalid):
        """Test unknown keys with verbose output"""
        result = validation_toolkit.check_unknown_keys(
            truth_ids, pred_ids_invalid, verbose=True
        )
        assert "Found 1 unknown ID(s)" in result
        assert "id4" in result


class TestCheckDuplicateKeys:
    """Tests for check_duplicate_keys function"""

    def test_no_duplicates(self, pred_ids_valid):
        """Test when no duplicate keys are present"""
        result = validation_toolkit.check_duplicate_keys(pred_ids_valid)
        assert result == ""

    def test_duplicates(self, pred_ids_invalid):
        """Test when duplicate keys are present"""
        result = validation_toolkit.check_duplicate_keys(pred_ids_invalid)
        assert "Found 1 duplicate ID(s)" in result

    def test_duplicates_verbose(self, pred_ids_invalid):
        """Test duplicate keys with verbose output"""
        result = validation_toolkit.check_duplicate_keys(pred_ids_invalid, verbose=True)
        assert "Found 1 duplicate ID(s)" in result
        assert "id1" in result


class TestCheckNanValues:
    """Tests for check_nan_values function"""

    def test_no_nan_values(self, pred_values_valid):
        """Test when no NaN values are present"""
        result = validation_toolkit.check_nan_values(pred_values_valid["predictions"])
        assert result == ""

    def test_with_nan_values(self, pred_values_invalid):
        """Test when NaN values are present"""
        result = validation_toolkit.check_nan_values(pred_values_invalid["predictions"])
        assert "'predictions' column contains" in result
        assert "NaN" in result

    def test_with_inf_values(self):
        """Test that inf values are flagged when include_inf=True"""
        import numpy as np

        col = pd.Series([0.5, np.inf], name="predictions")
        result = validation_toolkit.check_nan_values(col, include_inf=True)
        assert "infinite" in result

    def test_inf_ignored_by_default(self):
        """Test that inf values are ignored when include_inf=False (default)"""
        import numpy as np

        col = pd.Series([0.5, np.inf], name="predictions")
        result = validation_toolkit.check_nan_values(col)
        assert result == ""

    def test_with_nan_and_inf_values(self):
        """Test when both NaN and infinite values are present"""
        import numpy as np

        col = pd.Series([None, np.inf], name="predictions")
        result = validation_toolkit.check_nan_values(col, include_inf=True)
        assert "NaN" in result
        assert "infinite" in result


class TestCheckBinaryValues:
    """Tests for check_binary_values function"""

    def test_valid_binary_values_default(self, pred_values_valid):
        """Test valid binary values with default labels (0, 1)"""
        result = validation_toolkit.check_binary_values(
            pred_values_valid["predictions"]
        )
        assert result == ""

    def test_invalid_binary_values(self):
        """Test invalid binary values"""
        col = pd.Series([0, 1, 2], name="predictions")
        result = validation_toolkit.check_binary_values(col)
        assert "'predictions' values should only be 0 or 1" in result

    def test_nan_does_not_trigger_binary_error(self):
        """NaN values should not produce a binary error (check_nan_values handles them)"""
        col = pd.Series([0, 1, None], name="predictions")
        result = validation_toolkit.check_binary_values(col)
        assert result == ""


class TestCheckNotConstant:
    """Tests for check_not_constant function"""

    def test_not_constant(self, pred_values_valid):
        """Test when column has multiple unique values"""
        result = validation_toolkit.check_not_constant(pred_values_valid["predictions"])
        assert result == ""

    def test_constant(self):
        """Test when all values are the same"""
        col = pd.Series([0, 0, 0], name="predictions")
        result = validation_toolkit.check_not_constant(col)
        assert "'predictions' column contains only one unique value" in result

    def test_constant_ignores_nan(self):
        """NaN values are ignored when checking for constant columns"""
        col = pd.Series([1, 1, None], name="predictions")
        result = validation_toolkit.check_not_constant(col)
        assert "'predictions' column contains only one unique value" in result


class TestCheckValuesRange:
    """Tests for check_values_range function"""

    def test_valid_range_default(self, pred_values_valid):
        """Test values within default range [0, 1]"""
        result = validation_toolkit.check_values_range(
            pred_values_valid["probabilities"]
        )
        assert result == ""

    def test_invalid_range_below_min(self, pred_values_invalid):
        """Test values below minimum"""
        result = validation_toolkit.check_values_range(
            pred_values_invalid["probabilities"]
        )
        assert "'probabilities' values should be between [0, 1]" in result

    def test_invalid_range_above_max(self, pred_values_invalid):
        """Test values above maximum"""
        result = validation_toolkit.check_values_range(
            pred_values_invalid["probabilities"]
        )
        assert "'probabilities' values should be between [0, 1]" in result

    def test_nan_does_not_trigger_range_error(self):
        """NaN values should be ignored; use check_nan_values to catch them"""
        col = pd.Series([0.5, None], name="probabilities")
        result = validation_toolkit.check_values_range(col)
        assert result == ""


class TestCheckValidValues:
    """Tests for check_valid_values function"""

    def test_all_valid(self):
        """Test when all values are in the allowed set"""
        col = pd.Series(["low", "medium", "high"], name="label")
        result = validation_toolkit.check_valid_values(col, {"low", "medium", "high"})
        assert result == ""

    def test_invalid_values(self):
        """Test when values outside the allowed set are present"""
        col = pd.Series(["low", "medium", "unknown"], name="label")
        result = validation_toolkit.check_valid_values(col, {"low", "medium", "high"})
        assert "'label' contains invalid value(s)" in result
        assert "unknown" in result

    def test_nan_ignored(self):
        """NaN values should not be flagged as invalid values"""
        col = pd.Series(["low", None], name="label")
        result = validation_toolkit.check_valid_values(col, {"low", "medium", "high"})
        assert result == ""
