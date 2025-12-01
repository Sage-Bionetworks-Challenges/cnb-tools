"""Unit tests for cnb_tools.modules.submission"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import submission
from cnb_tools.modules.base import UnknownSynapseID


class TestGetSubmission:
    """Tests for get_submission function"""

    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submission_success(
        self, mock_get_client, mock_syn, mock_submission_file
    ):
        """Test successfully getting a submission"""
        mock_get_client.return_value = mock_syn
        mock_syn.getSubmission.return_value = mock_submission_file

        result = submission.get_submission(12345, download_file=False)

        mock_syn.getSubmission.assert_called_once_with(12345, downloadFile=False)
        assert result == mock_submission_file

    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submission_invalid_id(self, mock_get_client, mock_syn):
        """Test error handling for invalid submission ID"""
        mock_get_client.return_value = mock_syn
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Submission not found"}
        mock_syn.getSubmission.side_effect = SynapseHTTPError(response=mock_response)

        with pytest.raises(UnknownSynapseID) as exc_info:
            submission.get_submission(99999)

        assert "Submission not found" in str(exc_info.value)


class TestDeleteSubmission:
    """Tests for delete_submission function"""

    @patch("cnb_tools.modules.submission.get_synapse_client")
    @patch("cnb_tools.modules.submission.get_submission")
    def test_delete_submission(
        self, mock_get_sub, mock_get_client, mock_syn, mock_submission_file, capsys
    ):
        """Test deleting a submission"""
        mock_get_client.return_value = mock_syn
        mock_get_sub.return_value = mock_submission_file

        submission.delete_submission(12345)

        mock_get_sub.assert_called_once_with(12345)
        mock_syn.delete.assert_called_once_with(mock_submission_file)

        captured = capsys.readouterr()
        assert "Submission deleted: 12345" in captured.out


class TestDownloadSubmission:
    """Tests for download_submission function"""

    @patch("cnb_tools.modules.submission.get_synapse_client")
    @patch("cnb_tools.modules.submission.get_submission")
    def test_download_submission_file(
        self, mock_get_sub, mock_get_client, mock_syn, mock_submission_file, capsys
    ):
        """Test downloading a file submission"""
        mock_get_client.return_value = mock_syn
        mock_get_sub.return_value = mock_submission_file

        submission.download_submission(12345, dest="/tmp")

        mock_syn.getSubmission.assert_called_once_with(12345, downloadLocation="/tmp")

        captured = capsys.readouterr()
        assert "Submission ID 12345 downloaded to:" in captured.out

    @patch("cnb_tools.modules.submission.get_synapse_client")
    @patch("cnb_tools.modules.submission.get_submission")
    def test_download_submission_docker(
        self, mock_get_sub, mock_get_client, mock_syn, mock_submission_docker, capsys
    ):
        """Test 'downloading' a Docker submission (displays pull command)"""
        mock_get_client.return_value = mock_syn
        mock_get_sub.return_value = mock_submission_docker

        submission.download_submission(12345)

        captured = capsys.readouterr()
        assert "Docker image" in captured.out
        assert "docker pull" in captured.out
        assert "docker.synapse.org/syn12345/model@sha256:abc123" in captured.out


class TestGetSubmitterName:
    """Tests for get_submitter_name function"""

    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submitter_name_team(self, mock_get_client, mock_syn):
        """Test getting team name"""
        mock_get_client.return_value = mock_syn
        mock_syn.getTeam.return_value = {"name": "Test Team"}

        result = submission.get_submitter_name(111)

        assert result == "Test Team"

    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submitter_name_user(self, mock_get_client, mock_syn):
        """Test getting username when team lookup fails"""
        mock_get_client.return_value = mock_syn
        mock_syn.getTeam.side_effect = SynapseHTTPError(response=Mock())
        mock_syn.getUserProfile.return_value = {"userName": "testuser"}

        result = submission.get_submitter_name(222)

        assert result == "testuser"


class TestGetChallengeName:
    """Tests for get_challenge_name function"""

    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_challenge_name(self, mock_get_client, mock_syn):
        """Test getting challenge name from evaluation"""
        mock_get_client.return_value = mock_syn
        mock_eval = MagicMock()
        mock_eval.contentSource = "syn98765"
        mock_syn.getEvaluation.return_value = mock_eval

        mock_challenge = MagicMock()
        mock_challenge.name = "Test Challenge"
        mock_syn.get.return_value = mock_challenge

        result = submission.get_challenge_name(12345)

        assert result == "Test Challenge"
        mock_syn.get.assert_called_once_with("syn98765")


class TestPrintSubmissionInfo:
    """Tests for print_submission_info function"""

    @patch("cnb_tools.modules.submission.get_submission")
    @patch("cnb_tools.modules.submission.get_challenge_name")
    @patch("cnb_tools.modules.submission.get_submitter_name")
    def test_print_submission_info_basic(
        self,
        mock_get_submitter,
        mock_get_challenge,
        mock_get_sub,
        mock_submission_file,
        capsys,
    ):
        """Test printing basic submission info"""
        mock_get_sub.return_value = mock_submission_file
        mock_get_challenge.return_value = "Test Challenge"
        mock_get_submitter.return_value = "Test Team"

        submission.print_submission_info(12345, verbose=False)

        captured = capsys.readouterr()
        assert "ID: 12345" in captured.out
        assert "Challenge: Test Challenge" in captured.out
        assert "Date: 2025-11-26" in captured.out
        assert "Submitter: Test Team" in captured.out

    @patch("cnb_tools.modules.submission.annotation")
    @patch("cnb_tools.modules.submission.get_submission")
    @patch("cnb_tools.modules.submission.get_challenge_name")
    @patch("cnb_tools.modules.submission.get_submitter_name")
    def test_print_submission_info_verbose(
        self,
        mock_get_submitter,
        mock_get_challenge,
        mock_get_sub,
        mock_annotation,
        mock_submission_file,
    ):
        """Test printing submission info with annotations"""
        mock_get_sub.return_value = mock_submission_file
        mock_get_challenge.return_value = "Test Challenge"
        mock_get_submitter.return_value = "Test Team"

        mock_status = MagicMock()
        mock_annotation.get_submission_status.return_value = mock_status
        mock_annotation.format_annotations.return_value = "Formatted annotations"

        submission.print_submission_info(12345, verbose=True)

        mock_annotation.get_submission_status.assert_called_once_with(12345)
        mock_annotation.format_annotations.assert_called_once_with(mock_status)
