"""Unit tests for cnb_tools.modules.queue"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import queue
from cnb_tools.modules.client import UnknownSynapseID


class TestGetEvaluation:
    """Tests for get_evaluation function"""

    @patch("cnb_tools.modules.queue.Evaluation")
    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_get_evaluation_success(
        self, mock_get_client, MockEvaluation, mock_evaluation
    ):
        """Test successfully getting an evaluation"""
        MockEvaluation.return_value.get.return_value = mock_evaluation

        result = queue.get_evaluation(98765)

        MockEvaluation.assert_called_once_with(id="98765")
        MockEvaluation.return_value.get.assert_called_once()
        assert result == mock_evaluation

    @patch("cnb_tools.modules.queue.Evaluation")
    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_get_evaluation_invalid_id(self, mock_get_client, MockEvaluation):
        """Test error handling for invalid evaluation ID"""
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Evaluation not found"}
        MockEvaluation.return_value.get.side_effect = SynapseHTTPError(
            response=mock_response
        )

        with pytest.raises(UnknownSynapseID) as exc_info:
            queue.get_evaluation(99999)

        assert "Evaluation not found" in str(exc_info.value)
