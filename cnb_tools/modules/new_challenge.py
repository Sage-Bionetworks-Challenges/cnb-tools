"""Module for creating a new challenge site on Synapse.

Scaffolds the single-project structure used by challenges hosted on
https://challenges.synapse.org: a live project with Participants/Organizers
teams, per-task evaluation queues, data folders, and a wiki copied from the
Portal Challenge template.
"""

import logging

import synapseutils
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.models import Folder, Project

from cnb_tools.modules import challenge as challenge_module
from cnb_tools.modules import participant
from cnb_tools.modules import permissions
from cnb_tools.modules import queue as queue_module
from cnb_tools.modules.client import get_synapse_client

logger = logging.getLogger(__name__)


# Synapse ID of the 'Curated Challenge Projects' submission view on the portal.
PORTAL_TABLE = "syn51476218"

# Synapse ID of the CNB challenge wiki template project.
CHALLENGE_TEMPLATE_SYNID = "syn52941681"

# Synapse user/team ID for the Sage CNB admin team.
SAGE_CNB_TEAM = "3379097"


def _create_project(name: str) -> Project:
    """Create a Synapse project and return the stored instance."""
    project = Project(name=name)
    project = project.store()
    logger.info(f"Project created: {project.name} ({project.id})")
    return project


def _update_wikipage_string(
    wikipage_string: str,
    challenge_id: str,
    team_id: str,
    challenge_name: str,
    syn_id: str,
) -> str:
    """Replace portal template placeholders with the real IDs for this challenge."""
    replacements = {
        "challengeId=0": f"challengeId={challenge_id}",
        "{teamId}": team_id,
        "teamId=0": f"teamId={team_id}",
        "#!Map:0": f"#!Map:{team_id}",
        "{challengeName}": challenge_name,
        "projectId=syn0": f"projectId={syn_id}",
    }
    for old, new in replacements.items():
        wikipage_string = wikipage_string.replace(old, new)
    return wikipage_string


def _create_teams(challenge_name: str) -> dict[str, str]:
    """Create the Participants and Organizers teams for the challenge."""
    team_part = participant.create_team(
        name=f"{challenge_name} Participants",
        description="Challenge Participant Team",
        can_public_join=True,
    )
    team_org = participant.create_team(
        name=f"{challenge_name} Organizers",
        description="Challenge Organizing Team",
        can_public_join=False,
    )
    return {
        "participant_team_id": str(team_part.id),
        "organizer_team_id": str(team_org.id),
    }


def _create_challenge_widget(project_id: str, participant_team_id: str):
    """Activate the live project as a challenge.

    Creates the challenge widget if it does not already exist, otherwise
    returns the existing challenge object.
    """
    try:
        chal_obj = challenge_module.create_challenge(
            project_id,
            participant_team_id,
        )
        logger.info(f"Activated as Challenge (ID: {chal_obj['id']})")
    except SynapseHTTPError:
        chal_obj = challenge_module.get_challenge(project_id)
        logger.info(f"Fetched existing Challenge (ID: {chal_obj['id']})")
    return chal_obj


def _create_data_folders(
    project_id: str,
    organizer_team_id: str,
    participant_team_id: str,
) -> None:
    """Create Data and Private Data folders with subfolders.

    - Data (Training, Validation): participants receive download access.
    - Private Data (Groundtruth, Test): organizers only.
    """
    public_folder = Folder(name="Data", parent_id=project_id)
    public_folder = public_folder.store()
    logger.info(f"Folder created: {public_folder.name} ({public_folder.id})")
    permissions.set_entity_permissions(
        public_folder.id, organizer_team_id, permission_level="edit"
    )
    permissions.set_entity_permissions(
        public_folder.id, participant_team_id, permission_level="download"
    )
    for name in ("Training", "Validation"):
        sub = Folder(name=name, parent_id=public_folder.id)
        sub.store()
        logger.info(f"  Subfolder created: {name}")

    private_folder = Folder(name="Private Data", parent_id=project_id)
    private_folder = private_folder.store()
    logger.info(f"Folder created: {private_folder.name} ({private_folder.id})")
    permissions.set_entity_permissions(
        private_folder.id, organizer_team_id, permission_level="edit"
    )
    for name in ("Groundtruth", "Test"):
        sub = Folder(name=name, parent_id=private_folder.id)
        sub.store()
        logger.info(f"  Subfolder created: {name}")


def _add_to_portal(project_id: str) -> None:
    """Register the live project in the Challenge Portal's curated projects table."""
    syn = get_synapse_client()
    project_view = syn.get(PORTAL_TABLE)
    project_view.scopeIds.append(project_id)
    syn.store(project_view)
    logger.info(f"Challenge added to 'Curated Challenge Projects' ({PORTAL_TABLE})")


