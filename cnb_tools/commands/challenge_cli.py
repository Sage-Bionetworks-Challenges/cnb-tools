"""CLI command: challenge

Manage challenge.

Example:
    $ cnb-tools challenge --help
"""

from typing_extensions import Annotated
import typer

from cnb_tools.classes.challenge import Challenge

app = typer.Typer()


@app.command()
def create(
    name: Annotated[str, typer.Argument(help="New challenge name")],
    tasks_count: Annotated[
        int,
        typer.Option(
            "--tasks_count", "-t", help="Number of challenge tasks (default: 1)"
        ),
    ] = 1,
    is_private: Annotated[
        bool,
        typer.Option(
            "--private",
            "-p",
            help="Challenge should be private, even to the Sage CNB Team (default: false)",
        ),
    ] = False,
):
    pass
