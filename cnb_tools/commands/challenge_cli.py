"""CLI command: challenge

Manage Synapse challenges.

Example:
    $ cnb-tools challenge --help
"""

import sys

from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools.modules import challenge, create_challenge
from cnb_tools.modules.client import UnknownSynapseID

app = typer.Typer()


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
            help="Skip registering the challenge in the CNB portal table",
        ),
    ] = False,
):
    """Scaffold a new challenge on the Sage CNB portal.

    Creates a live project, a staging project, Participants and Organizers
    teams, per-task evaluation queues and data folders, and copies the CNB
    wiki template to the staging project.
    """
    result = create_challenge.main(
        challenge_name=name,
        tasks_count=tasks,
        live_site=live_site,
        add_to_portal=not no_portal,
    )
    typer.echo(f"✅ Challenge scaffold complete:")
    typer.echo(f"   Live project:    {result['live_projectid']}")
    typer.echo(f"   Staging project: {result['staging_projectid']}")
    typer.echo(f"   Participants:    {result['participant_teamid']}")
    typer.echo(f"   Organizers:      {result['organizer_teamid']}")


@app.command()
def get(
    project_id: Annotated[
        str, typer.Argument(help="Synapse ID of the challenge project")
    ],
):
    """Get challenge info for a Synapse project."""
    try:
        chal = challenge.get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    typer.echo(f"Challenge ID:          {chal.id}")
    typer.echo(f"Project ID:            {chal.project_id}")
    typer.echo(f"Participant Team ID:   {chal.participant_team_id}")
