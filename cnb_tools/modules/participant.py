"""Module for managing submission teams or individual participants.

This module provides utility functions that extend synapseclient for managing
teams and participants in Synapse challenges.
"""

import sys

from synapseclient.models import Team, UserProfile
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.client import get_synapse_client


def get_participant_name(participant_id: int) -> str:
    """Get the name of a participant (team or user).

    Args:
        participant_id: Team ID or User ID.

    Returns:
        Team name or username.
    """
    get_synapse_client()  # ensure login / caching
    try:
        team = Team.from_id(id=participant_id)
        return team.name or ""
    except SynapseHTTPError:
        profile = UserProfile.from_id(user_id=str(participant_id))
        return profile.user_name or ""


def create_team(
    name: str, description: str | None = None, can_public_join: bool = False
) -> Team:
    """Create a new team or return an existing team with the given name.

    Uses ``synapseclient.models.Team`` OOP. If a team with *name* already
    exists the user is prompted to confirm reuse; otherwise a new team is
    created and stored on Synapse.

    Args:
        name: Team name.
        description: Team description (optional).
        can_public_join: Whether the team can be joined publicly.

    Returns:
        The existing or newly created ``synapseclient.models.Team``.

    Raises:
        SystemExit: If the user chooses not to use the existing team.
    """
    get_synapse_client()  # ensure login / caching
    try:
        team = Team.from_name(name=name)
        response = input(f"Team '{name}' already exists. Use this team? (Y/n) ") or "y"
        if response.lower() not in ("y", "yes"):
            sys.exit("OK. Try again with a new challenge name.")
        return team
    except ValueError:
        new_team = Team(
            name=name,
            description=description,
            can_public_join=can_public_join,
        )
        return new_team.create()


def remove_team_member(team_id: int | str, user_id: int | str) -> None:
    """Remove a user from a team.

    Args:
        team_id: Synapse Team ID.
        user_id: Synapse User ID to remove.
    """
    syn = get_synapse_client()
    syn.restDELETE(f"/team/{team_id}/member/{user_id}")


def get_team_member_count(team_id: int | str) -> int:
    """Return the number of users in a team.

    Args:
        team_id: Synapse Team ID.

    Returns:
        User count.
    """
    syn = get_synapse_client()
    result = syn.restGET(f"/teamMembers/count/{team_id}")
    return int(result.get("count", 0))
