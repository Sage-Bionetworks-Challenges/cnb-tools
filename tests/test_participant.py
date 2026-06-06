"""Unit tests for cnb_tools.modules.participant"""

from unittest.mock import MagicMock, patch

import pytest
from synapseclient.models import Team

from cnb_tools.modules import participant



class TestCreateTeam:
    """Tests for create_team function"""

    @patch("cnb_tools.modules.participant.Team.from_name")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_new(self, mock_get_client, mock_from_name, mock_syn):
        """Test creating a new team when no team with the name exists"""
        mock_get_client.return_value = mock_syn
        mock_from_name.side_effect = ValueError("Team not found")

        mock_created = MagicMock(spec=Team)
        mock_created.name = "New Team"
        mock_created.description = "Test description"
        mock_created.can_public_join = True

        with patch.object(Team, "create", return_value=mock_created):
            result = participant.create_team(
                name="New Team", description="Test description", can_public_join=True
            )

        assert result.name == "New Team"

    @patch("builtins.input")
    @patch("cnb_tools.modules.participant.Team.from_name")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_existing_confirmed(
        self, mock_get_client, mock_from_name, mock_input, mock_syn
    ):
        """Test using an existing team when user confirms"""
        mock_get_client.return_value = mock_syn
        existing_team = MagicMock(spec=Team)
        existing_team.name = "Dream Team"
        mock_from_name.return_value = existing_team
        mock_input.return_value = "y"

        result = participant.create_team(name="Dream Team")

        assert result == existing_team
        mock_input.assert_called_once_with(
            "Team 'Dream Team' already exists. Use this team? (Y/n) "
        )

    @patch("builtins.input")
    @patch("cnb_tools.modules.participant.Team.from_name")
    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_create_team_existing_declined(
        self, mock_get_client, mock_from_name, mock_input, mock_syn
    ):
        """Test declining to use existing team exits"""
        mock_get_client.return_value = mock_syn
        existing_team = MagicMock(spec=Team)
        mock_from_name.return_value = existing_team
        mock_input.return_value = "n"

        with pytest.raises(SystemExit) as exc_info:
            participant.create_team(name="Existing Team")

        assert "Try again with a new challenge name" in str(exc_info.value)
