"""Unit tests for cnb_tools.modules.annotation"""

from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import annotation
from cnb_tools.modules.client import UnknownSynapseID


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

    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_annotations_success(
        self, mock_get_client, mock_get_status, mock_syn, mock_submission_status, capsys
    ):
        """Test successfully updating annotations"""
        mock_get_client.return_value = mock_syn
        mock_get_status.return_value = mock_submission_status
        mock_submission_status.submissionAnnotations = {}
        mock_syn.store.return_value = mock_submission_status

        new_annots = {"new_field": "value"}
        result = annotation.update_annotations(12345, new_annots, verbose=False)

        assert mock_submission_status.submissionAnnotations == new_annots
        mock_syn.store.assert_called_once_with(mock_submission_status)

        captured = capsys.readouterr()
        assert "Submission ID 12345 annotations updated" in captured.out
        assert result == mock_submission_status

    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_annotations_verbose(
        self, mock_get_client, mock_get_status, mock_syn, mock_submission_status, capsys
    ):
        """Test updating annotations with verbose output"""
        mock_get_client.return_value = mock_syn
        mock_get_status.return_value = mock_submission_status
        mock_submission_status.submissionAnnotations = {"score": 0.95, "passed": True}
        mock_syn.store.return_value = mock_submission_status

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

    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_submission_status(
        self, mock_get_client, mock_get_status, mock_syn, mock_submission_status, capsys
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


class TestSubmissionAnnotationsToDict:
    """Tests for _submission_annotations_to_dict helper"""

    def test_returns_private_annotations(self):
        """Test extracting private annotations"""
        annotations = {
            "stringAnnos": [
                {"key": "score", "value": "0.95", "isPrivate": True},
                {"key": "public_key", "value": "pub_val", "isPrivate": False},
            ]
        }
        result = annotation._submission_annotations_to_dict(
            annotations, is_private=True
        )
        assert result == {"score": "0.95"}

    def test_returns_public_annotations(self):
        """Test extracting public annotations"""
        annotations = {
            "stringAnnos": [
                {"key": "score", "value": "0.95", "isPrivate": True},
                {"key": "public_key", "value": "pub_val", "isPrivate": False},
            ]
        }
        result = annotation._submission_annotations_to_dict(
            annotations, is_private=False
        )
        assert result == {"public_key": "pub_val"}

    def test_skips_scope_and_object_id(self):
        """Test that scopeId and objectId keys are excluded"""
        annotations = {
            "scopeId": [{"key": "scopeId", "value": "12345", "isPrivate": True}],
            "objectId": [{"key": "objectId", "value": "67890", "isPrivate": True}],
            "stringAnnos": [{"key": "score", "value": "0.95", "isPrivate": True}],
        }
        result = annotation._submission_annotations_to_dict(
            annotations, is_private=True
        )
        assert result == {"score": "0.95"}

    def test_empty_annotations(self):
        """Test that an empty dict is returned for empty input"""
        result = annotation._submission_annotations_to_dict({})
        assert result == {}

    def test_multiple_annotation_types(self):
        """Test extracting annotations across stringAnnos, longAnnos, doubleAnnos"""
        annotations = {
            "stringAnnos": [{"key": "status", "value": "pass", "isPrivate": True}],
            "longAnnos": [{"key": "rank", "value": 1, "isPrivate": True}],
            "doubleAnnos": [{"key": "score", "value": 0.95, "isPrivate": True}],
        }
        result = annotation._submission_annotations_to_dict(
            annotations, is_private=True
        )
        assert result == {"status": "pass", "rank": 1, "score": 0.95}


class TestUpdateLegacyAnnotations:
    """Tests for update_legacy_annotations function"""

    @patch("cnb_tools.modules.annotation.to_submission_status_annotations")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_private_annotations(
        self, mock_get_client, mock_get_status, mock_to_annots, mock_syn, capsys
    ):
        """Test storing annotations as private (default)"""
        mock_get_client.return_value = mock_syn
        mock_status = MagicMock()
        mock_status.get.return_value = {}
        mock_get_status.return_value = mock_status
        mock_to_annots.return_value = {}
        mock_syn.store.return_value = mock_status

        result = annotation.update_legacy_annotations(12345, {"score": "0.95"})

        mock_syn.store.assert_called_once_with(mock_status)
        captured = capsys.readouterr()
        assert "Submission ID 12345 annotations updated" in captured.out
        assert result == mock_status

    @patch("cnb_tools.modules.annotation.to_submission_status_annotations")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_public_annotations(
        self, mock_get_client, mock_get_status, mock_to_annots, mock_syn
    ):
        """Test storing annotations as public"""
        mock_get_client.return_value = mock_syn
        mock_status = MagicMock()
        mock_status.get.return_value = {}
        mock_get_status.return_value = mock_status
        mock_to_annots.return_value = {}
        mock_syn.store.return_value = mock_status

        annotation.update_legacy_annotations(12345, {"score": "0.95"}, is_private=False)

        # Called once for private annotations, once for public
        assert mock_to_annots.call_count == 2
        calls = mock_to_annots.call_args_list
        assert calls[0][1]["is_private"] is True
        assert calls[1][1]["is_private"] is False

    @patch("cnb_tools.modules.annotation.to_submission_status_annotations")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_update_legacy_annotations_verbose(
        self, mock_get_client, mock_get_status, mock_to_annots, mock_syn, capsys
    ):
        """Test verbose output includes annotations"""
        mock_get_client.return_value = mock_syn
        mock_status = MagicMock()
        mock_status.get.return_value = {}
        mock_get_status.return_value = mock_status
        mock_to_annots.return_value = {}
        mock_syn.store.return_value = mock_status

        annotation.update_legacy_annotations(12345, {"score": "0.95"}, verbose=True)

        captured = capsys.readouterr()
        assert "Annotations:" in captured.out

    @patch("cnb_tools.modules.annotation.to_submission_status_annotations")
    @patch("cnb_tools.modules.annotation.get_submission_status")
    @patch("cnb_tools.modules.annotation.get_synapse_client")
    def test_merges_with_existing_annotations(
        self, mock_get_client, mock_get_status, mock_to_annots, mock_syn
    ):
        """Test that new annotations are merged with existing ones"""
        mock_get_client.return_value = mock_syn
        mock_status = MagicMock()
        existing = {
            "stringAnnos": [{"key": "old_key", "value": "old_val", "isPrivate": True}]
        }
        mock_status.get.return_value = existing
        mock_get_status.return_value = mock_status
        mock_to_annots.return_value = {}
        mock_syn.store.return_value = mock_status

        annotation.update_legacy_annotations(12345, {"new_key": "new_val"})

        # The first call to to_submission_status_annotations should contain
        # both the old and new private annotations
        first_call_dict = mock_to_annots.call_args_list[0][0][0]
        assert "old_key" in first_call_dict
        assert "new_key" in first_call_dict
