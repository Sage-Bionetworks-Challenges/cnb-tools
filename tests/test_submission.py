"""Unit tests for cnb_tools.modules.submission"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import submission
from cnb_tools.modules.client import UnknownSynapseID


class TestGetSubmission:
    """Tests for get_submission function"""

    @patch("cnb_tools.modules.submission.Submission")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submission_success(
        self, mock_get_client, MockSubmission, mock_submission_file
    ):
        """Test successfully getting a submission"""
        MockSubmission.return_value.get.return_value = mock_submission_file

        result = submission.get_submission(12345)

        MockSubmission.assert_called_once_with(id="12345")
        MockSubmission.return_value.get.assert_called_once()
        assert result == mock_submission_file

    @patch("cnb_tools.modules.submission.Submission")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_submission_invalid_id(self, mock_get_client, MockSubmission):
        """Test error handling for invalid submission ID"""
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Submission not found"}
        MockSubmission.return_value.get.side_effect = SynapseHTTPError(
            response=mock_response
        )

        with pytest.raises(UnknownSynapseID) as exc_info:
            submission.get_submission(99999)

        assert "Submission not found" in str(exc_info.value)


class TestDeleteSubmission:
    """Tests for delete_submission function"""

    @patch("cnb_tools.modules.submission.Submission")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_delete_submission(self, mock_get_client, MockSubmission, capsys):
        """Test deleting a submission"""
        submission.delete_submission(12345)

        MockSubmission.assert_called_once_with(id="12345")
        MockSubmission.return_value.delete.assert_called_once()

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

    @patch("cnb_tools.modules.submission.Evaluation")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_get_challenge_name(self, mock_get_client, MockEvaluation, mock_syn):
        """Test getting challenge name from evaluation"""
        mock_get_client.return_value = mock_syn
        mock_eval = MagicMock()
        mock_eval.content_source = "syn98765"
        MockEvaluation.return_value.get.return_value = mock_eval

        mock_challenge = MagicMock()
        mock_challenge.name = "Test Challenge"
        mock_syn.get.return_value = mock_challenge

        result = submission.get_challenge_name(12345)

        assert result == "Test Challenge"
        MockEvaluation.assert_called_once_with(id="12345")
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
        assert "ID:        12345" in captured.out
        assert "Challenge: Test Challenge" in captured.out
        assert "Date:      2025-11-26" in captured.out
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


class TestGetSubmissionContributors:
    """Tests for get_submission_contributors function"""

    @patch("cnb_tools.modules.submission.get_submission")
    def test_returns_contributor_ids(
        self, mock_get_sub, mock_submission_with_contributors
    ):
        """Test that contributor principal IDs are returned"""
        mock_get_sub.return_value = mock_submission_with_contributors

        result = submission.get_submission_contributors(12345)

        assert result == [
            {"principalId": "333", "createdOn": "2025-11-26T10:30:00.000Z"},
            {"principalId": "444", "createdOn": "2025-11-26T10:30:00.000Z"},
        ]
        mock_get_sub.assert_called_once_with(12345)

    @patch("cnb_tools.modules.submission.get_submission")
    def test_returns_empty_list_when_no_contributors(
        self, mock_get_sub, mock_submission_file
    ):
        """Test that an empty list is returned when there are no contributors"""
        mock_get_sub.return_value = mock_submission_file

        result = submission.get_submission_contributors(12345)

        assert result == []


class TestBatchDownloadSubmissions:
    """Tests for batch_download_submissions function"""

    @patch("cnb_tools.modules.submission.get_submitter_name")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_downloads_file_submissions(
        self, mock_get_client, mock_get_submitter, mock_syn, tmp_path, capsys
    ):
        """Test that file submissions are downloaded and renamed"""
        mock_get_client.return_value = mock_syn
        mock_get_submitter.return_value = "Test Team"

        sub = {"id": "12345", "teamId": "111", "userId": None, "dockerDigest": None}
        mock_syn.getSubmissions.return_value = [sub]

        # Create a real file that Path.rename can act on
        original_file = tmp_path / "predictions.csv"
        original_file.touch()
        downloaded = MagicMock()
        downloaded.filePath = str(original_file)
        mock_syn.getSubmission.return_value = downloaded

        submission.batch_download_submissions(98765, dest=str(tmp_path))

        mock_syn.getSubmissions.assert_called_once_with(98765, status=None)
        mock_syn.getSubmission.assert_called_once_with(
            "12345", downloadLocation=str(tmp_path / "Test_Team")
        )

        captured = capsys.readouterr()
        assert "Downloaded submission 12345" in captured.out
        assert "1 file(s) downloaded" in captured.out

    @patch("cnb_tools.modules.submission.get_submitter_name")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_skips_docker_submissions(
        self, mock_get_client, mock_get_submitter, mock_syn, tmp_path, capsys
    ):
        """Test that Docker submissions are skipped"""
        mock_get_client.return_value = mock_syn
        mock_get_submitter.return_value = "Test Team"

        sub = {
            "id": "12345",
            "teamId": "111",
            "userId": None,
            "dockerDigest": "sha256:abc123",
        }
        mock_syn.getSubmissions.return_value = [sub]

        submission.batch_download_submissions(98765, dest=str(tmp_path))

        mock_syn.getSubmission.assert_not_called()

        captured = capsys.readouterr()
        assert "Skipping submission 12345" in captured.out
        assert "0 file(s) downloaded" in captured.out

    @patch("cnb_tools.modules.submission.get_submitter_name")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_filters_by_status(
        self, mock_get_client, mock_get_submitter, mock_syn, tmp_path
    ):
        """Test that the status filter is passed to getSubmissions"""
        mock_get_client.return_value = mock_syn
        mock_syn.getSubmissions.return_value = []

        submission.batch_download_submissions(
            98765, dest=str(tmp_path), status="SCORED"
        )

        mock_syn.getSubmissions.assert_called_once_with(98765, status="SCORED")

    @patch("cnb_tools.modules.submission.get_submitter_name")
    @patch("cnb_tools.modules.submission.get_synapse_client")
    def test_organizes_by_submitter(
        self, mock_get_client, mock_get_submitter, mock_syn, tmp_path, capsys
    ):
        """Test that files from different submitters go into separate directories"""
        mock_get_client.return_value = mock_syn

        subs = [
            {"id": "111", "teamId": "11", "userId": None, "dockerDigest": None},
            {"id": "222", "teamId": "22", "userId": None, "dockerDigest": None},
        ]
        mock_syn.getSubmissions.return_value = subs
        mock_get_submitter.side_effect = ["Team A", "Team B"]

        for sub_id in ["111", "222"]:
            f = tmp_path / f"{sub_id}.csv"
            f.touch()

        def fake_get_submission(sid, downloadLocation):
            dl = MagicMock()
            dl.filePath = str(tmp_path / f"{sid}.csv")
            return dl

        mock_syn.getSubmission.side_effect = fake_get_submission

        submission.batch_download_submissions(98765, dest=str(tmp_path))

        captured = capsys.readouterr()
        assert "Team_A" in captured.out
        assert "Team_B" in captured.out
        assert "2 file(s) downloaded" in captured.out
