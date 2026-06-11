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


class TestDisableTeamEmail:
    """Tests for disable_team_email function"""

    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_removes_send_message_from_team_acl(self, mock_get_client, mock_syn):
        """Test that the team's ACL entry is reduced to READ only"""
        mock_get_client.return_value = mock_syn
        mock_syn.restGET.return_value = {
            "id": "123",
            "resourceAccess": [
                {"principalId": 123, "accessType": ["READ", "SEND_MESSAGE"]},
                {"principalId": 456, "accessType": ["READ", "SEND_MESSAGE", "UPDATE"]},
            ],
        }

        participant.disable_team_email(123)

        mock_syn.restGET.assert_called_once_with("/team/123/acl")
        put_payload = mock_syn.restPUT.call_args
        import json

        acl = json.loads(put_payload[0][1])
        team_entry = next(e for e in acl["resourceAccess"] if e["principalId"] == 123)
        assert team_entry["accessType"] == ["READ"]

    @patch("cnb_tools.modules.participant.get_synapse_client")
    def test_does_not_modify_other_acl_entries(self, mock_get_client, mock_syn):
        """Test that only the team's own ACL entry is modified"""
        mock_get_client.return_value = mock_syn
        mock_syn.restGET.return_value = {
            "id": "123",
            "resourceAccess": [
                {"principalId": 123, "accessType": ["READ", "SEND_MESSAGE"]},
                {"principalId": 456, "accessType": ["READ", "SEND_MESSAGE", "UPDATE"]},
            ],
        }

        participant.disable_team_email(123)

        import json

        acl = json.loads(mock_syn.restPUT.call_args[0][1])
        other_entry = next(e for e in acl["resourceAccess"] if e["principalId"] == 456)
        assert "SEND_MESSAGE" in other_entry["accessType"]
