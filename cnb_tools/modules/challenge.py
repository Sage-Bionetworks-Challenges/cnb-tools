"""Module for managing Synapse Challenges.

Thin wrappers over the Synapse Challenge REST API. All functions return the
raw dict from the API so callers are not coupled to any local dataclass — when
synapseclient ships native Challenge support these can be replaced one-for-one.
"""

import json

from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID


def get_challenge(project_id: str) -> dict:
    """Get the Challenge associated with a Synapse project.

    Args:
        project_id: Synapse ID of the project.

    Returns:
        Challenge dict with keys ``id``, ``projectId``, ``participantTeamId``,
        and ``etag``.

    Raises:
        UnknownSynapseID: If the project has no associated challenge.
    """
    syn = get_synapse_client()
    try:
        return syn.restGET(f"/entity/{project_id}/challenge")
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. "
            "Check the project ID and try again."
        ) from err


def create_challenge(project_id: str, team_id: str) -> dict:
    """Create a Challenge on a Synapse project and link a participant team.

    Args:
        project_id: Synapse ID of the project to host the challenge.
        team_id: Synapse ID of the participant team.

    Returns:
        The newly created Challenge dict.
    """
    syn = get_synapse_client()
    body = {"participantTeamId": team_id, "projectId": project_id}
    return syn.restPOST("/challenge", json.dumps(body))


def delete_challenge(challenge_id: str) -> None:
    """Delete a Challenge.

    Args:
        challenge_id: A Synapse Challenge ID.
    """
    syn = get_synapse_client()
    syn.restDELETE(f"/challenge/{challenge_id}")


def get_registered_teams(challenge_id: str) -> list[dict]:
    """Get all teams registered to a challenge.

    Args:
        challenge_id: A Synapse Challenge ID.

    Returns:
        List of challenge-team record dicts.
    """
    syn = get_synapse_client()
    return list(syn._GET_paginated(f"/challenge/{challenge_id}/challengeTeam"))
