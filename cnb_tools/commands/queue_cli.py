"""CLI command: queue

Manage Synapse evaluation queues.

Example:
    $ cnb-tools queue --help
"""

import json
import sys
from typing import Optional
from typing_extensions import Annotated
import typer

from cnb_tools.modules import queue
from cnb_tools.modules.client import UnknownSynapseID

app = typer.Typer()


@app.command()
def get(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Output raw JSON instead of formatted text"),
    ] = False,
):
    """Get details about an evaluation queue."""
    try:
        ev = queue.get_evaluation(evaluation_id)
    except UnknownSynapseID as err:
        sys.exit(err)
    if as_json:
        typer.echo(json.dumps(dict(ev), indent=2))
    else:
        typer.echo(f"ID:          {ev.id}")
        typer.echo(f"Name:        {ev.name}")
        typer.echo(f"Description: {ev.description or '—'}")
        typer.echo(f"Project:     {ev.contentSource}")
        if ev.quota:
            typer.echo(f"Quota:       {ev.quota}")


@app.command()
def set_quota(
    evaluation_id: Annotated[int, typer.Argument(help="Evaluation queue ID")],
    first_round_start: Annotated[
        Optional[str],
        typer.Option(
            "--start",
            help='Local datetime for the first round start, e.g. "2025-01-01 00:00:00"',
        ),
    ] = None,
    round_duration_millis: Annotated[
        Optional[int],
        typer.Option("--round-duration", help="Duration of each round in milliseconds"),
    ] = None,
    number_of_rounds: Annotated[
        Optional[int],
        typer.Option("--rounds", help="Total number of rounds"),
    ] = None,
    submissions_per_round: Annotated[
        Optional[int],
        typer.Option("--per-round", help="Max submissions per participant per round"),
    ] = None,
    total_submissions: Annotated[
        Optional[int],
        typer.Option("--total", help="Hard cap on total submissions per participant"),
    ] = None,
):
    """Set the submission quota for an evaluation queue.

    Only the options you provide are updated; existing quota settings are
    preserved.
    """
    try:
        queue.set_evaluation_quota(
            evaluation_id,
            first_round_start=first_round_start,
            round_duration_millis=round_duration_millis,
            number_of_rounds=number_of_rounds,
            submissions_per_round=submissions_per_round,
            total_submissions=total_submissions,
        )
    except UnknownSynapseID as err:
        sys.exit(err)
    typer.echo(f"✅ Quota updated for evaluation queue {evaluation_id}.")
