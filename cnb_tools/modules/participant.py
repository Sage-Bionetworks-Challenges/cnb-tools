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

    Uses the new ``synapseclient.models`` OOP to look up by ID.

    Args:
        participant_id: Team ID or User ID

    Returns:
        Team name or username
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


def get_team_member_count(team_id: int | str) -> int:
    """Return the number of members in a team.

    Args:
        team_id: Synapse Team ID.

    Returns:
        Member count.
    """
    syn = get_synapse_client()
    result = syn.restGET(f"/teamMembers/count/{team_id}")
    return int(result.get("count", 0))


def remove_team_member(team_id: int | str, user_id: int | str) -> None:
    """Remove a user from a team.

    Args:
        team_id: Synapse Team ID.
        user_id: Synapse User ID to remove.
    """
    syn = get_synapse_client()
    syn.restDELETE(f"/team/{team_id}/member/{user_id}")


def _team_member_ids(team_id: int | str) -> set[str]:
    """Return the set of member IDs for *team_id* (as strings)."""
    get_synapse_client()  # ensure login / caching
    team = Team.from_id(id=int(team_id))
    return {str(m.member.owner_id) for m in team.members() if m.member is not None}


def team_members_diff(team_a_id: int | str, team_b_id: int | str) -> set[str]:
    """Return member IDs in *team_a* that are **not** in *team_b*.

    Args:
        team_a_id: Synapse Team ID for team A.
        team_b_id: Synapse Team ID for team B.

    Returns:
        Set of user IDs (strings) present in A but absent from B.
    """
    return _team_member_ids(team_a_id) - _team_member_ids(team_b_id)


def team_members_intersection(team_a_id: int | str, team_b_id: int | str) -> set[str]:
    """Return member IDs present in **both** *team_a* and *team_b*.

    Args:
        team_a_id: Synapse Team ID for team A.
        team_b_id: Synapse Team ID for team B.

    Returns:
        Set of user IDs (strings) common to both teams.
    """
    return _team_member_ids(team_a_id) & _team_member_ids(team_b_id)


def team_members_union(team_a_id: int | str, team_b_id: int | str) -> set[str]:
    """Return the union of member IDs across both teams.

    Args:
        team_a_id: Synapse Team ID for team A.
        team_b_id: Synapse Team ID for team B.

    Returns:
        Set of all user IDs (strings) that belong to either team.
    """
    return _team_member_ids(team_a_id) | _team_member_ids(team_b_id)
