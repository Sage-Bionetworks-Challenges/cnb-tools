"""Unit tests for cnb_tools.modules.participant"""

from unittest.mock import MagicMock, patch

import pytest
from synapseclient import Team
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules import participant


class TestGetParticipantName:
    """Tests for get_participant_name function"""

    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_get_participant_name_team(self, mock_get_client, mock_syn):
        """Test getting team name"""
        mock_get_client.return_value = mock_syn
        mock_syn.getTeam.return_value = {"name": "Dream Team"}

        result = participant.get_participant_name(12345)

        assert result == "Dream Team"
        mock_syn.getTeam.assert_called_once_with(12345)

    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_get_participant_name_user(self, mock_get_client, mock_syn):
        """Test getting username when team lookup fails"""
        mock_get_client.return_value = mock_syn
        mock_syn.getTeam.side_effect = SynapseHTTPError(response=MagicMock())
        mock_syn.getUserProfile.return_value = {"userName": "john_doe"}

        result = participant.get_participant_name(67890)

        assert result == "john_doe"
        mock_syn.getUserProfile.assert_called_once_with(67890)


class TestCreateTeam:
    """Tests for create_team function"""

    @patch("cnb_tools.modules.participant.typer.confirm")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_new(self, mock_get_client, mock_confirm, mock_syn):
        """Test creating a new team"""
        mock_get_client.return_value = mock_syn
        mock_syn.getTeam.side_effect = ValueError("Team not found")

        result = participant.create_team(
            name="New Team", description="Test description", can_public_join=True
        )

        assert isinstance(result, Team)
        assert result.name == "New Team"
        assert result.description == "Test description"
        assert result.canPublicJoin is True

    @patch("cnb_tools.modules.participant.typer.confirm")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_existing_confirmed(
        self, mock_get_client, mock_confirm, mock_syn
    ):
        """Test using an existing team when user confirms"""
        mock_get_client.return_value = mock_syn
        existing_team = MagicMock(spec=Team)
        existing_team.name = "Dream Team"
        mock_syn.getTeam.return_value = existing_team
        mock_confirm.return_value = True

        result = participant.create_team(name="Dream Team")

        assert result == existing_team
        mock_confirm.assert_called_once_with(
            "Team 'Dream Team' already exists. Use this team?"
        )

    @patch("cnb_tools.modules.participant.typer.confirm")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_existing_declined(
        self, mock_get_client, mock_confirm, mock_syn
    ):
        """Test declining to use existing team exits"""
        mock_get_client.return_value = mock_syn
        existing_team = MagicMock(spec=Team)
        mock_syn.getTeam.return_value = existing_team
        mock_confirm.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            participant.create_team(name="Existing Team")

        assert "Try again with a new challenge name" in str(exc_info.value)
