"""Unit tests for cnb_tools.modules.queue"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import queue
from cnb_tools.modules.base import UnknownSynapseID


class TestGetEvaluation:
    """Tests for get_evaluation function"""

    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_get_evaluation_success(self, mock_get_client, mock_syn, mock_evaluation):
        """Test successfully getting an evaluation"""
        mock_get_client.return_value = mock_syn
        mock_syn.getEvaluation.return_value = mock_evaluation

        result = queue.get_evaluation(98765)

        mock_syn.getEvaluation.assert_called_once_with(98765)
        assert result == mock_evaluation

    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_get_evaluation_invalid_id(self, mock_get_client, mock_syn):
        """Test error handling for invalid evaluation ID"""
        mock_get_client.return_value = mock_syn
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Evaluation not found"}
        mock_syn.getEvaluation.side_effect = SynapseHTTPError(response=mock_response)

        with pytest.raises(UnknownSynapseID) as exc_info:
            queue.get_evaluation(99999)

        assert "Evaluation not found" in str(exc_info.value)


class TestGetEvaluationName:
    """Tests for get_evaluation_name function"""

    @patch("cnb_tools.modules.queue.get_evaluation")
    def test_get_evaluation_name(self, mock_get_eval, mock_evaluation):
        """Test getting evaluation name"""
        mock_get_eval.return_value = mock_evaluation

        result = queue.get_evaluation_name(98765)

        assert result == "Test Queue"
        mock_get_eval.assert_called_once_with(98765)


class TestGetChallengeNameFromEvaluation:
    """Tests for get_challenge_name_from_evaluation function"""

    @patch("cnb_tools.modules.queue.get_synapse_client")
    @patch("cnb_tools.modules.queue.get_evaluation")
    def test_get_challenge_name_from_evaluation(
        self, mock_get_eval, mock_get_client, mock_syn, mock_evaluation
    ):
        """Test getting challenge name from evaluation"""
        mock_get_eval.return_value = mock_evaluation
        mock_get_client.return_value = mock_syn

        mock_challenge = MagicMock()
        mock_challenge.name = "Amazing Challenge"
        mock_syn.get.return_value = mock_challenge

        result = queue.get_challenge_name_from_evaluation(98765)

        assert result == "Amazing Challenge"
        mock_syn.get.assert_called_once_with("syn12345")
