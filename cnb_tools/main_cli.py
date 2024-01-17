"""Reference guide to cnb-tools CLI commands

Manage challenges and benchmarking on Synapse from the CLI.

Examples:
    ```
    $ cnb-tools create-challenge "challenge name" -t 2
    ```

This CLI application contains the following commands:

- `create-challenge` - Creates a new challenge on the Sage Challenge Portal
"""
from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools import __version__
from cnb_tools.commands import submission_cli


app = typer.Typer(rich_markup_mode="rich")
app.add_typer(submission_cli.app, name="submission", help="Manage submissions")


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
    CNB Tools - convenience tools/functions for challenges and
    benchmarking on Synapse.org

    [red](some commands will require admin priviledges)[/red]

    If you are a challenge admin and are experiencing issues, contact us at
    [bold blue]SageCNBTeam@synapse.org[/bold blue]
    """
    if ctx.invoked_subcommand is None:
        print("Manage challenges on Synapse.org from the CLI\n")
        print("Enter `cnb-tools --help` for usage information.")