def main(
    challenge_name: str,
    tasks_count: int = 1,
    live_site: str | None = None,
    add_to_portal: bool = True,
) -> dict[str, str]:
    """Create a new challenge ready for release on the Challenge Portal.

    Create the full challenge project in a single call:

    - **Teams**: Participants and Organizers.
    - **Evaluation queues**: one queue per task.
    - **Data folders**: ``Data/`` (Training, Validation — open to participants)
      and ``Private Data/`` (Groundtruth, Test — organizers only).
    - **Wiki**: copied from the portal template and updated with the real challenge/team/project IDs.
    - **Portal registration** (optional): adds the project to the Curated Challenges table.

    Tip: Example Use Case
      Create a two-task challenge from a single command without
      touching the Synapse web interface.

    Args:
      challenge_name: Name of the new challenge.
      tasks_count: Number of task evaluation queues to create. Default ``1``.
      live_site: Synapse ID of an already-existing project to use as the
        live site. If given, no new project is created and the caller is
        responsible for its permissions and wiki. Default ``None``.
      add_to_portal: Whether to register the challenge in the Challenge Portal
        table. Default ``True``.

    Returns:
      A dict with keys ``live_project_synid``, ``organizer_team_id``, and
      ``participant_team_id``.
    """
    syn = get_synapse_client()
    teams = _create_teams(challenge_name)
    participant.disable_team_email(teams["participant_team_id"])

    # --- Project -------------------------------------------------------
    if live_site is None:
        project_live = _create_project(challenge_name)
        permissions.set_entity_permissions(
            project_live.id,
            teams["organizer_team_id"],
            permission_level="moderate",
        )
        permissions.set_entity_permissions(
            project_live.id,
            SAGE_CNB_TEAM,
            permission_level="admin",
        )
        project_entity = syn.get(project_live.id)
        project_entity["Status"] = "Upcoming"
        syn.store(project_entity)
    else:
        live_entity = syn.get(live_site, downloadFile=False)
        project_live = Project(id=live_site, name=live_entity.name)

    challenge_obj = _create_challenge_widget(
        project_live.id,
        teams["participant_team_id"],
    )

    for i in range(tasks_count):
        ev = queue_module.create_evaluation(
            name=f"{challenge_name} Task {i + 1}",
            description=f"Task {i + 1} Submission",
            project_id=project_live.id,
        )
        permissions.set_evaluation_permissions(
            ev.id, SAGE_CNB_TEAM, permission_level="admin"
        )

    _create_data_folders(
        project_live.id,
        organizer_team_id=teams["organizer_team_id"],
        participant_team_id=teams["participant_team_id"],
    )

    # --- Wiki ---------------------------------------------------------------
    logger.info(f"Copying wiki template to {project_live.name}")
    new_wikiids = synapseutils.copyWiki(syn, CHALLENGE_TEMPLATE_SYNID, project_live.id)
    for page in new_wikiids:
        wikipage = syn.getWiki(project_live.id, page["id"])
        wikipage.markdown = _update_wikipage_string(
            wikipage.markdown,
            challenge_obj["id"],
            teams["participant_team_id"],
            challenge_name,
            project_live.id,
        )
        syn.store(wikipage)

    if add_to_portal:
        _add_to_portal(project_live.id)

    return {
        "live_project_synid": project_live.id,
        "organizer_team_id": teams["organizer_team_id"],
        "participant_team_id": teams["participant_team_id"],
    }


def close_challenge(project_id: str) -> None:
    """Close a challenge by locking submissions and the participant team.

    Performs three actions in sequence:

    1. Sets the project's ``Status`` annotation to ``"Closed"``.
    2. Downgrades the participant team's evaluation queue permissions from
       ``"submit"`` to ``"view"`` on every queue in the project.
    3. Locks the participant team so no new members can join or request
       membership.

    Tip: Example Use Case
      Run this after the submission deadline to prevent new submissions
      while keeping the project and results visible.

    Args:
      project_id: Synapse ID of the challenge project.
    """
    syn = get_synapse_client()

    challenge_obj = challenge_module.get_challenge(project_id)
    participant_team_id = challenge_obj["participantTeamId"]

    # 1. Mark the project as Closed
    entity = syn.get(project_id)
    entity["Status"] = "Closed"
    syn.store(entity)
    logger.info(f"Project {project_id} Status set to 'Closed'")

    # 2. Downgrade participant team permissions on every queue
    eval_ids = queue_module.get_evaluation_ids_by_project(project_id)
    for eval_id in eval_ids:
        permissions.set_evaluation_permissions(
            eval_id, participant_team_id, permission_level="view"
        )
        logger.info(
            f"Evaluation {eval_id}: participant team downgraded to view-only"
        )

    # 3. Lock the participant team
    participant.lock_team(participant_team_id)
    logger.info(f"Participant team {participant_team_id} locked (no public join or requests)")
