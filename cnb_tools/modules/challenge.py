"""Module for managing Synapse Challenges.

Provides functions and a class for creating, retrieving, updating, and
deleting Challenges and their associated teams on Synapse.
"""

import json
import re
from dataclasses import dataclass
from typing import Iterator

from synapseclient import Synapse
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.models import Project

from cnb_tools.modules.client import get_synapse_client, UnknownSynapseID


def _camel_to_snake(name: str) -> str:
    """Convert a camelCase string to snake_case."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


def _from_dict(cls: type, data: dict):
    """Construct a dataclass from an API response dict, converting camelCase keys."""
    converted = {_camel_to_snake(k): v for k, v in data.items()}
    return cls(**{k: v for k, v in converted.items() if k in cls.__dataclass_fields__})


@dataclass
class Challenge:
    """Represents a Synapse Challenge object."""

    id: str
    project_id: str
    participant_team_id: str
    etag: str | None = None


class ChallengeApi:
    """Low-level wrapper around the Synapse Challenge REST API.

    Args:
        syn: An authenticated Synapse client. If not provided, one will be
            created automatically via ``get_synapse_client()``.
    """

    def __init__(self, syn: Synapse | None = None):
        self.syn = syn or get_synapse_client()

    def create_challenge(self, team_id: str, project_id: str) -> Challenge:
        """
        Args:
            team_id: ID of the Synapse participant team.
            project_id: Synapse ID of the project to host the challenge.
        """
        body = {"participantTeamId": team_id, "projectId": project_id}
        result = self.syn.restPOST("/challenge", json.dumps(body))
        return _from_dict(Challenge, result)

    def get_challenge(
        self,
        challenge_id: str | None = None,
        project_id: str | None = None,
    ) -> Challenge:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
            project_id: A Synapse Project ID.

        Raises:
            ValueError: If neither ``challenge_id`` nor ``project_id`` is given.
        """
        if challenge_id is not None:
            url = f"/challenge/{challenge_id}"
        elif project_id is not None:
            url = f"/entity/{project_id}/challenge"
        else:
            raise ValueError("Must provide either `challenge_id` or `project_id`.")
        result = self.syn.restGET(url)
        return _from_dict(Challenge, result)

    def update_challenge(
        self,
        challenge_id: str,
        team_id: str | None = None,
        project_id: str | None = None,
    ) -> Challenge:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
            team_id: New participant team ID (optional).
            project_id: New project ID (optional).
        """
        body = {
            "id": challenge_id,
            "participantTeamId": team_id,
            "projectId": project_id,
        }
        result = self.syn.restPUT(f"/challenge/{challenge_id}", json.dumps(body))
        return _from_dict(Challenge, result)

    def delete_challenge(self, challenge_id: str) -> None:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
        """
        self.syn.restDELETE(f"/challenge/{challenge_id}")

    def get_registered_challenges(self, participant_id: str) -> Iterator[Challenge]:
        """
        Args:
            participant_id: A Synapse User ID.
        """
        for item in self.syn._GET_paginated(
            f"/challenge?participantId={participant_id}"
        ):
            yield _from_dict(Challenge, item)

    def get_registered_participants(self, challenge_id: str) -> list:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
        """
        return list(self.syn._GET_paginated(f"/challenge/{challenge_id}/participant"))

    def get_registered_teams(self, challenge_id: str) -> list:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
        """
        return list(self.syn._GET_paginated(f"/challenge/{challenge_id}/challengeTeam"))

    def register_team(self, challenge_id: str, team_id: str) -> dict:
        """
        Args:
            challenge_id: A Synapse Challenge ID.
            team_id: A Synapse Team ID.
        """
        body = {"challengeId": challenge_id, "teamId": team_id}
        return self.syn.restPOST(
            f"/challenge/{challenge_id}/challengeTeam", json.dumps(body)
        )


# ---------------------------------------------------------------------------
# Public convenience functions
# ---------------------------------------------------------------------------


def get_challenge(project_id: str) -> Challenge:
    """Get the Challenge associated with a Synapse project.

    Args:
        project_id: Synapse ID of the project.

    Returns:
        The Challenge attached to the project.

    Raises:
        UnknownSynapseID: If the project has no associated challenge.
    """
    syn = get_synapse_client()
    api = ChallengeApi(syn)
    try:
        return api.get_challenge(project_id=project_id)
    except SynapseHTTPError as err:
        raise UnknownSynapseID(
            f"⛔ {err.response.json().get('reason')}. "
            "Check the project ID and try again."
        ) from err


def create_challenge(project_id: str, team_id: str) -> Challenge:
    """Create a Challenge on a Synapse project and link a participant team.

    Args:
        project_id: Synapse ID of the project to host the challenge.
        team_id: Synapse ID of the participant team.

    Returns:
        The newly created Challenge.
    """
    syn = get_synapse_client()
    api = ChallengeApi(syn)
    return api.create_challenge(team_id=team_id, project_id=project_id)


def get_registered_challenges(userid: str | None = None) -> Iterator[Project]:
    """Yield all Synapse challenge projects the user is registered for.

    Args:
        userid: Synapse User ID. Defaults to the currently logged-in user.

    Yields:
        ``synapseclient.models.Project`` objects.
    """
    syn = get_synapse_client()
    api = ChallengeApi(syn)
    profile = syn.getUserProfile(userid)
    for challenge in api.get_registered_challenges(str(profile["ownerId"])):
        yield Project(id=challenge.project_id).get(download_file=False)
