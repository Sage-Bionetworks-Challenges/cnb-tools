"""Unit tests for cnb_tools.modules.annotation"""

from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import annotation
from cnb_tools.modules.base import UnknownSynapseID


class TestGetSubmissionStatus:
    """Tests for get_submission_status function"""

    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_get_submission_status_success(
        self, mock_get_client, mock_syn, mock_submission_status
    ):
        """Test successfully getting submission status"""
        mock_get_client.return_value = mock_syn
        mock_syn.getSubmissionStatus.return_value = mock_submission_status

        result = annotation.get_submission_status(12345)

        mock_syn.getSubmissionStatus.assert_called_once_with(12345)
        assert result == mock_submission_status

    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_get_submission_status_invalid_id(self, mock_get_client, mock_syn):
        """Test error handling for invalid submission ID"""
        mock_get_client.return_value = mock_syn
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Submission not found"}
        mock_syn.getSubmissionStatus.side_effect = SynapseHTTPError(
            response=mock_response
        )

        with pytest.raises(UnknownSynapseID) as exc_info:
            annotation.get_submission_status(99999)
        assert "Submission not found" in str(exc_info.value)


class TestUpdateAnnotations:
    """Tests for update_annotations function"""

    @patch("cnb_tools.modules.annotation.get_synapse_client")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    def test_update_annotations_success(
        self, mock_get_status, mock_get_client, mock_syn, mock_submission_status, capsys
    ):
        """Test successfully updating annotations"""
        mock_get_client.return_value = mock_syn
        mock_get_status.return_value = mock_submission_status
        mock_syn.store.return_value = mock_submission_status

        # Mock the submissionAnnotations attribute as a dictionary
        mock_submission_status.submissionAnnotations = MagicMock()

        new_annots = {"new_field": "value"}
        result = annotation.update_annotations(12345, new_annots, verbose=False)

        mock_submission_status.submissionAnnotations.update.assert_called_once_with(
            new_annots
        )
        mock_syn.store.assert_called_once_with(mock_submission_status)

        captured = capsys.readouterr()
        assert "Submission ID 12345 annotations updated" in captured.out
        assert result == mock_submission_status

    @patch("cnb_tools.modules.annotation.get_synapse_client")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    def test_update_annotations_verbose(
        self, mock_get_status, mock_get_client, mock_syn, mock_submission_status, capsys
    ):
        """Test updating annotations with verbose output"""
        mock_get_client.return_value = mock_syn
        mock_get_status.return_value = mock_submission_status
        mock_syn.store.return_value = mock_submission_status

        # Mock submissionAnnotations as a dict for JSON serialization
        mock_submission_status.submissionAnnotations = {"score": 0.95, "passed": True}

        annotation.update_annotations(12345, {"test": "value"}, verbose=True)

        captured = capsys.readouterr()
        assert "Annotations:" in captured.out
        assert "score" in captured.out


class TestUpdateAnnotationsFromFile:
    """Tests for update_annotations_from_file function"""

    @patch("cnb_tools.modules.annotation.with_retry")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"score": 0.85, "status": "pass", "null_field": null, "empty_list": []}',
    )
    def test_update_annotations_from_file(self, mock_file, mock_retry):
        """Test updating annotations from JSON file"""
        mock_retry.return_value = MagicMock()

        annotation.update_annotations_from_file(12345, "test.json", verbose=False)

        mock_file.assert_called_once_with("test.json", encoding="utf-8")

        # Verify with_retry was called
        assert mock_retry.called

        # Verify null and empty list values were filtered
        call_args = mock_retry.call_args
        assert call_args[1]["wait"] == 3
        assert call_args[1]["retries"] == 10


class TestUpdateSubmissionStatus:
    """Tests for update_submission_status function"""

    @patch("cnb_tools.modules.annotation.get_synapse_client")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    def test_update_submission_status(
        self, mock_get_status, mock_get_client, mock_syn, mock_submission_status, capsys
    ):
        """Test updating submission status"""
        mock_get_client.return_value = mock_syn
        mock_get_status.return_value = mock_submission_status
        mock_syn.store.return_value = mock_submission_status

        result = annotation.update_submission_status(12345, "ACCEPTED")

        assert mock_submission_status.status == "ACCEPTED"
        mock_syn.store.assert_called_once_with(mock_submission_status)

        captured = capsys.readouterr()
        assert "Updated submission ID 12345 to status: ACCEPTED" in captured.out
        assert result == mock_submission_status
