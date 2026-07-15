"""Unit tests for cnb_tools.modules.challenge"""

from unittest.mock import Mock, patch

import pytest
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import challenge
from cnb_tools.modules.client import UnknownSynapseID


class TestGetChallenge:
    """Tests for get_challenge function"""

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_returns_challenge_dict(self, mock_get_client, mock_syn):
        """Test successfully retrieving a challenge for a project"""
        mock_get_client.return_value = mock_syn
        mock_syn.restGET.return_value = {
            "id": "1",
            "projectId": "syn12345",
            "participantTeamId": "99",
            "etag": "abc",
        }

        result = challenge.get_challenge("syn12345")

        mock_syn.restGET.assert_called_once_with("/entity/syn12345/challenge")
        assert result["id"] == "1"
        assert result["participantTeamId"] == "99"

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_raises_unknown_synapse_id_when_not_a_challenge(self, mock_get_client, mock_syn):
        """Test error raised when project has no associated challenge"""
        mock_get_client.return_value = mock_syn
        mock_response = Mock()
        mock_response.json.return_value = {"reason": "Not a challenge project"}
        mock_syn.restGET.side_effect = SynapseHTTPError(response=mock_response)

        with pytest.raises(UnknownSynapseID) as exc_info:
            challenge.get_challenge("syn99999")

        assert "Not a challenge project" in str(exc_info.value)


class TestCreateChallenge:
    """Tests for create_challenge function"""

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_posts_correct_body_and_returns_result(self, mock_get_client, mock_syn):
        """Test that create_challenge POSTs with correct body"""
        import json

        mock_get_client.return_value = mock_syn
        mock_syn.restPOST.return_value = {
            "id": "2",
            "projectId": "syn12345",
            "participantTeamId": "77",
        }

        result = challenge.create_challenge("syn12345", "77")

        args, _ = mock_syn.restPOST.call_args
        assert args[0] == "/challenge"
        body = json.loads(args[1])
        assert body["projectId"] == "syn12345"
        assert body["participantTeamId"] == "77"
        assert result["id"] == "2"


class TestDeleteChallenge:
    """Tests for delete_challenge function"""

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_calls_delete_with_challenge_id(self, mock_get_client, mock_syn):
        """Test that delete_challenge calls the correct REST endpoint"""
        mock_get_client.return_value = mock_syn

        challenge.delete_challenge("42")

        mock_syn.restDELETE.assert_called_once_with("/challenge/42")


class TestGetRegisteredTeams:
    """Tests for get_registered_teams function"""

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_returns_list_of_team_records(self, mock_get_client, mock_syn):
        """Test successfully listing registered teams"""
        mock_get_client.return_value = mock_syn
        mock_syn._GET_paginated.return_value = iter([{"teamId": "10"}, {"teamId": "20"}])

        result = challenge.get_registered_teams("1")

        mock_syn._GET_paginated.assert_called_once_with("/challenge/1/challengeTeam")
        assert len(result) == 2
        assert result[0]["teamId"] == "10"

    @patch("cnb_tools.modules.challenge.get_synapse_client")
    def test_returns_empty_list_when_no_teams(self, mock_get_client, mock_syn):
        """Test returns empty list when no teams are registered"""
        mock_get_client.return_value = mock_syn
        mock_syn._GET_paginated.return_value = iter([])

        result = challenge.get_registered_teams("1")

        assert result == []
