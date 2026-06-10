"""CLI command: challenge

Manage challenges.

Example:
    $ cnb-tools challenge --help
"""

import json
import sys

from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools.modules import challenge, new_challenge, permissions
from cnb_tools.modules.client import UnknownSynapseID, get_synapse_client

app = typer.Typer()

# Synapse principal ID for all authenticated users.
_AUTHENTICATED_USERS = 273948

# Synapse principal ID for anonymous/public access.
_PUBLIC = 273949


@app.command()
def create(
    name: Annotated[str, typer.Argument(help="Name of the new challenge")],
    tasks: Annotated[
        int,
        typer.Option(
            "--tasks",
            "-t",
            help="Number of task evaluation queues and data folders to create",
        ),
    ] = 1,
    live_site: Annotated[
        Optional[str],
        typer.Option(
            "--live-site",
            help="Synapse ID of an existing live project (skips live project creation)",
        ),
    ] = None,
    no_portal: Annotated[
        bool,
        typer.Option(
            "--no-portal",
            help="Skip registering the challenge in the Challenge Portal table",
        ),
    ] = False,
):
    """Create a new challenge on Synapse. Use --no-portal to skip registering
    the challenge on the Synapse Challenge Portal (challenges.synapse.org)

    Creates a live project, a staging project, Participants and Organizers
    teams, per-task evaluation queues and data folders, and copies the CNB
    wiki template to the staging project.
    """
    result = new_challenge.main(
        challenge_name=name,
        tasks_count=tasks,
        live_site=live_site,
        add_to_portal=not no_portal,
    )
    typer.echo(f"✅ Challenge creation complete:")
    typer.echo(f"   Live project synID:    {result['live_project_synid']}")
    typer.echo(f"   Participants teamID:    {result['participant_teamid']}")
    typer.echo(f"   Organizers teamID:      {result['organizer_teamid']}")


@app.command()
def launch(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
):
    """Launch a challenge by making the project publicly viewable.

    Grants READ access to all authenticated Synapse users on the project
    and sets the project's Status annotation to 'Active'.
    """
    permissions.set_entity_permissions(
        project_id, _AUTHENTICATED_USERS, permission_level="view"
    )
    permissions.set_entity_permissions(project_id, _PUBLIC, permission_level="view")
    syn = get_synapse_client()
    entity = syn.get(project_id)
    entity["Status"] = "Active"
    syn.store(entity)
    typer.echo(f"✅ {project_id} is now publicly viewable with Status='Active'.")


@app.command()
def register(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the project to register as a challenge")
    ],
    team_id: Annotated[str, typer.Argument(help="Synapse ID of the participant team")],
):
    """Register an existing Synapse project as a challenge.

    Attaches a participant team to the project and creates the challenge
    object, without scaffolding any additional infrastructure.
    """
    try:
        chal = challenge.create_challenge(project_id, team_id)
    except Exception as err:
        sys.exit(f"⛔ {err}")
    typer.echo(f"Challenge ID:          {chal['id']}")
    typer.echo(f"Project ID:            {chal['projectId']}")
    typer.echo(f"Participant Team ID:   {chal['participantTeamId']}")


@app.command()
def unregister(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
):
    """Unregister a Synapse project as a challenge.

    Looks up the challenge by project ID and deletes the challenge object.
    The project and its teams are not affected.
    """
    try:
        chal = challenge.get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    challenge.delete_challenge(chal["id"])
    typer.echo(f"Challenge {chal['id']} unregistered from {project_id}.")


@app.command()
def get(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """Get challenge info for a Synapse project."""
    try:
        chal = challenge.get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    if as_json:
        typer.echo(json.dumps(chal, indent=2))
    else:
        typer.echo(f"Challenge ID:          {chal['id']}")
        typer.echo(f"Project ID:            {chal['projectId']}")
        typer.echo(f"Participant Team ID:   {chal['participantTeamId']}")


@app.command()
def close(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project to close")
    ],
):
    """Close a challenge.

    Sets the project Status annotation to 'Closed', downgrades the
    participant team's evaluation queue permissions from 'Can submit' to
    'Can view', and locks the participant team so no new members can join
    or request membership.
    """
    new_challenge.close_challenge(project_id)
    typer.echo(f"\u2705 Challenge {project_id} is now closed.")
