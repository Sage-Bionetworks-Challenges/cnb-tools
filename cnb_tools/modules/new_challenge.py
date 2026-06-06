"""Module for creating challenge infrastructure on the Sage CNB portal.

Scaffolds the standard two-project structure used by challenges hosted on
https://challenges.synapse.org: a live (public) project and a staging
(private) project, with Participants/Organizers teams, per-task evaluation
queues, data folders, and a wiki copied from the CNB challenge template.
"""

import logging

import synapseclient
import synapseutils
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.models import Folder, Project

from cnb_tools.modules import challenge as challenge_module
from cnb_tools.modules import participant
from cnb_tools.modules import permissions
from cnb_tools.modules import queue as queue_module
from cnb_tools.modules.client import get_synapse_client

logger = logging.getLogger(__name__)


#: Synapse ID of the 'Curated Challenge Projects' submission view on the portal.
PORTAL_TABLE = "syn51476218"
#: Synapse ID of the CNB challenge wiki template project.
CHALLENGE_TEMPLATE_SYNID = "syn52941681"
#: Synapse user/team ID for the Sage CNB admin team.
SAGE_CNB_TEAM = "3379097"


def _create_project(name: str) -> Project:
    """Create a Synapse project and return the stored instance."""
    project = Project(name=name)
    project = project.store()
    logger.info(f"Project created: {project.name} ({project.id})")
    return project


def _create_live_wiki(project_id: str) -> None:
    """Create a placeholder 'coming soon' wiki on the live project."""
    syn = get_synapse_client()
    markdown = (
        '<div align="center" class="alert alert-info">\n\n'
        "###! More information coming soon!\n\n</div>\n"
    )
    syn.store(synapseclient.Wiki(title="", owner=project_id, markdown=markdown))


def _update_wikipage_string(
    wikipage_string: str,
    challenge_id: str,
    team_id: str,
    challenge_name: str,
    syn_id: str,
) -> str:
    """Replace CNB template placeholders with the real IDs for this challenge."""
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
    )
    return {
        "team_part_id": str(team_part.id),
        "team_org_id": str(team_org.id),
    }


def _create_challenge_widget(project_id: str, team_part_id: str):
    """Activate the live project as a challenge.

    Creates the challenge widget if it does not already exist, otherwise
    returns the existing challenge object.
    """
    try:
        chal_obj = challenge_module.create_challenge(project_id, team_part_id)
        logger.info(f"Activated as Challenge (ID: {chal_obj['id']})")
    except SynapseHTTPError:
        chal_obj = challenge_module.get_challenge(project_id)
        logger.info(f"Fetched existing Challenge (ID: {chal_obj['id']})")
    return chal_obj


def _create_data_folders(project_id: str, tasks_count: int) -> dict[int, str]:
    """Create one data folder per task on the live project."""
    folder_ids: dict[int, str] = {}
    for i in range(tasks_count):
        folder = Folder(name=f"Task {i + 1}", parent_id=project_id)
        folder = folder.store()
        folder_ids[i] = str(folder.id)
        logger.info(f"Folder created: {folder.name} ({folder.id})")
    return folder_ids


def _check_existing_and_delete_wiki(project_id: str) -> None:
    """If the staging project already has a wiki, prompt the user to delete it."""
    syn = get_synapse_client()
    wiki = None
    try:
        wiki = syn.getWiki(project_id)
    except SynapseHTTPError:
        pass

    if wiki is not None:
        logger.info("The staging project already has a wiki.")
        user_input = input("Delete the existing wiki before continuing? (y/N) ") or "n"
        if user_input.lower() not in ("y", "yes"):
            logger.info("Exiting.")
            sys.exit(1)
        syn.delete(wiki)
        logger.info(f"Deleted wiki ({wiki.id}) from staging project.")


def _add_to_portal(project_id: str) -> None:
    """Register the live project in the CNB portal's curated projects table."""
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
    """Create a new challenge on the Sage CNB portal.

    Scaffolds:

    - **Teams**: Participants (public join) and Organizers.
    - **Live project**: placeholder wiki, one evaluation queue + data folder
      per task, permissions granted to Organizers and the CNB admin team.
    - **Staging project**: wiki copied from the CNB template and updated with
      the real challenge/team/project IDs.
    - **Portal registration** (optional): adds the live project to the CNB
      portal's curated-challenges submission view.

    Args:
        challenge_name: Name of the new challenge.
        tasks_count: Number of task evaluation queues and data folders to
            create. Default is ``1``.
        live_site: Synapse ID of an already-existing live project. If given,
            no new live project is created and the caller is responsible for
            its permissions and wiki. Default is ``None``.
        add_to_portal: Whether to register the challenge in the CNB portal
            table. Default is ``True``.

    Returns:
        A ``dict`` with keys ``live_projectid``, ``staging_projectid``,
        ``organizer_teamid``, and ``participant_teamid``.
    """
    syn = get_synapse_client()
    teams = _create_teams(challenge_name)

    # --- Live project -------------------------------------------------------
    if live_site is None:
        project_live = _create_project(challenge_name)
        permissions.set_entity_permissions(
            project_live.id, teams["team_org_id"], permission_level="moderate"
        )
        permissions.set_entity_permissions(
            project_live.id, SAGE_CNB_TEAM, permission_level="admin"
        )
        _create_live_wiki(project_live.id)
    else:
        live_entity = syn.get(live_site, downloadFile=False)
        project_live = Project(id=live_site, name=live_entity.name)

    challenge_obj = _create_challenge_widget(project_live.id, teams["team_part_id"])

    for i in range(tasks_count):
        ev = queue_module.create_evaluation(
            name=f"{challenge_name} Task {i + 1}",
            description=f"Task {i + 1} Submission",
            project_id=project_live.id,
        )
        permissions.set_evaluation_permissions(
            ev.id, SAGE_CNB_TEAM, permission_level="admin"
        )

    folders = _create_data_folders(project_live.id, tasks_count)
    for folder_id in folders.values():
        permissions.set_entity_permissions(
            folder_id, teams["team_org_id"], permission_level="download"
        )
        permissions.set_entity_permissions(
            folder_id, teams["team_part_id"], permission_level="download"
        )

    # --- Staging project ----------------------------------------------------
    project_staging = _create_project(f"{challenge_name} - staging")
    permissions.set_entity_permissions(
        project_staging.id, teams["team_org_id"], permission_level="edit"
    )
    permissions.set_entity_permissions(
        project_staging.id, SAGE_CNB_TEAM, permission_level="admin"
    )

    _check_existing_and_delete_wiki(project_staging.id)
    logger.info(f"Copying wiki template to {project_staging.name}")
    new_wikiids = synapseutils.copyWiki(
        syn, CHALLENGE_TEMPLATE_SYNID, project_staging.id
    )
    for page in new_wikiids:
        wikipage = syn.getWiki(project_staging.id, page["id"])
        wikipage.markdown = _update_wikipage_string(
            wikipage.markdown,
            challenge_obj["id"],
            teams["team_part_id"],
            challenge_name,
            project_live.id,
        )
        syn.store(wikipage)

    if add_to_portal:
        _add_to_portal(project_live.id)

    return {
        "live_projectid": project_live.id,
        "staging_projectid": project_staging.id,
        "organizer_teamid": teams["team_org_id"],
        "participant_teamid": teams["team_part_id"],
    }
