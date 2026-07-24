"""CLI command: challenge

Manage challenges.

Example:
    $ cnb-tools challenge --help
"""

import dataclasses
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import typer
from typing_extensions import Annotated

from cnb_tools.modules import challenge, new_challenge, participant, permissions, queue
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

    Creates a live project, Participants and Organizers teams, per-task
    evaluation queues, and data folders, and copies the CNB wiki template
    to the project.
    """
    result = new_challenge.main(
        challenge_name=name,
        tasks_count=tasks,
        live_site=live_site,
        add_to_portal=not no_portal,
    )
    typer.echo("✅ Challenge creation complete:")
    typer.echo(f"   Live project synID:    {result['live_project_synid']}")
    typer.echo(f"   Participants teamID:    {result['participant_teamid']}")
    typer.echo(f"   Organizers teamID:      {result['organizer_teamid']}")


@app.command()
def launch(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
):
    """Launch a challenge by making the project publicly viewable.

    Grants READ access to all authenticated Synapse users on the project
    and sets the project's Status annotation to 'Active'.
    """
    permissions.set_entity_permissions(project_id, _AUTHENTICATED_USERS, permission_level="view")
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
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
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
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
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
def teams(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """List all teams registered to a challenge."""
    try:
        chal = challenge.get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    registered = challenge.get_registered_teams(chal["id"])
    if as_json:
        typer.echo(json.dumps(registered, indent=2))
    else:
        if not registered:
            typer.echo("No teams registered.")
            return
        from cnb_tools.modules.participant import get_participant_name

        def _resolve(entry: dict) -> tuple[str, str]:
            team_id = entry.get("teamId", "")
            try:
                name = get_participant_name(int(team_id))
            except Exception:
                name = ""
            return team_id, name

        results: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=min(8, len(registered))) as pool:
            futures = {pool.submit(_resolve, e): e for e in registered}
            for future in as_completed(futures):
                team_id, name = future.result()
                results[team_id] = name
        for entry in registered:
            team_id = entry.get("teamId", "")
            name = results.get(team_id, "")
            line = f"  {team_id}"
            if name:
                line += f"  {name}"
            typer.echo(line)


@app.command()
def queues(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """List all evaluation queues for a challenge project."""
    try:
        evaluations = queue.get_evaluations_by_project(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    if not evaluations:
        typer.echo(f"No evaluation queues found for {project_id}.")
        return
    if as_json:
        typer.echo(json.dumps([dataclasses.asdict(ev) for ev in evaluations], indent=2))
    else:
        for ev in evaluations:
            typer.echo(f"{ev.id}  {ev.name}")


@app.command()
def close(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project to close")],
):
    """Close a challenge.

    Sets the project Status annotation to 'Closed', downgrades the
    participant team's evaluation queue permissions from 'Can submit' to
    'Can view', and locks the participant team so no new members can join
    or request membership.
    """
    new_challenge.close_challenge(project_id)
    typer.echo(f"\u2705 Challenge {project_id} is now closed.")


@app.command()
def stats(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the challenge project")],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """Show basic statistics for a challenge.

    Reports registered participants, registered teams, evaluation queues,
    total submissions across all queues (fetched in parallel), and
    discussion thread count.
    """
    syn = get_synapse_client()

    try:
        chal = challenge.get_challenge(project_id)
    except UnknownSynapseID as err:
        sys.exit(err)

    challenge_id = chal["id"]
    participant_team_id = chal["participantTeamId"]

    num_participants = participant.get_team_member_count(participant_team_id)
    num_teams = len(challenge.get_registered_teams(challenge_id))

    try:
        evaluations = queue.get_evaluations_by_project(project_id)
    except UnknownSynapseID:
        evaluations = []
    num_queues = len(evaluations)

    def _count_submissions(ev) -> int:
        return syn.restGET(f"/evaluation/{ev.id}/submission/count")

    if evaluations:
        with ThreadPoolExecutor(max_workers=min(8, len(evaluations))) as pool:
            submissions_per_queue = list(pool.map(_count_submissions, evaluations))
        num_submissions = sum(submissions_per_queue)
    else:
        num_submissions = 0

    if as_json:
        result: dict = {
            "project_id": project_id,
            "registered_participants": num_participants,
            "registered_teams": num_teams,
            "evaluation_queues": num_queues,
            "total_submissions": num_submissions,
        }
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"Registered participants: {num_participants}")
        typer.echo(f"Registered teams:        {num_teams}")
        typer.echo(f"Evaluation queues:       {num_queues}")
        typer.echo(f"Total submissions:       {num_submissions}")
