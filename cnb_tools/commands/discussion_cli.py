"""CLI command: discussion

Manage Synapse discussion forums and threads.

Example:
    $ cnb-tools discussion --help
"""

from typing_extensions import Annotated
import typer

from cnb_tools.modules import discussion

app = typer.Typer()


@app.command()
def list_threads(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the project")],
):
    """List all discussion threads in a project's forum."""
    threads = list(discussion.get_forum_threads(project_id))
    if not threads:
        typer.echo("No threads found.")
        return
    typer.echo(f"{'ID':<12} {'Created by':<20} {'Title'}")
    typer.echo("-" * 60)
    for t in threads:
        typer.echo(f"{t.id:<12} {t.created_by:<20} {t.title}")


@app.command()
def create_thread(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the project")],
    title: Annotated[str, typer.Argument(help="Thread title")],
    message: Annotated[str, typer.Argument(help="Thread body (markdown supported)")],
):
    """Create a new discussion thread in a project's forum."""
    thread = discussion.create_thread(project_id, title, message)
    typer.echo(f"✅ Thread created (ID: {thread.id}): {thread.title}")


@app.command()
def participants(
    project_id: Annotated[str, typer.Argument(help="Synapse ID of the project")],
):
    """List all users who have posted in a project's forum."""
    user_ids = discussion.get_forum_participants(project_id)
    if not user_ids:
        typer.echo("No forum participants found.")
        return
    typer.echo(f"{len(user_ids)} participant(s):")
    for uid in sorted(user_ids):
        typer.echo(f"  {uid}")
