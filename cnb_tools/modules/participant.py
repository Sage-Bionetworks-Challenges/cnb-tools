"""Module for managing submission teams or individual participants.

This module provides utility functions that extend synapseclient for managing
teams and participants in Synapse challenges.
"""

import sys

import typer
from synapseclient import Team
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.base import get_synapse_client


def get_participant_name(participant_id: int) -> str:
    """Get the name of a participant (team or user).

    Args:
        participant_id: Team ID or User ID

    Returns:
        Team name or username
    """
    syn = get_synapse_client()
    try:
        return syn.getTeam(participant_id).get("name")
    except SynapseHTTPError:
        return syn.getUserProfile(participant_id).get("userName")


def create_team(
    name: str, description: str | None = None, can_public_join: bool = False
) -> Team:
    """Create a new team or get an existing team by name.

    Args:
        name: Team name
        description: Team description (optional)
        can_public_join: Whether the team can be joined publicly

    Returns:
        Team object (existing or new)

    Raises:
        SystemExit: If user chooses not to use an existing team
    """
    syn = get_synapse_client()
    try:
        team = syn.getTeam(name)
        use_team = typer.confirm(f"Team '{name}' already exists. Use this team?")
        if not use_team:
            sys.exit("OK. Try again with a new challenge name.")
    except ValueError:
        team = Team(name=name, description=description, canPublicJoin=can_public_join)
        # team = syn.store(team)
    return team
