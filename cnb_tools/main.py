from typing import Optional

import typer
from cnb_tools import __version__
from typing_extensions import Annotated

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"cnb-tools v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    CNB Tools - convenience tools/functions for challenges and benchmarking
    """
