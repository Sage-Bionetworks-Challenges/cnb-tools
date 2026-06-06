"""CLI command: team

Manage Synapse teams and their users.

Example:
    $ cnb-tools team --help
"""

from typing_extensions import Annotated
import typer

from synapseclient.models import Team

from cnb_tools.modules import participant
from cnb_tools.modules.client import get_synapse_client

app = typer.Typer()


@app.command()
def create(
    name: Annotated[str, typer.Argument(help="Team name")],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Team description"),
    ] = "",
    public: Annotated[
        bool,
        typer.Option("--public", help="Allow anyone to join without an invitation"),
    ] = False,
):
    """Create a new Synapse team."""
    team = participant.create_team(
        name=name,
        description=description or None,
        can_public_join=public,
    )
    typer.echo(f"✅ Team '{team.name}' ready (ID: {team.id}).")


@app.command(name="list")
def list_members(
    team_id: Annotated[int, typer.Argument(help="Team ID")],
):
    """List all users in a team."""
    get_synapse_client()  # ensure login
    team = Team.from_id(id=team_id)
    members = list(team.members())
    if not members:
        typer.echo("No users found.")
        return
    typer.echo(f"{len(members)} user(s) in '{team.name}':\n")
    typer.echo(f"  {'Username':<30} {'User ID'}")
    typer.echo(f"  {'-'*30} {'-'*10}")
    for m in members:
        if m.member:
            typer.echo(f"  {m.member.user_name or '—':<30} {m.member.owner_id}")


@app.command()
def remove_user(
    team_id: Annotated[int, typer.Argument(help="Team ID")],
    user_id: Annotated[int, typer.Argument(help="User ID to remove")],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="❗Are you sure you want to remove this user?",
            help="Skip confirmation prompt",
        ),
    ] = False,
):
    """Remove a user from a team."""
    if force:
        participant.remove_team_member(team_id, user_id)
        typer.echo(f"✅ User {user_id} removed from team {team_id}.")
    else:
        typer.echo("No changes made.")


@app.command()
def invite(
    team_id: Annotated[int, typer.Argument(help="Team ID")],
    user: Annotated[
        str,
        typer.Argument(help="Username or user ID to invite"),
    ],
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Invitation message"),
    ] = "",
):
    """Invite a user to a team."""
    get_synapse_client()  # ensure login
    team = Team.from_id(id=team_id)
    result = team.invite(user=user, message=message)
    if result is None:
        typer.echo(f"User '{user}' is already in '{team.name}'.")
    else:
        typer.echo(f"✅ Invitation sent to '{user}' for team '{team.name}'.")
