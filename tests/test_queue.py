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


class TestGetEvaluationsByProject:
    """Tests for get_evaluations_by_project function"""

    @patch("cnb_tools.modules.queue.Evaluation")
    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_returns_list_of_evaluations(
        self, mock_get_client, MockEvaluation, mock_evaluation
    ):
        """Test successfully listing evaluations for a project"""
        MockEvaluation.get_evaluations_by_project.return_value = [mock_evaluation]

        result = queue.get_evaluations_by_project("syn12345")

        MockEvaluation.get_evaluations_by_project.assert_called_once_with(
            project_id="syn12345"
        )
        assert result == [mock_evaluation]

    @patch("cnb_tools.modules.queue.Evaluation")
    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_returns_empty_list_when_no_queues(self, mock_get_client, MockEvaluation):
        """Test returns empty list when project has no evaluation queues"""
        MockEvaluation.get_evaluations_by_project.return_value = []

        result = queue.get_evaluations_by_project("syn12345")

        assert result == []

    @patch("cnb_tools.modules.queue.Evaluation")
    @patch("cnb_tools.modules.queue.get_synapse_client")
    def test_raises_unknown_synapse_id_on_invalid_project(
        self, mock_get_client, MockEvaluation
    ):
        """Test error handling for invalid project ID"""
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Entity not found"}
        MockEvaluation.get_evaluations_by_project.side_effect = SynapseHTTPError(
            response=mock_response
        )

        with pytest.raises(UnknownSynapseID) as exc_info:
            queue.get_evaluations_by_project("syn99999")

        assert "Entity not found" in str(exc_info.value)
