"""Module for managing submission teams or individual participants.

This module provides utility functions that extend synapseclient for managing
teams and participants in Synapse challenges.
"""

import sys

from synapseclient.models import Team, UserProfile
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.client import get_synapse_client


def get_participant_name(participant_id: int) -> str:
    """Get the display name of a participant (team or individual user).

    Tip: Example Use Case
      Resolve a raw principal ID to a readable name when building a
      list of registered teams or participants.

    Args:
      participant_id: Synapse Team ID or User ID.

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

    Tip: Example Use Case
      Create the Participants team for a new challenge. If the team name
      was used before, you will be prompted to reuse the existing team.

    Args:
      name: Team name.
      description: Team description (optional).
      can_public_join: If True, anyone can join without an invitation.
        Mutually exclusive with ``can_request_membership``.

    Returns:
      The existing or newly created ``synapseclient.models.Team``.

    Raises:
      SystemExit: If the team already exists and the user declines to reuse it.
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
            can_request_membership=not can_public_join,
        )
        return new_team.create()


def remove_team_member(team_id: int | str, user_id: int | str) -> None:
    """Remove a user from a team.

    Tip: Example Use Case
      Remove a participant who violated the challenge rules from the
      Participants team to revoke their submission access.

    Args:
      team_id: Synapse Team ID.
      user_id: Synapse User ID to remove.
    """
    syn = get_synapse_client()
    syn.restDELETE(f"/team/{team_id}/member/{user_id}")


def get_team_member_count(team_id: int | str) -> int:
    """Return the number of users in a team.

    Tip: Example Use Case
      Check how many participants have registered after sending out
      the challenge announcement.

    Args:
      team_id: Synapse Team ID.

    Returns:
      Number of members in the team.
    """
    syn = get_synapse_client()
    result = syn.restGET(f"/teamMembers/count/{team_id}")
    return int(result.get("count", 0))
