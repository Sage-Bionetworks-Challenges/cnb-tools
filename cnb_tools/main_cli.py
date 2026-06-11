"""Main CLI application.

Examples:
    $ cnb-tools
    $ cnb-tools --help
    $ cnb-tools --version
"""

from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools import __version__
from cnb_tools.commands import (
    challenge_cli,
    queue_cli,
    submission_cli,
)

app = typer.Typer(rich_markup_mode="rich")
app.add_typer(
    challenge_cli.app,
    name="challenge",
    help="Create and manage Synapse challenges.",
)
app.add_typer(
    queue_cli.app,
    name="queue",
    help="Manage evaluation queues and submission quotas.",
)
app.add_typer(
    submission_cli.app,
    name="submission",
    help=("Manage submissions."),
)


def version_callback(value: bool):
    if value:
        print(f"cnb-tools v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Manage challenges on Synapse.org from the CLI

    [blue](Note: some commands will require challenge admin permissions)[/blue]
    """
    if ctx.invoked_subcommand is None:
        print("Manage challenges on Synapse.org from the CLI\n")
        print("Enter `cnb-tools --help` for usage information.")
